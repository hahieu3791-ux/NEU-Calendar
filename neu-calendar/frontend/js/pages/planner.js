// Study Planner Page Controller
import { initNav } from "../nav.js";
import { api } from "../api.js";
import { escapeHtml, formatDateTime, renderIcons } from "../utils.js";
import { showToast } from "../components/toast.js";
import { openModal, closeModal, confirmAction } from "../components/modal.js";

let currentActivePlan = null;

document.addEventListener("DOMContentLoaded", async () => {
  initNav("planner");
  setupButtons();
  setupModalEvents();
  await loadActivePlan();
});

async function loadActivePlan() {
  const container = document.getElementById("plan-items-container");
  try {
    currentActivePlan = await api.get("/plans/active");

    if (!currentActivePlan || !currentActivePlan.items || currentActivePlan.items.length === 0) {
      document.getElementById("stat-plan-title").textContent = "Chưa có";
      document.getElementById("stat-items-done").textContent = "0/0";
      document.getElementById("stat-total-hours").textContent = "0h";

      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon">
            <i data-lucide="sparkles" style="width: 28px; height: 28px; color: #4F46E5;"></i>
          </div>
          <h4>Chưa có kế hoạch học tập đang hoạt động</h4>
          <p>Bấm nút <strong>"Tạo kế hoạch AI"</strong> để trợ lý tự động phân bổ các khung giờ tự học tối ưu nhất cho bạn.</p>
        </div>
      `;
      renderIcons();
      return;
    }

    // Render Stats
    const items = currentActivePlan.items;
    const doneCount = items.filter(i => i.is_done).length;
    let totalMinutes = 0;
    items.forEach(i => {
      const s = new Date(i.start_at).getTime();
      const e = new Date(i.end_at).getTime();
      if (!isNaN(s) && !isNaN(e)) {
        totalMinutes += (e - s) / (1000 * 60);
      }
    });

    document.getElementById("stat-plan-title").textContent = currentActivePlan.source === "ai" ? "Kế hoạch AI" : "Kế hoạch thủ công";
    document.getElementById("stat-items-done").textContent = `${doneCount}/${items.length}`;
    document.getElementById("stat-total-hours").textContent = `${(totalMinutes / 60).toFixed(1)}h`;
    document.getElementById("plan-section-title").textContent = currentActivePlan.title;

    // Render Items
    container.innerHTML = items.map(item => {
      return `
        <div class="plan-item-card ${item.is_done ? 'done' : ''}" data-id="${item.id}">
          <div class="plan-item-left">
            <button class="plan-check-btn ${item.is_done ? 'checked' : ''}" data-id="${item.id}" title="${item.is_done ? 'Chưa hoàn thành' : 'Đánh dấu đã học'}">
              <i data-lucide="check" style="width: 14px; height: 14px;"></i>
            </button>
            <div class="plan-item-info">
              <div class="plan-item-title">${escapeHtml(item.title)}</div>
              <div class="plan-item-time">
                <i data-lucide="clock" style="width: 14px; height: 14px; color: var(--primary-blue);"></i>
                <span>${formatDateTime(item.start_at)} – ${formatDateTime(item.end_at)}</span>
              </div>
              ${item.ai_reason ? `
                <div class="plan-ai-reason">
                  <i data-lucide="zap" style="width: 12px; height: 12px;"></i>
                  <span>${escapeHtml(item.ai_reason)}</span>
                </div>
              ` : ''}
            </div>
          </div>
        </div>
      `;
    }).join("");

    // Attach toggle listeners
    container.querySelectorAll(".plan-check-btn").forEach(btn => {
      btn.addEventListener("click", async () => {
        const itemId = btn.getAttribute("data-id");
        await togglePlanItem(itemId);
      });
    });

    renderIcons();
  } catch (err) {
    showToast(err.message || "Lỗi tải kế hoạch học tập", "error");
  }
}

async function togglePlanItem(itemId) {
  try {
    const updated = await api.patch(`/plans/items/${itemId}/toggle`);
    showToast(updated.is_done ? "Đã đánh dấu hoàn thành phiên học!" : "Đã chuyển về chưa hoàn thành", "success");
    await loadActivePlan();
  } catch (err) {
    showToast(err.message || "Lỗi cập nhật phiên học", "error");
  }
}

function setupButtons() {
  const aiBtn = document.getElementById("ai-generate-plan-btn");
  if (aiBtn) {
    aiBtn.addEventListener("click", async () => {
      try {
        aiBtn.disabled = true;
        aiBtn.innerHTML = `<span>Đang phân tích và tối ưu...</span>`;
        showToast("AI Copilot đang phân tích lịch học, deadline và lịch thi...", "info");

        await api.post("/plans/ai-generate", {
          days_ahead: 7,
          daily_max_hours: 5.0,
          include_breaks: true
        });

        showToast("Đã lập kế hoạch học tập AI 7 ngày thành công!", "success");
        await loadActivePlan();
      } catch (err) {
        showToast(err.message || "Không thể tạo kế hoạch AI lúc này", "error");
      } finally {
        aiBtn.disabled = false;
        aiBtn.innerHTML = `
          <i data-lucide="sparkles" style="width: 17px; height: 17px; color: #4F46E5;"></i>
          <span>Tạo kế hoạch AI (7 ngày)</span>
        `;
        renderIcons();
      }
    });
  }

  const archiveBtn = document.getElementById("archive-plan-btn");
  if (archiveBtn) {
    archiveBtn.addEventListener("click", () => {
      if (!currentActivePlan) return;
      confirmAction({
        title: "Lưu trữ kế hoạch",
        message: "Bạn có chắc chắn muốn lưu trữ hoặc xóa kế hoạch học tập hiện tại không?",
        onConfirm: async () => {
          try {
            await api.delete(`/plans/${currentActivePlan.id}`);
            showToast("Đã lưu trữ kế hoạch", "success");
            await loadActivePlan();
          } catch (err) {
            showToast(err.message || "Lỗi khi xóa kế hoạch", "error");
          }
        }
      });
    });
  }
}

function setupModalEvents() {
  const modal = "manual-plan-modal";
  document.getElementById("open-manual-plan-btn")?.addEventListener("click", () => {
    document.getElementById("manual-plan-form").reset();
    const now = new Date();
    now.setHours(14, 0, 0, 0);
    const end = new Date(now);
    end.setHours(16, 0, 0, 0);

    document.getElementById("mpi-start").value = now.toISOString().slice(0, 16);
    document.getElementById("mpi-end").value = end.toISOString().slice(0, 16);
    openModal(modal);
  });

  document.getElementById("close-manual-modal")?.addEventListener("click", () => closeModal(modal));
  document.getElementById("cancel-manual-modal")?.addEventListener("click", () => closeModal(modal));

  document.getElementById("manual-plan-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const title = document.getElementById("mpi-title").value.trim();
    const startAt = document.getElementById("mpi-start").value;
    const endAt = document.getElementById("mpi-end").value;
    const reason = document.getElementById("mpi-reason").value.trim() || null;

    if (!title || !startAt || !endAt) {
      showToast("Vui lòng nhập đầy đủ thông tin", "error");
      return;
    }

    try {
      const today = new Date().toISOString().slice(0, 10);
      const nextWeek = new Date(Date.now() + 7 * 86400000).toISOString().slice(0, 10);

      // Create new manual plan if none exists or add item
      if (!currentActivePlan) {
        await api.post("/plans", {
          title: `Kế hoạch học tập cá nhân`,
          start_date: today,
          end_date: nextWeek,
          source: "manual",
          status: "active",
          items: [{
            title,
            start_at: new Date(startAt).toISOString(),
            end_at: new Date(endAt).toISOString(),
            is_done: false,
            ai_reason: reason
          }]
        });
      } else {
        // Create as a plan item by recreating/updating plan
        await api.post("/plans", {
          title: currentActivePlan.title,
          start_date: currentActivePlan.start_date,
          end_date: currentActivePlan.end_date,
          source: currentActivePlan.source,
          status: "active",
          items: [
            ...(currentActivePlan.items || []).map(i => ({
              title: i.title,
              start_at: i.start_at,
              end_at: i.end_at,
              is_done: i.is_done,
              ai_reason: i.ai_reason,
              task_id: i.task_id,
              exam_id: i.exam_id
            })),
            {
              title,
              start_at: new Date(startAt).toISOString(),
              end_at: new Date(endAt).toISOString(),
              is_done: false,
              ai_reason: reason
            }
          ]
        });
      }

      closeModal(modal);
      showToast("Đã thêm phiên học vào kế hoạch!", "success");
      await loadActivePlan();
    } catch (err) {
      showToast(err.message || "Lỗi lưu phiên học", "error");
    }
  });
}
