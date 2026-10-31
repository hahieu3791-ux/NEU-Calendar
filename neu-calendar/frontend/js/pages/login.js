// Login Page Controller
import { api } from "../api.js";
import { setTokens, setCurrentUser } from "../auth.js";
import { showToast } from "../components/toast.js";
import { renderIcons } from "../utils.js";

document.addEventListener("DOMContentLoaded", () => {
  renderIcons();

  const form = document.getElementById("login-form");
  const emailInput = document.getElementById("email");
  const passwordInput = document.getElementById("password");
  const submitBtn = document.getElementById("submit-btn");
  const demoBtn = document.getElementById("demo-btn");

  // Quick Demo fill
  if (demoBtn) {
    demoBtn.addEventListener("click", () => {
      emailInput.value = "demo@neu.edu.vn";
      passwordInput.value = "Password123!";
      showToast("Đã điền thông tin tài khoản demo", "info");
      submitBtn.click();
    });
  }

  // Submit Handler
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = emailInput.value.trim();
    const password = passwordInput.value;

    if (!email || !password) {
      showToast("Vui lòng điền đầy đủ email và mật khẩu", "error");
      return;
    }

    try {
      submitBtn.disabled = true;
      submitBtn.innerHTML = `<span>Đang đăng nhập...</span>`;

      const tokenData = await api.post("/auth/login", { email, password });
      setTokens(tokenData.access_token, tokenData.refresh_token);

      // Fetch user profile
      const user = await api.get("/auth/me");
      setCurrentUser(user);

      showToast("Đăng nhập thành công!", "success");
      setTimeout(() => {
        window.location.href = "dashboard.html";
      }, 500);
    } catch (err) {
      showToast(err.message || "Đăng nhập thất bại", "error");
      submitBtn.disabled = false;
      submitBtn.innerHTML = `
        <i data-lucide="log-in" style="width: 18px; height: 18px;"></i>
        <span>Đăng nhập</span>
      `;
      renderIcons();
    }
  });
});
