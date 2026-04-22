document.addEventListener('DOMContentLoaded', () => {
  const tokenInput = document.getElementById('token');
  const saveBtn = document.getElementById('saveBtn');
  const syncBtn = document.getElementById('syncBtn');
  const scanBtn = document.getElementById('scanBtn');
  const statusDiv = document.getElementById('status');
  const scanProgress = document.getElementById('scan-progress');
  const foundCount = document.getElementById('found-count');
  const progressFill = document.getElementById('progress-fill');
  const progressPhase = document.getElementById('progress-phase');

  // Load existing token
  chrome.storage.local.get(['consentOsToken'], (result) => {
    if (result.consentOsToken) {
      tokenInput.value = result.consentOsToken;
      setStatus('✅ Токен загружен', 'green');
    } else {
      setStatus('⚠️ Токен не задан — нажми Синхронизировать', 'orange');
    }
  });

  // Load history
  chrome.storage.local.get(['consentHistory'], (result) => {
    if (result.consentHistory && result.consentHistory.length > 0) {
      const list = document.getElementById('historyList');
      list.innerHTML = '';
      result.consentHistory.forEach(item => {
        const div = document.createElement('div');
        div.className = 'h-item';
        const timeStr = new Date(item.time).toLocaleTimeString('ru-RU', {hour: '2-digit', minute:'2-digit'});
        div.innerHTML = `
          <span class="h-time">${timeStr}</span>
          <span class="h-domain">${item.domain}</span>
          <div class="h-scopes">${item.scopes}</div>
        `;
        list.appendChild(div);
      });
    }
  });

  // Check if scan is already running on popup open
  chrome.storage.local.get(['scanRunning', 'scanCount'], (res) => {
    if (res.scanRunning) {
      startProgressUI();
      updateProgress(res.scanCount || 0, 'Сканирование продолжается...');
    }
  });

  // Listen for live messages from background.js
  chrome.runtime.onMessage.addListener((msg) => {
    if (msg.type === 'SCAN_PROGRESS') {
      startProgressUI();
      const count = msg.count || 0;
      // Animate bar: estimate progress as a "loading" animation since we don't know total
      const cappedPct = Math.min(10 + count * 2, 85);
      updateProgress(count, `Обнаружено приложений: ${count}`, cappedPct);
    }

    if (msg.type === 'SCAN_DONE') {
      updateProgress(msg.count, `✅ Готово! Найдено ${msg.count} сервисов. Отправляем в дашборд...`, 95);
      setTimeout(() => {
        updateProgress(msg.count, '🎉 Синхронизировано с Consent OS!', 100);
        setTimeout(() => stopProgressUI(), 3000);
      }, 1500);
    }

    if (msg.type === 'SCAN_FAILED') {
      updateProgress(0, '❌ Не удалось обнаружить сервисы. Убедитесь, что вы залогинены в Google.', 0);
      setTimeout(() => stopProgressUI(), 4000);
    }
  });

  // Save manual token
  saveBtn.addEventListener('click', () => {
    const token = tokenInput.value.trim();
    if (!token) { setStatus('❌ Введи токен!', 'red'); return; }
    chrome.storage.local.set({ consentOsToken: token }, () => {
      setStatus('✅ Токен сохранён!', 'green');
    });
  });

  // Auto-sync token from Consent OS dashboard tab
  syncBtn.addEventListener('click', () => {
    chrome.tabs.query({}, (tabs) => {
      const dashTab = tabs.find(t =>
        t.url && (t.url.includes('localhost:5173') || t.url.includes('localhost:3000') || t.url.includes('localhost:8000'))
      );

      if (!dashTab) {
        setStatus('❌ Открой дашборд Consent OS в браузере!', 'red');
        return;
      }

      chrome.scripting.executeScript({
        target: { tabId: dashTab.id },
        func: () => localStorage.getItem('token'),
      }, (results) => {
        if (chrome.runtime.lastError) {
          setStatus('❌ Ошибка: ' + chrome.runtime.lastError.message, 'red');
          return;
        }
        const token = results?.[0]?.result;
        if (token) {
          tokenInput.value = token;
          chrome.storage.local.set({ consentOsToken: token }, () => {
            setStatus('✅ Токен синхронизирован!', 'green');
          });
        } else {
          setStatus('❌ Токен не найден в дашборде.', 'red');
        }
      });
    });
  });

  // Start Scan
  if (scanBtn) {
    scanBtn.addEventListener('click', () => {
      chrome.runtime.sendMessage({ type: "START_OLD_CONSENTS_SCAN" });
      startProgressUI();
      updateProgress(0, 'Открываем страницу Google Connections...');
      setStatus('', '');
    });
  }

  // ── Helpers ────────────────────────────────────────────────────────────────
  function startProgressUI() {
    scanProgress.classList.add('visible');
    scanBtn.disabled = true;
  }

  function stopProgressUI() {
    scanProgress.classList.remove('visible');
    scanBtn.disabled = false;
    chrome.storage.local.set({ scanRunning: false, scanCount: 0 });
  }

  function updateProgress(count, phase, pct) {
    foundCount.textContent = `${count} сервисов`;
    progressPhase.textContent = phase;
    if (pct !== undefined) {
      progressFill.style.width = `${pct}%`;
    }
  }

  function setStatus(msg, color) {
    statusDiv.textContent = msg;
    statusDiv.style.color = color === 'green' ? '#10b981' : color === 'orange' ? '#f59e0b' : '#ef4444';
    if (msg) setTimeout(() => { statusDiv.textContent = ''; }, 5000);
  }
});
