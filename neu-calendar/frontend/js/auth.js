// Authentication State Manager

export function getAccessToken() {
  return localStorage.getItem("neu_access_token");
}

export function getRefreshToken() {
  return localStorage.getItem("neu_refresh_token");
}

export function setTokens(accessToken, refreshToken) {
  if (accessToken) localStorage.setItem("neu_access_token", accessToken);
  if (refreshToken) localStorage.setItem("neu_refresh_token", refreshToken);
}

export function getCurrentUser() {
  const userJson = localStorage.getItem("neu_user");
  if (!userJson) return null;
  try {
    return JSON.parse(userJson);
  } catch {
    return null;
  }
}

export function setCurrentUser(user) {
  if (user) {
    localStorage.setItem("neu_user", JSON.stringify(user));
  } else {
    localStorage.removeItem("neu_user");
  }
}

export function clearAuth() {
  localStorage.removeItem("neu_access_token");
  localStorage.removeItem("neu_refresh_token");
  localStorage.removeItem("neu_user");
}

export function checkAuth(redirectIfUnauthenticated = true) {
  const token = getAccessToken();
  if (!token) {
    if (redirectIfUnauthenticated) {
      window.location.href = "login.html";
    }
    return false;
  }
  return true;
}

export function logout() {
  clearAuth();
  window.location.href = "login.html";
}
