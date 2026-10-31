// Exams Page Controller
import { initNav } from "../nav.js";
import { api } from "../api.js";
import { escapeHtml, formatDate, renderIcons } from "../utils.js";
import { showToast } from "../components/toast.js";
import { openModal, closeModal, confirmAction } from "../components/modal.js";

let cachedCourses = [];

document.addEventListener("DOMContentLoaded", async () => {
  initNav("exams");
  setupModalEvents();
  await loadCourses();
  await loadExams();
});

async function loadCourses() {
  try {
    cachedCourses = await api.get("/courses");
    const select = document.getElementById("exam-course");
    select.innerHTML = `<option value="">-- Chọn môn học --</option>` +
      cachedCourses.map(c => `<option value="${c.id}">${escapeHtml(c.code)} - ${escapeHtml(c.name)}</option>`).join("");
  } catch (err) {
    console.error("Failed to load courses", err);
  }
}

async function loadExams() {
  const container = document.getElementById("exams-container");
  try {
    const exams = await api.get("/exams");

    if (!exams || exams.length === 0) {
      container.innerHTML = `
        <div class="card empty-state">
          <div class="empty-state-icon">
            <i data-lucide="award" style="width: 28px; height: 28px;"></i>
          </div>
          <h4>Chưa có lịch thi nào được ghi nhận</h4>
          <p>Bấm nút "Thêm lịch thi" phía trên để lưu thông tin ngày thi và số báo danh của bạn.</p>
        </div>
      `;
      renderIcons();
      return;
    }

    container.innerHTML = exams.map(ex => {
      let urgencyClass = "normal";
      let urgencyText = "Bình thường";
      let badgeClass = "badge-info";

      if (ex.countdown_days < 0) {
        urgencyClass = "past";
        urgencyText = "Đã thi xong";
        badgeClass = "badge-info";
      } else if (ex.countdown_days <= 3) {
        urgencyClass = "critical";
        urgencyText = "Khẩn cấp (≤ 3 ngày)";
        badgeClass = "badge-critical";
      } else if (ex.countdown_days <= 7) {
        urgencyClass = "warning";
        urgencyText = "Sắp thi (≤ 7 ngày)";
        badgeClass = "badge-warning";
      }

      return `
        <div class="exam-card ${urgencyClass}">
          <div class="exam-info-col">
            <div class="exam-title-row">
              <span class="exam-course-name">${escapeHtml(ex.course ? ex.course.name : 'Môn thi')}</span>
              <span class="badge ${badgeClass}">${urgencyText}</span>
              <span class="badge badge-lecture">${escapeHtml(ex.exam_type)}</span>
            </div>

            <div class="exam-meta-grid">
              <div class="exam-meta-item">
                <i data-lucide="calendar" style="width: 15px; height: 15px; color: var(--primary-blue);"></i>
                <span>Ngày thi: <strong>${formatDate(ex.exam_date)}</strong></span>
              </div>
              <div class="exam-meta-item">
                <i data-lucide="clock" style="width: 15px; height: 15px; color: var(--primary-blue);"></i>
                <span>Giờ thi: <strong>${escapeHtml(ex.start_time)}</strong> (${ex.duration_minutes} phút)</span>
              </div>
              <div class="exam-meta-item">
                <i data-lucide="map-pin" style="width: 15px; height: 15px; color: #DC2626;"></i>
                <span>Phòng thi: <strong>${escapeHtml(ex.room)}</strong></span>
              </div>
              <div class="exam-meta-item">
                <i data-lucide="hash" style="width: 15px; height: 15px; color: #059669;"></i>
                <span>Số báo danh: <code>${escapeHtml(ex.seat_number || 'Chưa cập nhật')}</code></span>
              </div>
            </div>

            ${ex.notes ? `
              <div style="margin-top: 10px; font-size: 12.5px; color: var(--text-muted); background: #F8FAFC; padding: 6px 10px; border-radius: 4px; border-left: 2px solid #CBD5E1;">
                <strong>Ghi chú:</strong> ${escapeHtml(ex.notes)}
              </div>
            ` : ''}
          </div>

          <div class="exam-countdown-col">
            <div class="exam-countdown-days ${urgencyClass}">
              ${ex.countdown_days >= 0 ? ex.countdown_days : 0}
            </div>
            <div class="exam-countdown-label">
              ${ex.countdown_days >= 0 ? 'Ngày đếm ngược' : 'Đã diễn ra'}
            </div>
          </div>

          <div class="exam-actions-col">
            <button class="btn btn-outline btn-sm edit-exam-btn" data-id="${ex.id}" title="Chỉnh sửa">
              <i data-lucide="edit-3" style="width: 14px; height: 14px;"></i>
              <span>Sửa</span>
            </button>
            <button class="btn btn-outline btn-sm delete-exam-btn" data-id="${ex.id}" style="color: #DC2626;" title="Xóa">
              <i data-lucide="trash-2" style="width: 14px; height: 14px;"></i>
              <span>Xóa</span>
            </button>
          </div>
        </div>
      `;
    }).join("");

    // Attach card event listeners
    container.querySelectorAll(".edit-exam-btn").forEach(btn => {
      btn.addEventListener("click", () => editExam(btn.getAttribute("data-id")));
    });

    container.querySelectorAll(".delete-exam-btn").forEach(btn => {
      btn.addEventListener("click", () => deleteExam(btn.getAttribute("data-id")));
    });

    renderIcons();
  } catch (err) {
    showToast(err.message || "Lỗi tải danh sách lịch thi", "error");
  }
}

function setupModalEvents() {
  const modal = "exam-modal";
  document.getElementById("open-add-exam-btn")?.addEventListener("click", () => openExamModal());
  document.getElementById("close-exam-modal")?.addEventListener("click", () => closeModal(modal));
  document.getElementById("cancel-exam-modal")?.addEventListener("click", () => closeModal(modal));

  document.getElementById("exam-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const editId = document.getElementById("exam-edit-id").value;
    const courseId = parseInt(document.getElementById("exam-course").value);
    const examDate = document.getElementById("exam-date").value;
    const startTime = document.getElementById("exam-time").value.trim();
    const durationMinutes = parseInt(document.getElementById("exam-duration").value) || 60;
    const examType = document.getElementById("exam-type").value;
    const room = document.getElementById("exam-room").value.trim();
    const seatNumber = document.getElementById("exam-seat").value.trim() || null;
    const notes = document.getElementById("exam-notes").value.trim() || null;

    if (!courseId || !examDate || !startTime || !room) {
      showToast("Vui lòng điền các trường bắt buộc (*)", "error");
      return;
    }

    try {
      const payload = {
        course_id: courseId,
        exam_date: examDate,
        start_time: startTime,
        duration_minutes: durationMinutes,
        exam_type: examType,
        room,
        seat_number: seatNumber,
        notes
      };

      if (editId) {
        await api.put(`/exams/${editId}`, payload);
        showToast("Đã cập nhật lịch thi thành công!", "success");
      } else {
        await api.post("/exams", payload);
        showToast("Đã thêm lịch thi mới!", "success");
      }

      closeModal(modal);
      await loadExams();
    } catch (err) {
      showToast(err.message || "Lỗi lưu lịch thi", "error");
    }
  });
}

function openExamModal(data = null) {
  document.getElementById("exam-form").reset();
  const modalTitle = document.getElementById("exam-modal-title");
  const editId = document.getElementById("exam-edit-id");

  if (data) {
    modalTitle.textContent = "Chỉnh sửa lịch thi";
    editId.value = data.id;
    document.getElementById("exam-course").value = data.course_id;
    document.getElementById("exam-date").value = data.exam_date;
    document.getElementById("exam-time").value = data.start_time;
    document.getElementById("exam-duration").value = data.duration_minutes;
    document.getElementById("exam-type").value = data.exam_type;
    document.getElementById("exam-room").value = data.room;
    document.getElementById("exam-seat").value = data.seat_number || "";
    document.getElementById("exam-notes").value = data.notes || "";
  } else {
    modalTitle.textContent = "Thêm lịch thi mới";
    editId.value = "";
    document.getElementById("exam-time").value = "08:00";
    document.getElementById("exam-duration").value = 60;
  }

  openModal("exam-modal");
}

async function editExam(id) {
  try {
    const exam = await api.get(`/exams/${id}`);
    openExamModal(exam);
  } catch (err) {
    showToast(err.message || "Không thể tải thông tin lịch thi", "error");
  }
}

function deleteExam(id) {
  confirmAction({
    title: "Xóa lịch thi",
    message: "Bạn có chắc chắn muốn xóa kỳ thi này? Cảnh báo liên quan sẽ được tự động xóa.",
    onConfirm: async () => {
      try {
        await api.delete(`/exams/${id}`);
        showToast("Đã xóa lịch thi thành công", "success");
        await loadExams();
      } catch (err) {
        showToast(err.message || "Lỗi khi xóa lịch thi", "error");
      }
    }
  });
}
