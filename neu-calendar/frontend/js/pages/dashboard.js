// Dashboard Page Controller
import { initNav } from "../nav.js";
import { api } from "../api.js";
import { escapeHtml, formatDateTime, formatDate, renderIcons } from "../utils.js";
import { showToast } from "../components/toast.js";
import { openModal, closeModal } from "../components/modal.js";

document.addEventListener("DOMContentLoaded", async () => {
  initNav("dashboard");
  await loadDashboardData();
  setupQuickActions();
});

async function loadDashboardData() {
  try {
    const data = await api.get("/dashboard/summary");

    // 1. Header Hero
    document.getElementById("hero-date-text").textContent = `${data.current_date_text} • ${data.semester_name}`;
    document.getElementById("hero-greeting").textContent = data.greeting;
    document.getElementById("hero-summary-text").innerHTML = escapeHtml(data.subtitle_summary);

    // 2. Top Alert Banner
    const bannerContainer = document.getElementById("top-alert-banner-container");
    if (data.top_alert && !data.top_alert.is_read) {
      const bannerClass = data.top_alert.severity === "critical" ? "alert-banner-critical" : "alert-banner-warning";
      bannerContainer.innerHTML = `
        <div class="alert-banner ${bannerClass}">
          <div class="alert-banner-content">
            <i data-lucide="${data.top_alert.severity === 'critical' ? 'alert-triangle' : 'alert-circle'}" style="width: 20px; height: 20px;"></i>
            <span><strong>Cảnh báo học tập:</strong> ${escapeHtml(data.top_alert.message)}</span>
          </div>
          <button class="btn btn-sm btn-outline" id="banner-dismiss-btn" style="background: rgba(255,255,255,0.7); font-size: 11.5px;">
            Đã hiểu
          </button>
        </div>
      `;
      document.getElementById("banner-dismiss-btn")?.addEventListener("click", async () => {
        await api.patch(`/alerts/${data.top_alert.id}/read`);
        bannerContainer.innerHTML = "";
      });
    } else {
      bannerContainer.innerHTML = "";
    }

    // 3. Timeline Items
    const timelineEl = document.getElementById("today-timeline");
    const countBadge = document.getElementById("timeline-count-badge");
    countBadge.textContent = `${data.today_timeline.length} Mục`;

    if (!data.today_timeline || data.today_timeline.length === 0) {
      timelineEl.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon">
            <i data-lucide="calendar-check-2" style="width: 26px; height: 26px;"></i>
          </div>
          <h4>Hôm nay không có lịch học trên lớp</h4>
          <p>Tận dụng ngày trống để tự học hoặc giải quyết các deadline sắp tới nhé!</p>
        </div>
      `;
    } else {
      timelineEl.innerHTML = data.today_timeline.map((item, idx) => {
        let badgeClass = "badge-lecture";
        if (item.badge_variant === "self_study") badgeClass = "badge-self-study";
        if (item.badge_variant === "ai_suggested") badgeClass = "badge-ai";
        if (item.badge_variant === "deadline") badgeClass = "badge-deadline";

        const isLast = idx === data.today_timeline.length - 1;

        return `
          <div class="timeline-item">
            <div class="timeline-time-col">
              <div class="timeline-time-start">${escapeHtml(item.start_time)}</div>
              <div class="timeline-time-end">${escapeHtml(item.end_time)}</div>
            </div>
            <div class="timeline-line-col">
              <div class="timeline-dot ${escapeHtml(item.badge_variant)}"></div>
              ${!isLast ? '<div class="timeline-stem"></div>' : ''}
            </div>
            <div class="timeline-card">
              <div class="timeline-card-header">
                <span class="timeline-card-title">${escapeHtml(item.title)}</span>
                <span class="badge ${badgeClass}">${escapeHtml(item.badge_text)}</span>
              </div>
              <div class="timeline-card-meta">
                ${item.subtitle ? `<span>${escapeHtml(item.subtitle)}</span>` : ''}
              </div>
            </div>
          </div>
        `;
      }).join("");
    }

    // 4. Upcoming Tasks (Top 3)
    const tasksEl = document.getElementById("upcoming-tasks-list");
    if (!data.upcoming_tasks || data.upcoming_tasks.length === 0) {
      tasksEl.innerHTML = `
        <div class="empty-state" style="padding: 24px;">
          <p>Không có bài tập hay deadline nào cần hoàn thành!</p>
        </div>
      `;
    } else {
      tasksEl.innerHTML = data.upcoming_tasks.map(t => {
        let priorityBadge = "badge-info";
        let priorityText = "Ưu tiên: Bình thường";
        if (t.priority === "critical") {
          priorityBadge = "badge-critical";
          priorityText = "Ưu tiên: Khẩn cấp";
        } else if (t.priority === "high") {
          priorityBadge = "badge-warning";
          priorityText = "Ưu tiên: Cao";
        }

        let progressColor = "var(--primary-blue)";
        if (t.progress >= 80) progressColor = "#10B981";
        else if (t.priority === "critical") progressColor = "#DC2626";

        return `
          <div class="task-item-dash">
            <div class="task-item-dash-top">
              <div>
                <span class="task-item-dash-title">${escapeHtml(t.title)}</span>
                <span class="badge ${priorityBadge}" style="margin-left: 8px;">${priorityText}</span>
              </div>
              <span class="badge ${t.urgency_severity === 'critical' ? 'badge-critical' : 'badge-warning'}">
                ${escapeHtml(t.urgency_label || '')}
              </span>
            </div>
            <div class="task-item-dash-meta">
              <span>Môn: <strong>${escapeHtml(t.course ? t.course.name : 'Chung')}</strong></span>
              <span>Hạn nộp: ${formatDateTime(t.due_at)}</span>
              <span>Tiến độ: ${t.progress}%</span>
            </div>
            <div class="progress-bar-container">
              <div class="progress-bar-fill" style="width: ${t.progress}%; background-color: ${progressColor};"></div>
            </div>
          </div>
        `;
      }).join("");
    }

    // 5. Nearest Exam Card
    const examBox = document.getElementById("nearest-exam-box");
    if (data.nearest_exam) {
      const ex = data.nearest_exam;
      let countdownClass = "normal";
      if (ex.countdown_days <= 3) countdownClass = "critical";
      else if (ex.countdown_days <= 7) countdownClass = "warning";

      examBox.innerHTML = `
        <div class="exam-item-mini">
          <div class="exam-item-mini-info">
            <h4>${escapeHtml(ex.course ? ex.course.name : 'Kỳ thi môn học')}</h4>
            <div class="exam-item-mini-meta">
              <div>Ngày: <strong>${formatDate(ex.exam_date)}</strong> lúc ${escapeHtml(ex.start_time)}</div>
              <div>Phòng: <strong>${escapeHtml(ex.room)}</strong> • SBD: <code>${escapeHtml(ex.seat_number || 'Chưa có')}</code></div>
            </div>
          </div>
          <div class="exam-countdown-badge">
            <div class="exam-days-num ${countdownClass}">
              ${ex.countdown_days >= 0 ? ex.countdown_days : 0}
            </div>
            <div class="exam-days-label">Ngày tới</div>
          </div>
        </div>
      `;
    } else {
      examBox.innerHTML = `
        <div style="padding: 16px; text-align: center; color: var(--text-muted); font-size: 13px;">
          Chưa có lịch thi nào được xếp trong hệ thống.
        </div>
      `;
    }

    // 6. AI Suggestion Body
    if (data.ai_suggestion) {
      document.getElementById("ai-suggestion-text").textContent = data.ai_suggestion.description;
    }

    // 7. Study Stats
    if (data.study_progress) {
      document.getElementById("stat-study-hours").textContent = `${data.study_progress.self_study_hours}h`;
      document.getElementById("stat-task-done").textContent = `${data.study_progress.completed_tasks}/${data.study_progress.total_tasks}`;
      document.getElementById("study-progress-bar").style.width = `${data.study_progress.task_completion_rate}%`;
      document.getElementById("study-week-badge").textContent = `Tuần ${data.study_progress.current_week} / ${data.study_progress.total_weeks}`;
    }

    renderIcons();
  } catch (err) {
    showToast(err.message || "Lỗi tải dữ liệu Dashboard", "error");
  }
}

function setupQuickActions() {
  // Quick Add Class Button
  document.getElementById("quick-add-class-btn")?.addEventListener("click", () => {
    window.location.href = "schedule.html?action=new";
  });

  // Quick AI Plan Button
  document.getElementById("quick-ai-plan-btn")?.addEventListener("click", async () => {
    try {
      showToast("Đang kích hoạt AI tạo kế hoạch học tập tối ưu...", "info");
      await api.post("/plans/ai-generate", { days_ahead: 7, daily_max_hours: 5.0, include_breaks: true });
      showToast("Kế hoạch học tập AI đã được tạo thành công!", "success");
      setTimeout(() => {
        window.location.href = "planner.html";
      }, 500);
    } catch (err) {
      showToast(err.message || "Không thể tạo kế hoạch AI lúc này", "error");
    }
  });

  // Quick Add Task Modal
  const modal = "quick-task-modal";
  document.getElementById("quick-add-task-btn")?.addEventListener("click", async () => {
    // Populate course dropdown
    try {
      const courses = await api.get("/courses");
      const courseSelect = document.getElementById("qt-course");
      courseSelect.innerHTML = `<option value="">-- Chung (Không gắn môn cụ thể) --</option>` +
        courses.map(c => `<option value="${c.id}">${escapeHtml(c.code)} - ${escapeHtml(c.name)}</option>`).join("");
    } catch (e) {
      console.warn("Could not load courses", e);
    }

    // Default due_at to tomorrow
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(23, 59, 0, 0);
    document.getElementById("qt-due").value = tomorrow.toISOString().slice(0, 16);

    openModal(modal);
  });

  document.getElementById("close-quick-task-modal")?.addEventListener("click", () => closeModal(modal));
  document.getElementById("cancel-quick-task")?.addEventListener("click", () => closeModal(modal));

  document.getElementById("quick-task-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const title = document.getElementById("qt-title").value.trim();
    const courseIdVal = document.getElementById("qt-course").value;
    const dueAt = document.getElementById("qt-due").value;
    const priority = document.getElementById("qt-priority").value;
    const hours = parseFloat(document.getElementById("qt-hours").value) || 2.0;

    if (!title || !dueAt) {
      showToast("Vui lòng điền đầy đủ tiêu đề và hạn chót", "error");
      return;
    }

    try {
      await api.post("/tasks", {
        title,
        course_id: courseIdVal ? parseInt(courseIdVal) : null,
        due_at: new Date(dueAt).toISOString(),
        priority,
        status: "not_started",
        progress: 0,
        estimated_hours: hours
      });

      closeModal(modal);
      showToast("Đã thêm công việc thành công!", "success");
      await loadDashboardData();
    } catch (err) {
      showToast(err.message || "Thêm công việc thất bại", "error");
    }
  });
}
