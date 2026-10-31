// Alert Bell & Notification Dropdown Component
import { api } from "../api.js";
import { escapeHtml, formatDateTime, renderIcons } from "../utils.js";
import { showToast } from "./toast.js";

export class AlertBell {
  constructor() {
    this.unreadCount = 0;
    this.alerts = [];
    this.badgeEl = null;
    this.dropdownEl = null;
    this.listEl = null;
    this.isOpen = false;
  }

  init() {
    this.badgeEl = document.getElementById("notif-badge");
    this.dropdownEl = document.getElementById("notif-dropdown");
    this.listEl = document.getElementById("notif-list");
    const notifBtn = document.getElementById("notif-btn");
    const markAllBtn = document.getElementById("mark-all-read-btn");

    if (notifBtn) {
      notifBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        this.toggleDropdown();
      });
    }

    if (markAllBtn) {
      markAllBtn.addEventListener("click", async (e) => {
        e.stopPropagation();
        await this.markAllRead();
      });
    }

    // Close on click outside
    document.addEventListener("click", (e) => {
      if (this.isOpen && this.dropdownEl && !this.dropdownEl.contains(e.target)) {
        this.closeDropdown();
      }
    });

    this.fetchAlerts();
  }

  async fetchAlerts() {
    try {
      const summary = await api.get("/alerts/summary");
      this.unreadCount = summary.total_unread;
      this.alerts = summary.latest_unread;
      this.render();
    } catch (err) {
      console.warn("Could not fetch alert summary", err);
    }
  }

  render() {
    // Update badge
    if (this.badgeEl) {
      if (this.unreadCount > 0) {
        this.badgeEl.textContent = this.unreadCount > 9 ? "9+" : this.unreadCount;
        this.badgeEl.style.display = "flex";
      } else {
        this.badgeEl.style.display = "none";
      }
    }

    // Render list in dropdown
    if (this.listEl) {
      if (!this.alerts || this.alerts.length === 0) {
        this.listEl.innerHTML = `
          <li style="padding: 24px; text-align: center; color: var(--text-muted); font-size: 13px;">
            <i data-lucide="bell-off" style="width: 24px; height: 24px; margin-bottom: 6px; display: inline-block;"></i>
            <p>Không có cảnh báo mới nào.</p>
          </li>
        `;
      } else {
        this.listEl.innerHTML = this.alerts.map(a => {
          let badgeClass = "badge-info";
          let badgeText = "Thông báo";
          if (a.severity === "critical") {
            badgeClass = "badge-critical";
            badgeText = "Khẩn cấp";
          } else if (a.severity === "warning") {
            badgeClass = "badge-warning";
            badgeText = "Cảnh báo";
          }

          return `
            <li class="notif-item ${a.is_read ? '' : 'unread'}" data-id="${a.id}">
              <div class="notif-item-header">
                <span class="badge ${badgeClass}">${badgeText}</span>
                <span class="notif-item-time">${formatDateTime(a.created_at)}</span>
              </div>
              <div style="color: var(--text-main); font-weight: 500;">
                ${escapeHtml(a.message)}
              </div>
            </li>
          `;
        }).join("");

        // Attach click listeners to mark individual alert as read
        this.listEl.querySelectorAll(".notif-item").forEach(item => {
          item.addEventListener("click", async () => {
            const id = item.getAttribute("data-id");
            if (id) {
              await api.patch(`/alerts/${id}/read`);
              this.fetchAlerts();
            }
          });
        });
      }
      renderIcons();
    }
  }

  toggleDropdown() {
    this.isOpen = !this.isOpen;
    if (this.dropdownEl) {
      this.dropdownEl.classList.toggle("show", this.isOpen);
      if (this.isOpen) {
        this.fetchAlerts();
      }
    }
  }

  closeDropdown() {
    this.isOpen = false;
    if (this.dropdownEl) {
      this.dropdownEl.classList.remove("show");
    }
  }

  async markAllRead() {
    try {
      await api.post("/alerts/mark-all-read");
      showToast("Đã đánh dấu tất cả cảnh báo là đã đọc", "success");
      await this.fetchAlerts();
    } catch (err) {
      showToast(err.message || "Lỗi khi cập nhật cảnh báo", "error");
    }
  }
}
