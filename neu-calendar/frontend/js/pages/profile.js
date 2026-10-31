// Profile & Support Page Controller
import { initNav } from "../nav.js";
import { api } from "../api.js";
import { getCurrentUser, setCurrentUser } from "../auth.js";
import { escapeHtml, formatDateTime, renderIcons } from "../utils.js";
import { showToast } from "../components/toast.js";

document.addEventListener("DOMContentLoaded", async () => {
  initNav();
  setupTabs();
  setupForms();
  await loadProfile();

  // Check URL param tab
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get("tab") === "support") {
    switchTab("support");
  }
});

function setupTabs() {
  document.getElementById("tab-btn-info")?.addEventListener("click", () => switchTab("info"));
  document.getElementById("tab-btn-pwd")?.addEventListener("click", () => switchTab("pwd"));
  document.getElementById("tab-btn-support")?.addEventListener("click", () => switchTab("support"));
}

function switchTab(tabKey) {
  const tabs = ["info", "pwd", "support"];
  tabs.forEach(k => {
    const btn = document.getElementById(`tab-btn-${k}`);
    const content = document.getElementById(`tab-content-${k}`);
    if (k === tabKey) {
      btn?.classList.add("active");
      if (content) content.style.display = "block";
    } else {
      btn?.classList.remove("active");
      if (content) content.style.display = "none";
    }
  });

  if (tabKey === "support") {
    loadSupportHistory();
  }

  renderIcons();
}

async function loadProfile() {
  try {
    const user = await api.get("/users/me");
    setCurrentUser(user);

    document.getElementById("display-full-name").textContent = user.full_name;
    document.getElementById("display-email").textContent = user.email;
    document.getElementById("profile-avatar-box").textContent = user.full_name.charAt(0);

    document.getElementById("prof-name").value = user.full_name;
    document.getElementById("prof-code").value = user.student_code || "";
    document.getElementById("prof-cohort").value = user.cohort || "";
    document.getElementById("prof-faculty").value = user.faculty || "";
  } catch (err) {
    showToast(err.message || "Lỗi tải thông tin cá nhân", "error");
  }
}

function setupForms() {
  // Update Profile Info
  document.getElementById("profile-info-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fullName = document.getElementById("prof-name").value.trim();
    const studentCode = document.getElementById("prof-code").value.trim();
    const cohort = document.getElementById("prof-cohort").value.trim();
    const faculty = document.getElementById("prof-faculty").value.trim();

    if (!fullName) {
      showToast("Vui lòng nhập họ và tên", "error");
      return;
    }

    try {
      const updated = await api.put("/users/me", {
        full_name: fullName,
        student_code: studentCode || null,
        cohort: cohort || null,
        faculty: faculty || null
      });

      setCurrentUser(updated);
      showToast("Đã cập nhật thông tin thành công!", "success");
      await loadProfile();
    } catch (err) {
      showToast(err.message || "Cập nhật thất bại", "error");
    }
  });

  // Change Password Form
  document.getElementById("change-pwd-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const oldPassword = document.getElementById("old-pwd").value;
    const newPassword = document.getElementById("new-pwd").value;
    const confirmPassword = document.getElementById("confirm-pwd").value;

    if (newPassword !== confirmPassword) {
      showToast("Mật khẩu mới và xác nhận mật khẩu không khớp!", "error");
      return;
    }

    try {
      await api.put("/users/me/change-password", {
        old_password: oldPassword,
        new_password: newPassword
      });

      showToast("Đổi mật khẩu thành công!", "success");
      document.getElementById("change-pwd-form").reset();
    } catch (err) {
      showToast(err.message || "Đổi mật khẩu thất bại", "error");
    }
  });

  // Support Form
  document.getElementById("support-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const subject = document.getElementById("sup-subject").value.trim();
    const message = document.getElementById("sup-msg").value.trim();

    if (!subject || !message) {
      showToast("Vui lòng điền tiêu đề và chi tiết vấn đề", "error");
      return;
    }

    try {
      await api.post("/support", { subject, message });
      showToast("Đã gửi yêu cầu hỗ trợ thành công! Ban quản trị sẽ phản hồi sớm.", "success");
      document.getElementById("support-form").reset();
      await loadSupportHistory();
    } catch (err) {
      showToast(err.message || "Gửi yêu cầu thất bại", "error");
    }
  });
}

async function loadSupportHistory() {
  const container = document.getElementById("support-history-list");
  try {
    const list = await api.get("/support");
    if (!list || list.length === 0) {
      container.innerHTML = `<p style="color: var(--text-muted); font-size: 13px;">Bạn chưa gửi yêu cầu hỗ trợ nào.</p>`;
      return;
    }

    container.innerHTML = list.map(item => {
      let statusBadge = "badge-info";
      let statusText = "Đang chờ xử lý";
      if (item.status === "in_progress") {
        statusBadge = "badge-warning";
        statusText = "Đang xử lý";
      } else if (item.status === "resolved") {
        statusBadge = "badge-self-study";
        statusText = "Đã giải quyết";
      }

      return `
        <div class="support-history-item">
          <div class="support-history-item-header">
            <span class="support-history-item-title">${escapeHtml(item.subject)}</span>
            <div style="display: flex; align-items: center; gap: 8px;">
              <span class="badge ${statusBadge}">${statusText}</span>
              <span style="font-size: 11.5px; color: var(--text-light);">${formatDateTime(item.created_at)}</span>
            </div>
          </div>
          <div class="support-history-item-msg">${escapeHtml(item.message)}</div>
        </div>
      `;
    }).join("");
    renderIcons();
  } catch (err) {
    container.innerHTML = `<p style="color: #DC2626;">Lỗi tải lịch sử hỗ trợ: ${escapeHtml(err.message)}</p>`;
  }
}
