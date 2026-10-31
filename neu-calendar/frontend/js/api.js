// API Request Client
import { API_BASE_URL } from "./config.js";
import { getAccessToken, getRefreshToken, setTokens, logout } from "./auth.js";

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

async function request(endpoint, options = {}) {
  const url = endpoint.startsWith("http") ? endpoint : `${API_BASE_URL}${endpoint}`;
  
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {})
  };

  const token = getAccessToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const config = {
    ...options,
    headers
  };

  try {
    const res = await fetch(url, config);

    // If 401 Unauthorized, attempt token refresh (except for auth endpoints)
    if (res.status === 401 && !endpoint.includes("/auth/login") && !endpoint.includes("/auth/register") && !endpoint.includes("/auth/refresh")) {
      const refreshToken = getRefreshToken();
      if (!refreshToken) {
        logout();
        throw new Error("Phiên làm việc đã hết hạn");
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then((newToken) => {
          config.headers["Authorization"] = `Bearer ${newToken}`;
          return fetch(url, config).then((r) => r.json());
        });
      }

      isRefreshing = true;

      try {
        const refreshRes = await fetch(`${API_BASE_URL}/auth/refresh`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ refresh_token: refreshToken })
        });

        if (!refreshRes.ok) {
          throw new Error("Không thể làm mới token");
        }

        const data = await refreshRes.json();
        setTokens(data.access_token, data.refresh_token);
        processQueue(null, data.access_token);
        isRefreshing = false;

        // Retry original request with new token
        config.headers["Authorization"] = `Bearer ${data.access_token}`;
        const retryRes = await fetch(url, config);
        return handleResponse(retryRes);
      } catch (refreshErr) {
        processQueue(refreshErr, null);
        isRefreshing = false;
        logout();
        throw new Error("Phiên làm việc hết hạn, vui lòng đăng nhập lại");
      }
    }

    return handleResponse(res);
  } catch (error) {
    throw error;
  }
}

async function handleResponse(res) {
  if (res.status === 204) {
    return null;
  }

  const contentType = res.headers.get("content-type");
  const isJson = contentType && contentType.includes("application/json");
  const data = isJson ? await res.json() : await res.text();

  if (!res.ok) {
    let errorMsg = "Đã xảy ra lỗi";
    if (data && typeof data === "object") {
      errorMsg = data.detail || data.message || JSON.stringify(data);
    } else if (typeof data === "string" && data.trim()) {
      errorMsg = data;
    }
    throw new Error(errorMsg);
  }

  return data;
}

export const api = {
  get: (endpoint) => request(endpoint, { method: "GET" }),
  post: (endpoint, body) => request(endpoint, { method: "POST", body: JSON.stringify(body) }),
  put: (endpoint, body) => request(endpoint, { method: "PUT", body: JSON.stringify(body) }),
  patch: (endpoint, body) => request(endpoint, { method: "PATCH", body: JSON.stringify(body) }),
  delete: (endpoint) => request(endpoint, { method: "DELETE" }),
};
