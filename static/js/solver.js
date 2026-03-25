'use strict';

/* ───────────────── STATE ───────────────── */
const state = {
  file: null,
  latex: '',
  solution: null,
};

/* ───────────────── DOM ───────────────── */
const el = {
  dropZone: document.getElementById('dropZone'),
  input: document.getElementById('imageInput'),
  preview: document.getElementById('imagePreview'),
  btnConvert: document.getElementById('btnConvert'),
  btnSolve: document.getElementById('btnSolve'),
  btnMistakes: document.getElementById('btnCheckMistakes'),
  equationSection: document.getElementById('equationSection'),
  latexDisplay: document.getElementById('latexDisplay'),
  confidence: document.getElementById('confidenceLabel'),
  solutionSection: document.getElementById('solutionSection'),
  steps: document.getElementById('stepsContainer'),
  final: document.getElementById('finalAnswer'),
  mistakesSection: document.getElementById('mistakesSection'),
  mistakes: document.getElementById('mistakesContainer'),
  error: document.getElementById('errorBanner')
};

/* ───────────────── UTILS ───────────────── */
const UI = {
  show: (...els) => els.forEach(e => e.classList.remove('hidden')),
  hide: (...els) => els.forEach(e => e.classList.add('hidden')),

  loading(btn, state) {
    if (!btn) return;
    if (state) {
      btn.dataset.txt = btn.innerHTML;
      btn.disabled = true;
      btn.innerHTML = '⏳ Processing...';
    } else {
      btn.disabled = false;
      btn.innerHTML = btn.dataset.txt;
    }
  },

  error(msg) {
    el.error.textContent = '⚠ ' + msg;
    UI.show(el.error);
    setTimeout(() => UI.hide(el.error), 5000);
  },

  toast(msg) {
    alert(msg);
  }
};

const API = {
  async post(url, data, isFile = false) {
    const opt = { method: 'POST' };

    if (isFile) {
      opt.body = data;
    } else {
      opt.headers = { 'Content-Type': 'application/json' };
      opt.body = JSON.stringify(data);
    }

    const res = await fetch(url, opt);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  }
};

/* ───────────────── FILE HANDLING ───────────────── */
function setFile(file) {
  if (!file || !file.type.startsWith('image/')) {
    return UI.error('Upload valid image');
  }

  state.file = file;
  el.btnConvert.disabled = false;

  const reader = new FileReader();
  reader.onload = e => {
    el.preview.innerHTML = `<img src="${e.target.result}" />`;
    UI.show(el.preview);
  };
  reader.readAsDataURL(file);

  el.input.value = '';
  UI.hide(el.equationSection, el.solutionSection, el.mistakesSection);
}

/* ───────────────── ACTIONS ───────────────── */
async function convertImage() {
  if (!state.file || el.btnConvert.disabled) return;

  UI.loading(el.btnConvert, true);

  try {
    const fd = new FormData();
    fd.append('image', state.file);

    const data = await API.post('/api/image-to-latex', fd, true);

    if (!data?.latex) throw new Error('Invalid response');

    state.latex = data.latex;

    el.latexDisplay.innerText = `\\(${data.latex}\\)`;
    el.confidence.textContent =
      `Confidence: ${Math.round((data.confidence || 0) * 100)}%`;

    UI.show(el.equationSection);
    el.btnMistakes.disabled = true;

    UI.toast('Converted!');
  } catch (e) {
    UI.error(e.message);
  } finally {
    UI.loading(el.btnConvert, false);
  }
}

async function solveEquation() {
  if (!state.latex) return;

  UI.loading(el.btnSolve, true);

  try {
    const data = await API.post('/api/solve-equation', {
      equation: state.latex
    });

    state.solution = data;
    renderSteps(data.steps || []);
    renderFinal(data.solution || []);

    UI.show(el.solutionSection);
    el.btnMistakes.disabled = false;

    UI.toast('Solved!');
  } catch (e) {
    UI.error(e.message);
  } finally {
    UI.loading(el.btnSolve, false);
  }
}

async function checkMistakes() {
  if (!state.latex) return;

  el.btnMistakes.disabled = true;

  try {
    const data = await API.post('/api/mistake-check', {
      equation: state.latex,
      steps: state.solution?.steps || []
    });

    renderMistakes(data);
    UI.show(el.mistakesSection);

    UI.toast('Checked!');
  } catch (e) {
    UI.error(e.message);
  } finally {
    el.btnMistakes.disabled = false;
  }
}

/* ───────────────── RENDER ───────────────── */
function renderSteps(steps) {
  el.steps.innerHTML = '';
  steps.forEach(s => {
    const div = document.createElement('div');
    div.innerHTML = `
      <b>Step ${s.step}</b><br>
      ${escapeHtml(s.description)}<br>
      \\(${s.expression || ''}\\)
    `;
    el.steps.appendChild(div);
  });
}

function renderFinal(sol) {
  el.final.innerHTML = sol.length
    ? `✅ \\(${sol.join(', ')}\\)`
    : '⚠ No solution';
}

function renderMistakes(data) {
  el.mistakes.innerHTML = '';

  if (!data?.has_mistakes) {
    el.mistakes.innerHTML = '✅ No mistakes';
    return;
  }

  data.mistakes.forEach(m => {
    const div = document.createElement('div');
    div.innerHTML = `<b>${m.name}</b><br>${m.description}`;
    el.mistakes.appendChild(div);
  });
}

/* ───────────────── EVENTS ───────────────── */
el.dropZone.addEventListener('dragover', e => {
  e.preventDefault();
  el.dropZone.classList.add('dragover');
});

el.dropZone.addEventListener('dragleave', () => {
  el.dropZone.classList.remove('dragover');
});

el.dropZone.addEventListener('drop', e => {
  e.preventDefault();
  el.dropZone.classList.remove('dragover');
  setFile(e.dataTransfer.files[0]);
});

el.dropZone.addEventListener('click', e => {
  if (e.target.tagName !== 'INPUT') el.input.click();
});

el.input.addEventListener('change', () => {
  setFile(el.input.files[0]);
});

el.btnConvert.addEventListener('click', convertImage);
el.btnSolve.addEventListener('click', solveEquation);
el.btnMistakes.addEventListener('click', checkMistakes);

/* ───────────────── SECURITY ───────────────── */
function escapeHtml(str = '') {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;');
}