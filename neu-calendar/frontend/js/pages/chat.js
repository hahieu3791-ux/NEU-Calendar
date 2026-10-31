// AI Chat Assistant Page Controller
import { initNav } from "../nav.js";
import { api } from "../api.js";
import { escapeHtml, formatDateTime, renderIcons } from "../utils.js";
import { showToast } from "../components/toast.js";
import { confirmAction } from "../components/modal.js";

const messagesContainer = document.getElementById("chat-messages");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const sendBtn = document.getElementById("send-btn");
const clearBtn = document.getElementById("clear-history-btn");
const suggestionsBar = document.getElementById("suggestions-bar");

document.addEventListener("DOMContentLoaded", async () => {
  initNav("chat");
  setupEventListeners();
  await loadHistory();
});

async function loadHistory() {
  try {
    const history = await api.get("/chat/history");
    if (!history || history.length === 0) {
      appendWelcomeMessage();
    } else {
      messagesContainer.innerHTML = "";
      history.forEach(msg => {
        appendMessage(msg.role, msg.content, msg.created_at);
      });
      scrollToBottom();
    }
  } catch (err) {
    showToast(err.message || "Lỗi tải lịch sử chat", "error");
    appendWelcomeMessage();
  }
}

function appendWelcomeMessage() {
  messagesContainer.innerHTML = `
    <div class="chat-message assistant">
      <div class="chat-avatar-ai" style="width: 32px; height: 32px; flex-shrink: 0; margin-top: 2px;">
        <i data-lucide="bot" style="width: 18px; height: 18px;"></i>
      </div>
      <div>
        <div class="chat-bubble">
          <p>Xin chào bạn! Tôi là <strong>NEU Copilot</strong> – trợ lý học tập cá nhân hóa của bạn tại Đại học Kinh tế Quốc dân.</p>
          <p>Tôi đã kết nối trực tiếp với dữ liệu thời khóa biểu, danh sách bài tập và lịch thi của bạn. Bạn có thể hỏi tôi bất cứ điều gì liên quan đến việc học tập tại trường!</p>
        </div>
        <div class="chat-time">Vừa xong</div>
      </div>
    </div>
  `;
  renderIcons();
  scrollToBottom();
}

function appendMessage(role, content, timestamp = new Date()) {
  const isUser = role === "user";
  const msgEl = document.createElement("div");
  msgEl.className = `chat-message ${isUser ? 'user' : 'assistant'}`;

  // Simple Markdown parsing for assistant replies:
  // Convert **bold** to <strong>, *italic* to <em>, `code` to <code>, \n to <br> or <p>
  let formattedContent = escapeHtml(content);
  if (!isUser) {
    formattedContent = formattedContent
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/\n\n/g, '</p><p>')
      .replace(/\n/g, '<br/>');
  }

  msgEl.innerHTML = `
    ${!isUser ? `
      <div class="chat-avatar-ai" style="width: 32px; height: 32px; flex-shrink: 0; margin-top: 2px;">
        <i data-lucide="bot" style="width: 18px; height: 18px;"></i>
      </div>
    ` : ''}
    <div>
      <div class="chat-bubble">
        <p>${formattedContent}</p>
      </div>
      <div class="chat-time">${formatDateTime(timestamp)}</div>
    </div>
  `;

  messagesContainer.appendChild(msgEl);
  renderIcons();
  scrollToBottom();
}

function showTypingIndicator() {
  const typingEl = document.createElement("div");
  typingEl.id = "typing-indicator";
  typingEl.className = "chat-message assistant";
  typingEl.innerHTML = `
    <div class="chat-avatar-ai" style="width: 32px; height: 32px; flex-shrink: 0; margin-top: 2px;">
      <i data-lucide="bot" style="width: 18px; height: 18px;"></i>
    </div>
    <div class="typing-indicator">
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
    </div>
  `;
  messagesContainer.appendChild(typingEl);
  renderIcons();
  scrollToBottom();
}

function removeTypingIndicator() {
  const typingEl = document.getElementById("typing-indicator");
  if (typingEl) {
    typingEl.parentNode.removeChild(typingEl);
  }
}

function scrollToBottom() {
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function setupEventListeners() {
  // Chat form submit
  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const msg = chatInput.value.trim();
    if (!msg) return;

    chatInput.value = "";
    appendMessage("user", msg, new Date());
    showTypingIndicator();
    sendBtn.disabled = true;

    try {
      const res = await api.post("/chat", { message: msg });
      removeTypingIndicator();
      appendMessage("assistant", res.assistant_message.content, res.assistant_message.created_at);

      // Update suggestion chips if provided
      if (res.quick_suggestions && res.quick_suggestions.length > 0) {
        suggestionsBar.innerHTML = res.quick_suggestions.map(s => `
          <button class="suggestion-chip">${escapeHtml(s)}</button>
        `).join("");
        attachChipListeners();
      }
    } catch (err) {
      removeTypingIndicator();
      appendMessage("assistant", "Xin lỗi bạn, trợ lý AI đang bận xử lý. Bạn vui lòng thử lại sau giây lát nhé!");
    } finally {
      sendBtn.disabled = false;
      chatInput.focus();
    }
  });

  // Suggestion chips
  attachChipListeners();

  // Clear history
  clearBtn.addEventListener("click", () => {
    confirmAction({
      title: "Xóa lịch sử cuộc trò chuyện",
      message: "Bạn có chắc chắn muốn xóa toàn bộ tin nhắn đã trò chuyện với AI không?",
      onConfirm: async () => {
        try {
          await api.delete("/chat/history");
          showToast("Đã xóa lịch sử trò chuyện", "success");
          appendWelcomeMessage();
        } catch (err) {
          showToast(err.message || "Lỗi khi xóa lịch sử", "error");
        }
      }
    });
  });
}

function attachChipListeners() {
  suggestionsBar.querySelectorAll(".suggestion-chip").forEach(chip => {
    chip.addEventListener("click", () => {
      chatInput.value = chip.textContent.trim();
      chatForm.dispatchEvent(new Event("submit"));
    });
  });
}
