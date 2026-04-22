// Consent OS Extension - Background Service Worker

const API_URL = "http://127.0.0.1:8000/api/track-consent";
const SYNC_API_URL = "http://127.0.0.1:8000/api/sync-old-consents";

let scanningTabId = null;

chrome.runtime.onInstalled.addListener(() => {
  chrome.notifications.create("startup", {
    type: "basic",
    iconUrl: "icon.png",
    title: "Consent OS Scanner",
    message: "Scanner Active"
  });
});

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === "START_OLD_CONSENTS_SCAN") {
    chrome.notifications.create({
      type: "basic", iconUrl: "icon.png",
      title: "Consent OS", message: "Инжект в Google Connections..."
    });

    chrome.tabs.create({ url: "https://myaccount.google.com/connections", active: false }, (tab) => {
      scanningTabId = tab.id;
      setTimeout(() => {
        chrome.scripting.executeScript({
          target: { tabId: tab.id },
          files: ["content_scanner.js"]
        });
      }, 3000);
    });
  }

  if (msg.type === "SCAN_PROGRESS") {
    // Relay to popup and store current count
    chrome.storage.local.set({ scanRunning: true, scanCount: msg.count });
    chrome.runtime.sendMessage({ type: "SCAN_PROGRESS", count: msg.count }).catch(() => {});
  }

  if (msg.type === "GOOGLE_CONNECTIONS_RESULT") {
    if (scanningTabId) {
      chrome.tabs.remove(scanningTabId);
      scanningTabId = null;
    }

    if (msg.success && msg.apps.length > 0) {
      chrome.runtime.sendMessage({ type: "SCAN_DONE", count: msg.apps.length }).catch(() => {});

      chrome.storage.local.get(["consentOsToken"], async (res) => {
        if (!res.consentOsToken) return;
        try {
          const resp = await fetch(SYNC_API_URL, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "Authorization": "Bearer " + res.consentOsToken
            },
            body: JSON.stringify(msg.apps)
          });
          if (resp.ok) {
            chrome.notifications.create({
              type: "basic", iconUrl: "icon.png",
              title: "Consent OS", message: `✅ ${msg.apps.length} сервисов успешно синхронизировано!`
            });
            chrome.storage.local.set({ scanRunning: false, scanCount: 0 });
          }
        } catch (e) {}
      });
    } else {
      chrome.runtime.sendMessage({ type: "SCAN_FAILED" }).catch(() => {});
      chrome.storage.local.set({ scanRunning: false, scanCount: 0 });
      chrome.notifications.create({
        type: "basic", iconUrl: "icon.png",
        title: "Consent OS", message: msg.error || "Скан не нашёл приложений."
      });
    }
  }

  if (msg.type === "START_REAL_REVOKE") {
    let revokeUrl = "";
    if (msg.externalId) {
       revokeUrl = `https://myaccount.google.com/connections/app/${msg.externalId}`;
    } else if (msg.searchName) {
       revokeUrl = `https://myaccount.google.com/connections?consent_os_target=${encodeURIComponent(msg.searchName)}`;
    } else {
       return;
    }

    chrome.tabs.create({ url: revokeUrl, active: true }, (tab) => {
      chrome.notifications.create({
        type: "basic", iconUrl: "icon.png",
        title: "Consent OS", message: "Робот-ликвидатор запущен. Пожалуйста, не закрывайте вкладку."
      });
      
      // Explicitly clear old states before setting new ones
      chrome.storage.local.remove(['consentOsTarget', 'consentOsTargetId'], () => {
          chrome.storage.local.set({ 
              consentOsTarget: msg.searchName || "", 
              consentOsTargetId: msg.externalId || "" 
          }, () => {
              // Give page time to load its dynamic content
              setTimeout(() => {
                chrome.scripting.executeScript({
                  target: { tabId: tab.id },
                  files: ["auto_revoker.js"]
                });
              }, 4000); 
          });
      });
    });
  }

  if (msg.type === "REVOKE_COMPLETED") {
    // 1. Notify Dashboard tab if it's open
    chrome.tabs.query({ url: ["http://localhost:5173/*", "http://127.0.0.1:5173/*"] }, (tabs) => {
      tabs.forEach(tab => {
        chrome.tabs.sendMessage(tab.id, { 
          type: "REVOKE_VERIFIED_BY_EXTENSION", 
          externalId: msg.externalId,
          searchName: msg.searchName
        });
      });
    });

    // 2. Show internal notification
    chrome.notifications.create({
      type: "basic", iconUrl: "icon.png",
      title: "Consent OS", message: "🎉 Приложение официально отвязано от Google Account!"
    });

    // 3. Close the Google connections tab
    if (sender.tab) {
        chrome.tabs.remove(sender.tab.id);
    }
  }

  if (msg.type === "NAVIGATING_TO_DETAILS") {
    // The content script triggered a hard navigation to the app's detail page.
    // It will die. We must re-inject it after a short delay.
    chrome.storage.local.set({ 
        consentOsTargetId: "placeholder_to_force_details_flow", 
        consentOsTarget: msg.searchName 
    }, () => {
        setTimeout(() => {
            if (sender.tab) {
                chrome.scripting.executeScript({
                    target: { tabId: sender.tab.id },
                    files: ["auto_revoker.js"]
                });
            }
        }, 3000);
    });
  }
});

chrome.webNavigation.onBeforeNavigate.addListener(async (details) => {
  if (details.frameId !== 0) return;
  let url;
  try { url = new URL(details.url); } catch (e) { return; }
  if (url.hostname === "localhost" || url.hostname === "127.0.0.1") return;
  if (url.protocol === "chrome:" || url.protocol === "chrome-extension:") return;

  const params = Object.fromEntries(url.searchParams.entries());
  const isOAuthPath = url.pathname.includes("oauth") || url.pathname.includes("/authorize") || url.pathname.includes("/auth/") || url.pathname.includes("/connect/");
  const hasOAuthParams = (params.client_id || params.response_type) && params.scope;

  if (!isOAuthPath && !hasOAuthParams) return;
  if (!params.scope) return;

  let domain = "";
  const isGoogleClientId = (s) => s && (s.includes("apps.googleusercontent.com") || /^\d{10,}-/.test(s));

  if (params.client_id && !isGoogleClientId(params.client_id)) domain = params.client_id;
  if ((!domain || isGoogleClientId(domain)) && params.redirect_uri) {
    try {
      const ru = new URL(params.redirect_uri);
      if (ru.hostname !== "localhost" && ru.hostname !== "127.0.0.1") domain = ru.hostname;
    } catch (e) {}
  }
  if (!domain || isGoogleClientId(domain)) domain = url.hostname;

  domain = domain.replace(/^www\./, "").split(":")[0].trim();
  if (domain.includes("googleusercontent")) domain = url.hostname;
  if (!domain) return;

  chrome.notifications.create({
    type: "basic", iconUrl: "icon.png",
    title: "🚨 OAuth перехват!", message: `Сервис: ${domain}`
  });

  chrome.storage.local.get(["consentOsToken"], async (res) => {
    if (!res.consentOsToken) return;
    try {
      const resp = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": "Bearer " + res.consentOsToken },
        body: JSON.stringify({ domain, scopes: params.scope })
      });
      if (resp.ok) {
        chrome.notifications.create({
          type: "basic", iconUrl: "icon.png",
          title: "✅ Анализ готов", message: `${domain} обработан.`
        });
      }
    } catch (err) {}
  });
});
