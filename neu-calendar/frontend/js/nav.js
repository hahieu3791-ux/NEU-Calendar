// Top Horizontal Navigation Controller
import { getCurrentUser, checkAuth, logout } from "./auth.js";
import { AlertBell } from "./components/alert-bell.js";
import { escapeHtml, renderIcons } from "./utils.js";

export function initNav(activePage = "") {
  // Verify authentication
  if (!checkAuth(true)) {
    return;
  }

  const user = getCurrentUser() || {
    full_name: "Sinh viên NEU",
    student_code: "11210001",
    cohort: "K64"
  };

  const navHtml = `
    <header class="top-navbar">
      <div class="nav-container">
        <!-- Brand Left -->
        <a href="dashboard.html" class="nav-brand">
          <div class="brand-icon-box">
            <i data-lucide="calendar-check" style="width: 22px; height: 22px;"></i>
          </div>
          <div class="brand-text-box">
            <h1>NEU Calendar</h1>
            <span>Smart Academic Planner</span>
          </div>
        </a>

        <!-- Center Nav Links -->
        <ul class="nav-links" id="nav-links">
          <li class="nav-item">
            <a href="dashboard.html" class="nav-link ${activePage === 'dashboard' ? 'active' : ''}">
              <i data-lucide="layout-dashboard" style="width: 17px; height: 17px;"></i>
              <span>Tổng quan</span>
            </a>
          </li>
          <li class="nav-item">
            <a href="schedule.html" class="nav-link ${activePage === 'schedule' ? 'active' : ''}">
              <i data-lucide="calendar" style="width: 17px; height: 17px;"></i>
              <span>Lịch học</span>
            </a>
          </li>
          <li class="nav-item">
            <a href="exams.html" class="nav-link ${activePage === 'exams' ? 'active' : ''}">
              <i data-lucide="award" style="width: 17px; height: 17px;"></i>
              <span>Lịch thi</span>
            </a>
          </li>
          <li class="nav-item">
            <a href="tasks.html" class="nav-link ${activePage === 'tasks' ? 'active' : ''}">
              <i data-lucide="check-square" style="width: 17px; height: 17px;"></i>
              <span>Deadline</span>
            </a>
          </li>
          <li class="nav-item">
            <a href="planner.html" class="nav-link ${activePage === 'planner' ? 'active' : ''}">
              <i data-lucide="sparkles" style="width: 17px; height: 17px;"></i>
              <span>Kế hoạch học tập</span>
            </a>
          </li>
          <li class="nav-item">
            <a href="chat.html" class="nav-link ${activePage === 'chat' ? 'active' : ''}">
              <i data-lucide="bot" style="width: 17px; height: 17px;"></i>
              <span>Trợ lý AI</span>
            </a>
          </li>
        </ul>

        <!-- Right Side: Alerts & User Profile -->
        <div class="nav-actions">
          <!-- Notification Bell -->
          <div class="notif-wrapper">
            <button class="notif-btn" id="notif-btn" title="Cảnh báo">
              <i data-lucide="bell" style="width: 18px; height: 18px;"></i>
              <span class="notif-badge" id="notif-badge" style="display: none;">0</span>
            </button>
            <div class="notif-dropdown" id="notif-dropdown">
              <div class="notif-header">
                <h4>Cảnh báo & Thông báo</h4>
                <button class="btn btn-outline btn-sm" id="mark-all-read-btn" style="font-size: 11px; padding: 3px 8px;">Đã đọc tất cả</button>
              </div>
              <ul class="notif-list" id="notif-list">
                <li style="padding: 16px; text-align: center; color: var(--text-muted); font-size: 13px;">Đang tải...</li>
              </ul>
            </div>
          </div>

          <!-- User Menu -->
          <div class="user-menu-wrapper">
            <button class="user-btn" id="user-menu-btn">
              <div class="user-avatar">
                ${user.avatar_url ? `<img src="${escapeHtml(user.avatar_url)}" alt="Avatar" />` : escapeHtml(user.full_name.charAt(0))}
              </div>
              <div class="user-info-text">
                <span class="user-info-name">${escapeHtml(user.full_name)}</span>
                <span class="user-info-sub">${escapeHtml(user.student_code || '')} • ${escapeHtml(user.cohort || 'NEU')}</span>
              </div>
              <i data-lucide="chevron-down" style="width: 15px; height: 15px; color: var(--text-muted);"></i>
            </button>
            <div class="user-dropdown" id="user-dropdown">
              <a href="profile.html" class="user-dropdown-item">
                <i data-lucide="user" style="width: 16px; height: 16px;"></i>
                <span>Hồ sơ cá nhân</span>
              </a>
              <a href="profile.html?tab=support" class="user-dropdown-item">
                <i data-lucide="help-circle" style="width: 16px; height: 16px;"></i>
                <span>Hỗ trợ kỹ thuật</span>
              </a>
              <div class="user-dropdown-divider"></div>
              <div class="user-dropdown-item" id="logout-btn" style="color: #DC2626;">
                <i data-lucide="log-out" style="width: 16px; height: 16px;"></i>
                <span>Đăng xuất</span>
              </div>
            </div>
          </div>

          <!-- Mobile Hamburger -->
          <button class="mobile-menu-btn" id="mobile-menu-btn">
            <i data-lucide="menu" style="width: 20px; height: 20px;"></i>
          </button>
        </div>
      </div>
    </header>
  `;

  // Inject navbar at the beginning of body
  const temp = document.createElement("div");
  temp.innerHTML = navHtml;
  document.body.insertBefore(temp.firstElementChild, document.body.firstChild);

  // Initialize Alert Bell
  const bell = new AlertBell();
  bell.init();

  // User Dropdown toggle
  const userBtn = document.getElementById("user-menu-btn");
  const userDropdown = document.getElementById("user-dropdown");
  if (userBtn && userDropdown) {
    userBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      userDropdown.classList.toggle("show");
    });

    document.addEventListener("click", (e) => {
      if (!userDropdown.contains(e.target)) {
        userDropdown.classList.remove("show");
      }
    });
  }

  // Logout Handler
  const logoutBtn = document.getElementById("logout-btn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      logout();
    });
  }

  // Mobile Hamburger Toggle
  const mobileBtn = document.getElementById("mobile-menu-btn");
  const navLinks = document.getElementById("nav-links");
  if (mobileBtn && navLinks) {
    mobileBtn.addEventListener("click", () => {
      navLinks.classList.toggle("mobile-open");
    });
  }

  renderIcons();
}
