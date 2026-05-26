/* ═══════════════════════════════════════════════════════════════════
   BUBBLE CANVAS ANIMATION
   ═══════════════════════════════════════════════════════════════════ */
(function initBubbles() {
  const canvas = document.getElementById('bubble-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  function resize() {
    canvas.width  = window.innerWidth;
    canvas.height = window.innerHeight;
  }
  resize();
  window.addEventListener('resize', resize);

  const NEON     = [0, 212, 255];   // #00d4ff
  const PURPLE   = [123, 95, 245];  // #7b5ff5
  const COUNT    = 28;

  const bubbles = Array.from({ length: COUNT }, () => makeBubble());

  function makeBubble() {
    const color = Math.random() > 0.6 ? PURPLE : NEON;
    return {
      x:      Math.random() * window.innerWidth,
      y:      Math.random() * window.innerHeight,
      r:      6 + Math.random() * 80,
      dx:     (Math.random() - 0.5) * 0.35,
      dy:     (Math.random() - 0.5) * 0.35,
      alpha:  0.04 + Math.random() * 0.1,
      color,
      pulse:  Math.random() * Math.PI * 2,
      pSpeed: 0.008 + Math.random() * 0.012,
    };
  }

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    bubbles.forEach(b => {
      b.pulse += b.pSpeed;
      const a = b.alpha + Math.sin(b.pulse) * 0.03;
      const r = b.r + Math.sin(b.pulse) * 3;

      // Outer glow
      const grad = ctx.createRadialGradient(b.x, b.y, 0, b.x, b.y, r);
      grad.addColorStop(0,   `rgba(${b.color},${a * 1.5})`);
      grad.addColorStop(0.5, `rgba(${b.color},${a * 0.6})`);
      grad.addColorStop(1,   `rgba(${b.color},0)`);

      ctx.beginPath();
      ctx.arc(b.x, b.y, r, 0, Math.PI * 2);
      ctx.fillStyle = grad;
      ctx.fill();

      // Thin ring
      ctx.beginPath();
      ctx.arc(b.x, b.y, r * 0.75, 0, Math.PI * 2);
      ctx.strokeStyle = `rgba(${b.color},${a * 0.8})`;
      ctx.lineWidth = 0.6;
      ctx.stroke();

      b.x += b.dx;
      b.y += b.dy;

      if (b.x < -b.r * 2) b.x = canvas.width  + b.r;
      if (b.x > canvas.width  + b.r * 2) b.x = -b.r;
      if (b.y < -b.r * 2) b.y = canvas.height + b.r;
      if (b.y > canvas.height + b.r * 2) b.y = -b.r;
    });

    requestAnimationFrame(draw);
  }
  draw();
})();

/* ═══════════════════════════════════════════════════════════════════
   TAB SYSTEM
   ═══════════════════════════════════════════════════════════════════ */
function switchTab(name) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  const btn   = document.querySelector(`.tab-btn[data-tab="${name}"]`);
  const panel = document.getElementById(`tab-${name}`);
  if (btn)   btn.classList.add('active');
  if (panel) panel.classList.add('active');
  const url = new URL(window.location);
  url.searchParams.set('tab', name);
  history.replaceState({}, '', url);
}

document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => switchTab(btn.dataset.tab));
});

(function () {
  const fromUrl    = new URLSearchParams(window.location.search).get('tab');
  const fromServer = document.body.dataset.activeTab;
  switchTab(fromUrl || fromServer || 'upload');
})();

const heroCta = document.getElementById('hero-cta');
if (heroCta) {
  heroCta.addEventListener('click', (e) => {
    e.preventDefault();
    switchTab('upload');
    document.getElementById('upload-tab-anchor')?.scrollIntoView({ behavior: 'smooth' });
  });
}

/* ═══════════════════════════════════════════════════════════════════
   LOADING OVERLAY
   ═══════════════════════════════════════════════════════════════════ */
const overlay = document.getElementById('loading-overlay');

function showLoading(msg = 'Processing…', sub = 'This may take a moment') {
  if (!overlay) return;
  overlay.querySelector('.loading-text').textContent = msg;
  overlay.querySelector('.loading-sub').textContent  = sub;
  overlay.classList.add('show');
}
function hideLoading() { overlay?.classList.remove('show'); }

/* ═══════════════════════════════════════════════════════════════════
   UPLOAD FORM
   ═══════════════════════════════════════════════════════════════════ */
const uploadForm = document.getElementById('upload-form');
const fileInput  = document.getElementById('pdf-input');
const fileLabel  = document.getElementById('file-label');
const uploadZone = document.getElementById('upload-zone');

if (uploadForm) {
  uploadForm.addEventListener('submit', (e) => {
    if (!fileInput?.files.length) {
      e.preventDefault();
      alert('Please select a PDF file first.');
      return;
    }
    showLoading('Analysing your book…', 'Detecting chapters — usually under 5 seconds');
  });
}

if (fileInput && fileLabel) {
  fileInput.addEventListener('change', () => {
    if (fileInput.files.length) {
      fileLabel.textContent = `✓  ${fileInput.files[0].name}`;
      fileLabel.style.color = 'var(--success)';
    }
  });
}

if (uploadZone) {
  uploadZone.addEventListener('dragover',  (e) => { e.preventDefault(); uploadZone.classList.add('drag-over'); });
  uploadZone.addEventListener('dragleave', ()  => uploadZone.classList.remove('drag-over'));
  uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('drag-over');
    if (e.dataTransfer.files.length && fileInput) {
      const dt = new DataTransfer();
      dt.items.add(e.dataTransfer.files[0]);
      fileInput.files = dt.files;
      fileInput.dispatchEvent(new Event('change'));
    }
  });
}

/* ═══════════════════════════════════════════════════════════════════
   QUIZ VALIDATION
   ═══════════════════════════════════════════════════════════════════ */
const quizForm = document.getElementById('quiz-form');
if (quizForm) {
  quizForm.addEventListener('submit', (e) => {
    const total = parseInt(quizForm.querySelector('[name="total_questions"]')?.value || 0);
    for (let i = 0; i < total; i++) {
      if (!quizForm.querySelector(`input[name="q${i}"]:checked`)) {
        e.preventDefault();
        // Highlight the unanswered card
        const card = quizForm.querySelectorAll('.question-card')[i];
        if (card) {
          card.scrollIntoView({ behavior: 'smooth', block: 'center' });
          card.style.borderColor = 'var(--danger)';
          card.style.boxShadow   = '0 0 20px rgba(255,77,109,0.2)';
          setTimeout(() => {
            card.style.borderColor = '';
            card.style.boxShadow   = '';
          }, 2000);
        }
        return;
      }
    }
    showLoading('Checking your answers…', 'Calculating score');
  });
}

/* ═══════════════════════════════════════════════════════════════════
   LOADING TRIGGERS FOR NAVIGATION
   ═══════════════════════════════════════════════════════════════════ */
document.querySelectorAll('.chapter-card').forEach(el =>
  el.addEventListener('click', () => showLoading('Loading chapter…', 'Generating summary and topics'))
);
document.querySelectorAll('.topic-item').forEach(el =>
  el.addEventListener('click', () => showLoading('Loading topic…', 'Generating explanation and quiz with AI'))
);

/* ═══════════════════════════════════════════════════════════════════
   CARD ENTRANCE ANIMATION
   ═══════════════════════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {
  const items = document.querySelectorAll(
    '.chapter-card, .topic-item, .question-card, .review-item, .stat-card, .feature-card, .about-card, .hero-stat, .step-row'
  );
  items.forEach((el, i) => {
    el.style.opacity   = '0';
    el.style.transform = 'translateY(18px)';
    el.style.transition = `opacity 0.4s ease ${i * 0.055}s, transform 0.4s ease ${i * 0.055}s`;
    requestAnimationFrame(() => requestAnimationFrame(() => {
      el.style.opacity   = '1';
      el.style.transform = 'translateY(0)';
    }));
  });
});

/* ═══════════════════════════════════════════════════════════════════
   PROGRESS CHARTS  (Chart.js via CDN)
   ═══════════════════════════════════════════════════════════════════ */
function initProgressCharts() {
  const dataEl = document.getElementById('progress-data');
  if (!dataEl) return;
  const records = JSON.parse(dataEl.textContent);
  if (!records.length) return;

  const cSuccess = '#00e891';
  const cWarning = '#ffb830';
  const cDanger  = '#ff4d6d';
  const cNeon    = '#00d4ff';
  const cMuted   = 'rgba(160,175,210,0.6)';
  const cText    = '#f0f4ff';
  const cBorder  = 'rgba(255,255,255,0.06)';

  Chart.defaults.color = cMuted;
  Chart.defaults.font.family = "'Inter', system-ui, sans-serif";

  const passed  = records.filter(r => r.pct >= 60).length;
  const failed  = records.length - passed;
  const band80  = records.filter(r => r.pct >= 80).length;
  const band60  = records.filter(r => r.pct >= 60 && r.pct < 80).length;
  const bandLow = records.filter(r => r.pct < 60).length;

  const doughnutOpts = (labels, data, colors) => ({
    type: 'doughnut',
    data: {
      labels,
      datasets: [{ data, backgroundColor: colors, borderColor: '#000', borderWidth: 2, hoverOffset: 8 }],
    },
    options: {
      cutout: '62%',
      animation: { duration: 700, easing: 'easeOutQuart' },
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: ctx => ` ${ctx.label}: ${ctx.parsed}` } }
      }
    },
  });

  new Chart(document.getElementById('chart-passfail'),
    doughnutOpts(['Passed', 'Failed'], [passed, failed], [cSuccess, cDanger])
  );
  new Chart(document.getElementById('chart-bands'),
    doughnutOpts(['80–100%', '60–79%', '<60%'], [band80, band60, bandLow], [cSuccess, cWarning, cDanger])
  );

  // Topic bar
  const seen = new Set();
  const topicRecs = [];
  for (const r of records) {
    if (!seen.has(r.topic)) { seen.add(r.topic); topicRecs.push(r); }
    if (topicRecs.length >= 10) break;
  }
  topicRecs.reverse();

  new Chart(document.getElementById('chart-topics'), {
    type: 'bar',
    data: {
      labels: topicRecs.map(r => r.topic.length > 22 ? r.topic.slice(0,22) + '…' : r.topic),
      datasets: [{
        data:            topicRecs.map(r => r.pct),
        backgroundColor: topicRecs.map(r => r.pct >= 80 ? cSuccess : r.pct >= 60 ? cWarning : cDanger),
        borderColor: 'transparent',
        borderRadius: 6,
      }],
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 700 },
      scales: {
        x: {
          min: 0, max: 100,
          ticks: { color: cMuted, font: { size: 11 }, callback: v => v + '%' },
          grid: { color: cBorder },
        },
        y: {
          ticks: { color: cText, font: { size: 11 } },
          grid: { display: false },
        },
      },
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: ctx => ` ${ctx.parsed.x}%` } }
      }
    },
  });
}

(function loadChartJs() {
  if (!document.getElementById('chart-passfail')) return;
  const s = document.createElement('script');
  s.src   = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js';
  s.onload = initProgressCharts;
  document.head.appendChild(s);
})();
