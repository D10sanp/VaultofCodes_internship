/**
 * VaultOfCodes chat widget client logic.
 * Talks to the FastAPI backend at /api/chat and /api/suggested-questions.
 */
(function () {
  "use strict";

  const API_BASE = ""; // same origin; set to your API URL if hosted separately

  const launcher = document.getElementById("chat-launcher");
  const launcherBadge = document.getElementById("launcher-badge");
  const chatWindow = document.getElementById("chat-window");
  const closeBtn = document.getElementById("chat-close");
  const messagesEl = document.getElementById("chat-messages");
  const typingEl = document.getElementById("typing-indicator");
  const quickRepliesEl = document.getElementById("quick-replies");
  const form = document.getElementById("chat-form");
  const input = document.getElementById("chat-input");
  const sendBtn = document.getElementById("chat-send");
  const chatBody = document.getElementById("chat-body");

  const STORAGE_KEY = "vault_chat_session_id";
  let sessionId = sessionStorage.getItem(STORAGE_KEY) || null;
  let hasOpenedOnce = false;

  // ---------------------------------------------------------------
  // Utilities
  // ---------------------------------------------------------------

  function scrollToBottom() {
    chatBody.scrollTop = chatBody.scrollHeight;
  }

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }

  /** Very small markdown-ish formatter: **bold** and line breaks, safely. */
  function formatReply(text) {
    const escaped = escapeHtml(text);
    return escaped
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/\n/g, "<br>");
  }

  function addMessage(role, html) {
    const wrap = document.createElement("div");
    wrap.className = "msg msg--" + role;
    wrap.innerHTML = `<div class="bubble">${html}</div>`;
    messagesEl.appendChild(wrap);
    scrollToBottom();
    return wrap;
  }

  function addUserMessage(text) {
    addMessage("user", formatReply(text));
  }

  function addBotMessage(data) {
    const wrap = document.createElement("div");
    wrap.className = "msg msg--bot";

    let stampHtml = "";
    if (data.intent === "certificate_verification" || data.intent === "certificate_query") {
      stampHtml = `<div class="verified-stamp">⛨ knowledge base verified</div>`;
    }

    let bubbleHtml = `<div class="bubble">${stampHtml}${formatReply(data.reply)}`;

    if (data.links && data.links.length) {
      bubbleHtml += `<div class="msg-links">`;
      data.links.forEach((link) => {
        bubbleHtml += `<a class="msg-link" href="${escapeHtml(link.url)}" target="_blank" rel="noopener">${escapeHtml(link.label)}</a>`;
      });
      bubbleHtml += `</div>`;
    }

    if (data.escalate && data.whatsapp_link) {
      bubbleHtml += `
        <div class="escalation-card">
          <p class="escalation-card__tag">Case forwarded · human support</p>
          <a class="whatsapp-btn" href="${escapeHtml(data.whatsapp_link)}" target="_blank" rel="noopener">
            💬 Continue on WhatsApp
          </a>
        </div>`;
    }

    bubbleHtml += `</div>`;
    wrap.innerHTML = bubbleHtml;
    messagesEl.appendChild(wrap);
    scrollToBottom();
  }

  function showTyping() {
    typingEl.classList.remove("hidden");
    scrollToBottom();
  }
  function hideTyping() {
    typingEl.classList.add("hidden");
  }

  function renderQuickReplies(list) {
    quickRepliesEl.innerHTML = "";
    (list || []).forEach((q) => {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "quick-reply-chip";
      chip.textContent = q;
      chip.addEventListener("click", () => sendMessage(stripEmoji(q)));
      quickRepliesEl.appendChild(chip);
    });
  }

  function stripEmoji(text) {
    // Quick-reply chips are prefixed with an emoji for scannability;
    // strip it before sending as the actual query text.
    return text.replace(/^[^\w]+/, "").trim();
  }

  // ---------------------------------------------------------------
  // Networking
  // ---------------------------------------------------------------

  async function sendMessage(text) {
    if (!text || !text.trim()) return;

    addUserMessage(text);
    input.value = "";
    sendBtn.disabled = true;
    showTyping();

    try {
      const res = await fetch(API_BASE + "/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, message: text }),
      });

      if (!res.ok) throw new Error("Request failed: " + res.status);

      const data = await res.json();
      sessionId = data.session_id;
      sessionStorage.setItem(STORAGE_KEY, sessionId);

      // Small artificial delay so the typing indicator feels natural,
      // rather than flashing instantly.
      await new Promise((r) => setTimeout(r, 350));

      hideTyping();
      addBotMessage(data);
      renderQuickReplies(data.quick_replies);
    } catch (err) {
      hideTyping();
      addMessage(
        "bot",
        "Something went wrong reaching support right now. Please try again, or reach us on WhatsApp."
      );
      console.error(err);
    } finally {
      sendBtn.disabled = false;
      input.focus();
    }
  }

  async function loadSuggestedQuestions() {
    try {
      const res = await fetch(API_BASE + "/api/suggested-questions");
      const data = await res.json();
      renderQuickReplies(data.questions);
    } catch (err) {
      console.error("Could not load suggested questions", err);
    }
  }

  // ---------------------------------------------------------------
  // Widget open / close
  // ---------------------------------------------------------------

  function openChat() {
    chatWindow.classList.remove("hidden");
    chatWindow.setAttribute("aria-hidden", "false");
    launcher.setAttribute("aria-expanded", "true");
    launcherBadge.hidden = true;

    if (!hasOpenedOnce) {
      hasOpenedOnce = true;
      addMessage(
        "bot",
        "Hi! 👋 I'm the VaultOfCodes support assistant. I can help with courses, internships, certificates, offer letters, and finding your way around the site. What can I help with?"
      );
      loadSuggestedQuestions();
    }
    input.focus();
  }

  function closeChat() {
    chatWindow.classList.add("hidden");
    chatWindow.setAttribute("aria-hidden", "true");
    launcher.setAttribute("aria-expanded", "false");
  }

  launcher.addEventListener("click", () => {
    const isHidden = chatWindow.classList.contains("hidden");
    if (isHidden) openChat();
    else closeChat();
  });

  closeBtn.addEventListener("click", closeChat);

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    sendMessage(input.value);
  });

  // Show a subtle "new message" badge on the launcher after a short delay,
  // to invite first-time visitors to open the chat (only if never opened).
  setTimeout(() => {
    if (!hasOpenedOnce) launcherBadge.hidden = false;
  }, 4000);
})();
