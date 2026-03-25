/**
 * main.js
 * Shared utilities used across all pages of AI Math Tutor.
 */

'use strict';

// ── Toast notifications ──────────────────────────────────────────────────────
function showToast(message, type = 'info') {
  const existing = document.getElementById('toast');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.id = 'toast';
  toast.style.cssText = `
    position:fixed; bottom:1.5rem; right:1.5rem;
    background:${type === 'error' ? '#c0392b' : type === 'success' ? '#34a853' : '#1a73e8'};
    color:#fff; padding:.75rem 1.25rem; border-radius:8px;
    font-size:.9rem; font-weight:600; z-index:9999;
    box-shadow:0 4px 16px rgba(0,0,0,.2);
    animation:slideIn .25s ease;
  `;
  toast.textContent = message;

  if (!document.getElementById('toast-style')) {
    const s = document.createElement('style');
    s.id = 'toast-style';
    s.textContent = `@keyframes slideIn{from{transform:translateY(20px);opacity:0}to{transform:none;opacity:1}}`;
    document.head.appendChild(s);
  }

  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3500);
}

// ── Button loading state ─────────────────────────────────────────────────────
function setLoading(btn, loading) {
  const text    = btn.querySelector('.btn-text');
  const spinner = btn.querySelector('.spinner');
  btn.disabled  = loading;
  if (text)    text.classList.toggle('hidden', loading);
  if (spinner) spinner.classList.toggle('hidden', !loading);
}

// ── API helper ───────────────────────────────────────────────────────────────
async function apiPost(url, body, isFormData = false) {
  const opts = { method: 'POST' };
  if (isFormData) {
    opts.body = body;
  } else {
    opts.headers = { 'Content-Type': 'application/json' };
    opts.body    = JSON.stringify(body);
  }
  const res  = await fetch(url, opts);
  const json = await res.json();
  if (!res.ok || json.status === 'error') {
    throw new Error(json.message || `HTTP ${res.status}`);
  }
  return json.data;
}

// ── MathJax re-render ────────────────────────────────────────────────────────
function renderMath(el) {
  if (window.MathJax && MathJax.typesetPromise) {
    MathJax.typesetPromise([el]).catch(console.warn);
  }
}

window.MathUtils = { showToast, setLoading, apiPost, renderMath };
