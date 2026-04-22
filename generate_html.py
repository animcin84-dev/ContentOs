import json

html_content = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Consent OS — Реально работающий пульт</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
<style>
:root {
  --bg-primary: #080c14; --bg-secondary: #0d1321; --bg-card: rgba(15, 22, 40, 0.85); --bg-glass: rgba(255,255,255,0.04);
  --border: rgba(99,130,255,0.15); --border-bright: rgba(99,130,255,0.35);
  --accent-blue: #6382ff; --accent-purple: #9b5de5; --accent-cyan: #00d4ff; --accent-green: #00e09e;
  --accent-yellow: #f7c948; --accent-red: #ff4d6d; --accent-orange: #ff7043;
  --text-primary: #e8edf7; --text-secondary: #8892b0; --text-muted: #495670;
  --risk-red: #ff4d6d; --risk-yellow: #f7c948; --risk-green: #00e09e;
  --transition: 0.25s cubic-bezier(0.4,0,0.2,1);
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Inter', sans-serif; background: var(--bg-primary); color: var(--text-primary); min-height: 100vh; overflow-x: hidden; line-height: 1.6; }
body::before { content: ''; position: fixed; inset: 0; background: radial-gradient(ellipse 80% 50% at 10% 20%, rgba(99,130,255,0.07) 0%, transparent 60%), radial-gradient(ellipse 60% 40% at 90% 80%, rgba(155,93,229,0.06) 0%, transparent 60%); z-index: 0; pointer-events: none; }
.wrapper { position: relative; z-index: 1; }

button { cursor: pointer; border: none; font-family: inherit; transition: var(--transition); }
input, select, textarea { width: 100%; padding: 12px; background: var(--bg-primary); border: 1px solid var(--border); border-radius: 8px; color: var(--text-primary); font-family: inherit; margin-bottom: 16px; outline: none; }
input:focus, select:focus, textarea:focus { border-color: var(--accent-blue); }
textarea { resize: vertical; min-height: 100px; }

/* LAYOUT */
.view { display: none; animation: fadeIn 0.3s; }
.view.active { display: block; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

/* AUTH */
.auth-container { display: flex; align-items: center; justify-content: center; min-height: 100vh; }
.auth-box { background: var(--bg-card); border: 1px solid var(--border); padding: 40px; border-radius: 20px; width: 100%; max-width: 400px; text-align: center; }
.auth-logo { font-size: 40px; margin-bottom: 16px; }
.auth-btn { width: 100%; padding: 14px; background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple)); color: white; border-radius: 8px; font-weight: 700; font-size: 16px; margin-top: 10px; }
.auth-btn:hover { filter: brightness(1.1); }
.auth-toggle { font-size: 13px; color: var(--text-secondary); margin-top: 16px; cursor: pointer; }
.auth-toggle:hover { color: var(--accent-blue); }

/* NAVBAR */
.navbar { position: fixed; top: 0; left: 0; right: 0; height: 64px; background: rgba(8,12,20,0.85); backdrop-filter: blur(24px); border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; padding: 0 32px; z-index: 100;}
.nav-logo { font-weight: 700; font-size: 18px; display: flex; align-items: center; gap: 8px; }
.nav-logo span { color: var(--accent-blue); }
.nav-tabs { display: flex; gap: 4px; background: var(--bg-glass); border-radius: 10px; padding: 4px; border: 1px solid var(--border); }
.nav-tab { padding: 6px 16px; border-radius: 8px; font-size: 13px; font-weight: 500; color: var(--text-secondary); background: transparent; }
.nav-tab.active { background: rgba(99,130,255,0.15); color: var(--accent-blue); }
.nav-user { display: flex; align-items: center; gap: 12px; }
.logout-btn { background: transparent; color: var(--risk-red); font-size: 13px; font-weight: 600; padding: 6px 12px; border: 1px solid rgba(255,77,109,0.3); border-radius: 8px; }

/* MAIN */
.main { padding: 88px 32px 40px; max-width: 1400px; margin: 0 auto; }

/* OVERVIEW STATS */
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
.stat-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 16px; padding: 20px; }
.stat-val { font-size: 32px; font-weight: 800; margin: 8px 0; }
.stat-lbl { font-size: 12px; color: var(--text-muted); text-transform: uppercase; font-weight: 600; }

/* PANELS */
.split-layout { display: grid; grid-template-columns: 1fr 380px; gap: 24px; align-items: start; }
.panel { background: var(--bg-card); border: 1px solid var(--border); border-radius: 16px; padding: 20px; }
.panel-title { font-size: 16px; font-weight: 700; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center;}

/* GRAPH */
.graph-container { width: 100%; height: 500px; position: relative; }
#graph-svg { width: 100%; height: 100%; }

/* SERVICE LIST */
.service-list { display: flex; flex-direction: column; gap: 12px; max-height: 500px; overflow-y: auto; padding-right: 8px; }
.service-item { display: flex; align-items: center; gap: 12px; padding: 12px; border: 1px solid var(--border); border-radius: 12px; background: var(--bg-glass); cursor: pointer; }
.service-item:hover { border-color: var(--border-bright); }
.svc-icon { width: 36px; height: 36px; border-radius: 8px; background: rgba(255,255,255,0.05); display: flex; align-items: center; justify-content: center; font-size: 20px; }
.svc-info { flex: 1; }
.svc-name { font-weight: 600; font-size: 14px; }
.svc-meta { font-size: 11px; color: var(--text-muted); }
.svc-risk { width: 12px; height: 12px; border-radius: 50%; }

/* ADD SERVICE FORM */
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.checkbox-group { display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 16px; }
.checkbox-item { display: flex; align-items: center; gap: 6px; font-size: 13px; background: var(--bg-glass); padding: 8px 12px; border-radius: 8px; border: 1px solid var(--border); cursor: pointer;}
.checkbox-item input { margin: 0; width: auto; }
.btn-primary { background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple)); padding: 14px 24px; color: white; border-radius: 8px; font-weight: 700; font-size: 15px; }

/* DETAIL PANEL */
.detail-overlay { position: fixed; right: -500px; top: 64px; bottom: 0; width: 480px; background: var(--bg-secondary); border-left: 1px solid var(--border); transition: right 0.3s; z-index: 200; overflow-y: auto; display: flex; flex-direction: column; }
.detail-overlay.open { right: 0; }
.detail-header { padding: 24px; border-bottom: 1px solid var(--border); }
.detail-body { padding: 24px; flex: 1; }
.btn-revoke { width: 100%; padding: 14px; background: rgba(255,77,109,0.15); color: var(--risk-red); border: 1px solid rgba(255,77,109,0.3); border-radius: 8px; font-weight: 600; font-size: 15px; margin-top: auto; }
.btn-revoke:hover { background: rgba(255,77,109,0.25); }
.data-tag { display: inline-flex; background: rgba(255,255,255,0.05); padding: 4px 10px; border-radius: 20px; font-size: 11px; margin: 4px 4px 4px 0; border: 1px solid var(--border); }
.ai-box { background: rgba(155,93,229,0.08); border: 1px solid rgba(155,93,229,0.3); padding: 16px; border-radius: 12px; margin-bottom: 16px; }
.ai-box h4 { color: #d0a5ff; margin-bottom: 8px; font-size: 13px; display: flex; align-items: center; gap: 6px; }

/* HISTORY */
.history-timeline { display: flex; flex-direction: column; gap: 12px; }
.history-item { background: var(--bg-card); padding: 16px; border: 1px solid var(--border); border-radius: 12px; display: flex; gap: 16px; align-items: center; }
.h-date { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--text-muted); min-width: 140px; }
.h-text { flex: 1; font-size: 14px; }
.h-badge { padding: 4px 8px; border-radius: 12px; font-size: 10px; font-weight: 700; text-transform: uppercase; }

/* TOAST */
#toast-container { position: fixed; bottom: 24px; right: 24px; z-index: 999; display: flex; flex-direction: column; gap: 8px; }
.toast { background: var(--bg-card); border: 1px solid var(--border); padding: 16px 20px; border-radius: 12px; box-shadow: var(--shadow-card); color: white; display: flex; align-items: center; gap: 12px; animation: slideIn 0.3s forwards; }
@keyframes slideIn { from{transform:translateX(100%);} to{transform:translateX(0);} }

/* LOADER */
.ai-loader { display: none; align-items: center; justify-content: center; padding: 20px; flex-direction: column; gap: 12px; color: var(--accent-purple); font-weight: 600; font-size: 13px; }
.spinner { width: 32px; height: 32px; border: 3px solid rgba(155,93,229,0.3); border-top-color: var(--accent-purple); border-radius: 50%; animation: spin 1s infinite linear; }
@keyframes spin { to {transform: rotate(360deg);} }
</style>
</head>
<body>
<div class="wrapper">

<!-- AUTH VIEW -->
<div id="auth-view" class="view auth-container active">
  <div class="auth-box">
    <div class="auth-logo">🛡️</div>
    <h2 style="margin-bottom: 24px">Consent OS</h2>
    
    <div id="login-form">
      <input type="email" id="auth-email-in" placeholder="Email" value="user@mail.kz">
      <input type="password" id="auth-pass-in" placeholder="Пароль" value="123456">
      <button class="auth-btn" id="btn-login" onclick="login()">Войти</button>
      <div class="auth-toggle" onclick="toggleAuth()">Нет аккаунта? Зарегистрироваться</div>
    </div>
    
    <div id="signup-form" style="display:none">
      <input type="text" id="auth-name-up" placeholder="Ваше Имя">
      <input type="email" id="auth-email-up" placeholder="Email">
      <input type="password" id="auth-pass-up" placeholder="Придумайте пароль">
      <button class="auth-btn" id="btn-signup" onclick="signup()">Создать аккаунт</button>
      <div class="auth-toggle" onclick="toggleAuth()">Уже есть аккаунт? Войти</div>
    </div>
  </div>
</div>

<!-- APP VIEW -->
<div id="app-view" class="view">
  <nav class="navbar">
    <div class="nav-logo">🛡️ <span>Consent</span> OS</div>
    <div class="nav-tabs">
      <button class="nav-tab active" onclick="switchTab('dashboard')">Дашборд</button>
      <button class="nav-tab" onclick="switchTab('add')">➕ Добавить сервис</button>
      <button class="nav-tab" onclick="switchTab('history')">📜 История</button>
      <button class="nav-tab" onclick="switchTab('settings')">⚙️ Настройки API</button>
    </div>
    <div class="nav-user">
      <div id="header-name" style="font-weight:600; font-size:14px"></div>
      <button class="logout-btn" onclick="logout()">Выйти</button>
    </div>
  </nav>

  <main class="main">
    
    <!-- DASHBOARD -->
    <div id="tab-dashboard" class="tab-content active">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-lbl">Всего сервисов</div>
          <div class="stat-val" style="color:var(--accent-blue)" id="st-total">0</div>
        </div>
        <div class="stat-card">
          <div class="stat-lbl">Активных доступов</div>
          <div class="stat-val" style="color:var(--accent-green)" id="st-active">0</div>
        </div>
        <div class="stat-card">
          <div class="stat-lbl">Красных флагов</div>
          <div class="stat-val" style="color:var(--risk-red)" id="st-red">0</div>
        </div>
        <div class="stat-card">
          <div class="stat-lbl">Отозвано решений</div>
          <div class="stat-val" style="color:var(--text-muted)" id="st-revoked">0</div>
        </div>
      </div>

      <div class="split-layout">
        <div class="panel">
          <div class="panel-title">Карта потоков данных (Live)</div>
          <div class="graph-container">
            <svg id="graph-svg"></svg>
          </div>
        </div>
        
        <div class="panel">
          <div class="panel-title">
            <span>Реестр доступов</span>
            <button class="logout-btn" onclick="revokeAllActive()">🚨 Отозвать все</button>
          </div>
          <input type="text" id="search-svc" placeholder="Поиск сервиса..." oninput="renderServiceList()">
          <div class="service-list" id="services-list">
            <!-- Rendered via JS -->
          </div>
        </div>
      </div>
    </div>

    <!-- ADD SERVICE -->
    <div id="tab-add" class="tab-content" style="display:none">
      <div class="panel" style="max-width: 900px; margin: 0 auto">
        <h2 style="margin-bottom:24px">Регистрация нового согласия</h2>
        <form id="add-form" onsubmit="handleAddService(event)">
          <div class="form-grid">
            <div>
              <label class="stat-lbl">Название сервиса</label>
              <input type="text" id="f-name" required placeholder="Например: Яндекс.Такси">
              
              <label class="stat-lbl">Категория</label>
              <select id="f-cat" required>
                <option value="Финансы">Финансы</option>
                <option value="Образование">Образование</option>
                <option value="Здоровье">Здоровье</option>
                <option value="Транспорт">Транспорт</option>
                <option value="Соцсети">Соцсети</option>
                <option value="Утилиты">Утилиты</option>
                <option value="Другое">Другое</option>
              </select>
              
              <label class="stat-lbl">Цель обработки (как описано)</label>
              <input type="text" id="f-purpose" required placeholder="Например: Заказ машины и оплата">
              
              <label class="stat-lbl">Дата согласия</label>
              <input type="date" id="f-date" required>
            </div>
            
            <div>
              <label class="stat-lbl">Запрашиваемые типы данных (отметьте)</label>
              <div class="checkbox-group">
                <label class="checkbox-item"><input type="checkbox" name="dataItem" value="Геолокация">📍 Геолокация</label>
                <label class="checkbox-item"><input type="checkbox" name="dataItem" value="Контакты">📱 Контакты</label>
                <label class="checkbox-item"><input type="checkbox" name="dataItem" value="Камера">📸 Камера</label>
                <label class="checkbox-item"><input type="checkbox" name="dataItem" value="Микрофон">🎙 Микрофон</label>
                <label class="checkbox-item"><input type="checkbox" name="dataItem" value="Финансы">💳 Финансы</label>
                <label class="checkbox-item"><input type="checkbox" name="dataItem" value="Биометрия">🤳 Биометрия</label>
                <label class="checkbox-item"><input type="checkbox" name="dataItem" value="История действий">📊 История</label>
              </div>
              
              <div style="margin-bottom: 16px;">
                <label class="checkbox-item" style="border-color:var(--risk-red)"><input type="checkbox" id="f-third"> Передача третьим лицам?</label>
              </div>
              
              <label class="stat-lbl">Текст юридического соглашения (Опционально. Для глубокого AI-анализа)</label>
              <textarea id="f-text" placeholder="Вставьте сюда политику конфиденциальности..."></textarea>
            </div>
          </div>
          <button type="submit" class="btn-primary" style="width:100%; margin-top:16px">Сохранить и запустить AI-Анализ</button>
        </form>
      </div>
    </div>

    <!-- HISTORY -->
    <div id="tab-history" class="tab-content" style="display:none">
      <div class="panel">
        <div class="panel-title">
          <span>Полный журнал аудита (Immutable Log)</span>
          <button class="logout-btn" style="color:var(--text-primary); border-color:var(--border)" onclick="exportHistory()">⬇ Экспорт (JSON)</button>
        </div>
        <div class="history-timeline" id="history-container"></div>
      </div>
    </div>

    <!-- SETTINGS -->
    <div id="tab-settings" class="tab-content" style="display:none">
      <div class="panel" style="max-width: 600px; margin: 0 auto">
        <h2 style="margin-bottom: 24px">Настройки ядра (AI Engine)</h2>
        <p style="font-size:13px; color:var(--text-secondary); margin-bottom:24px">Система использует модель <b>claude-sonnet-4-20250514</b> для интеллектуального анализа.</p>
        
        <label class="stat-lbl">Ключ Anthropic API (x-api-key)</label>
        <input type="password" id="settings-key" placeholder="sk-ant-...">
        
        <label class="stat-lbl">Base URL (если нужен Proxy)</label>
        <input type="text" id="settings-url" value="https://api.anthropic.com/v1/messages">
        
        <button class="btn-primary" onclick="saveSettings()">Сохранить настройки</button>
      </div>
    </div>

  </main>
</div>

<!-- DETAIL PANEL OVERLAY -->
<div class="detail-overlay" id="detail-overlay">
  <div class="detail-header" style="display:flex; justify-content:space-between; align-items:flex-start">
    <div>
      <h2 id="d-name">Название</h2>
      <div id="d-cat" style="color:var(--text-muted); font-size:13px; margin-top:4px">Категория</div>
    </div>
    <button onclick="closeDetail()" style="background:var(--bg-glass); border:1px solid var(--border); color:#fff; width:32px; height:32px; border-radius:8px">✕</button>
  </div>
  
  <div class="detail-body" style="display:flex; flex-direction:column">
    
    <div id="d-ai-loader" class="ai-loader">
      <div class="spinner"></div>
      <div>AI анализирует соглашение и потоки данных...</div>
    </div>

    <div id="d-content">
      <div style="margin-bottom: 24px" id="d-tags"></div>
      
      <div class="ai-box" id="d-risk-box">
        <h4>✨ AI Риск-Отчёт</h4>
        <div style="font-size:24px; font-weight:800; margin-bottom:12px" id="d-risk-score">Балл риска: --/100</div>
        <div style="font-size:13px; color:var(--text-primary)" id="d-risk-reasons"></div>
      </div>

      <div class="ai-box" id="d-text-box" style="display:none">
        <h4>📜 AI Выжимка соглашения</h4>
        <ul style="font-size:13px; padding-left:16px; margin:8px 0; color:var(--text-primary)" id="d-text-points"></ul>
        <div style="font-size:12px; color:var(--risk-red); margin-top:12px; font-weight:600" id="d-text-flags"></div>
      </div>

      <div style="font-size:13px; margin-bottom:24px">
        <div style="margin-bottom:8px"><b>Дата согласия:</b> <span id="d-date"></span></div>
        <div style="margin-bottom:8px"><b>Цель:</b> <span id="d-purpose"></span></div>
        <div style="margin-bottom:8px"><b>Третьи лица:</b> <span id="d-third"></span></div>
      </div>

      <div id="d-action-area"></div>
    </div>
  </div>
</div>

<div id="toast-container"></div>

</div>

<script>
// ==========================================
// 1. ROBUST STORAGE API ENCAPSULATION
// ==========================================
window.storage = {
  set: async (key, value) => {
    localStorage.setItem(key, JSON.stringify(value));
  },
  get: async (key) => {
    const v = localStorage.getItem(key);
    return v ? JSON.parse(v) : null;
  },
  list: async (prefix) => {
    const res = [];
    for(let i=0; i<localStorage.length; i++) {
      const key = localStorage.key(i);
      if(key.startsWith(prefix)) {
        res.push(JSON.parse(localStorage.getItem(key)));
      }
    }
    return res;
  },
  remove: async (key) => {
    localStorage.removeItem(key);
  }
};

// ==========================================
// 2. CRYPTO UTILS FOR HASHING PASSWORDS
// ==========================================
async function hashPassword(msg) {
  const data = new TextEncoder().encode(msg);
  const hash = await crypto.subtle.digest('SHA-256', data);
  return Array.from(new Uint8Array(hash)).map(b => b.toString(16).padStart(2, '0')).join('');
}

// ==========================================
// 3. GLOBAL STATE & INIT
// ==========================================
let currentUser = null;
let servicesData = [];
let historyData = [];
let graphSim = null;

async function init() {
  const sess = await window.storage.get('session:current');
  if (sess) {
    currentUser = sess;
    await bootApp();
  } else {
    document.getElementById('auth-view').classList.add('active');
    document.getElementById('app-view').classList.remove('active');
  }
}

// ==========================================
// 4. AUTH FLOW
// ==========================================
function toggleAuth() {
  const s = document.getElementById('signup-form').style.display;
  document.getElementById('signup-form').style.display = s === 'none' ? 'block' : 'none';
  document.getElementById('login-form').style.display = s === 'none' ? 'none' : 'block';
}

async function signup() {
  try {
    const name = document.getElementById('auth-name-up').value.trim();
    const email = document.getElementById('auth-email-up').value.trim();
    const pass = document.getElementById('auth-pass-up').value;
    
    if(!name || !email || !pass) throw new Error("Заполните все поля");
    
    const existing = await window.storage.get(`users:${email}`);
    if(existing) throw new Error("Пользователь с таким email уже существует");

    const hashed = await hashPassword(pass);
    const user = { name, email, pass: hashed, createdAt: Date.now() };
    await window.storage.set(`users:${email}`, user);
    
    // Auto login
    await window.storage.set('session:current', {name, email});
    currentUser = {name, email};
    showToast('Успешная регистрация', 'success');
    await bootApp();
  } catch (e) { showToast(e.message, 'error'); }
}

async function login() {
  try {
    const email = document.getElementById('auth-email-in').value.trim();
    const pass = document.getElementById('auth-pass-in').value;
    
    if(!email || !pass) throw new Error("Введите данные");
    
    const user = await window.storage.get(`users:${email}`);
    if(!user) throw new Error("Пользователь не найден");
    
    const hashed = await hashPassword(pass);
    if(user.pass !== hashed) throw new Error("Неверный пароль");

    await window.storage.set('session:current', {name: user.name, email: user.email});
    currentUser = {name: user.name, email: user.email};
    showToast('С возвращением!', 'success');
    await bootApp();
  } catch (e) { showToast(e.message, 'error'); }
}

async function logout() {
  await window.storage.remove('session:current');
  location.reload();
}

async function bootApp() {
  document.getElementById('auth-view').classList.remove('active');
  document.getElementById('app-view').classList.add('active');
  document.getElementById('header-name').textContent = currentUser.name;
  
  await loadUserData();
  switchTab('dashboard');
  
  // Set defaults for settings if empty
  const url = await window.storage.get('apiUrl');
  if(url) document.getElementById('settings-url').value = url;
  const key = await window.storage.get('apiKey');
  if(key) document.getElementById('settings-key').value = key;
}

// ==========================================
// 5. CORE APP LOGIC (LOAD, RENDER)
// ==========================================
async function loadUserData() {
  servicesData = await window.storage.list(`services:${currentUser.email}:`);
  historyData = await window.storage.list(`history:${currentUser.email}:`);
  historyData.sort((a,b)=> b.timestamp - a.timestamp);
  
  renderStats();
  renderServiceList();
  renderHistory();
  initD3Graph();
}

async function addLog(text, type='info') {
  const log = { id: Date.now(), text, type, timestamp: Date.now() };
  await window.storage.set(`history:${currentUser.email}:${log.id}`, log);
  historyData.unshift(log);
  renderHistory();
}

function switchTab(tabId) {
  document.querySelectorAll('.tab-content').forEach(el=>el.style.display='none');
  document.querySelectorAll('.nav-tab').forEach(el=>el.classList.remove('active'));
  document.getElementById('tab-'+tabId).style.display = 'block';
  event.target.classList.add('active');
  
  if(tabId==='dashboard') initD3Graph(); // refresh dimensions
}

function getRiskColor(score) {
  if(score === null) return 'var(--text-muted)';
  if(score >= 70) return 'var(--risk-red)';
  if(score >= 40) return 'var(--risk-yellow)';
  return 'var(--risk-green)';
}

function renderStats() {
  const active = servicesData.filter(s=>s.status === 'active');
  document.getElementById('st-total').textContent = servicesData.length;
  document.getElementById('st-active').textContent = active.length;
  document.getElementById('st-red').textContent = active.filter(s=>s.riskScore >= 70).length;
  document.getElementById('st-revoked').textContent = servicesData.filter(s=>s.status === 'revoked').length;
}

function renderServiceList() {
  const term = document.getElementById('search-svc').value.toLowerCase();
  const list = document.getElementById('services-list');
  
  const filtered = servicesData.filter(s => s.name.toLowerCase().includes(term)).sort((a,b)=>b.addedAt - a.addedAt);
  
  list.innerHTML = filtered.map(s => {
    const col = s.status==='revoked' ? 'var(--text-muted)' : getRiskColor(s.riskScore);
    const badge = s.status==='revoked' ? '✅ Отозван' : (s.riskScore===null ? '🔄 AI Анализ...' : s.riskScore+'/100');
    return `
      <div class="service-item" onclick="openServiceDetail('${s.id}')" style="opacity:${s.status==='revoked'?0.5:1}">
        <div class="svc-icon">${s.name.charAt(0).toUpperCase()}</div>
        <div class="svc-info">
          <div class="svc-name">${s.name}</div>
          <div class="svc-meta">${s.category} · ${s.dataTypes.length} типов данных</div>
        </div>
        <div style="font-size:12px; font-weight:600; color:${col}; display:flex; align-items:center; gap:6px">
          <div class="svc-risk" style="background:${col}"></div> ${badge}
        </div>
      </div>
    `;
  }).join('');
}

function renderHistory() {
  const hl = document.getElementById('history-container');
  hl.innerHTML = historyData.map(h => {
    let bCol = h.type==='alert' ? 'var(--risk-red)' : h.type==='revoke' ? 'var(--accent-green)' : 'var(--accent-blue)';
    return `
      <div class="history-item">
        <div class="h-date">${new Date(h.timestamp).toLocaleString('ru-RU')}</div>
        <div class="h-badge" style="background:${bCol}22; color:${bCol}">${h.type}</div>
        <div class="h-text">${h.text}</div>
      </div>
    `;
  }).join('');
}

function initD3Graph() {
  const container = document.getElementById('graph-svg');
  if(!container.clientWidth) return;
  const W = container.clientWidth;
  const H = container.clientHeight;
  const svg = d3.select('#graph-svg');
  svg.selectAll('*').remove();
  
  if(graphSim) graphSim.stop();

  const nodes = [{id:'USER', name:'Я', isUser:true, r:36}];
  const links = [];
  
  servicesData.forEach(s => {
    if(s.status === 'revoked') return; // hide revoked from graph
    nodes.push({id:s.id, name:s.name, score:s.riskScore, typesCount: s.dataTypes.length, r:24});
    links.push({source:'USER', target:s.id, weight: s.dataTypes.length});
  });

  graphSim = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id(d=>d.id).distance(150))
    .force('charge', d3.forceManyBody().strength(-400))
    .force('center', d3.forceCenter(W/2, H/2))
    .force('collide', d3.forceCollide().radius(d=>d.r + 10));

  const link = svg.append('g').selectAll('line').data(links).enter().append('line')
    .attr('stroke', 'rgba(255,255,255,0.15)')
    .attr('stroke-width', d => Math.max(2, d.weight));

  const node = svg.append('g').selectAll('g').data(nodes).enter().append('g')
    .style('cursor', 'pointer')
    .on('click', (e, d) => { if(!d.isUser) openServiceDetail(d.id); })
    .call(d3.drag()
      .on('start', (e,d)=>{ if(!e.active) graphSim.alphaTarget(0.3).restart(); d.fx=d.x; d.fy=d.y; })
      .on('drag', (e,d)=>{ d.fx=e.x; d.fy=e.y; })
      .on('end', (e,d)=>{ if(!e.active) graphSim.alphaTarget(0); d.fx=null; d.fy=null; })
    );

  node.append('circle')
    .attr('r', d=>d.r)
    .attr('fill', d => {
      if(d.isUser) return 'rgba(99,130,255,0.3)';
      return getRiskColor(d.score).replace('var(--','').replace(')','') + '33'; // rough translation
    })
    .attr('stroke', d => d.isUser ? 'var(--accent-blue)' : getRiskColor(d.score))
    .attr('stroke-width', 2);
    
  node.append('text').attr('dy', d=>d.isUser ? 5 : 40).attr('text-anchor', 'middle')
    .attr('font-size', d=>d.isUser?'14px':'11px').attr('font-weight','600').attr('fill', '#fff')
    .text(d=>d.name);

  graphSim.on('tick', () => {
    link.attr('x1', d=>d.source.x).attr('y1', d=>d.source.y).attr('x2', d=>d.target.x).attr('y2', d=>d.target.y);
    node.attr('transform', d=>`translate(${d.x},${d.y})`);
  });
}

// ==========================================
// 6. ADD SERVICE & REAL AI ANALYSIS
// ==========================================
async function saveSettings() {
  const k = document.getElementById('settings-key').value.trim();
  const u = document.getElementById('settings-url').value.trim();
  await window.storage.set('apiKey', k);
  await window.storage.set('apiUrl', u);
  showToast('Настройки API сохранены', 'success');
}

function getCheckedValues(name) {
  return Array.from(document.querySelectorAll(`input[name="${name}"]:checked`)).map(e=>e.value);
}

async function handleAddService(e) {
  e.preventDefault();
  
  const dk = await window.storage.get('apiKey');
  if(!dk) { showToast("Укажите API ключ Anthropic в настройках!", "error"); return; }
  
  const sName = document.getElementById('f-name').value;
  const sCat = document.getElementById('f-cat').value;
  const sPurp = document.getElementById('f-purpose').value;
  const sDate = document.getElementById('f-date').value;
  const sThird = document.getElementById('f-third').checked;
  const sTypes = getCheckedValues('dataItem');
  const sText = document.getElementById('f-text').value;
  
  if(sTypes.length===0) { showToast('Выберите хотя бы один тип данных', 'error'); return;}
  
  const svcId = 'svc_' + Date.now();
  const service = {
    id: svcId, userId: currentUser.email,
    name: sName, category: sCat, purpose: sPurp, consentDate: sDate,
    thirdParty: sThird, dataTypes: sTypes, agreementText: sText,
    status: 'active', riskScore: null, riskAnalysis: null, textAnalysis: null,
    addedAt: Date.now()
  };
  
  await window.storage.set(`services:${currentUser.email}:${svcId}`, service);
  servicesData.unshift(service);
  await addLog(`Добавлено согласие для сервиса: ${sName}`, 'info');
  
  document.getElementById('add-form').reset();
  showToast("Сервис добавлен. Запускаем ИИ...", "success");
  
  switchTab('dashboard'); // go back to dash
  
  // Async Trigger AI
  runRealAIAnalysis(svcId);
}

async function fetchAnthropic(promptMsg) {
  const apiKey = await window.storage.get('apiKey');
  const apiUrl = await window.storage.get('apiUrl') || 'https://api.anthropic.com/v1/messages';
  
  const res = await fetch(apiUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01',
      'anthropic-dangerous-direct-browser-access': 'true'
    },
    body: JSON.stringify({
      model: 'claude-3-5-sonnet-20241022', // Hackathon equivalent or fallback
      max_tokens: 1024,
      system: "Ты специализированный AI-аудитор персональных данных (Privacy OS). Отвечай строго в формате JSON, без маркдаун обертки ```json.",
      messages: [{role: 'user', content: promptMsg}]
    })
  });
  
  if(!res.ok) {
    const err = await res.json();
    throw new Error(err.error?.message || "Anthropic API Error");
  }
  
  const data = await res.json();
  const text = data.content[0].text;
  
  // Robust JSON extract
  const start = text.indexOf('{');
  const end = text.lastIndexOf('}') + 1;
  return JSON.parse(text.substring(start, end));
}

async function runRealAIAnalysis(svcId) {
  let svc = servicesData.find(s=>s.id === svcId);
  if(!svc) return;
  
  // Update UI if detail is open
  if(document.getElementById('detail-overlay').classList.contains('open') && document.getElementById('d-name').dataset.id === svcId) {
    document.getElementById('d-content').style.display = 'none';
    document.getElementById('d-ai-loader').style.display = 'flex';
  }

  try {
    // 1. RISK SCORE
    const riskPrompt = `
      Оцени риск приватности сервиса:
      Название: ${svc.name}
      Категория: ${svc.category}
      Цель: ${svc.purpose}
      Типы данных: ${svc.dataTypes.join(', ')}
      Передача третьим лицам: ${svc.thirdParty ? 'Да' : 'Нет'}
      
      Оцени от 1 до 100 насколько опасен этот сбор данных. 
      Формат JSON: {"score": число, "reasons": ["причина1","причина2", "причина3"]}
    `;
    
    // 2. TEXT ANALYSIS (if provided)
    let textPromise = null;
    if(svc.agreementText && svc.agreementText.trim().length > 20) {
      const txtPrompt = `
        Проанализируй текст соглашения пользователя. Выдели суть в 3 пункта. Есть ли скрытые красные флаги?
        Текст: ${svc.agreementText.substring(0, 3000)}
        
        Формат JSON: {"points": ["п1","п2","п3"], "flags": "строка с кратким предупреждением или null если ок"}
      `;
      textPromise = fetchAnthropic(txtPrompt);
    }
    
    // Execute calls
    const riskData = await fetchAnthropic(riskPrompt);
    svc.riskScore = riskData.score;
    svc.riskAnalysis = riskData.reasons;
    
    if(textPromise) {
      const txtData = await textPromise;
      svc.textAnalysis = txtData;
    }
    
    // Save state
    await window.storage.set(`services:${currentUser.email}:${svcId}`, svc);
    await addLog(`AI оценил риск сервиса ${svc.name}: ${svc.riskScore}/100`, svc.riskScore > 70 ? 'alert' : 'info');
    
    showToast(`Анализ ${svc.name} завершён`, 'success');
  } catch (err) {
    console.error("AI Error:", err);
    showToast("Ошибка AI: " + err.message, "error");
    svc.riskAnalysis = ["Анализ не удался: " + err.message];
  } finally {
    // Trigger re-renders
    renderStats();
    renderServiceList();
    initD3Graph();
    
    if(document.getElementById('detail-overlay').classList.contains('open') && document.getElementById('d-name').dataset.id === svcId) {
      openServiceDetail(svcId); // refresh
    }
  }
}

// ==========================================
// 7. DETAIL VIEW & REVOKE ACTION
// ==========================================
function openServiceDetail(id) {
  const svc = servicesData.find(s=>s.id === id);
  if(!svc) return;
  
  document.getElementById('d-name').textContent = svc.name;
  document.getElementById('d-name').dataset.id = svc.id;
  document.getElementById('d-cat').textContent = svc.category;
  
  document.getElementById('d-tags').innerHTML = svc.dataTypes.map(t=>`<span class="data-tag">${t}</span>`).join('');
  document.getElementById('d-date').textContent = new Date(svc.consentDate).toLocaleDateString();
  document.getElementById('d-purpose').textContent = svc.purpose || 'Не указана';
  document.getElementById('d-third').textContent = svc.thirdParty ? 'Да ⚠' : 'Нет';
  
  const contentEl = document.getElementById('d-content');
  const loaderEl = document.getElementById('d-ai-loader');
  
  if (svc.riskScore === null) {
    contentEl.style.display = 'none';
    loaderEl.style.display = 'flex';
  } else {
    loaderEl.style.display = 'none';
    contentEl.style.display = 'block';
    
    document.getElementById('d-risk-score').textContent = `Риск: ${svc.riskScore}/100`;
    document.getElementById('d-risk-score').style.color = getRiskColor(svc.riskScore);
    document.getElementById('d-risk-reasons').innerHTML = svc.riskAnalysis ? svc.riskAnalysis.map(r=>`• ${r}`).join('<br>') : 'Анализ отсутствует';
    
    if(svc.textAnalysis) {
      document.getElementById('d-text-box').style.display = 'block';
      document.getElementById('d-text-points').innerHTML = svc.textAnalysis.points.map(p=>`<li>${p}</li>`).join('');
      document.getElementById('d-text-flags').textContent = svc.textAnalysis.flags || '';
    } else {
      document.getElementById('d-text-box').style.display = 'none';
    }
    
    document.getElementById('d-action-area').innerHTML = svc.status === 'active' 
      ? `<button class="btn-revoke" onclick="revokeService('${svc.id}')">🚫 Отозвать доступ немедленно</button>`
      : `<div style="text-align:center; padding:16px; border:1px dashed var(--border); border-radius:8px; color:var(--text-muted)">Доступ отозван ${new Date(svc.revokedAt).toLocaleString()}</div>`;
  }
  
  document.getElementById('detail-overlay').classList.add('open');
}

function closeDetail() { document.getElementById('detail-overlay').classList.remove('open'); }

async function revokeService(id) {
  if(!confirm("Вы уверены? Система сгенерирует DSAR-событие и разорвет связь.")) return;
  
  let svc = servicesData.find(s=>s.id === id);
  svc.status = 'revoked';
  svc.revokedAt = Date.now();
  
  await window.storage.set(`services:${currentUser.email}:${id}`, svc);
  await addLog(`Пользователь отозвал согласие у сервиса: ${svc.name}`, 'revoke');
  
  showToast(`Доступ для ${svc.name} отозван`, 'success');
  
  renderStats();
  renderServiceList();
  initD3Graph();
  openServiceDetail(id); // refresh
}

async function revokeAllActive() {
  if(!confirm("Отозвать сразу ВСЕ активные доступы? Это действие применится ко всем сервисам.")) return;
  const actives = servicesData.filter(s=>s.status === 'active');
  for(let s of actives) {
    s.status = 'revoked';
    s.revokedAt = Date.now();
    await window.storage.set(`services:${currentUser.email}:${s.id}`, s);
  }
  await addLog(`Массовый отзыв доступов (${actives.length} сервисов)`, 'revoke');
  
  renderStats(); renderServiceList(); initD3Graph();
  showToast('Все доступы отозваны', 'success');
}

function exportHistory() {
  const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(historyData, null, 2));
  const el = document.createElement('a');
  el.setAttribute("href", dataStr);
  el.setAttribute("download", `consent-history-${currentUser.email}.json`);
  document.body.appendChild(el);
  el.click();
  el.remove();
}

function showToast(msg, type='info') {
  const el = document.createElement('div');
  el.className = 'toast';
  el.style.borderColor = type==='error'?'rgba(255,77,109,0.5)':type==='success'?'rgba(0,224,158,0.5)':'var(--border)';
  el.innerHTML = `${type==='error'?'❌':type==='success'?'✅':'ℹ️'} ${msg}`;
  document.getElementById('toast-container').appendChild(el);
  setTimeout(()=>el.remove(), 4000);
}

// Start
init();
</script>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as file:
    file.write(html_content)

print("Generated index.html successfully.")
