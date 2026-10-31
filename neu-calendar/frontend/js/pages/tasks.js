// Tasks Page Controller
import { initNav } from "../nav.js";
import { api } from "../api.js";
import { escapeHtml, formatDateTime, renderIcons } from "../utils.js";
import { showToast } from "../components/toast.js";
import { openModal, closeModal, confirmAction } from "../components/modal.js";

let cachedCourses = [];

document.addEventListener("DOMContentLoaded", async () => {
  initNav("tasks");
  setupFilterEvents();
  setupModalEvents();
  await loadCourses();
  await loadTasks();
});

function setupFilterEvents() {
  document.getElementById("filter-status")?.addEventListener("change", () => loadTasks());
  document.getElementById("filter-priority")?.addEventListener("change", () => loadTasks());
  document.getElementById("filter-course")?.addEventListener("change", () => loadTasks());
}

async function loadCourses() {
  try {
    cachedCourses = await api.get("/courses");
    const filterSelect = document.getElementById("filter-course");
    const modalSelect = document.getElementById("task-course");

    const options = cachedCourses.map(c => `<option value="${c.id}">${escapeHtml(c.code)} - ${escapeHtml(c.name)}</option>`).join("");
    if (filterSelect) {
      filterSelect.innerHTML = `<option value="">Tất cả môn học</option>` + options;
    }
    if (modalSelect) {
      modalSelect.innerHTML = `<option value="">-- Chung (Không gắn môn cụ thể) --</option>` + options;
    }
  } catch (err) {
    console.error("Failed to load courses", err);
  }
}

async function loadTasks() {
  const container = document.getElementById("tasks-container");
  const status = document.getElementById("filter-status")?.value || "";
  const priority = document.getElementById("filter-priority")?.value || "";
  const courseId = document.getElementById("filter-course")?.value || "";

  let query = [];
  if (status) query.push(`status=${encodeURIComponent(status)}`);
  if (priority) query.push(`priority=${encodeURIComponent(priority)}`);
  if (courseId) query.push(`course_id=${encodeURIComponent(courseId)}`);
  const endpoint = `/tasks${query.length ? '?' + query.join('&') : ''}`;

  try {
    const tasks = await api.get(endpoint);

    if (!tasks || tasks.length === 0) {
      container.innerHTML = `
        <div class="card empty-state">
          <div class="empty-state-icon">
            <i data-lucide="check-circle-2" style="width: 28px; height: 28px;"></i>
          </div>
          <h4>Không tìm thấy công việc phù hợp</h4>
          <p>Tất cả deadline đã được xử lý hoặc bộ lọc không khớp dữ liệu.</p>
        </div>
      `;
      renderIcons();
      return;
    }

    container.innerHTML = tasks.map(t => {
      const isDone = t.status === "done";

      let priorityBadge = "badge-info";
      let priorityText = "Ưu tiên: Bình thường";
      if (t.priority === "critical") {
        priorityBadge = "badge-critical";
        priorityText = "Khẩn cấp";
      } else if (t.priority === "high") {
        priorityBadge = "badge-warning";
        priorityText = "Cao";
      } else if (t.priority === "low") {
        priorityBadge = "badge-info";
        priorityText = "Thấp";
      }

      let urgencyClass = "badge-info";
      if (t.urgency_severity === "critical") urgencyClass = "badge-critical";
      else if (t.urgency_severity === "warning") urgencyClass = "badge-warning";

      let progressColor = "var(--primary-blue)";
      if (t.progress >= 100) progressColor = "#10B981";
      else if (t.priority === "critical") progressColor = "#DC2626";

      return `
        <div class="task-card ${isDone ? 'done' : ''}" data-id="${t.id}">
          <div class="task-left-col">
            <button class="task-checkbox-btn ${isDone ? 'checked' : ''}" data-id="${t.id}" title="${isDone ? 'Đánh dấu chưa xong' : 'Đánh dấu đã hoàn thành'}">
              <i data-lucide="check" style="width: 14px; height: 14px;"></i>
            </button>

            <div class="task-content">
              <div class="task-title-row">
                <span class="task-title">${escapeHtml(t.title)}</span>
                <span class="badge ${priorityBadge}">${priorityText}</span>
                <span class="badge ${urgencyClass}">${escapeHtml(t.urgency_label || '')}</span>
              </div>

              ${t.description ? `<p class="task-desc">${escapeHtml(t.description)}</p>` : ''}

              <div class="task-meta-row">
                <div class="task-meta-item">
                  <i data-lucide="book-open" style="width: 14px; height: 14px; color: var(--primary-blue);"></i>
                  <span>${escapeHtml(t.course ? t.course.name : 'Chung')}</span>
                </div>
                <div class="task-meta-item">
                  <i data-lucide="calendar" style="width: 14px; height: 14px; color: #D97706;"></i>
                  <span>Hạn chót: <strong>${formatDateTime(t.due_at)}</strong></span>
                </div>
                <div class="task-meta-item">
                  <i data-lucide="clock" style="width: 14px; height: 14px; color: var(--text-muted);"></i>
                  <span>Ước tính: ${t.estimated_hours}h</span>
                </div>
              </div>
            </div>
          </div>

          <div class="task-progress-col">
            <div class="task-progress-info">
              <span>Tiến độ</span>
              <span>${t.progress}%</span>
            </div>
            <div class="progress-bar-container">
              <div class="progress-bar-fill" style="width: ${t.progress}%; background-color: ${progressColor};"></div>
            </div>
          </div>

          <div class="task-actions-col">
            <button class="btn btn-outline btn-sm edit-task-btn" data-id="${t.id}" title="Chỉnh sửa">
              <i data-lucide="edit-3" style="width: 14px; height: 14px;"></i>
            </button>
            <button class="btn btn-outline btn-sm delete-task-btn" data-id="${t.id}" style="color: #DC2626;" title="Xóa">
              <i data-lucide="trash-2" style="width: 14px; height: 14px;"></i>
            </button>
          </div>
        </div>
      `;
    }).join("");

    // Event listeners
    container.querySelectorAll(".task-checkbox-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const id = btn.getAttribute("data-id");
        const isChecked = btn.classList.contains("checked");
        toggleTaskDone(id, !isChecked);
      });
    });

    container.querySelectorAll(".edit-task-btn").forEach(btn => {
      btn.addEventListener("click", () => editTask(btn.getAttribute("data-id")));
    });

    container.querySelectorAll(".delete-task-btn").forEach(btn => {
      btn.addEventListener("click", () => deleteTask(btn.getAttribute("data-id")));
    });

    renderIcons();
  } catch (err) {
    showToast(err.message || "Lỗi tải danh sách công việc", "error");
  }
}

async function toggleTaskDone(id, markDone) {
  try {
    const newProgress = markDone ? 100 : 0;
    const newStatus = markDone ? "done" : "not_started";
    await api.patch(`/tasks/${id}/progress`, { progress: newProgress, status: newStatus });
    showToast(markDone ? "Đã đánh dấu hoàn thành!" : "Đã chuyển về chưa hoàn thành", "success");
    await loadTasks();
  } catch (err) {
    showToast(err.message || "Lỗi cập nhật tiến độ", "error");
  }
}

function setupModalEvents() {
  const modal = "task-modal";
  document.getElementById("open-add-task-btn")?.addEventListener("click", () => openTaskModal());
  document.getElementById("close-task-modal")?.addEventListener("click", () => closeModal(modal));
  document.getElementById("cancel-task-modal")?.addEventListener("click", () => closeModal(modal));

  document.getElementById("task-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const editId = document.getElementById("task-edit-id").value;
    const title = document.getElementById("task-title").value.trim();
    const courseId = document.getElementById("task-course").value;
    const description = document.getElementById("task-desc").value.trim() || null;
    const dueAt = document.getElementById("task-due").value;
    const priority = document.getElementById("task-priority").value;
    const progress = parseInt(document.getElementById("task-progress").value) || 0;
    const hours = parseFloat(document.getElementById("task-hours").value) || 2.0;

    if (!title || !dueAt) {
      showToast("Vui lòng nhập tên công việc và hạn nộp", "error");
      return;
    }

    try {
      const payload = {
        title,
        course_id: courseId ? parseInt(courseId) : null,
        description,
        due_at: new Date(dueAt).toISOString(),
        priority,
        status: progress === 100 ? "done" : (progress > 0 ? "in_progress" : "not_started"),
        progress,
        estimated_hours: hours
      };

      if (editId) {
        await api.put(`/tasks/${editId}`, payload);
        showToast("Đã cập nhật công việc thành công!", "success");
      } else {
        await api.post("/tasks", payload);
        showToast("Đã thêm bài tập mới!", "success");
      }

      closeModal(modal);
      await loadTasks();
    } catch (err) {
      showToast(err.message || "Lỗi lưu công việc", "error");
    }
  });
}

function openTaskModal(data = null) {
  document.getElementById("task-form").reset();
  const modalTitle = document.getElementById("task-modal-title");
  const editId = document.getElementById("task-edit-id");

  if (data) {
    modalTitle.textContent = "Chỉnh sửa bài tập / Deadline";
    editId.value = data.id;
    document.getElementById("task-title").value = data.title;
    document.getElementById("task-course").value = data.course_id || "";
    document.getElementById("task-desc").value = data.description || "";
    document.getElementById("task-due").value = new Date(data.due_at).toISOString().slice(0, 16);
    document.getElementById("task-priority").value = data.priority;
    document.getElementById("task-progress").value = data.progress;
    document.getElementById("task-hours").value = data.estimated_hours;
  } else {
    modalTitle.textContent = "Thêm bài tập / Deadline mới";
    editId.value = "";
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(23, 59, 0, 0);
    document.getElementById("task-due").value = tomorrow.toISOString().slice(0, 16);
    document.getElementById("task-progress").value = 0;
    document.getElementById("task-hours").value = 2.0;
  }

  openModal("task-modal");
}

async function editTask(id) {
  try {
    const task = await api.get(`/tasks/${id}`);
    openTaskModal(task);
  } catch (err) {
    showToast(err.message || "Không thể tải thông tin công việc", "error");
  }
}

function deleteTask(id) {
  confirmAction({
    title: "Xóa bài tập / Deadline",
    message: "Bạn có chắc chắn muốn xóa bài tập này không?",
    onConfirm: async () => {
      try {
        await api.delete(`/tasks/${id}`);
        showToast("Đã xóa công việc thành công", "success");
        await loadTasks();
      } catch (err) {
        showToast(err.message || "Lỗi khi xóa bài tập", "error");
      }
    }
  });
}
