// Modal Dialog Manager
import { escapeHtml, renderIcons } from "../utils.js";

export function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add("show");
    renderIcons();
  }
}

export function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove("show");
  }
}

// Global confirm dialog
export function confirmAction({ title = "Xác nhận xóa", message = "Bạn có chắc chắn muốn xóa mục này không? Hành động này không thể hoàn tác.", onConfirm }) {
  let confirmModal = document.getElementById("global-confirm-modal");
  if (!confirmModal) {
    confirmModal = document.createElement("div");
    confirmModal.id = "global-confirm-modal";
    confirmModal.className = "modal-backdrop";
    confirmModal.innerHTML = `
      <div class="modal-box" style="max-width: 420px;">
        <div class="modal-header">
          <h3 id="confirm-modal-title">Xác nhận</h3>
          <button class="modal-close-btn" id="confirm-modal-close">
            <i data-lucide="x" style="width: 18px; height: 18px;"></i>
          </button>
        </div>
        <div class="modal-body">
          <p id="confirm-modal-message" style="font-size: 14px; color: var(--text-muted); line-height: 1.5;"></p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline btn-sm" id="confirm-modal-cancel">Hủy bỏ</button>
          <button class="btn btn-danger btn-sm" id="confirm-modal-ok">Đồng ý</button>
        </div>
      </div>
    `;
    document.body.appendChild(confirmModal);
  }

  document.getElementById("confirm-modal-title").textContent = title;
  document.getElementById("confirm-modal-message").textContent = message;

  const closeBtn = document.getElementById("confirm-modal-close");
  const cancelBtn = document.getElementById("confirm-modal-cancel");
  const okBtn = document.getElementById("confirm-modal-ok");

  const cleanup = () => {
    confirmModal.classList.remove("show");
    closeBtn.onclick = null;
    cancelBtn.onclick = null;
    okBtn.onclick = null;
  };

  closeBtn.onclick = cleanup;
  cancelBtn.onclick = cleanup;
  okBtn.onclick = () => {
    cleanup();
    if (typeof onConfirm === "function") {
      onConfirm();
    }
  };

  confirmModal.classList.add("show");
  renderIcons();
}
