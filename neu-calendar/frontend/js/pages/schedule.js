// Schedule Page Controller
import { initNav } from "../nav.js";
import { api } from "../api.js";
import { escapeHtml, renderIcons } from "../utils.js";
import { showToast } from "../components/toast.js";
import { openModal, closeModal, confirmAction } from "../components/modal.js";

let currentView = "week"; // "week" or "day"
let cachedCourses = [];
let allWeekData = null;

document.addEventListener("DOMContentLoaded", async () => {
  initNav("schedule");
  setupViewToggles();
  setupModalEvents();
  await loadCourses();
  await loadSchedule();

  // Check URL query param for auto-open add modal
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get("action") === "new") {
    openClassModal();
  }
});

function setupViewToggles() {
  const weekBtn = document.getElementById("view-week-btn");
  const dayBtn = document.getElementById("view-day-btn");
  const weekView = document.getElementById("schedule-week-view");
  const dayView = document.getElementById("schedule-day-view");

  weekBtn.addEventListener("click", () => {
    currentView = "week";
    weekBtn.classList.add("active");
    dayBtn.classList.remove("active");
    weekView.style.display = "grid";
    dayView.style.display = "none";
    renderSchedule();
  });

  dayBtn.addEventListener("click", () => {
    currentView = "day";
    dayBtn.classList.add("active");
    weekBtn.classList.remove("active");
    weekView.style.display = "none";
    dayView.style.display = "flex";
    renderSchedule();
  });
}

async function loadCourses() {
  try {
    cachedCourses = await api.get("/courses");
    const select = document.getElementById("class-course");
    select.innerHTML = `<option value="">-- Chọn môn học --</option>` +
      cachedCourses.map(c => `<option value="${c.id}">${escapeHtml(c.code)} - ${escapeHtml(c.name)}</option>`).join("");
  } catch (err) {
    console.error("Failed to load courses", err);
  }
}

async function loadSchedule() {
  try {
    allWeekData = await api.get("/classes/week");
    renderSchedule();
  } catch (err) {
    showToast(err.message || "Lỗi tải thời khóa biểu", "error");
  }
}

function renderSchedule() {
  if (!allWeekData) return;

  if (currentView === "week") {
    renderWeekView();
  } else {
    renderDayView();
  }
}

function renderWeekView() {
  const container = document.getElementById("schedule-week-view");
  const todayDay = new Date().getDay(); // 0 is Sunday, 1 is Monday...
  // NEU day: 1->2, 2->3, ..., 6->7, 0->8
  const currentNeuDay = todayDay === 0 ? 8 : todayDay + 1;

  container.innerHTML = allWeekData.days.map(dayObj => {
    const isToday = dayObj.day_of_week === currentNeuDay;
    const sessions = dayObj.sessions || [];

    const sessionsHtml = sessions.length === 0
      ? `<div style="text-align: center; padding: 30px 10px; color: var(--text-light); font-size: 12px;">Không có ca học</div>`
      : sessions.map(s => {
          const typeClass = s.session_type || "lecture";
          return `
            <div class="class-session-card ${typeClass}">
              <div class="class-title">${escapeHtml(s.course ? s.course.name : 'Môn học')}</div>
              <div class="class-detail">
                <i data-lucide="clock" style="width: 12px; height: 12px;"></i>
                <span>${escapeHtml(s.start_time)} - ${escapeHtml(s.end_time)} (Tiết ${s.start_period}-${s.end_period})</span>
              </div>
              <div class="class-detail">
                <i data-lucide="map-pin" style="width: 12px; height: 12px;"></i>
                <span>Phòng: <strong>${escapeHtml(s.room)}</strong></span>
              </div>
              ${s.course && s.course.lecturer ? `
                <div class="class-detail">
                  <i data-lucide="user" style="width: 12px; height: 12px;"></i>
                  <span>GV: ${escapeHtml(s.course.lecturer)}</span>
                </div>
              ` : ''}
              <div class="class-card-actions">
                <button class="icon-btn edit-class-btn" data-id="${s.id}" title="Chỉnh sửa">
                  <i data-lucide="edit-3" style="width: 14px; height: 14px;"></i>
                </button>
                <button class="icon-btn delete delete-class-btn" data-id="${s.id}" title="Xóa">
                  <i data-lucide="trash-2" style="width: 14px; height: 14px;"></i>
                </button>
              </div>
            </div>
          `;
        }).join("");

    return `
      <div class="week-col">
        <div class="week-col-header ${isToday ? 'today' : ''}">
          <h4>${escapeHtml(dayObj.day_name)}</h4>
          <span style="font-size: 11px; color: var(--text-muted);">${sessions.length} ca</span>
        </div>
        <div class="week-col-body">
          ${sessionsHtml}
        </div>
      </div>
    `;
  }).join("");

  attachCardActionEvents(container);
  renderIcons();
}

async function renderDayView() {
  const container = document.getElementById("schedule-day-view");
  try {
    const todaySessions = await api.get("/classes/today");
    if (!todaySessions || todaySessions.length === 0) {
      container.innerHTML = `
        <div class="card empty-state">
          <div class="empty-state-icon">
            <i data-lucide="calendar" style="width: 26px; height: 26px;"></i>
          </div>
          <h4>Hôm nay không có ca học nào</h4>
          <p>Thời gian rảnh rỗi này bạn có thể vào mục <strong>Kế hoạch học tập</strong> để lập phiên tự học cá nhân.</p>
        </div>
      `;
    } else {
      container.innerHTML = `
        <div class="card">
          <div class="card-header">
            <h3>Lịch học hôm nay (${todaySessions.length} ca)</h3>
          </div>
          <div class="timeline">
            ${todaySessions.map((s, idx) => `
              <div class="timeline-item">
                <div class="timeline-time-col">
                  <div class="timeline-time-start">${escapeHtml(s.start_time)}</div>
                  <div class="timeline-time-end">${escapeHtml(s.end_time)}</div>
                </div>
                <div class="timeline-line-col">
                  <div class="timeline-dot ${escapeHtml(s.session_type || 'lecture')}"></div>
                  ${idx < todaySessions.length - 1 ? '<div class="timeline-stem"></div>' : ''}
                </div>
                <div class="timeline-card">
                  <div class="timeline-card-header">
                    <span class="timeline-card-title">${escapeHtml(s.course ? s.course.name : 'Môn học')}</span>
                    <span class="badge badge-lecture">Tiết ${s.start_period} - ${s.end_period}</span>
                  </div>
                  <div class="timeline-card-meta">
                    <span>Phòng: <strong>${escapeHtml(s.room)}</strong></span>
                    ${s.course && s.course.lecturer ? `<span>GV: ${escapeHtml(s.course.lecturer)}</span>` : ''}
                    <span>Tuần ${s.week_from} - ${s.week_to}</span>
                  </div>
                </div>
              </div>
            `).join("")}
          </div>
        </div>
      `;
    }
  } catch (err) {
    container.innerHTML = `<p style="color: #DC2626;">Lỗi tải lịch hôm nay: ${escapeHtml(err.message)}</p>`;
  }
  renderIcons();
}

function attachCardActionEvents(parentEl) {
  parentEl.querySelectorAll(".edit-class-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const id = btn.getAttribute("data-id");
      editClass(id);
    });
  });

  parentEl.querySelectorAll(".delete-class-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const id = btn.getAttribute("data-id");
      deleteClass(id);
    });
  });
}

function setupModalEvents() {
  const modal = "class-modal";
  document.getElementById("open-add-class-btn")?.addEventListener("click", () => openClassModal());
  document.getElementById("close-class-modal")?.addEventListener("click", () => closeModal(modal));
  document.getElementById("cancel-class-modal")?.addEventListener("click", () => closeModal(modal));

  // Auto calculate time from period selection
  const periodTimes = {
    1: "06:45", 2: "07:40", 3: "08:40", 4: "09:40", 5: "10:35", 6: "11:30",
    7: "12:45", 8: "13:40", 9: "14:40", 10: "15:40", 11: "16:35", 12: "17:30", 13: "18:15"
  };
  const endPeriodTimes = {
    3: "09:30", 6: "12:20", 9: "15:30", 12: "18:20", 15: "20:55"
  };

  const startPeriodSelect = document.getElementById("class-start-period");
  const endPeriodSelect = document.getElementById("class-end-period");

  startPeriodSelect.addEventListener("change", () => {
    const s = parseInt(startPeriodSelect.value);
    document.getElementById("class-start-time").value = periodTimes[s] || "07:00";
  });

  endPeriodSelect.addEventListener("change", () => {
    const e = parseInt(endPeriodSelect.value);
    document.getElementById("class-end-time").value = endPeriodTimes[e] || "09:30";
  });

  // Form Submit
  document.getElementById("class-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const editId = document.getElementById("class-edit-id").value;
    const courseId = parseInt(document.getElementById("class-course").value);
    const dayOfWeek = parseInt(document.getElementById("class-day").value);
    const sessionType = document.getElementById("class-type").value;
    const startPeriod = parseInt(document.getElementById("class-start-period").value);
    const endPeriod = parseInt(document.getElementById("class-end-period").value);
    const startTime = document.getElementById("class-start-time").value.trim() || undefined;
    const endTime = document.getElementById("class-end-time").value.trim() || undefined;
    const room = document.getElementById("class-room").value.trim();
    const weekFrom = parseInt(document.getElementById("class-week-from").value) || 1;
    const weekTo = parseInt(document.getElementById("class-week-to").value) || 16;

    if (!courseId || !room) {
      showToast("Vui lòng chọn môn học và nhập phòng học", "error");
      return;
    }

    try {
      const payload = {
        course_id: courseId,
        day_of_week: dayOfWeek,
        session_type: sessionType,
        start_period: startPeriod,
        end_period: endPeriod,
        start_time: startTime,
        end_time: endTime,
        room,
        week_from: weekFrom,
        week_to: weekTo
      };

      if (editId) {
        await api.put(`/classes/${editId}`, payload);
        showToast("Đã cập nhật ca học thành công!", "success");
      } else {
        await api.post("/classes", payload);
        showToast("Đã thêm ca học mới vào thời khóa biểu!", "success");
      }

      closeModal(modal);
      await loadSchedule();
    } catch (err) {
      showToast(err.message || "Lỗi lưu ca học", "error");
    }
  });
}

function openClassModal(data = null) {
  document.getElementById("class-form").reset();
  const modalTitle = document.getElementById("class-modal-title");
  const editIdInput = document.getElementById("class-edit-id");

  if (data) {
    modalTitle.textContent = "Chỉnh sửa ca học";
    editIdInput.value = data.id;
    document.getElementById("class-course").value = data.course_id;
    document.getElementById("class-day").value = data.day_of_week;
    document.getElementById("class-type").value = data.session_type;
    document.getElementById("class-start-period").value = data.start_period;
    document.getElementById("class-end-period").value = data.end_period;
    document.getElementById("class-start-time").value = data.start_time;
    document.getElementById("class-end-time").value = data.end_time;
    document.getElementById("class-room").value = data.room;
    document.getElementById("class-week-from").value = data.week_from;
    document.getElementById("class-week-to").value = data.week_to;
  } else {
    modalTitle.textContent = "Thêm lịch học mới";
    editIdInput.value = "";
    document.getElementById("class-start-time").value = "07:00";
    document.getElementById("class-end-time").value = "09:30";
  }

  openModal("class-modal");
}

async function editClass(id) {
  try {
    const session = await api.get(`/classes/${id}`);
    openClassModal(session);
  } catch (err) {
    showToast(err.message || "Không thể tải chi tiết ca học", "error");
  }
}

function deleteClass(id) {
  confirmAction({
    title: "Xóa ca học khỏi thời khóa biểu",
    message: "Bạn có chắc chắn muốn xóa ca học này không?",
    onConfirm: async () => {
      try {
        await api.delete(`/classes/${id}`);
        showToast("Đã xóa ca học thành công", "success");
        await loadSchedule();
      } catch (err) {
        showToast(err.message || "Lỗi khi xóa ca học", "error");
      }
    }
  });
}
