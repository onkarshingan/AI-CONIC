/**
 * AI Smart Attendance System – Shared JavaScript
 * Utility functions used across all pages
 */

// ── Toast Notifications ────────────────────────────────────────────────────

/**
 * Show a non-blocking toast message at the bottom of the screen.
 * @param {string} message
 * @param {"success"|"error"|"info"} type
 * @param {number} duration  milliseconds
 */
function showToast(message, type = "info", duration = 3500) {
  // Create container if missing
  let container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    Object.assign(container.style, {
      position  : "fixed",
      bottom    : "1.5rem",
      right     : "1.5rem",
      zIndex    : "9999",
      display   : "flex",
      flexDirection: "column",
      gap       : "0.5rem",
      maxWidth  : "340px"
    });
    document.body.appendChild(container);
  }

  const colors = {
    success: { bg: "rgba(0,255,148,0.12)", border: "rgba(0,255,148,0.35)", text: "#00ff94" },
    error  : { bg: "rgba(255,77,109,0.12)", border: "rgba(255,77,109,0.35)", text: "#ff4d6d" },
    info   : { bg: "rgba(0,229,255,0.12)", border: "rgba(0,229,255,0.35)", text: "#00e5ff" }
  };
  const c = colors[type] || colors.info;

  const toast = document.createElement("div");
  Object.assign(toast.style, {
    background   : c.bg,
    border       : `1px solid ${c.border}`,
    color        : c.text,
    padding      : "0.75rem 1.1rem",
    borderRadius : "8px",
    fontSize     : "0.82rem",
    fontFamily   : "var(--font-mono, monospace)",
    backdropFilter: "blur(10px)",
    animation    : "slideInRight 0.3s ease both",
    maxWidth     : "340px",
    wordBreak    : "break-word"
  });
  toast.textContent = message;

  // Inject keyframe once
  if (!document.getElementById("toast-style")) {
    const style = document.createElement("style");
    style.id = "toast-style";
    style.textContent = `
      @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to   { transform: translateX(0);   opacity: 1; }
      }
      @keyframes fadeOutRight {
        from { transform: translateX(0);   opacity: 1; }
        to   { transform: translateX(100%); opacity: 0; }
      }
    `;
    document.head.appendChild(style);
  }

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = "fadeOutRight 0.3s ease both";
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// ── Format helpers ─────────────────────────────────────────────────────────

function formatDate(dateStr) {
  if (!dateStr) return "—";
  try {
    return new Date(dateStr).toLocaleDateString("en-IN", {
      day: "2-digit", month: "short", year: "numeric"
    });
  } catch {
    return dateStr;
  }
}

// ── API wrapper ────────────────────────────────────────────────────────────

async function apiGet(url) {
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    showToast(`API Error: ${err.message}`, "error");
    return null;
  }
}

async function apiPost(url, body) {
  try {
    const res = await fetch(url, {
      method : "POST",
      headers: { "Content-Type": "application/json" },
      body   : JSON.stringify(body)
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    showToast(`API Error: ${err.message}`, "error");
    return null;
  }
}

// ── Active nav highlight ────────────────────────────────────────────────────

(function highlightActiveNav() {
  const path = window.location.pathname;
  document.querySelectorAll(".nav-links a").forEach(a => {
    const href = a.getAttribute("href");
    if (href === path || (href !== "/" && path.startsWith(href))) {
      a.classList.add("active");
    } else {
      a.classList.remove("active");
    }
  });
})();

// ── Webcam utils ───────────────────────────────────────────────────────────

/**
 * Start a webcam stream and bind it to a <video> element.
 * @param {string} videoId   id of the <video> element
 * @returns {MediaStream|null}
 */
async function startWebcam(videoId) {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    const video  = document.getElementById(videoId);
    if (video) video.srcObject = stream;
    return stream;
  } catch (err) {
    showToast("Camera access denied. Please allow webcam permissions.", "error");
    return null;
  }
}

/**
 * Capture a single frame from a <video> element and return base64 JPEG.
 * @param {string} videoId
 * @param {string} canvasId   hidden canvas to draw on
 * @returns {string}  base64 dataURL
 */
function captureFrame(videoId, canvasId) {
  const video  = document.getElementById(videoId);
  const canvas = document.getElementById(canvasId);
  if (!video || !canvas) return null;
  canvas.width  = video.videoWidth  || 320;
  canvas.height = video.videoHeight || 240;
  canvas.getContext("2d").drawImage(video, 0, 0);
  return canvas.toDataURL("image/jpeg", 0.85);
}

// ── Export for modules if ever needed ─────────────────────────────────────
if (typeof module !== "undefined") {
  module.exports = { showToast, formatDate, apiGet, apiPost, startWebcam, captureFrame };
}
