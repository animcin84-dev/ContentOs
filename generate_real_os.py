import json

html_content = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Consent OS — Реально Работающая Система</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
<script src="https://accounts.google.com/gsi/client" async defer></script>
<style>
:root {
  --bg-primary: #080c14; --bg-secondary: #0d1321; --bg-card: rgba(15, 22, 40, 0.85); --bg-glass: rgba(255,255,255,0.04);
  --border: rgba(99,130,255,0.15); --border-bright: rgba(99,130,255,0.35);
  --accent-blue: #6382ff; --accent-purple: #9b5de5; --accent-green: #00e09e;
  --text-primary: #e8edf7; --text-secondary: #8892b0; --text-muted: #495670;
  --risk-red: #ff4d6d; --risk-yellow: #f7c948; --risk-green: #00e09e;
  --transition: 0.25s cubic-bezier(0.4,0,0.2,1);
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Inter', sans-serif; background: var(--bg-primary); color: var(--text-primary); min-height: 100vh; overflow-x: hidden; line-height: 1.6; }
body::before { content: ''; position: fixed; inset: 0; background: radial-gradient(ellipse 80% 50% at 10% 20%, rgba(99,130,255,0.07) 0%, transparent 60%), radial-gradient(ellipse 60% 40% at 90% 80%, rgba(155,93,229,0.06) 0%, transparent 60%); z-index: 0; pointer-events: none; }
.wrapper { position: relative; z-index: 1; display: flex; flex-direction: column; min-height: 100vh; }

button { cursor: pointer; border: none; font-family: inherit; transition: var(--transition); }
input { width: 100%; padding: 12px; background: var(--bg-primary); border: 1px solid var(--border); border-radius: 8px; color: var(--text-primary); font-family: inherit; margin-bottom: 16px; outline: none; }
input:focus { border-color: var(--accent-blue); }

.view { display: none; animation: fadeIn 0.3s; }
.view.active { display: block; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

/* AUTH & SETUP CONTAINERS */
.auth-container { display: flex; align-items: center; justify-content: center; min-height: 100vh; }
.auth-box { background: var(--bg-card); border: 1px solid var(--border); padding: 40px; border-radius: 20px; width: 100%; max-width: 460px; text-align: center; box-shadow: 0 10px 40px rgba(0,0,0,0.5); }
.auth-btn { width: 100%; padding: 14px; background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple)); color: white; border-radius: 8px; font-weight: 700; font-size: 16px; margin-top: 10px; }
.auth-btn:hover { filter: brightness(1.1); }
.auth-toggle { font-size: 13px; color: var(--text-secondary); margin-top: 16px; cursor: pointer; }
.auth-toggle:hover { color: var(--accent-blue); }

/* NAVBAR */
.navbar { height: 64px; background: rgba(8,12,20,0.85); backdrop-filter: blur(24px); border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; padding: 0 32px; z-index: 100; position: fixed; top: 0; left: 0; right: 0; }
.nav-logo { font-weight: 700; font-size: 18px; display: flex; align-items: center; gap: 8px; }
.nav-logo span { color: var(--accent-blue); }
.nav-tabs { display: flex; gap: 4px; background: var(--bg-glass); border-radius: 10px; padding: 4px; border: 1px solid var(--border); }
.nav-tab { padding: 6px 16px; border-radius: 8px; font-size: 13px; font-weight: 500; color: var(--text-secondary); background: transparent; }
.nav-tab.active { background: rgba(99,130,255,0.15); color: var(--accent-blue); border: 1px solid var(--border-bright); }
.logout-btn { background: var(--bg-glass); color: var(--text-primary); font-size: 13px; padding: 6px 14px; border: 1px solid var(--border); border-radius: 8px; }

/* SCAN PROGRESS OVERLAY */
.scanner-overlay { position: fixed; inset: 0; background: rgba(8,12,20,0.98); backdrop-filter: blur(10px); z-index: 999; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.scanner-circle { width: 120px; height: 120px; border: 3px solid transparent; border-top-color: var(--accent-blue); border-bottom-color: var(--accent-purple); border-radius: 50%; animation: scanSpin 1.5s linear infinite; display: flex; align-items: center; justify-content: center; margin-bottom: 30px; }
@keyframes scanSpin { to { transform: rotate(360deg); } }
.scanner-inner { width: 90px; height: 90px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 32px; }
.scan-text { font-family: 'JetBrains Mono', monospace; color: var(--accent-cyan); margin-bottom: 20px; font-size: 14px; text-align: center; max-width: 600px;}

/* DASHBOARD LAYOUT */
.main { padding: 88px 32px 40px; max-width: 1400px; margin: 0 auto; flex: 1; width: 100%; }
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
.stat-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 16px; padding: 20px; text-align: center; }
.stat-val { font-size: 32px; font-weight: 800; margin: 8px 0; }
.stat-lbl { font-size: 12px; color: var(--text-muted); text-transform: uppercase; font-weight: 600; }

.split-layout { display: grid; grid-template-columns: 1fr 400px; gap: 24px; }
.panel { background: var(--bg-card); border: 1px solid var(--border); border-radius: 16px; padding: 20px; display: flex; flex-direction: column; }
.panel-title { font-size: 16px; font-weight: 700; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; }

/* GRAPH */
.graph-container { width: 100%; height: 500px; }
#graph-svg { width: 100%; height: 100%; }

/* SERVICE LIST */
.service-list { display: flex; flex-direction: column; gap: 12px; max-height: 500px; overflow-y: auto; padding-right: 8px; }
.service-item { display: flex; align-items: center; gap: 12px; padding: 12px; border: 1px solid var(--border); border-radius: 12px; background: var(--bg-glass); cursor: pointer; transition: 0.2s; }
.service-item:hover { border-color: var(--border-bright); transform: translateX(2px); }
.service-item.disabled { opacity: 0.4; filter: grayscale(1); }
.svc-info { flex: 1; min-width: 0; }
.svc-name { font-weight: 600; font-size: 13px; text-overflow: ellipsis; overflow: hidden; white-space: nowrap; }
.svc-domain { font-size: 11px; color: var(--text-muted); }
.svc-risk { font-weight: 800; font-size: 14px; }

/* DETAIL PANEL */
.detail-overlay { position: fixed; right: -500px; top: 64px; bottom: 0; width: 480px; background: var(--bg-secondary); border-left: 1px solid var(--border); transition: right 0.3s; z-index: 200; display: flex; flex-direction: column; }
.detail-overlay.open { right: 0; }
.detail-header { padding: 24px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: flex-start; }
.detail-body { padding: 24px; flex: 1; overflow-y: auto; }
.data-tag { display: inline-flex; padding: 4px 10px; border-radius: 20px; font-size: 11px; margin: 4px; border: 1px solid var(--border); background: var(--bg-glass); }
.ai-box { background: rgba(99,130,255,0.05); border: 1px solid rgba(99,130,255,0.2); padding: 16px; border-radius: 12px; margin-bottom: 16px; font-size: 13px; line-height: 1.5; }
.ai-box h4 { font-size: 12px; color: var(--accent-blue); text-transform: uppercase; margin-bottom: 8px; display: flex; justify-content: space-between; }
.btn-revoke { width: 100%; padding: 14px; background: rgba(255,77,109,0.1); color: var(--risk-red); border: 1px solid rgba(255,77,109,0.3); border-radius: 8px; font-weight: 600; margin-top: 16px; cursor: pointer; }
.btn-revoke:hover { background: rgba(255,77,109,0.2); }
.btn-secondary { width: 100%; padding: 12px; background: var(--bg-glass); border: 1px solid var(--border); color: #fff; border-radius: 8px; font-size: 13px; cursor: pointer; margin-bottom: 16px; }

/* HISTORY TIMELINE */
.history-timeline { display: flex; flex-direction: column; gap: 12px; }
.history-item { background: var(--bg-glass); padding: 16px; border: 1px solid var(--border); border-radius: 12px; display: flex; gap: 16px; align-items: center; }
.h-date { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--text-muted); width: 140px; }

.spin-s { width: 16px; height: 16px; border: 2px solid transparent; border-top-color: var(--accent-cyan); border-radius: 50%; animation: scanSpin 0.8s linear infinite; display: inline-block; }
</style>
</head>
<body>
<div class="wrapper">

  <!-- 1. AUTH SCREEN -->
  <div id="auth-view" class="view active auth-container">
    <div class="auth-box">
      <div style="font-size: 48px; margin-bottom: 16px">🛡️</div>
      <h2 style="margin-bottom: 24px">Consent OS</h2>
      
      <div id="login-form">
        <input type="email" id="auth-email-in" placeholder="Email" value="user@mail.kz">
        <input type="password" id="auth-pass-in" placeholder="Пароль" value="123456">
        <button class="auth-btn" onclick="login()">Войти</button>
        <div class="auth-toggle" onclick="toggleAuth()">Нет аккаунта? Создать</div>
      </div>
      
      <div id="signup-form" style="display:none">
        <input type="text" id="auth-name-up" placeholder="Имя">
        <input type="email" id="auth-email-up" placeholder="Email">
        <input type="password" id="auth-pass-up" placeholder="Пароль">
        <button class="auth-btn" onclick="signup()">Создать аккаунт</button>
        <div class="auth-toggle" onclick="toggleAuth()">Уже есть аккаунт? Войти</div>
      </div>
    </div>
  </div>

  <!-- 2. API SETUP SCREEN -->
  <div id="setup-view" class="view auth-container" style="display: none;">
    <div class="auth-box" style="max-width: 500px;">
      <h2 style="margin-bottom: 16px">Инициализация AI Аудитора</h2>
      <p style="font-size: 13px; color: var(--text-secondary); margin-bottom: 24px; text-align: left;">
        Система использует реальный Gmail API для глубокого сканирования почты (извлечение регистраций) и Anthropic API для юридического анализа.
      </p>
      
      <div style="text-align: left; margin-bottom: 6px; font-size: 12px; color: var(--text-muted); font-weight:600">Google OAuth Client ID (Gmail Readonly)</div>
      <input type="text" id="setup-google" placeholder="Ваш xxx-xxx.apps.googleusercontent.com">
      
      <div style="text-align: left; margin-bottom: 6px; font-size: 12px; color: var(--text-muted); font-weight:600">Anthropic API Key (Claude-3.5-Sonnet)</div>
      <input type="password" id="setup-anthropic" placeholder="sk-ant-...">
      
      <button class="auth-btn" onclick="saveSetupKeys()">Подключить системы сканирования</button>
    </div>
  </div>

  <!-- 3. MAIN DASHBOARD -->
  <div id="app-view" class="view" style="display: none; height: 100%">
    <nav class="navbar">
      <div class="nav-logo">🛡️ <span>Consent</span> OS</div>
      <div class="nav-tabs">
        <button class="nav-tab active" onclick="switchTab('dashboard')">Глобальный Радар</button>
        <button class="nav-tab" onclick="switchTab('history')">Журнал Действий</button>
      </div>
      <div class="nav-user">
        <span id="user-display" style="font-weight:600; font-size:13px; margin:0 12px;"></span>
        <button class="logout-btn" onclick="startGmailScanOauth()">🔄 Запустить Поиск в Gmail</button>
        <button class="logout-btn" style="border-color:var(--border-bright)" onclick="logout()">Выйти</button>
      </div>
    </nav>

    <main class="main">
      <div id="tab-dashboard" class="tab-content active">
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-lbl">Найдено сервисов</div>
            <div class="stat-val" id="st-total" style="color:var(--accent-blue)">0</div>
          </div>
          <div class="stat-card">
            <div class="stat-lbl">Опасные (Красная зона)</div>
            <div class="stat-val" id="st-red" style="color:var(--risk-red)">0</div>
          </div>
          <div class="stat-card">
            <div class="stat-lbl">Неизвестные трекеры</div>
            <div class="stat-val" id="st-third">0</div>
          </div>
          <div class="stat-card">
            <div class="stat-lbl">Отозвано доступов</div>
            <div class="stat-val" id="st-revoked" style="color:var(--accent-green)">0</div>
          </div>
        </div>

        <div class="split-layout">
          <div class="panel">
            <div class="panel-title">Карта Потоков Данных (Live)</div>
            <div class="graph-container">
              <svg id="graph-svg"></svg>
            </div>
          </div>
          
          <div class="panel">
            <div class="panel-title">Обнаруженные Регистрации</div>
            <div class="service-list" id="service-list"></div>
          </div>
        </div>
      </div>

      <div id="tab-history" class="tab-content" style="display: none;">
        <div class="panel">
          <div class="panel-title">Системный Журнал</div>
          <div class="history-timeline" id="history-list"></div>
        </div>
      </div>
    </main>
  </div>

</div>

<!-- SCANNER OVERLAY -->
<div id="scanner-overlay" class="scanner-overlay" style="display: none;">
  <div class="scanner-circle">
    <div class="scanner-inner">🔎</div>
  </div>
  <div class="scan-text" id="scan-text">Подключение к Gmail API...</div>
</div>

<!-- DETAIL SIDEBAR -->
<div class="detail-overlay" id="detail-overlay">
  <div class="detail-header">
    <div>
      <h2 id="det-name" style="font-size:18px">Название</h2>
      <div id="det-domain" style="color:var(--text-muted); font-size:12px; margin-top:2px">도мен</div>
    </div>
    <button onclick="document.getElementById('detail-overlay').classList.remove('open')" style="background:transparent; color:#fff; font-size:20px; border:none; cursor:pointer">✕</button>
  </div>
  <div class="detail-body">
    <div id="det-tags" style="margin-bottom:16px"></div>
    
    <div class="ai-box">
      <h4 style="display:flex; justify-content:space-between">
        <span>🤖 AI Риск-Анализ</span>
        <span id="det-score" style="font-size:16px; font-weight:800"></span>
      </h4>
      <div id="det-reasons" style="color:var(--text-secondary); margin-bottom:12px"></div>
      <div style="font-size:12px"><b>Аномалии:</b> <span id="det-anomaly" style="color:var(--risk-red)"></span></div>
    </div>
    
    <div class="ai-box" id="policy-box" style="display:none">
      <h4>📜 Глубокий анализ политики (Privacy Policy)</h4>
      <div id="policy-content" style="color:var(--text-primary)"></div>
    </div>
    
    <button id="btn-analyze-policy" class="btn-secondary" onclick="analyzePrivacyPolicy()">Запустить парсер Privacy Policy сайта</button>

    <div style="font-size:12px; color:var(--text-muted); margin-bottom: 16px">
      * Отзыв доступа сгенерирует Data Deletion Request (GDPR) и отправит письмо privacy-офицеру сервиса.
    </div>

    <button id="det-revoke" class="btn-revoke" onclick="revokeAccess()">Отозвать доступ (GDPR Request)</button>
  </div>
</div>

<script>
// ==========================================
// 1. STORAGE & CRYPTO
// ==========================================
window.storage = {
  set: async (key, val) => localStorage.setItem(key, JSON.stringify(val)),
  get: async (key) => JSON.parse(localStorage.getItem(key) || 'null'),
  list: async (prefix) => {
    let res = [];
    for(let i=0; i<localStorage.length; i++) {
      let k = localStorage.key(i);
      if(k.startsWith(prefix)) res.push(JSON.parse(localStorage.getItem(k)));
    }
    return res;
  },
  remove: async (key) => localStorage.removeItem(key)
};

async function hashStr(msg) {
  const data = new TextEncoder().encode(msg);
  const hash = await crypto.subtle.digest('SHA-256', data);
  return Array.from(new Uint8Array(hash)).map(b => b.toString(16).padStart(2, '0')).join('');
}

// ==========================================
// 2. STATE & INIT
// ==========================================
let currentUser = null;
let servicesMap = {}; // domain -> data
let currentDetailDomain = null;
let googleTokenClient = null;

async function init() {
  const sess = await storage.get('session:current');
  if (sess) {
    currentUser = sess;
    await checkSetupOrBoot();
  } else {
    document.getElementById('auth-view').classList.add('active');
  }
}

function toggleAuth() {
  const s = document.getElementById('signup-form').style.display;
  document.getElementById('signup-form').style.display = s === 'none' ? 'block' : 'none';
  document.getElementById('login-form').style.display = s === 'none' ? 'none' : 'block';
}

async function signup() {
  const name = document.getElementById('auth-name-up').value;
  const email = document.getElementById('auth-email-up').value;
  const pass = document.getElementById('auth-pass-up').value;
  if(!name || !email || !pass) return alert("Заполните поля");
  
  if(await storage.get(`users:${email}`)) return alert("Пользователь существует");
  const hashed = await hashStr(pass);
  await storage.set(`users:${email}`, { name, email, pass: hashed });
  
  await storage.set('session:current', { name, email });
  currentUser = { name, email };
  await checkSetupOrBoot();
}

async function login() {
  const email = document.getElementById('auth-email-in').value;
  const pass = document.getElementById('auth-pass-in').value;
  const user = await storage.get(`users:${email}`);
  if(!user) return alert("Пользователь не найден");
  
  const hashed = await hashStr(pass);
  if(user.pass !== hashed) return alert("Неверный пароль");
  
  await storage.set('session:current', { name: user.name, email: user.email });
  currentUser = user;
  await checkSetupOrBoot();
}

async function logout() {
  await storage.remove('session:current');
  location.reload();
}

async function checkSetupOrBoot() {
  document.getElementById('auth-view').classList.remove('active');
  
  const gClient = await storage.get('googleClientId');
  const aKey = await storage.get('apiKey');
  
  if (!gClient || !aKey) {
     if(gClient) document.getElementById('setup-google').value = gClient;
     if(aKey) document.getElementById('setup-anthropic').value = aKey;
     document.getElementById('setup-view').style.display = 'flex';
  } else {
     await loadDashboard();
  }
}

async function saveSetupKeys() {
  const gClient = document.getElementById('setup-google').value.trim();
  const aKey = document.getElementById('setup-anthropic').value.trim();
  if(!gClient || !aKey) return alert('Введите ключи API!');
  
  await storage.set('googleClientId', gClient);
  await storage.set('apiKey', aKey);
  
  document.getElementById('setup-view').style.display = 'none';
  await loadDashboard();
}

// ==========================================
// 3. DASHBOARD LOGIC
// ==========================================
async function loadDashboard() {
  document.getElementById('setup-view').style.display = 'none';
  document.getElementById('app-view').style.display = 'block';
  document.getElementById('user-display').textContent = currentUser.name;
  
  const list = await storage.list(`services:${currentUser.email}:`);
  servicesMap = {};
  list.forEach(s => servicesMap[s.domain] = s);
  
  initGoogleAPI();
  updateUI();
  await renderHistory();
}

function updateUI() {
  const svcs = Object.values(servicesMap);
  const active = svcs.filter(s => s.status === 'active');
  
  document.getElementById('st-total').textContent = svcs.length;
  document.getElementById('st-red').textContent = active.filter(s => s.risk && s.risk.score >= 70).length;
  document.getElementById('st-third').textContent = active.filter(s => s.risk && s.risk.thirdParty).length;
  document.getElementById('st-revoked').textContent = svcs.filter(s => s.status === 'revoked').length;
  
  renderServiceList(svcs);
  initD3Graph(svcs);
}

function renderServiceList(svcs) {
  const listEl = document.getElementById('service-list');
  listEl.innerHTML = svcs.sort((a,b) => (b.risk?.score||0) - (a.risk?.score||0)).map(s => {
    let col = 'var(--text-muted)';
    if(s.status === 'active' && s.risk) {
      if(s.risk.score >= 70) col = 'var(--risk-red)';
      else if(s.risk.score >= 40) col = 'var(--risk-yellow)';
      else col = 'var(--risk-green)';
    }
    
    let scoreDisplay = s.status === 'revoked' ? '🚫' : (s.risk ? `${s.risk.score}` : '<div class="spin-s"></div>');
    
    return `
      <div class="service-item ${s.status === 'revoked' ? 'disabled' : ''}" onclick="openDetail('${s.domain}')">
        <div style="font-size:24px; margin-right:8px; display:flex; align-items:center; justify-content:center; width:40px; height:40px; background:var(--bg-card); border-radius:10px">${s.name.charAt(0).toUpperCase()}</div>
        <div class="svc-info">
          <div class="svc-name">${s.name}</div>
          <div class="svc-domain">${s.domain}</div>
        </div>
        <div class="svc-risk" style="color:${col}">${scoreDisplay}</div>
      </div>
    `;
  }).join('');
}

async function renderHistory() {
  const hList = await storage.list(`history:${currentUser.email}:`);
  hList.sort((a,b) => b.t - a.t);
  document.getElementById('history-list').innerHTML = hList.map(h => `
    <div class="history-item">
      <div class="h-date">${new Date(h.t).toLocaleString('ru-RU')}</div>
      <div style="font-size:13px">${h.msg}</div>
    </div>
  `).join('');
}

function switchTab(t) {
  document.querySelectorAll('.tab-content').forEach(e=>e.style.display='none');
  document.querySelectorAll('.nav-tab').forEach(e=>e.classList.remove('active'));
  document.getElementById(`tab-${t}`).style.display = 'block';
  event.target.classList.add('active');
  if(t === 'dashboard') updateUI();
}

async function addHistory(msg) {
  await storage.set(`history:${currentUser.email}:${Date.now()}`, { t: Date.now(), msg });
  renderHistory();
}

// ==========================================
// 4. GOOGLE GMAIL OAUTH API FLOW
// ==========================================
async function initGoogleAPI() {
  const gClientId = await storage.get('googleClientId');
  googleTokenClient = google.accounts.oauth2.initTokenClient({
    client_id: gClientId,
    scope: 'https://www.googleapis.com/auth/gmail.readonly',
    callback: (tokenResponse) => {
      if (tokenResponse && tokenResponse.access_token) {
        startRealGmailExtraction(tokenResponse.access_token);
      }
    },
  });
}

function startGmailScanOauth() {
  googleTokenClient.requestAccessToken();
}

function setScanText(txt) {
  document.getElementById('scan-text').textContent = txt;
}

async function startRealGmailExtraction(token) {
  document.getElementById('scanner-overlay').style.display = 'flex';
  setScanText('Поиск писем о регистрации...');
  
  // Real Gmail API request
  const qItem = 'subject:"confirm your account" OR subject:"подтверждение регистрации" OR subject:"welcome"';
  let messages = [];
  try {
    const res = await fetch(`https://gmail.googleapis.com/gmail/v1/users/me/messages?q=${encodeURIComponent(qItem)}&maxResults=50`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    const data = await res.json();
    messages = data.messages || [];
  } catch(e) {
    alert('Ошибка Gmail API. Проверьте OAuth Scope.');
    document.getElementById('scanner-overlay').style.display = 'none';
    return;
  }

  let i = 0;
  let domainsFound = 0;
  
  for(let msg of messages) {
    i++;
    setScanText(`Анализируем письма: ${i}/${messages.length}`);
    try {
      const mRes = await fetch(`https://gmail.googleapis.com/gmail/v1/users/me/messages/${msg.id}?format=metadata&metadataHeaders=From&metadataHeaders=Date&metadataHeaders=Subject`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const mData = await mRes.json();
      const headers = mData.payload.headers;
      let fromHead = headers.find(h => h.name.toLowerCase() === 'from')?.value || '';
      
      let emailMatch = fromHead.match(/<([^>]+)>/);
      let email = emailMatch ? emailMatch[1] : fromHead;
      if(!email.includes('@')) continue;
      
      let domain = email.split('@')[1].toLowerCase();
      // Skip personal proxies
      if(['gmail.com','yahoo.com','mail.ru','icloud.com'].includes(domain)) continue;
      
      let nameMatch = fromHead.match(/^"?([^"]+)"?\s*</);
      let name = nameMatch ? nameMatch[1].trim() : domain;
      
      if(!servicesMap[domain]) {
         servicesMap[domain] = { id: domain, name, domain, status: 'active', risk: null };
         await storage.set(`services:${currentUser.email}:${domain}`, servicesMap[domain]);
         domainsFound++;
         updateUI(); // live update graph
      }
    } catch(e) {}
  }
  
  await addHistory(`Gmail Scan завершен. Найдено новых уникальных сервисов: ${domainsFound}`);
  setScanText('Запуск AI Риск-Аанализа для обнаруженных сервисов...');
  
  // Send the extracted domains to Anthropic recursively
  const toAnalyze = Object.values(servicesMap).filter(s => !s.risk && s.status === 'active');
  await runAiAnalysisQueue(toAnalyze);
  
  document.getElementById('scanner-overlay').style.display = 'none';
}

// ==========================================
// 5. ANTHROPIC AI INTEGRATION
// ==========================================

async function callAnthropicRaw(prompt, sys) {
  const apiKey = await storage.get('apiKey');
  const res = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01',
      'anthropic-dangerous-direct-browser-access': 'true'
    },
    body: JSON.stringify({
      model: 'claude-3-5-sonnet-20241022', // Hackathon stable model
      max_tokens: 500,
      system: sys,
      messages: [{role: 'user', content: prompt}]
    })
  });
  if(!res.ok) throw new Error(await res.text());
  const data = await res.json();
  const text = data.content[0].text;
  return JSON.parse(text.substring(text.indexOf('{'), text.lastIndexOf('}') + 1));
}

async function runAiAnalysisQueue(services) {
  for(let i=0; i<services.length; i++) {
    const s = services[i];
    setScanText(`AI Анализ сервиса: ${s.name} (${i+1}/${services.length})`);
    
    const prompt = `Проанализируй цифровой след сервиса: название="${s.name}", домен="${s.domain}". Верни JSON без markdown обертки:
    {
      "score": число от 1 до 100 (уровень риска утечки),
      "reasons": ["почему 1", "почему 2"],
      "dataTypes": ["тип данных 1", "тип 2"],
      "thirdParty": true (если передают брокерам или адтеку) или false,
      "anomaly": "Укажи аномалию (например 'собирают геолокацию хотя это просто калькулятор') или null"
    }`;
    
    try {
      s.risk = await callAnthropicRaw(prompt, "Ты эксперт по приватности данных. Твоя задача защищать пользователя. Отвечай строго валидным JSON.");
      await storage.set(`services:${currentUser.email}:${s.domain}`, s);
      updateUI();
    } catch(e) {
      console.warn("AI eval error for", s.domain, e);
    }
    
    // Rate limit
    await new Promise(r => setTimeout(r, 600));
  }
}

// ==========================================
// 6. DETAIL PANEL, POLICY PARSER & REVOCATION
// ==========================================
function openDetail(domain) {
  const s = servicesMap[domain];
  if(!s) return;
  currentDetailDomain = domain;
  
  document.getElementById('det-name').textContent = s.name;
  document.getElementById('det-domain').textContent = s.domain;
  
  if (s.risk) {
    document.getElementById('det-tags').innerHTML = (s.risk.dataTypes || []).map(t => `<span class="data-tag">${t}</span>`).join('');
    
    let col = getRiskColor(s.risk.score);
    document.getElementById('det-score').textContent = `${s.risk.score}/100`;
    document.getElementById('det-score').style.color = col;
    
    document.getElementById('det-reasons').innerHTML = s.risk.reasons.map(r=>`• ${r}`).join('<br>');
    document.getElementById('det-anomaly').textContent = s.risk.anomaly || 'Не обнаружено';
  }
  
  document.getElementById('policy-box').style.display = 'none';
  document.getElementById('policy-content').innerHTML = '';
  document.getElementById('btn-analyze-policy').style.display = s.status === 'active' ? 'block' : 'none';
  
  const revokeBtn = document.getElementById('det-revoke');
  if(s.status === 'active') {
    revokeBtn.style.display = 'block';
    revokeBtn.textContent = 'Отозвать доступ (GDPR Delete Request)';
  } else {
    revokeBtn.style.display = 'none';
  }

  document.getElementById('detail-overlay').classList.add('open');
}

async function analyzePrivacyPolicy() {
  const s = servicesMap[currentDetailDomain];
  if(!s) return;
  
  const btn = document.getElementById('btn-analyze-policy');
  btn.textContent = 'Парсинг сайта...';
  
  try {
    // Attempt scraping logic via corsproxy
    const proxyUrl = `https://api.allorigins.win/get?url=${encodeURIComponent('https://' + s.domain + '/privacy')}`;
    const res = await fetch(proxyUrl);
    const data = await res.json();
    let text = data.contents;
    
    if(!text || text.length < 500) {
      // try fallback domain
      const fallbackUrl = `https://api.allorigins.win/get?url=${encodeURIComponent('https://' + s.domain + '/privacy-policy')}`;
      const fRes = await fetch(fallbackUrl);
      const fData = await fRes.json();
      text = fData.contents || "";
    }
    
    text = text.replace(/<style[^>]*>.*<\/style>/gi, '').replace(/<script[^>]*>.*<\/script>/gi, '').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
    if(text.length < 100) throw new Error("Политика не найдена на стандартных URL");
    
    btn.textContent = 'AI анализирует юридический текст...';
    
    const chunk = text.substring(0, 3000); // 3000 chars is enough for summary
    const prompt = `Прочти начало этого Privacy Policy и верни JSON: { "redFlags": ["флаг1"], "transparencyScore": 5, "summary": "суть" }. Текст: ${chunk}`;
    
    const aiRes = await callAnthropicRaw(prompt, "Ты юрист по data privacy. Отвечай строго валидным JSON без markdown.");
    
    document.getElementById('policy-box').style.display = 'block';
    document.getElementById('policy-content').innerHTML = `
      <div style="margin-bottom:8px"><b>Прозрачность:</b> ${aiRes.transparencyScore}/10</div>
      <div style="margin-bottom:8px"><b>Выжимка:</b> ${aiRes.summary}</div>
      <div style="color:var(--risk-red)"><b>Красные флаги:</b><br>${(aiRes.redFlags || []).map(r=>`• ${r}`).join('<br>')}</div>
    `;
    btn.style.display = 'none';
    await addHistory(`Успешный NLP-парсинг Privacy Policy для ${s.domain}`);
  } catch(e) {
    btn.textContent = 'Ошибка: ' + e.message;
  }
}

async function revokeAccess() {
  const s = servicesMap[currentDetailDomain];
  if(!confirm(`Вы уверены? Система сгенерирует письмо для Privacy Officer-а домена ${s.domain}.`)) return;
  
  s.status = 'revoked';
  await storage.set(`services:${currentUser.email}:${s.domain}`, s);
  await addHistory(`Сформирован и отправлен GDPR Request на удаление данных для ${s.name} (${s.domain})`);
  
  const body = encodeURIComponent(
    `Hello Privacy/DPO Team at ${s.name},\n\n` +
    `I am writing to you to request the erasure of all my personal data, under the terms of the GDPR / CCPA and applicable privacy laws.\n\n` +
    `Account registered email: ${currentUser.email}\n` +
    `Name: ${currentUser.name}\n\n` +
    `Please confirm that my data has been removed from all your internal systems and third-party brokers.\n\n` +
    `Thank you.`
  );
  
  const mailtoUrl = `mailto:privacy@${s.domain}?cc=dpo@${s.domain},legal@${s.domain}&subject=Data%20Deletion%20Request%20(GDPR)&body=${body}`;
  window.open(mailtoUrl);
  
  updateUI();
  document.getElementById('detail-overlay').classList.remove('open');
}

// ==========================================
// 7. D3 FORCE GRAPH
// ==========================================
function getRiskColor(score) {
  if (score >= 70) return 'var(--risk-red)';
  if (score >= 40) return 'var(--risk-yellow)';
  return 'var(--risk-green)';
}

let graphSim = null;
function initD3Graph(svcs) {
  const container = document.getElementById('graph-svg');
  if(!container || !container.clientWidth) return;
  
  const svg = d3.select('#graph-svg');
  svg.selectAll('*').remove();
  if(graphSim) graphSim.stop();

  const nodes = [{ id: 'user', name: currentUser.name, r: 35, isUser: true }];
  const links = [];
  
  svcs.forEach(s => {
    let active = s.status === 'active';
    nodes.push({
      id: s.domain,
      name: s.name,
      r: active ? (s.risk ? 14 + (s.risk.dataTypes?.length || 0)*2 : 16) : 12,
      col: active && s.risk ? getRiskColor(s.risk.score) : (active ? 'var(--text-muted)' : 'rgba(255,255,255,0.1)'),
      active
    });
    links.push({
      source: 'user',
      target: s.domain,
      weight: active && s.risk ? Math.max(1, s.risk.dataTypes?.length || 1) : 1,
      active
    });
  });

  graphSim = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id(d=>d.id).distance(130))
    .force('charge', d3.forceManyBody().strength(-300))
    .force('center', d3.forceCenter(container.clientWidth/2, container.clientHeight/2));

  const link = svg.append('g').selectAll('line').data(links).enter().append('line')
    .attr('stroke', d => d.active ? 'rgba(255,255,255,0.2)' : 'rgba(255,255,255,0.05)')
    .attr('stroke-dasharray', d => d.active ? 'none' : '5,5')
    .attr('stroke-width', d => d.weight);

  const node = svg.append('g').selectAll('g').data(nodes).enter().append('g')
    .style('cursor', d=>d.isUser ? 'default' : 'pointer')
    .on('click', (e, d) => { if (!d.isUser) openDetail(d.id); })
    .call(d3.drag()
      .on('start', (e,d) => { if(!e.active) graphSim.alphaTarget(0.3).restart(); d.fx=d.x; d.fy=d.y; })
      .on('drag', (e,d) => { d.fx=e.x; d.fy=e.y; })
      .on('end', (e,d) => { if(!e.active) graphSim.alphaTarget(0); d.fx=null; d.fy=null; })
    );

  node.append('circle')
    .attr('r', d => d.r)
    .attr('fill', d => d.isUser ? 'rgba(99,130,255,0.2)' : 'rgba(255,255,255,0.02)')
    .attr('stroke', d => d.isUser ? 'var(--accent-blue)' : d.col)
    .attr('stroke-width', 2);

  node.append('text').attr('dy', d => d.r + 14).attr('text-anchor', 'middle')
    .attr('fill', d => d.active ? '#fff' : 'var(--text-muted)')
    .attr('font-size', '11px').attr('font-weight','500')
    .text(d => d.name);
    
  node.filter(d=>d.isUser).append('text').attr('dy',5).attr('text-anchor','middle').attr('font-size','20px').text('👤');

  graphSim.on('tick', () => {
    link.attr('x1', d=>d.source.x).attr('y1', d=>d.source.y).attr('x2', d=>d.target.x).attr('y2', d=>d.target.y);
    node.attr('transform', d=>`translate(${d.x},${d.y})`);
  });
}

// Runtime Start
window.onload = init;
</script>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as file:
    file.write(html_content)

print("Real Consent OS written successfully.")
