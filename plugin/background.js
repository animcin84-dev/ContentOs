// ============================================================
// Consent OS — Background Service Worker
// Хранит данные по каждому сайту, обновляет бейдж
// ============================================================

// ⬇️ ВСТАВЬТЕ ВАШ OPENAI API KEY СЮДА:
const OPENAI_API_KEY = 'YOUR_OPENAI_API_KEY_HERE';

// Aggregated tracker registry: { domain -> tracker_info }
let trackerRegistry = {};

// Site visit log: { siteDomain -> { domain, title, trackers[], lastSeen } }
let siteLog = {};

// Load from storage on startup
chrome.storage.local.get(['trackerRegistry', 'siteLog'], (data) => {
  if (data.trackerRegistry) trackerRegistry = data.trackerRegistry;
  if (data.siteLog) siteLog = data.siteLog;
});

function save() {
  chrome.storage.local.set({ trackerRegistry, siteLog });
}

// Listen for messages from content scripts
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === 'PAGE_SCAN') {
    const { url, domain, title, trackers, ts } = msg.payload;

    // Update site log
    siteLog[domain] = {
      domain,
      title,
      url,
      lastSeen: ts,
      firstSeen: siteLog[domain]?.firstSeen || ts,
      trackers: trackers.map(t => t.domain),
      trackerCount: trackers.length
    };

    // Update global tracker registry
    for (const t of trackers) {
      if (!trackerRegistry[t.domain]) {
        trackerRegistry[t.domain] = { ...t, firstSeen: ts, sites: [] };
      }
      if (!trackerRegistry[t.domain].sites.includes(domain)) {
        trackerRegistry[t.domain].sites.push(domain);
      }
      trackerRegistry[t.domain].lastSeen = ts;
    }

    save();

    // Update badge on tab
    if (sender.tab?.id) {
      const count = trackers.length;
      chrome.action.setBadgeText({ text: count > 0 ? String(count) : '', tabId: sender.tab.id });
      chrome.action.setBadgeBackgroundColor({
        color: count > 5 ? '#ff4d6d' : count > 2 ? '#f7c948' : '#00e09e',
        tabId: sender.tab.id
      });
    }
    sendResponse({ ok: true });
  }

  if (msg.type === 'GET_ALL_DATA') {
    sendResponse({ trackerRegistry, siteLog });
  }

  if (msg.type === 'GET_TAB_DATA') {
    sendResponse({
      site: siteLog[msg.domain] || null,
      trackers: (siteLog[msg.domain]?.trackers || []).map(d => trackerRegistry[d]).filter(Boolean)
    });
  }

  if (msg.type === 'AI_ANALYZE') {
    // Call OpenAI from background (no CORS issues here)
    const { trackers, site } = msg;
    const trackNames = trackers.map(t => `${t.name} (риск ${t.risk}/100, данные: ${(t.data||[]).join(', ')})`).join('\n');
    
    fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${OPENAI_API_KEY}`
      },
      body: JSON.stringify({
        model: 'gpt-4o-mini',
        max_tokens: 600,
        messages: [
          { role: 'system', content: 'Ты эксперт по цифровой приватности. Отвечай строго на русском языке. Будь конкретным и кратким.' },
          { role: 'user', content: `Сайт: ${site}\nОбнаруженные трекеры:\n${trackNames}\n\nДай:\n1. Общий риск (0-100)\n2. Главные угрозы (2-3 пункта)\n3. Рекомендации пользователю (2 пункта)\nОтвечай структурированно.` }
        ]
      })
    })
    .then(r => r.json())
    .then(data => {
      sendResponse({ ok: true, analysis: data.choices?.[0]?.message?.content || 'Ошибка ответа' });
    })
    .catch(e => sendResponse({ ok: false, error: e.message }));

    return true; // async response
  }

  if (msg.type === 'REVOKE') {
    // Mark tracker as revoked in storage
    const { domain } = msg;
    if (trackerRegistry[domain]) {
      trackerRegistry[domain].revoked = true;
      trackerRegistry[domain].revokedAt = Date.now();
    }
    save();
    sendResponse({ ok: true });
  }

  return true;
});
