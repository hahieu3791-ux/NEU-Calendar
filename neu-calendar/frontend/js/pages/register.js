// Register Page Controller
import { api } from "../api.js";
import { setTokens, setCurrentUser } from "../auth.js";
import { showToast } from "../components/toast.js";
import { renderIcons } from "../utils.js";

document.addEventListener("DOMContentLoaded", () => {
  renderIcons();

  const form = document.getElementById("register-form");
  const submitBtn = document.getElementById("submit-btn");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const fullName = document.getElementById("full-name").value.trim();
    const studentCode = document.getElementById("student-code").value.trim();
    const cohort = document.getElementById("cohort").value.trim();
    const faculty = document.getElementById("faculty").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    if (!fullName || !email || !password) {
      showToast("Vui lòng điền các trường bắt buộc (*)", "error");
      return;
    }

    try {
      submitBtn.disabled = true;
      submitBtn.innerHTML = `<span>Đang tạo tài khoản...</span>`;

      // 1. Register
      await api.post("/auth/register", {
        full_name: fullName,
        student_code: studentCode || null,
        cohort: cohort || null,
        faculty: faculty || null,
        email: email,
        password: password
      });

      // 2. Auto login
      const tokenData = await api.post("/auth/login", { email, password });
      setTokens(tokenData.access_token, tokenData.refresh_token);

      const user = await api.get("/auth/me");
      setCurrentUser(user);

      showToast("Đăng ký thành công! Đang chuyển hướng...", "success");
      setTimeout(() => {
        window.location.href = "dashboard.html";
      }, 600);
    } catch (err) {
      showToast(err.message || "Đăng ký thất bại", "error");
      submitBtn.disabled = false;
      submitBtn.innerHTML = `
        <i data-lucide="user-plus" style="width: 18px; height: 18px;"></i>
        <span>Đăng ký ngay</span>
      `;
      renderIcons();
    }
  });
});
