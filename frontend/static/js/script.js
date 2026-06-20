/**
 * SPAS — Antigravity Script
 * Particles, animations, API helpers, dashboard logic.
 */

// ── Particle system ────────────────────────────────────────────────────────
(function spawnParticles() {
  const colours = ['#A78BFA','#34D399','#ffffff'];
  for (let i = 0; i < 50; i++) {
    const p = document.createElement('div');
    p.className = 'particle';
    const size   = 2 + Math.random() * 3;
    const col    = colours[Math.floor(Math.random() * colours.length)];
    const dur    = (4 + Math.random() * 10).toFixed(1);
    const delay  = (Math.random() * 8).toFixed(1);
    const tx     = (Math.random() * 80 - 40).toFixed(0);
    const ty     = (60 + Math.random() * 40).toFixed(0);
    const opacity= (.4 + Math.random() * .4).toFixed(2);
    p.style.cssText = `
      width:${size}px;height:${size}px;background:${col};opacity:${opacity};
      left:${Math.random()*100}vw;top:${Math.random()*100}vh;
      --dur:${dur}s;animation-delay:${delay}s;
      animation-name:particleDrift;animation-duration:${dur}s;
      animation-iteration-count:infinite;animation-direction:alternate;
      animation-timing-function:ease-in-out;
      --tx:${tx}px;--ty:${ty}px;
    `;
    document.body.appendChild(p);
  }
})();

// ── Auto-dismiss flash messages ────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.flash-msg').forEach((msg, i) => {
    msg.style.animationDelay = `${i * 0.1}s`;
    setTimeout(() => {
      msg.style.opacity = '0';
      msg.style.transform = 'translateX(60px)';
      msg.style.transition = 'all 0.4s ease';
      setTimeout(() => msg.remove(), 400);
    }, 4000 + i * 200);
  });
});

// ── Rise-in stagger on cards ────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.card, .stat-card, .glass').forEach((el, i) => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(40px)';
    el.style.transition = `opacity 0.55s ease-out ${i*80}ms, transform 0.55s ease-out ${i*80}ms`;
    requestAnimationFrame(() => {
      setTimeout(() => { el.style.opacity = '1'; el.style.transform = 'translateY(0)'; }, 50);
    });
  });
});

// ── Stagger float delays on stat cards ────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.stat-card').forEach((el, i) => {
    el.style.animationDelay = `${i * 0.4}s`;
  });
  document.querySelectorAll('.feature-card').forEach((el, i) => {
    el.style.animationDelay = `${i * 0.3}s`;
  });
});

// ── Show/hide password toggle ──────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.input-toggle').forEach(btn => {
    btn.addEventListener('click', () => {
      const input = btn.closest('.input-wrap').querySelector('input');
      const isText = input.type === 'text';
      input.type = isText ? 'password' : 'text';
      btn.innerHTML = isText
        ? `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>`
        : `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>`;
    });
  });
});

// ── Demo login chips ───────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const credentials = {
    Admin:   { email: 'admin@gmail.com',   password: 'admin123!' },
    Teacher: { email: 'teacher@gmail.com', password: 'teach123!' },
    Student: { email: 'student@gmail.com', password: 'study123!' },
  };
  document.querySelectorAll('.demo-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const role = chip.dataset.role;
      const creds = credentials[role];
      if (!creds) return;
      const emailEl = document.getElementById('email');
      const pwEl    = document.getElementById('password');
      if (emailEl) emailEl.value = creds.email;
      if (pwEl)    pwEl.value    = creds.password;
    });
  });
});

// ── API Helper ────────────────────────────────────────────────────────────
const API = {
  async get(url) {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`GET ${url} failed`);
    return res.json();
  },
  async post(url, data) {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.error || 'POST request failed');
    }
    return res.json();
  },
  async del(url) {
    const res = await fetch(url, { method: 'DELETE' });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.error || 'DELETE request failed');
    }
    return res.json();
  }
};

// ── Toast notifications ───────────────────────────────────────────────────
function showToast(message, type = 'info') {
  let container = document.querySelector('.flash-messages');
  if (!container) {
    container = document.createElement('div');
    container.className = 'flash-messages';
    document.body.appendChild(container);
  }
  const toast = document.createElement('div');
  toast.className = `flash-msg ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(60px)';
    toast.style.transition = 'all 0.4s ease';
    setTimeout(() => toast.remove(), 400);
  }, 3500);
}

// ── Form validation ────────────────────────────────────────────────────────
function validateRegisterForm() {
  const fields = ['name','roll_number','department','semester','email','password'];
  document.querySelectorAll('.form-error').forEach(e => e.remove());
  let valid = true;
  function showError(field, msg) {
    const err = document.createElement('span');
    err.className = 'form-error';
    err.style.cssText = 'color:var(--clr-red);font-size:.8rem;margin-top:4px;display:block';
    err.textContent = msg;
    field.parentNode.appendChild(err);
    valid = false;
  }
  const get = id => document.getElementById(id);
  if (!get('name')?.value.trim())       showError(get('name'),       'Name is required');
  if (!get('roll_number')?.value.trim()) showError(get('roll_number'), 'Roll number is required');
  if (!get('department')?.value.trim())  showError(get('department'),  'Department is required');
  if (!get('semester')?.value)           showError(get('semester'),    'Select a semester');
  const email = get('email');
  if (!email?.value.trim())                               showError(email, 'Email is required');
  else if (!email.value.toLowerCase().endsWith('@gmail.com')) showError(email, 'Must be @gmail.com');
  const pw = get('password');
  if (!pw?.value)              showError(pw, 'Password is required');
  else if (pw.value.length < 8) showError(pw, 'Minimum 8 characters');
  return valid;
}

function validateLoginForm() {
  document.querySelectorAll('.form-error').forEach(e => e.remove());
  let valid = true;
  function showError(field, msg) {
    const err = document.createElement('span');
    err.className = 'form-error';
    err.style.cssText = 'color:var(--clr-red);font-size:.8rem;margin-top:4px;display:block';
    err.textContent = msg;
    field.parentNode.appendChild(err);
    valid = false;
  }
  const email = document.getElementById('email');
  const pw    = document.getElementById('password');
  if (!email?.value.trim())                                   showError(email, 'Email is required');
  else if (!email.value.toLowerCase().endsWith('@gmail.com')) showError(email, 'Must be @gmail.com');
  if (!pw?.value)              showError(pw, 'Password is required');
  else if (pw.value.length < 8) showError(pw, 'Minimum 8 characters');
  // Shake card on error
  if (!valid) {
    const card = document.querySelector('.auth-card');
    if (card) { card.classList.remove('shake'); void card.offsetWidth; card.classList.add('shake'); }
  }
  return valid;
}

// ── Calculation utilities ─────────────────────────────────────────────────
function calculateAverage(arr) {
  if (!arr.length) return 0;
  return Math.round((arr.reduce((a, b) => a + b, 0) / arr.length) * 10) / 10;
}

function getPerformanceStatus(avg) {
  if (avg >= 90) return { text: 'Outstanding', cls: 'badge-success' };
  if (avg >= 75) return { text: 'Good',        cls: 'badge-success' };
  if (avg >= 60) return { text: 'Average',     cls: 'badge-warning' };
  if (avg >= 40) return { text: 'Below Avg',   cls: 'badge-warning' };
  return             { text: 'Needs Help',     cls: 'badge-danger'  };
}

// ── Dashboard ─────────────────────────────────────────────────────────────
async function loadDashboard() {
  try {
    const [student, marks] = await Promise.all([
      API.get('/api/student'),
      API.get('/api/marks'),
    ]);

    // Profile
    const profileEl = document.getElementById('profile-section');
    if (profileEl) {
      const initials = student.name.split(' ').map(w => w[0]).join('').toUpperCase();
      profileEl.innerHTML = `
        <div class="profile-card">
          <div class="profile-avatar">${initials}</div>
          <div class="profile-info">
            <h2>${student.name}</h2>
            <p>${student.department} — Semester ${student.semester}</p>
            <p style="color:var(--clr-muted)">Roll: ${student.roll_number} | ${student.email}</p>
          </div>
        </div>`;
    }

    // Stats
    const pcts = marks.map(m => Math.round((m.marks / m.max_marks) * 100));
    const avg  = calculateAverage(pcts);
    
    // Calculate average attendance from subjects
    const attAvg = marks.length 
      ? Math.round(marks.reduce((sum, m) => sum + (m.attendance || 0), 0) / marks.length)
      : (student.attendance || 0);

    const status = getPerformanceStatus(avg);
    setStatCard('stat-avg',        avg + '%',   'Average Marks');
    setStatCard('stat-attendance', attAvg + '%', 'Attendance');
    setStatCard('stat-highest',    marks.length ? Math.max(...marks.map(m => m.marks)) : 0, 'Highest Mark');
    setStatCard('stat-status',     status.text, 'Performance');

    // Table
    const tbody = document.getElementById('marks-tbody');
    if (tbody) {
      tbody.innerHTML = marks.length ? marks.map((m, i) => {
        const pct = Math.round((m.marks / m.max_marks) * 100);
        const st  = getPerformanceStatus(pct);
        return `<tr>
          <td>${i + 1}</td>
          <td>${m.subject}</td>
          <td>${m.marks} / ${m.max_marks} (Study: ${m.study_hours || 0}h)</td>
          <td>
            <div class="progress-bar-wrap">
              <div class="progress-bar-fill" style="width:${pct}%"></div>
            </div>
          </td>
          <td><span class="badge ${st.cls}">${pct}%</span></td>
          <td><span class="badge ${pct >= 75 ? 'badge-success' : 'badge-warning'}">${m.attendance || 0}%</span></td>
          <td>
            <div style="display:flex; gap:6px;">
              <button class="btn btn-outline btn-sm edit-mark-btn" data-subject="${m.subject}" style="padding:4px 8px;font-size:.7rem;">✏️ Edit</button>
              <button class="btn btn-danger btn-sm delete-mark-btn" data-subject="${m.subject}" style="padding:4px 8px;font-size:.7rem;">🗑️</button>
            </div>
          </td>
        </tr>`;
      }).join('') : `<tr><td colspan="7" style="text-align:center;color:var(--clr-muted);padding:32px">No marks yet. Add your first subject!</td></tr>`;
      
      // Attach event listeners
      tbody.querySelectorAll('.delete-mark-btn').forEach(btn => {
        btn.onclick = () => deleteMark(btn.dataset.subject);
      });
      tbody.querySelectorAll('.edit-mark-btn').forEach(btn => {
        btn.onclick = () => editMark(btn.dataset.subject, marks);
      });
    }

    renderMarksBarChart(marks);
    renderAttendanceChart(attAvg);
    renderSubjectAttendanceChart(marks);
    renderStudyBarChart(marks);
  } catch (err) {
    console.error('Dashboard error:', err);
    showToast('Failed to load dashboard data', 'error');
  }
}

function setStatCard(id, value, label) {
  const el = document.getElementById(id);
  if (!el) return;
  el.querySelector('h3').textContent = value;
  el.querySelector('p').textContent  = label;
}

// ── Charts ────────────────────────────────────────────────────────────────
let marksChartInst = null;
let attendanceChartInst = null;
let studyChartInst = null;
let subjAttendanceChartInst = null;

function renderMarksBarChart(marks) {
  const ctx = document.getElementById('marksChart');
  if (!ctx) return;
  if (marksChartInst) marksChartInst.destroy();
  const labels = marks.map(m => m.subject);
  const pcts = marks.map(m => Math.round((m.marks / m.max_marks) * 100));
  marksChartInst = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Marks %',
        data: pcts,
        backgroundColor: pcts.map(p =>
          p >= 75 ? 'rgba(52,211,153,.7)' : p >= 60 ? 'rgba(251,191,36,.7)' : 'rgba(248,113,113,.7)'
        ),
        borderRadius: 8,
        maxBarThickness: 48,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, max: 100, grid: { color: 'rgba(255,255,255,.05)' }, ticks: { color: 'rgba(241,240,255,.5)' } },
        x: { grid: { display: false }, ticks: { color: 'rgba(241,240,255,.5)' } }
      }
    }
  });
}

function renderAttendanceChart(percent) {
  const ctx = document.getElementById('attendanceChart');
  const textEl = document.getElementById('attendance-text');
  if (!ctx) return;
  if (attendanceChartInst) attendanceChartInst.destroy();
  if (textEl) textEl.innerText = `${Math.round(percent)}%`;

  attendanceChartInst = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Attended', 'Missed'],
      datasets: [{
        data: [percent, 100 - percent],
        backgroundColor: ['#A78BFA', 'rgba(255,255,255,.05)'],
        borderWidth: 0,
        cutout: '80%'
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } }
    }
  });
}

function renderStudyBarChart(marks) {
  const ctx = document.getElementById('studyChart');
  if (!ctx || marks.length === 0) return;
  if (studyChartInst) studyChartInst.destroy();

  const labels = marks.map(m => m.subject);
  const data = marks.map(m => m.study_hours || 0);

  studyChartInst = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Study Hours',
        data,
        backgroundColor: 'rgba(251, 191, 36, 0.8)',
        borderRadius: 4
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: 'rgba(241,240,255,.5)' } },
        x: { grid: { display: false }, ticks: { color: 'rgba(241,240,255,.5)' } }
      }
    }
  });
}

function renderSubjectAttendanceChart(marks) {
  const ctx = document.getElementById('subjAttendanceChart');
  if (!ctx || marks.length === 0) return;
  if (subjAttendanceChartInst) subjAttendanceChartInst.destroy();

  const labels = marks.map(m => m.subject);
  const data = marks.map(m => m.attendance || 0);

  subjAttendanceChartInst = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Attendance %',
        data,
        backgroundColor: data.map(a => a >= 75 ? 'rgba(167,139,250,0.8)' : 'rgba(248,113,113,0.8)'),
        borderRadius: 6
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, max: 100, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: 'rgba(241,240,255,.5)' } },
        x: { grid: { display: false }, ticks: { color: 'rgba(241,240,255,.5)' } }
      }
    }
  });
}

// ── Analysis ──────────────────────────────────────────────────────────────
async function loadAnalysis() {
  try {
    const marks = await API.get('/api/marks');
    const pcts  = marks.map(m => ({ ...m, pct: Math.round((m.marks / m.max_marks) * 100) }));
    const sorted = [...pcts].sort((a, b) => b.pct - a.pct);

    const strongEl = document.getElementById('strong-subjects');
    if (strongEl) {
      const strong = sorted.filter(m => m.pct >= 75);
      strongEl.innerHTML = strong.length
        ? strong.map(m => `<div class="subject-item"><span><strong>${m.subject}</strong></span><span class="badge badge-success">${m.pct}%</span></div>`).join('')
        : '<p style="color:var(--clr-muted)">No strong subjects yet.</p>';
    }

    const weakEl = document.getElementById('weak-subjects');
    if (weakEl) {
      const weak = sorted.filter(m => m.pct < 60);
      weakEl.innerHTML = weak.length
        ? weak.map(m => `<div class="subject-item"><span><strong>${m.subject}</strong></span><span class="badge badge-danger">${m.pct}%</span></div>`).join('')
        : '<p style="color:var(--clr-muted)">No weak subjects — Great! 🎉</p>';
    }

    const avg    = calculateAverage(pcts.map(m => m.pct));
    const status = getPerformanceStatus(avg);
    const overallEl = document.getElementById('overall-performance');
    if (overallEl) {
      overallEl.innerHTML = `
        <div style="text-align:center;padding:20px 0">
          <h2 style="font-family:var(--font-head);font-size:3.5rem;font-weight:800;background:linear-gradient(135deg,var(--clr-accent),var(--clr-mint));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">${avg}%</h2>
          <span class="badge ${status.cls}" style="font-size:1rem;padding:8px 24px;margin-top:12px;display:inline-block">${status.text}</span>
          <p style="margin-top:12px;color:var(--clr-muted)">Based on ${marks.length} subject${marks.length !== 1 ? 's' : ''}</p>
        </div>`;
    }
    
    // Fetch AI Prediction
    try {
      const aiData = await API.get('/api/predict');
      const aiEl = document.getElementById('ai-prediction-result');
      if (aiEl) {
        if (aiData.prediction) {
          aiEl.innerHTML = `
            <h2 style="font-size:2.8rem; font-weight:800; color:var(--clr-accent)">${aiData.prediction}%</h2>
            <p style="color:var(--clr-text); font-weight:600; margin-top:8px">Predicted Final Semester Score</p>
            <p style="font-size:0.8rem; color:var(--clr-muted); margin-top:4px">Model: Random Forest Regressor</p>
          `;
        } else {
          aiEl.innerHTML = `<p style="color:var(--clr-muted)">${aiData.message || 'No data for prediction'}</p>`;
        }
      }
    } catch (e) {
      console.error('AI Prediction error:', e);
    }

    renderRadarChart(pcts);
  } catch (err) {
    console.error('Analysis error:', err);
    showToast('Failed to load analysis', 'error');
  }
}

let radarInst = null;
function renderRadarChart(marks) {
  const ctx = document.getElementById('radarChart');
  if (!ctx) return;
  if (radarInst) radarInst.destroy();
  radarInst = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: marks.map(m => m.subject),
      datasets: [{
        label: 'Score %',
        data: marks.map(m => m.pct),
        backgroundColor: 'rgba(167,139,250,.12)',
        borderColor: '#A78BFA',
        pointBackgroundColor: '#A78BFA',
        borderWidth: 2,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      scales: { r: { beginAtZero: true, max: 100, grid: { color: 'rgba(167,139,250,.1)' }, ticks: { color: 'rgba(241,240,255,.4)', backdropColor: 'transparent' }, pointLabels: { color: 'rgba(241,240,255,.7)' } } },
      plugins: { legend: { display: false } }
    }
  });
}

// ── Recommendations ───────────────────────────────────────────────────────
async function loadRecommendations() {
  try {
    const marks = await API.get('/api/marks');
    const pcts  = marks.map(m => ({ ...m, pct: Math.round((m.marks / m.max_marks) * 100) }));
    const avg   = calculateAverage(pcts.map(m => m.pct));
    const recs  = [];

    // AI Prediction for recommendations
    try {
      const aiData = await API.get('/api/predict');
      if (aiData.prediction) {
        recs.push({ 
          type: 'success', 
          title: `🤖 AI Projection: ${aiData.prediction}%`, 
          text: `Our AI model predicts your final score will be around ${aiData.prediction}%. ${aiData.prediction > avg ? 'You are trending upwards!' : 'Keep pushing to exceed this projection.'}` 
        });
      }
    } catch (e) { console.error(e); }

    pcts.forEach(m => {
      if (m.pct < 40) recs.push({ type: 'danger', title: `⚠️ Critical: ${m.subject} — ${m.pct}%`, text: `Your marks in ${m.subject} are critically low. Consider getting a tutor, attending extra classes, and practising daily.` });
      else if (m.pct < 60) recs.push({ type: 'warning', title: `📋 Needs Work: ${m.subject} — ${m.pct}%`, text: `Focus more on ${m.subject}. Revise core concepts, solve past papers, and ask doubts promptly.` });
      else if (m.pct >= 90) recs.push({ type: 'success', title: `🌟 Excellent: ${m.subject} — ${m.pct}%`, text: `Outstanding in ${m.subject}! Keep it up and consider mentoring classmates.` });
    });

    if (avg >= 85)      recs.push({ type: 'success', title: '🏆 Overall: Exceptional!', text: `Your average of ${avg}% is impressive. Aim for scholarships or competitive exams.` });
    else if (avg >= 60) recs.push({ type: 'warning', title: '📈 Overall: Room to Grow', text: `Average of ${avg}%. Create a study timetable and target your weak areas.` });
    else                recs.push({ type: 'danger',  title: '🚨 Overall: Action Needed', text: `Average is only ${avg}%. Seek teacher support, join study groups, and dedicate more hours.` });

    if (!recs.length) recs.push({ type: 'success', title: '👍 All Good!', text: 'Your performance is solid. Keep your current pace!' });

    const container = document.getElementById('recommendations-list');
    if (container) {
      container.innerHTML = recs.map(r => `
        <div class="rec-card ${r.type}">
          <h4>${r.title}</h4>
          <p>${r.text}</p>
        </div>`).join('');
    }
  } catch (err) {
    console.error('Recommendations error:', err);
    showToast('Failed to load recommendations', 'error');
  }
}

// ── Search ────────────────────────────────────────────────────────────────
async function searchStudents() {
  const q = document.getElementById('search-input')?.value.trim();
  if (!q) return;
  try {
    const results = await API.get(`/api/search?q=${encodeURIComponent(q)}`);
    const list = document.getElementById('search-results');
    if (!list) return;
    list.innerHTML = results.length
      ? `<table class="data-table"><thead><tr><th>Name</th><th>Roll</th><th>Dept</th><th>Sem</th></tr></thead><tbody>
          ${results.map(s => `<tr><td>${s.name}</td><td>${s.roll_number}</td><td>${s.department}</td><td>${s.semester}</td></tr>`).join('')}
         </tbody></table>`
      : '<p style="padding:16px;color:var(--clr-muted)">No students found.</p>';
    list.style.display = 'block';
  } catch (err) { showToast('Search failed', 'error'); }
}

// ── Download report ────────────────────────────────────────────────────────
async function downloadReport() {
  try {
    const [student, marks] = await Promise.all([API.get('/api/student'), API.get('/api/marks')]);
    const pcts = marks.map(m => Math.round((m.marks / m.max_marks) * 100));
    const avg  = calculateAverage(pcts);
    const status = getPerformanceStatus(avg);
    let r = `===========================================\n   STUDENT PERFORMANCE REPORT\n===========================================\n\n`;
    r += `Name       : ${student.name}\nRoll No.   : ${student.roll_number}\nDepartment : ${student.department}\nSemester   : ${student.semester}\nEmail      : ${student.email}\n\n`;
    r += `-------------------------------------------\nSUBJECT MARKS\n-------------------------------------------\n`;
    marks.forEach(m => { r += `${m.subject.padEnd(20)} : ${m.marks} / ${m.max_marks}\n`; });
    r += `\nAverage    : ${avg}%\nStatus     : ${status.text}\n\nGenerated on: ${new Date().toLocaleString()}\n`;
    const blob = new Blob([r], { type: 'text/plain' });
    const a = Object.assign(document.createElement('a'), { href: URL.createObjectURL(blob), download: `report_${student.roll_number}.txt` });
    a.click(); URL.revokeObjectURL(a.href);
    showToast('Report downloaded!', 'success');
  } catch (err) { showToast('Download failed', 'error'); }
}

// ── Marks modal ────────────────────────────────────────────────────────────
function openMarksModal()  { document.getElementById('marksModal')?.classList.add('show'); }
function closeMarksModal() { document.getElementById('marksModal')?.classList.remove('show'); }

async function submitMarksForm(event) {
  event.preventDefault();
  const subject     = document.getElementById('subject_input').value.trim();
  const marks       = document.getElementById('marks_input').value;
  const max_marks   = document.getElementById('max_marks_input').value;
  const study_hours = document.getElementById('study_hours_input').value;
  const attendance  = document.getElementById('subject_attendance_input').value;
  if (!subject || !marks || !max_marks) return;
  try {
    await API.post('/api/marks', { 
      subject, 
      marks: parseInt(marks), 
      max_marks: parseInt(max_marks),
      study_hours: parseInt(study_hours || 0),
      attendance: parseInt(attendance || 100)
    });
    closeMarksModal();
    document.getElementById('marksForm').reset();
    showToast('Marks saved!', 'success');
    window.location.pathname.includes('analysis') ? await loadAnalysis() : await loadDashboard();
  } catch (err) { showToast('Failed to save marks', 'error'); }
}

async function editMark(subject, marksArray) {
  const m = marksArray.find(item => item.subject === subject);
  if (!m) return;
  
  document.getElementById('subject_input').value = m.subject;
  document.getElementById('marks_input').value = m.marks;
  document.getElementById('max_marks_input').value = m.max_marks;
  document.getElementById('study_hours_input').value = m.study_hours || 0;
  document.getElementById('subject_attendance_input').value = m.attendance || 0;
  
  openMarksModal();
}

async function deleteMark(subject) {
  if (!subject) return;
  console.log(`[DELETE] UI Request for: ${subject}`);
  
  if (!window.confirm(`Are you sure you want to delete ${subject}?`)) {
    return;
  }
  
  try {
    const res = await API.del(`/api/marks/${encodeURIComponent(subject)}`);
    console.log('[DELETE] Response:', res);
    showToast(`${subject} deleted`, 'success');
    window.location.pathname.includes('analysis') ? await loadAnalysis() : await loadDashboard();
  } catch (err) { 
    console.error('[DELETE] Error:', err);
    showToast(err.message || 'Failed to delete', 'error'); 
  }
}

// ── Batch CSV Upload ───────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const fileInput = document.getElementById('batch-csv-input');
  if (!fileInput) return;

  fileInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      showToast('Uploading batch data...', 'info');
      const res = await fetch('/api/marks/batch', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      
      if (!res.ok) throw new Error(data.error || 'Batch upload failed');
      
      showToast(data.message, 'success');
      loadDashboard();
      fileInput.value = ''; // Reset
    } catch (err) {
      console.error('Batch upload error:', err);
      showToast(err.message, 'error');
      fileInput.value = '';
    }
  });
});


