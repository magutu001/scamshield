/* ════════════════════════════════════════════════
   ScamShield — Frontend App Logic
   ════════════════════════════════════════════════ */

const API = '';
let currentUser = null;
let userToken = null;

// ── Init ──────────────────────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {
  // Restore session from localStorage
  const saved = localStorage.getItem('ss_token');
  const savedUser = localStorage.getItem('ss_user');
  if (saved && savedUser) {
    userToken = saved;
    currentUser = JSON.parse(savedUser);
    updateNavUser();
  }
  loadStats();
});

// ── Page Navigation ───────────────────────────────────────────────────────────
function showPage(name) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
  document.getElementById(`page-${name}`).classList.add('active');
  document.querySelectorAll('.nav-tab').forEach(t => {
    if (t.textContent.toLowerCase().trim() === name) t.classList.add('active');
  });
  if (name === 'history') loadHistory();
}

// ── Auth Modal ────────────────────────────────────────────────────────────────
function openAuth(form) {
  document.getElementById('auth-modal').classList.remove('hidden');
  switchForm(form);
}
function closeAuth() {
  document.getElementById('auth-modal').classList.add('hidden');
  // Reset forgot password form state
  try {
    document.getElementById('forgot-fields').classList.remove('hidden');
    document.getElementById('forgot-verify-fields').classList.add('hidden');
    document.getElementById('forgot-error').classList.add('hidden');
  } catch {}
}
function closeAuthIfOutside(e) {
  if (e.target.id === 'auth-modal') closeAuth();
}
function switchForm(form) {
  document.getElementById('form-login').classList.toggle('hidden', form !== 'login');
  document.getElementById('form-register').classList.toggle('hidden', form !== 'register');
  document.getElementById('form-forgot').classList.toggle('hidden', form !== 'forgot');
  document.getElementById('login-error').classList.add('hidden');
  document.getElementById('register-error').classList.add('hidden');
}

async function submitLogin() {
  const email    = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value;
  const errEl    = document.getElementById('login-error');
  errEl.classList.add('hidden');
  if (!email || !password) { showErr(errEl, 'Please fill in all fields.'); return; }
  try {
    const res  = await fetch(`${API}/api/login`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();
    if (!res.ok) { showErr(errEl, data.detail || 'Invalid email or password.'); return; }
    saveSession(data);
    closeAuth();
    showToast(`Welcome back, ${data.name}! 👋`, 'success');
  } catch { showErr(errEl, 'Server error. Is the backend running?'); }
}

async function submitRegister() {
  const name     = document.getElementById('register-name').value.trim();
  const email    = document.getElementById('register-email').value.trim();
  const password = document.getElementById('register-password').value;
  const errEl    = document.getElementById('register-error');
  errEl.classList.add('hidden');
  if (!name || !email || !password) { showErr(errEl, 'Please fill in all fields.'); return; }
  if (password.length < 6) { showErr(errEl, 'Password must be at least 6 characters.'); return; }
  const btn = document.querySelector('#register-fields .modal-submit-btn');
  btn.textContent = 'Sending…'; btn.disabled = true;
  try {
    const res  = await fetch(`${API}/api/register/send-code`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password })
    });
    const data = await res.json();
    btn.textContent = 'Send Verification Code'; btn.disabled = false;
    if (!res.ok) { showErr(errEl, data.detail || 'Registration failed.'); return; }
    // Switch to verify step
    document.getElementById('register-fields').classList.add('hidden');
    document.getElementById('verify-fields').classList.remove('hidden');
    document.getElementById('register-switch-link').classList.add('hidden');
    document.getElementById('verify-sub').textContent = `Enter the 6-digit code sent to ${email}`;
    document.getElementById('verify-code').value = '';
    document.getElementById('verify-code').focus();
    // Dev fallback: if email failed, show code
    if (data.dev_code) {
      showErr(errEl, `Email not configured — dev code: ${data.dev_code}`);
      errEl.classList.remove('hidden');
    }
  } catch {
    btn.textContent = 'Send Verification Code'; btn.disabled = false;
    showErr(errEl, 'Server error. Is the backend running?');
  }
}

async function submitVerify() {
  const email  = document.getElementById('register-email').value.trim();
  const code   = document.getElementById('verify-code').value.trim();
  const errEl  = document.getElementById('register-error');
  errEl.classList.add('hidden');
  if (!code || code.length !== 6) { showErr(errEl, 'Please enter the 6-digit code.'); return; }
  const btn = document.querySelector('#verify-fields .modal-submit-btn');
  btn.textContent = 'Verifying…'; btn.disabled = true;
  try {
    const res  = await fetch(`${API}/api/register/verify`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, code })
    });
    const data = await res.json();
    btn.textContent = 'Verify & Create Account'; btn.disabled = false;
    if (!res.ok) { showErr(errEl, data.detail || 'Verification failed.'); return; }
    saveSession(data);
    closeAuth();
    showToast(`Account created! Welcome, ${data.name} 🎉`, 'success');
  } catch {
    btn.textContent = 'Verify & Create Account'; btn.disabled = false;
    showErr(errEl, 'Server error. Is the backend running?');
  }
}

function backToRegister() {
  document.getElementById('register-fields').classList.remove('hidden');
  document.getElementById('verify-fields').classList.add('hidden');
  document.getElementById('register-switch-link').classList.remove('hidden');
  document.getElementById('register-error').classList.add('hidden');
}

async function submitForgot() {
  const email = document.getElementById('forgot-email').value.trim();
  const errEl = document.getElementById('forgot-error');
  errEl.classList.add('hidden');
  if (!email) { showErr(errEl, 'Please enter your email address.'); return; }
  const btn = document.querySelector('#forgot-fields .modal-submit-btn');
  btn.textContent = 'Sending…'; btn.disabled = true;
  try {
    const res  = await fetch(`${API}/api/password-reset/send-code`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password: '' })
    });
    const data = await res.json();
    btn.textContent = 'Send Reset Code'; btn.disabled = false;
    if (!res.ok) { showErr(errEl, data.detail || 'Failed to send code.'); return; }
    document.getElementById('forgot-fields').classList.add('hidden');
    document.getElementById('forgot-verify-fields').classList.remove('hidden');
    document.getElementById('forgot-verify-sub').textContent = `Enter the code sent to ${email}`;
    document.getElementById('forgot-code').value = '';
    document.getElementById('forgot-new-password').value = '';
    document.getElementById('forgot-code').focus();
    if (data.dev_code) {
      showErr(errEl, `Email not configured — dev code: ${data.dev_code}`);
      errEl.classList.remove('hidden');
    }
  } catch {
    btn.textContent = 'Send Reset Code'; btn.disabled = false;
    showErr(errEl, 'Server error. Is the backend running?');
  }
}

async function submitResetPassword() {
  const email       = document.getElementById('forgot-email').value.trim();
  const code        = document.getElementById('forgot-code').value.trim();
  const newPassword = document.getElementById('forgot-new-password').value;
  const errEl       = document.getElementById('forgot-error');
  errEl.classList.add('hidden');
  if (!code || code.length !== 6) { showErr(errEl, 'Please enter the 6-digit code.'); return; }
  if (!newPassword || newPassword.length < 6) { showErr(errEl, 'Password must be at least 6 characters.'); return; }
  const btn = document.querySelector('#forgot-verify-fields .modal-submit-btn');
  btn.textContent = 'Resetting…'; btn.disabled = true;
  try {
    const res  = await fetch(`${API}/api/password-reset/verify`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, code, new_password: newPassword })
    });
    const data = await res.json();
    btn.textContent = 'Reset Password'; btn.disabled = false;
    if (!res.ok) { showErr(errEl, data.detail || 'Reset failed.'); return; }
    closeAuth();
    showToast('Password reset! Please log in with your new password.', 'success');
    setTimeout(() => openAuth('login'), 800);
  } catch {
    btn.textContent = 'Reset Password'; btn.disabled = false;
    showErr(errEl, 'Server error. Is the backend running?');
  }
}

function backToForgot() {
  document.getElementById('forgot-fields').classList.remove('hidden');
  document.getElementById('forgot-verify-fields').classList.add('hidden');
  document.getElementById('forgot-error').classList.add('hidden');
}

function saveSession(data) {
  userToken   = data.token;
  currentUser = { name: data.name, email: data.email };
  localStorage.setItem('ss_token', userToken);
  localStorage.setItem('ss_user', JSON.stringify(currentUser));
  updateNavUser();
}

async function logout() {
  if (userToken) {
    await fetch(`${API}/api/logout`, { method: 'POST', headers: { 'x-user-token': userToken } });
  }
  userToken = null; currentUser = null;
  localStorage.removeItem('ss_token');
  localStorage.removeItem('ss_user');
  updateNavUser();
  showToast('Logged out successfully.', 'success');
}

function forceLogout() {
  // Called when server returns 401 — account was deleted or session expired
  userToken = null; currentUser = null;
  localStorage.removeItem('ss_token');
  localStorage.removeItem('ss_user');
  updateNavUser();
  showLoading(false);
  showToast('Your session has expired. Please log in again.', 'error');
}

function updateNavUser() {
  const guestEl = document.getElementById('nav-guest');
  const userEl  = document.getElementById('nav-user');
  if (currentUser) {
    guestEl.classList.add('hidden');
    userEl.classList.remove('hidden');
    document.getElementById('user-name-display').textContent = currentUser.name;
    document.getElementById('user-avatar').textContent = currentUser.name.charAt(0).toUpperCase();
    document.getElementById('history-subtitle').textContent = 'Your personal scan history';
  } else {
    guestEl.classList.remove('hidden');
    userEl.classList.add('hidden');
    document.getElementById('history-subtitle').textContent = 'All previously analyzed job advertisements';
  }
}

function showErr(el, msg) {
  el.textContent = msg;
  el.classList.remove('hidden');
}

// ── Samples ───────────────────────────────────────────────────────────────────
const SAMPLES = {
  scam: {
    title: 'URGENT: Data Entry Clerks Needed – Work From Home',
    desc: `URGENT HIRING!! We are looking for 50 data entry clerks to work from home immediately.\n\nEARN KSh 5,000 - KSh 15,000 PER DAY working only 2-3 hours!\nNo experience required. No qualifications needed. Anyone can do this job.\n\nRequirements:\n- Must have a smartphone or laptop\n- Send KSh 500 registration fee via Mpesa to 0712345678 to get started\n- Send your National ID and bank details to activate your account\n\nContact us on WhatsApp ONLY: +254712345678\nLimited slots available – Apply NOW!\n\nThis is a 100% legitimate international company. Guaranteed income every week.`,
    domain: 'http://easyjobskenya-hiring.blogspot.com'
  },
  legit: {
    title: 'Software Developer – Full Stack (React/Node)',
    desc: `Safaricom PLC is seeking a talented Full Stack Developer to join our Digital Innovation team in Nairobi.\n\nRole: Full Stack Developer\nLocation: Westlands, Nairobi (Hybrid)\nSalary: KSh 180,000 – 250,000 per month\n\nMinimum Requirements:\n- Bachelor's degree in Computer Science or related field\n- 3+ years experience with React.js and Node.js\n- Experience with RESTful APIs and cloud platforms\n\nHow to Apply:\nSubmit your CV through our official careers portal at careers.safaricom.co.ke.\nNo application fee is required. Only shortlisted candidates will be contacted.\n\nApplication deadline: 30th March 2025`,
    domain: 'https://careers.safaricom.co.ke'
  },
  mixed: {
    title: 'Sales Representatives Needed – Nairobi',
    desc: `A growing FMCG company is looking for Sales Representatives across Nairobi.\n\nPositions Available: 20\nSalary: KSh 25,000 basic + commission\nStart: Immediate / Urgent\n\nQualifications:\n- Form 4 certificate minimum\n- Sales experience preferred but not required\n- Must be willing to travel within Nairobi\n\nHow to Apply:\nSend your CV to hiring2024@gmail.com or contact us via WhatsApp: 0798765432\nApply NOW – Limited positions available!`,
    domain: ''
  }
};

function loadSample(type) {
  const s = SAMPLES[type];
  document.getElementById('job-title').value = s.title;
  document.getElementById('job-desc').value  = s.desc;
  document.getElementById('job-domain').value = s.domain;
  document.getElementById('char-count').textContent = s.desc.length;
}

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('job-desc').addEventListener('input', function() {
    document.getElementById('char-count').textContent = this.value.length;
  });
});

// ── Analyze ───────────────────────────────────────────────────────────────────
async function analyzeJob() {
  const title  = document.getElementById('job-title').value.trim();
  const desc   = document.getElementById('job-desc').value.trim();
  const domain = document.getElementById('job-domain').value.trim();
  if (!desc) { showToast('Please paste a job advertisement text first.', 'error'); return; }

  showLoading(true);
  try {
    const headers = { 'Content-Type': 'application/json' };
    if (userToken) headers['x-user-token'] = userToken;
    const res  = await fetch(`${API}/api/analyze`, {
      method: 'POST', headers, body: JSON.stringify({ title, description: desc, domain })
    });
    if (res.status === 401) { forceLogout(); return; }
    const data = await res.json();
    renderResult(data);
    loadStats();
  } catch (err) {
    showToast('Analysis failed. Is the backend running?', 'error');
  } finally { showLoading(false); }
}

function renderResult(data) {
  document.getElementById('result-placeholder').classList.add('hidden');
  document.getElementById('result-card').classList.remove('hidden');
  const color = data.color;
  const banner = document.getElementById('verdict-banner');
  banner.className = `verdict-banner ${color}`;
  document.getElementById('verdict-emoji').textContent = data.emoji;
  const vt = document.getElementById('verdict-text');
  vt.textContent = data.verdict; vt.className = `verdict-text ${color}`;
  const vs = document.getElementById('verdict-score');
  vs.textContent = data.score; vs.className = `verdict-score ${color}`;
  document.getElementById('verdict-advice').textContent = data.advice;
  document.getElementById('score-bar-fill').style.width = `${Math.min(100,(data.score/100)*100)}%`;

  const allFlags = [...(data.text_flags||[]),...(data.domain_flags||[])];
  const fg = document.getElementById('flags-grid');
  fg.innerHTML = allFlags.length === 0
    ? '<span class="no-flags">No scam indicators detected in the text.</span>'
    : allFlags.map(f => `<div class="flag-chip ${(f.category==='domain'||f.category==='ssl')?'domain':''}">
        ${f.rule}<span class="flag-weight">+${f.weight}</span></div>`).join('');

  const di = data.domain_info;
  const ds = document.getElementById('domain-section');
  if (!di || di.domain_age === -1 && !di.ssl_valid && di.whois_info === 'Unavailable') {
    ds.innerHTML = `<h3 class="section-title">🌐 Domain Verification</h3><p class="no-flags">No domain provided for verification.</p>`;
  } else {
    const sslClass = di.ssl_valid ? 'good' : 'bad';
    const sslText  = di.ssl_valid ? '✓ Valid SSL Certificate' : '✗ No SSL Certificate';
    let ageClass = 'neutral', ageText = 'Unknown';
    if (di.domain_age >= 0) {
      ageText  = di.domain_age === 0 ? 'Less than 1 year old' : `${di.domain_age} year(s) old`;
      ageClass = di.domain_age === 0 ? 'bad' : di.domain_age < 2 ? 'neutral' : 'good';
    }
    document.getElementById('domain-checks').innerHTML = `
      <div class="domain-check-item"><span class="check-icon">🔒</span><span class="check-label">SSL Certificate</span><span class="check-value ${sslClass}">${sslText}</span></div>
      <div class="domain-check-item"><span class="check-icon">📅</span><span class="check-label">Domain Age</span><span class="check-value ${ageClass}">${ageText}</span></div>
      <div class="domain-check-item"><span class="check-icon">📋</span><span class="check-label">WHOIS Info</span><span class="check-value neutral" style="font-size:12px">${di.whois_info||'N/A'}</span></div>`;
  }
  if (window.innerWidth < 800) document.getElementById('result-card').scrollIntoView({behavior:'smooth',block:'start'});
}

// ── Stats ─────────────────────────────────────────────────────────────────────
async function loadStats() {
  try {
    const res  = await fetch(`${API}/api/stats`);
    const data = await res.json();
    document.getElementById('stat-total').textContent   = data.total;
    document.getElementById('stat-high').textContent    = data.high_risk;
    document.getElementById('stat-caution').textContent = data.caution;
    document.getElementById('stat-safe').textContent    = data.safe;
  } catch {}
}

// ── History ───────────────────────────────────────────────────────────────────
let historyData = [];

async function loadHistory() {
  try {
    const headers = {};
    if (userToken) headers['x-user-token'] = userToken;
    const res  = await fetch(`${API}/api/history`, { headers });
    if (res.status === 401) { forceLogout(); return; }
    historyData = await res.json();
    renderHistory(historyData);
  } catch { showToast('Failed to load history.', 'error'); }
}

function renderHistory(rows) {
  const tbody = document.getElementById('history-tbody');
  const empty = document.getElementById('history-empty');
  if (!rows.length) { tbody.innerHTML = ''; empty.classList.remove('hidden'); return; }
  empty.classList.add('hidden');
  tbody.innerHTML = rows.map(r => {
    const color = verdictColor(r.verdict);
    const date  = r.analyzed_date ? r.analyzed_date.slice(0,16).replace('T',' ') : '–';
    const scoreColor = color==='red'?'var(--danger)':color==='orange'?'var(--warning)':'var(--safe)';
    return `<tr>
      <td style="color:var(--text-3)">#${r.advert_id}</td>
      <td style="color:var(--text-1);font-weight:500;max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${escHtml(r.title||'Untitled')}</td>
      <td style="font-size:12px;max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${escHtml(r.domain||'—')}</td>
      <td><strong style="color:${scoreColor}">${r.scam_score}</strong></td>
      <td><span class="verdict-pill ${color}">${r.verdict}</span></td>
      <td style="font-size:12px">${date}</td>
    </tr>`;
  }).join('');
}

function filterHistory() {
  const q = document.getElementById('history-search').value.toLowerCase();
  renderHistory(historyData.filter(r =>
    (r.title||'').toLowerCase().includes(q) ||
    (r.verdict||'').toLowerCase().includes(q) ||
    (r.domain||'').toLowerCase().includes(q)
  ));
}

function verdictColor(v) {
  if (!v) return 'neutral';
  if (v.includes('HIGH')) return 'red';
  if (v.includes('CAUTION')) return 'orange';
  return 'green';
}

// ── Utilities ─────────────────────────────────────────────────────────────────
function showLoading(show) {
  document.getElementById('loading-overlay').classList.toggle('hidden', !show);
  document.getElementById('analyze-btn').disabled = show;
}

function showToast(msg, type='success') {
  const t = document.createElement('div');
  t.className = `toast ${type}`; t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 3500);
}

function escHtml(str) {
  const d = document.createElement('div');
  d.appendChild(document.createTextNode(str));
  return d.innerHTML;
}
