import json

html_content = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Consent OS — Автономная система контроля</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
<style>
:root {
  --bg-primary: #080c14; --bg-secondary: #0d1321; --bg-card: rgba(15, 22, 40, 0.85); --bg-glass: rgba(255,255,255,0.04);
  --border: rgba(99,130,255,0.15); --border-bright: rgba(99,130,255,0.35);
  --accent-blue: #6382ff; --accent-purple: #9b5de5; --accent-cyan: #00d4ff; --accent-green: #00e09e;
  --accent-yellow: #f7c948; --accent-red: #ff4d6d;
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

/* NAVBAR */
.navbar { height: 64px; background: rgba(8,12,20,0.85); backdrop-filter: blur(24px); border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; padding: 0 32px; z-index: 100; position: fixed; top: 0; left: 0; right: 0; }
.nav-logo { font-weight: 700; font-size: 18px; display: flex; align-items: center; gap: 8px; }
.nav-logo span { color: var(--accent-blue); }
.nav-tabs { display: flex; gap: 4px; background: var(--bg-glass); border-radius: 10px; padding: 4px; border: 1px solid var(--border); }
.nav-tab { padding: 6px 16px; border-radius: 8px; font-size: 13px; font-weight: 500; color: var(--text-secondary); background: transparent; }
.nav-tab.active { background: rgba(99,130,255,0.15); color: var(--accent-blue); }
.nav-user { display: flex; align-items: center; gap: 12px; }
.logout-btn { background: transparent; color: var(--text-muted); font-size: 13px; padding: 6px 12px; border: 1px solid var(--border); border-radius: 8px; }
.logout-btn:hover { border-color: var(--risk-red); color: var(--risk-red); }

/* SCANNER OVERLAY */
.scanner-overlay { position: fixed; inset: 0; background: rgba(8,12,20,0.95); backdrop-filter: blur(10px); z-index: 999; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.scanner-circle { width: 120px; height: 120px; border: 3px solid transparent; border-top-color: var(--accent-blue); border-bottom-color: var(--accent-purple); border-radius: 50%; animation: scanSpin 1.5s linear infinite; display: flex; align-items: center; justify-content: center; margin-bottom: 30px; position: relative; }
.scanner-inner { width: 90px; height: 90px; background: rgba(99,130,255,0.1); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 32px;}
@keyframes scanSpin { to { transform: rotate(360deg); } }
.scan-log { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: var(--accent-green); height: 100px; overflow: hidden; width: 400px; text-align: left; background: rgba(0,0,0,0.5); padding: 16px; border-radius: 12px; border: 1px solid rgba(0,224,158,0.3); }
.scan-line { margin-bottom: 6px; animation: slideUp 0.3s forwards; }
@keyframes slideUp { from{opacity:0; transform:translateY(10px)} to{opacity:1; transform:translateY(0)} }
.scan-progress { width: 400px; height: 6px; background: var(--bg-glass); border-radius: 3px; margin-top: 20px; overflow: hidden; }
.scan-bar { height: 100%; background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan)); width: 0%; transition: width 0.3s; }

/* MAIN */
.main { padding: 88px 32px 40px; max-width: 1400px; margin: 0 auto; flex: 1; width: 100%; }

/* PANELS */
.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px; }
.stat-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 16px; padding: 20px; position: relative; overflow: hidden; }
.stat-val { font-size: 32px; font-weight: 800; margin: 8px 0; }
.stat-lbl { font-size: 12px; color: var(--text-muted); text-transform: uppercase; font-weight: 600; }

.split-layout { display: grid; grid-template-columns: 1fr 380px; gap: 24px; }
.panel { background: var(--bg-card); border: 1px solid var(--border); border-radius: 16px; padding: 20px; }
.panel-title { font-size: 16px; font-weight: 700; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; }
.graph-container { width: 100%; height: 500px; }
#graph-svg { width: 100%; height: 100%; }

/* SERVICE LIST */
.service-list { display: flex; flex-direction: column; gap: 12px; max-height: 500px; overflow-y: auto; padding-right: 8px; }
.service-item { display: flex; align-items: center; gap: 12px; padding: 12px; border: 1px solid var(--border); border-radius: 12px; background: rgba(255,255,255,0.02); cursor: pointer; position: relative; overflow: hidden; transition: var(--transition); }
.service-item:hover { border-color: var(--accent-blue); transform: translateX(2px); background: rgba(99,130,255,0.05); }
.service-item.disabled { opacity: 0.4; filter: grayscale(1); }
.svc-icon { width: 36px; height: 36px; border-radius: 8px; font-size: 20px; display: flex; align-items: center; justify-content: center; }
.svc-info { flex: 1; min-width: 0; }
.svc-name { font-weight: 600; font-size: 13px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.svc-meta { font-size: 11px; color: var(--text-muted); }
.svc-risk { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }

/* DETAIL DRAWER */
.detail-overlay { position: fixed; right: -500px; top: 64px; bottom: 0; width: 480px; background: var(--bg-secondary); border-left: 1px solid var(--border); transition: right 0.3s; z-index: 200; display: flex; flex-direction: column; }
.detail-overlay.open { right: 0; }
.detail-header { padding: 24px; border-bottom: 1px solid var(--border); }
.detail-body { padding: 24px; flex: 1; overflow-y: auto; }
.data-tag { display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 20px; font-size: 11px; margin: 4px 4px 4px 0; border: 1px solid var(--border); background: var(--bg-glass); }
.ai-box { background: rgba(99,130,255,0.05); border: 1px solid rgba(99,130,255,0.2); padding: 16px; border-radius: 12px; margin-bottom: 16px; }
.ai-box h4 { font-size: 12px; color: var(--accent-blue); text-transform: uppercase; margin-bottom: 8px; }
.btn-revoke { width: 100%; padding: 14px; background: rgba(255,77,109,0.1); color: var(--risk-red); border: 1px solid rgba(255,77,109,0.3); border-radius: 8px; font-weight: 600; margin-top: auto; cursor: pointer; }
.btn-revoke:hover { background: rgba(255,77,109,0.2); }

/* HISTORY TIMELINE */
.history-timeline { display: flex; flex-direction: column; gap: 12px; }
.history-item { background: var(--bg-glass); padding: 16px; border: 1px solid var(--border); border-radius: 12px; display: flex; gap: 16px; align-items: flex-start; }
.h-date { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--text-muted); width: 140px; flex-shrink: 0;}
.h-text { font-size: 13px; flex: 1;}

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-thumb { background: var(--border-bright); border-radius: 3px; }

.toast-container { position: fixed; bottom: 24px; right: 24px; z-index: 9999; display: flex; flex-direction: column; gap: 8px; pointer-events: none; }
.toast { background: var(--bg-secondary); border: 1px solid var(--border); padding: 14px 20px; border-radius: 12px; font-size: 13px; font-weight: 500; display: flex; align-items: center; gap: 10px; animation: slideInTip 0.3s forwards; box-shadow: 0 4px 20px rgba(0,0,0,0.5); pointer-events: auto; }
@keyframes slideInTip { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
</style>
</head>
<body>

<div class="wrapper">
  <!-- START SCREEN (AUTO LOGIN) -->
  <div id="auth-view" class="view active auth-container">
    <div class="auth-box">
      <div class="auth-logo">🦅</div>
      <h2 style="margin-bottom: 12px">Consent OS Core</h2>
      <p style="font-size:13px; color:var(--text-secondary); margin-bottom:24px">Автономная система перехвата и распределения цифровых следов устройства.</p>
      <input type="text" id="auth-name" placeholder="Введите имя владельца устройства" value="Асель Серикова">
      <button class="auth-btn" onclick="startSystem()">Запустить систему локально</button>
    </div>
  </div>

  <!-- APP INTERFACE -->
  <div id="app-view" class="view" style="display: none; height: 100%">
    <nav class="navbar">
      <div class="nav-logo">🦅 <span>Consent</span> OS</div>
      <div class="nav-tabs">
        <button class="nav-tab active" onclick="switchTab('dashboard')">Глобальный Радар</button>
        <button class="nav-tab" onclick="switchTab('history')">Журнал Очистки</button>
      </div>
      <div class="nav-user">
        <button class="auth-btn" style="padding: 6px 12px; width: auto; font-size: 12px; margin: 0; background: rgba(0,224,158,0.1); border: 1px solid rgba(0,224,158,0.3); color: #00e09e;" onclick="triggerScan()">🔄 Глубокое сканирование</button>
        <span id="user-display" style="font-weight:600; font-size:13px; margin:0 12px;"></span>
        <button class="logout-btn" onclick="hardReset()">Сбросить ОС</button>
      </div>
    </nav>

    <main class="main">
      <div id="tab-dashboard" class="tab-content active">
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-lbl">Перехвачено связей</div>
            <div class="stat-val" id="stat-total" style="color:var(--accent-blue)">0</div>
            <div style="position:absolute; right:20; top:20; opacity:0.1; font-size:40px">🔗</div>
          </div>
          <div class="stat-card">
            <div class="stat-lbl">Критические утечки</div>
            <div class="stat-val" id="stat-critical" style="color:var(--risk-red)">0</div>
            <div style="position:absolute; right:20; top:20; opacity:0.1; font-size:40px">🚨</div>
          </div>
          <div class="stat-card">
            <div class="stat-lbl">Блокировано трекеров</div>
            <div class="stat-val" id="stat-revoked" style="color:var(--accent-green)">0</div>
            <div style="position:absolute; right:20; top:20; opacity:0.1; font-size:40px">🛡️</div>
          </div>
        </div>

        <div class="split-layout">
          <div class="panel">
            <div class="panel-title">Топология Доступа <span style="font-size:12px; color:var(--text-muted); font-weight:400">Autodiscovery Mode: ON</span></div>
            <div class="graph-container">
              <svg id="graph-svg"></svg>
            </div>
          </div>
          
          <div class="panel" style="display:flex; flex-direction:column">
            <div class="panel-title">
              <span>Обнаруженные сервисы</span>
              <button class="logout-btn" style="border-color:rgba(255,77,109,0.3); color:var(--risk-red)" onclick="revokeAllHighRisk()">Kill All Red</button>
            </div>
            <input type="text" id="search-input" placeholder="Поиск по цифровому следу..." oninput="renderList()">
            <div class="service-list" id="service-list"></div>
          </div>
        </div>
      </div>

      <div id="tab-history" class="tab-content" style="display: none;">
        <div class="panel">
          <div class="panel-title">Системный Журнал Действий (Local Event Log)</div>
          <div class="history-timeline" id="history-list"></div>
        </div>
      </div>
    </main>
  </div>
</div>

<!-- SCANNER OVERLAY -->
<div id="scanner-overlay" class="scanner-overlay" style="display: none;">
  <div class="scanner-circle">
    <div class="scanner-inner">🦅</div>
  </div>
  <h2 style="margin-bottom:20px; font-weight:600">Автономное Сканирование Устройства</h2>
  <div class="scan-log" id="scan-log"></div>
  <div class="scan-progress"><div class="scan-bar" id="scan-bar"></div></div>
</div>

<!-- DETAIL SIDEBAR -->
<div class="detail-overlay" id="detail-overlay">
  <div class="detail-header" style="display:flex; justify-content:space-between; align-items:flex-start">
    <div style="display:flex; align-items:center; gap:12px">
      <div id="det-icon" style="font-size:32px; background:var(--bg-glass); padding:8px; border-radius:12px"></div>
      <div>
        <h2 id="det-name">Название</h2>
        <div id="det-cat" style="color:var(--text-muted); font-size:12px; margin-top:4px">Категория</div>
      </div>
    </div>
    <button onclick="document.getElementById('detail-overlay').classList.remove('open')" style="background:transparent; color:#fff; font-size:20px">✕</button>
  </div>
  <div class="detail-body">
    <div style="margin-bottom:20px" id="det-tags"></div>
    
    <div class="ai-box">
      <h4 style="color:var(--text-primary); display:flex; align-items:center; justify-content:space-between">
        <span>🤖 Локальный AI-Аудит</span>
        <span id="det-score" style="font-size:18px; font-weight:800"></span>
      </h4>
      <div id="det-audit" style="font-size:13px; line-height:1.6; color:var(--text-secondary); margin-top:12px"></div>
    </div>
    
    <div style="font-size:13px; margin-bottom:20px;">
      <div style="margin-bottom:8px"><b>Обнаружено через:</b> <span id="det-source" style="color:var(--accent-blue)"></span></div>
      <div style="margin-bottom:8px"><b>Третьи лица:</b> <span id="det-third"></span></div>
    </div>

    <button id="det-revoke" class="btn-revoke">Блокировать доступ (Revoke)</button>
  </div>
</div>

<div class="toast-container" id="toast-container"></div>

<script>
// =====================================
// AUTONOMOUS LOCAL DATABASE MOCK
// =====================================
const PRE_DISCOVERED_SERVICES = [
  { id: '1', name: 'Google Workspace', cat: 'Экосистема', icon: '🌐', color: '#f7c948',
    data: ['Геолокация', 'Почта', 'Контакты', 'История поиска'], req: 'OAuth Token (Chrome)',
    score: 65, thirdParty: 'Да (AdSense)', 
    audit: '<b>Оценка: Стандартная.</b> Обширный сбор данных, но используется прозрачная архитектура контроля. Найдена активная сессия в браузере. Данные перекрёстно монетизируются через рекламную сеть Google.'},
  
  { id: '2', name: 'Kaspi.kz', cat: 'Финансы', icon: '💳', color: '#ff4d6d',
    data: ['Транзакции', 'Локация терминалов', 'Документы'], req: 'Cookie & LocalStorage',
    score: 82, thirdParty: 'Внутренняя экосистема',
    audit: '<b>Оценка: Требует внимания.</b> Зафиксирована привязка device_id к финансовому профилю. Приложение собирает историю покупок на сторонних сайтах (через виджеты оплаты). Выявлена передача данных партнерам Kaspi Travel.'},
  
  { id: '3', name: 'Instagram / Meta', cat: 'Соцсети', icon: '📸', color: '#9b5de5',
    data: ['Камера', 'Микрофон', 'Переписки', 'Биометрия'], req: 'Meta Pixel Tag',
    score: 95, thirdParty: 'Да (Брокеры данных)',
    audit: '<b>Оценка: КРИТИЧЕСКАЯ УТЕЧКА.</b> Обнаружен Meta Pixel на 4 независимых сайтах. Фоновый сбор данных о перемещениях. AI выявил пункт пользовательского соглашения, разрешающий продажу метаданных аудиозаписей сторонним алгоритмическим фондам.'},
  
  { id: '4', name: 'eGov.kz', cat: 'Государство', icon: '🏛', color: '#6382ff',
    data: ['ИИН', 'Семья', 'Налоги'], req: 'Сессия ЭЦП',
    score: 30, thirdParty: 'Нет (Только гос. реестры)',
    audit: '<b>Оценка: Безопасно.</b> Данные хранятся в защищенном контуре НИТ. Сессия найдена через остаточные куки-файлы в браузере. Выявлены перекрестные запросы из сервисов МВД и МЗ РК без явного нарушения логики.'},
  
  { id: '5', name: 'NumPro (Калькулятор)', cat: 'Утилиты', icon: '🧮', color: '#ff7043',
    data: ['Микрофон', 'Контакты', 'Буфер обмена'], req: 'Background Service',
    score: 99, thirdParty: 'Да (Неизвестные серверы)',
    audit: '<b>Оценка: ВРЕДОНОСНОЕ ПО (MALWARE).</b> Система зафиксировала аномалию: приложению-калькулятору назначен доступ к микрофону и буферу обмена на устройстве. Найдены сетевые запросы к китайским серверам. Немедленно заблокируйте.'},
    
  { id: '6', name: 'Яндекс.Go', cat: 'Транспорт', icon: '🚖', color: '#f7c948',
    data: ['Точная локация', 'Платежи', 'Поведение'], req: 'App API Keys',
    score: 75, thirdParty: 'Да (Рекламная сеть Яндекса)',
    audit: '<b>Оценка: Повышенный риск.</b> Локация отслеживается даже в фоновом режиме (приложение закрыто). Обнаружены запросы к трекерам AppMetrica. Рекомендуется перейти в режим "Локация только при использовании".'}
];

// =====================================
// STATE MANAGEMENT & LOCAL STORAGE
// =====================================
let sysState = {
  user: null,
  services: [],
  history: []
};

// =====================================
// INIT & CORE LOGIC
// =====================================
window.onload = () => {
  const savedUser = localStorage.getItem('consent_os_user');
  if (savedUser) {
    sysState.user = savedUser;
    loadState();
    bootApp();
  }
};

function startSystem() {
  const name = document.getElementById('auth-name').value.trim();
  if(!name) return;
  sysState.user = name;
  localStorage.setItem('consent_os_user', name);
  
  // Wipe old data for fresh demo 
  sysState.services = [];
  sysState.history = [{ t: Date.now(), msg: 'Система инициализирована', icon: '🚀' }];
  saveState();
  
  document.getElementById('auth-view').classList.remove('active');
  document.getElementById('app-view').classList.add('active');
  document.getElementById('user-display').textContent = name;
  
  // Auto trigger scan on first login
  setTimeout(() => triggerScan(), 300);
}

function bootApp() {
  document.getElementById('auth-view').classList.remove('active');
  document.getElementById('app-view').classList.add('active');
  document.getElementById('user-display').textContent = sysState.user;
  updateUI();
}

function hardReset() {
  localStorage.clear();
  location.reload();
}

// =====================================
// AUTONOMOUS SCANNER SIMULATION
// =====================================
async function triggerScan() {
  document.getElementById('scanner-overlay').style.display = 'flex';
  const logBox = document.getElementById('scan-log');
  const bar = document.getElementById('scan-bar');
  logBox.innerHTML = '';
  bar.style.width = '0%';
  
  const steps = [
    { m: 'Запуск Local AI Engine...', d: 400 },
    { m: 'Сканирование Cookie-сессий браузера...', d: 600 },
    { m: 'Обнаружено 3 активных OAuth токена.', d: 500 },
    { m: 'Анализ фоновых процессов устройства...', d: 800 },
    { m: 'Извлечение политик конфиденциальности (NLP Parsing)...', d: 1000 },
    { m: 'Построение графа связей завершено. Угроз: 2', d: 500 }
  ];

  for (let i = 0; i < steps.length; i++) {
    await new Promise(r => setTimeout(r, steps[i].d));
    const div = document.createElement('div');
    div.className = 'scan-line';
    div.textContent = `> ${steps[i].m}`;
    logBox.appendChild(div);
    logBox.scrollTop = logBox.scrollHeight;
    bar.style.width = `${((i+1)/steps.length)*100}%`;
  }
  
  await new Promise(r => setTimeout(r, 600));
  document.getElementById('scanner-overlay').style.display = 'none';
  
  // Populate Data autonomously
  sysState.services = JSON.parse(JSON.stringify(PRE_DISCOVERED_SERVICES)).map(s => {
    s.status = 'active'; return s;
  });
  
  sysState.history.unshift({ t: Date.now(), msg: `Сканирование завершено. Автоматически перехвачено ${sysState.services.length} сервисов.`, icon: '🦅' });
  saveState();
  updateUI();
  showToast('Сканирование завершено', 'success');
}

// =====================================
// UI UPDATES
// =====================================
function switchTab(tab) {
  document.querySelectorAll('.tab-content').forEach(e => e.style.display = 'none');
  document.querySelectorAll('.nav-tab').forEach(e => e.classList.remove('active'));
  document.getElementById(`tab-${tab}`).style.display = 'block';
  event.target.classList.add('active');
  if(tab === 'dashboard') initD3Graph();
}

function updateUI() {
  renderStats();
  renderList();
  renderHistory();
  initD3Graph();
}

function renderStats() {
  const active = sysState.services.filter(s => s.status === 'active');
  document.getElementById('stat-total').textContent = sysState.services.length;
  document.getElementById('stat-critical').textContent = active.filter(s => s.score > 80).length;
  document.getElementById('stat-revoked').textContent = sysState.services.filter(s => s.status === 'revoked').length;
}

function getRiskCol(score, status) {
  if (status === 'revoked') return 'var(--text-muted)';
  if (score > 80) return 'var(--risk-red)';
  if (score > 50) return 'var(--risk-yellow)';
  return 'var(--risk-green)';
}

function renderList() {
  const q = (document.getElementById('search-input').value || '').toLowerCase();
  const list = document.getElementById('service-list');
  list.innerHTML = sysState.services
    .filter(s => s.name.toLowerCase().includes(q))
    .sort((a,b) => b.score - a.score)
    .map(s => `
      <div class="service-item ${s.status === 'revoked' ? 'disabled' : ''}" onclick="openDetail('${s.id}')">
        <div class="svc-icon" style="color:${s.color}">${s.icon}</div>
        <div class="svc-info">
          <div class="svc-name">${s.name}</div>
          <div class="svc-meta">${s.cat} · Обнаружено через: ${s.req}</div>
        </div>
        <div class="svc-risk" style="background:${getRiskCol(s.score, s.status)}"></div>
      </div>
    `).join('');
}

function renderHistory() {
  const list = document.getElementById('history-list');
  list.innerHTML = sysState.history.map(h => `
    <div class="history-item">
      <div class="h-date">${new Date(h.t).toLocaleString('ru-RU')}</div>
      <div style="font-size:18px">${h.icon}</div>
      <div class="h-text">${h.msg}</div>
    </div>
  `).join('');
}

// =====================================
// DETAIL PANEL & REVOCATION
// =====================================
function openDetail(id) {
  const svc = sysState.services.find(s => s.id === id);
  if(!svc) return;
  
  document.getElementById('det-icon').textContent = svc.icon;
  document.getElementById('det-icon').style.color = svc.color;
  document.getElementById('det-name').textContent = svc.name;
  document.getElementById('det-cat').textContent = svc.cat;
  
  document.getElementById('det-tags').innerHTML = svc.data.map(d => `<span class="data-tag">${d}</span>`).join('');
  
  const rc = getRiskCol(svc.score, svc.status);
  document.getElementById('det-score').textContent = svc.status === 'revoked' ? 'ЗАБЛОКИРОВАН' : `${svc.score}/100`;
  document.getElementById('det-score').style.color = rc;
  
  document.getElementById('det-audit').innerHTML = svc.audit;
  document.getElementById('det-source').textContent = svc.req;
  document.getElementById('det-third').textContent = svc.thirdParty;
  
  const btn = document.getElementById('det-revoke');
  if (svc.status === 'active') {
    btn.style.display = 'block';
    btn.textContent = `Блокировать доступ API немедленно`;
    btn.onclick = () => revoke(id);
  } else {
    btn.style.display = 'none';
  }
  
  document.getElementById('detail-overlay').classList.add('open');
}

function revoke(id) {
  const svc = sysState.services.find(s => s.id === id);
  if(!svc) return;
  svc.status = 'revoked';
  sysState.history.unshift({ t: Date.now(), msg: `Экстренная блокировка: Доступ для ${svc.name} разорван на уровне системы.`, icon: '🛡️' });
  saveState();
  updateUI();
  document.getElementById('detail-overlay').classList.remove('open');
  showToast(`${svc.name} отключен`, 'success');
}

function revokeAllHighRisk() {
  let count = 0;
  sysState.services.forEach(s => {
    if (s.score > 80 && s.status === 'active') {
      s.status = 'revoked';
      count++;
    }
  });
  if(count > 0) {
    sysState.history.unshift({ t: Date.now(), msg: `Массовая блокировка: ${count} критических сервисов изолированы.`, icon: '🚨' });
    saveState(); updateUI();
    showToast(`Заблокировано ${count} угроз`, 'success');
  } else {
    showToast('Критических угроз не найдено', 'info');
  }
}

// =====================================
// D3 GRAPH
// =====================================
let graphSim = null;
function initD3Graph() {
  const svg = d3.select('#graph-svg');
  const container = document.getElementById('graph-svg');
  if(!container.clientWidth) return;
  
  svg.selectAll('*').remove();
  if(graphSim) graphSim.stop();

  const nodes = [{ id: 'core', name: 'Consent OS Node', r: 30, color: 'var(--accent-blue)' }];
  const links = [];
  
  sysState.services.forEach(s => {
    nodes.push({ id: s.id, name: s.name, r: 20, color: getRiskCol(s.score, s.status), revoked: s.status === 'revoked' });
    links.push({ source: 'core', target: s.id });
  });

  graphSim = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id(d=>d.id).distance(140))
    .force('charge', d3.forceManyBody().strength(-300))
    .force('center', d3.forceCenter(container.clientWidth/2, container.clientHeight/2));

  const link = svg.append('g').selectAll('line').data(links).enter().append('line')
    .attr('stroke', d => {
      const tg = sysState.services.find(s=>s.id === d.target.id);
      return tg && tg.status === 'revoked' ? 'rgba(255,255,255,0.05)' : 'rgba(255,255,255,0.15)';
    })
    .attr('stroke-dasharray', d => {
      const tg = sysState.services.find(s=>s.id === d.target.id);
      return tg && tg.status === 'revoked' ? '5,5' : 'none';
    })
    .attr('stroke-width', 2);

  const node = svg.append('g').selectAll('g').data(nodes).enter().append('g')
    .style('cursor', d=>d.id==='core'?'default':'pointer')
    .on('click', (e, d) => { if (d.id !== 'core') openDetail(d.id); })
    .call(d3.drag()
      .on('start', (e,d) => { if(!e.active) graphSim.alphaTarget(0.3).restart(); d.fx=d.x; d.fy=d.y; })
      .on('drag', (e,d) => { d.fx=e.x; d.fy=e.y; })
      .on('end', (e,d) => { if(!e.active) graphSim.alphaTarget(0); d.fx=null; d.fy=null; })
    );

  node.append('circle')
    .attr('r', d => d.r)
    .attr('fill', d => d.revoked ? 'rgba(255,255,255,0.02)' : 'rgba(255,255,255,0.08)')
    .attr('stroke', d => d.color)
    .attr('stroke-width', 2);

  node.append('text').attr('dy', d=>d.r + 14).attr('text-anchor', 'middle')
    .attr('fill', d=>d.revoked?'var(--text-muted)':'#fff')
    .attr('font-size', '11px').attr('font-weight','500')
    .text(d => d.name);
    
  node.filter(d=>d.id==='core').append('text').attr('dy',5).attr('text-anchor','middle').attr('font-size','20px').text('🦅');

  graphSim.on('tick', () => {
    link.attr('x1', d=>d.source.x).attr('y1', d=>d.source.y).attr('x2', d=>d.target.x).attr('y2', d=>d.target.y);
    node.attr('transform', d=>`translate(${d.x},${d.y})`);
  });
}

// =====================================
// UTILS
// =====================================
function saveState() {
  localStorage.setItem('consent_os_data', JSON.stringify({ svcs: sysState.services, hist: sysState.history }));
}
function loadState() {
  const d = localStorage.getItem('consent_os_data');
  if(d) { const parsed = JSON.parse(d); sysState.services = parsed.svcs; sysState.history = parsed.hist; }
}

function showToast(msg, type='info') {
  const el = document.createElement('div');
  el.className = 'toast';
  el.style.borderLeft = `4px solid ${type==='success'?'var(--accent-green)':'var(--accent-blue)'}`;
  el.innerHTML = `${type==='success'?'✅':'ℹ️'} ${msg}`;
  document.getElementById('toast-container').appendChild(el);
  setTimeout(()=>el.remove(), 4000);
}
</script>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as file:
    file.write(html_content)

print("Autonomous App Generated.")
