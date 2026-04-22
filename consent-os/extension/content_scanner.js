// Consent OS — Google Connections Page Scanner
// Injected into https://myaccount.google.com/connections

(function () {
  const MAX_WAIT_MS = 25000;
  const start = Date.now();

  function extractApps() {
    const results = [];
    const seen = new Set();

    function addApp(name, externalId) {
      const cleanName = name.trim();
      if (cleanName.length > 1 && cleanName.length < 120 && !seen.has(cleanName)) {
        seen.add(cleanName);
        results.push({
          name: cleanName,
          external_id: externalId || null,
          scopes: ["google_account_access"]
        });
      }
    }

    // Strategy 1: Find links pointing to specific app pages (best case — gives us external IDs)
    document.querySelectorAll('a[href*="/connections/app/"]').forEach(a => {
      const href = a.getAttribute('href');
      const match = href.match(/\/app\/([a-zA-Z0-9_\-]+)/);
      const externalId = match ? match[1] : null;

      // Try to get name from heading inside the link element
      const nameEl = a.querySelector('h3, h2, [role="heading"], span');
      const name = nameEl ? nameEl.textContent : a.textContent;
      addApp(name, externalId);
    });

    // Strategy 2: h3/h2 inside list items (Google's standard structure)
    if (results.length === 0) {
      const candidateSelectors = [
        "li h3", "li h2",
        "[data-view-action-button] h3",
        "c-wiz h3", "c-wiz h2",
        "[jsname] h3", "[jsname] h2",
        ".Qq6Gz", ".klLJHe", ".Y7eXSb",
        "[role='listitem'] [role='heading']",
        "[role='list'] [role='heading']",
        "div[tabindex='0'] h3",
      ];
      for (const sel of candidateSelectors) {
        try {
          document.querySelectorAll(sel).forEach(el => {
            addApp(el.textContent.trim(), null);
          });
        } catch (_) {}
      }
    }

    // Strategy 3: img alt/aria-label (app logos with names)
    if (results.length === 0) {
      document.querySelectorAll("img[alt], img[aria-label]").forEach(img => {
        const name = (img.getAttribute("alt") || img.getAttribute("aria-label") || "").trim();
        if (!/google/i.test(name)) addApp(name, null);
      });
    }

    // Strategy 4: Last resort — walk all list-like containers
    if (results.length === 0) {
      const lists = document.querySelectorAll("[role='list'], [role='listbox'], ul, ol");
      lists.forEach(list => {
        list.querySelectorAll("[role='listitem'], li").forEach(item => {
          const text = item.firstElementChild?.textContent?.trim() || item.textContent.split("\n")[0].trim();
          addApp(text, null);
        });
      });
    }

    return results;
  }

  // Progress reporting: how many we found so far
  function reportProgress(count) {
    chrome.runtime.sendMessage({ type: "SCAN_PROGRESS", count });
  }

  let prevCount = 0;

  function poll() {
    const apps = extractApps();
    const elapsed = Date.now() - start;

    // Report progress if count changed
    if (apps.length !== prevCount) {
      prevCount = apps.length;
      reportProgress(apps.length);
    }

    if (apps.length > 0 && elapsed >= 4000) {
      // Wait at least 4 seconds to ensure SPA fully renders all items
      chrome.runtime.sendMessage({
        type: "GOOGLE_CONNECTIONS_RESULT",
        apps,
        success: true
      });
    } else if (elapsed >= MAX_WAIT_MS) {
      if (apps.length > 0) {
        chrome.runtime.sendMessage({ type: "GOOGLE_CONNECTIONS_RESULT", apps, success: true });
      } else {
        chrome.runtime.sendMessage({
          type: "GOOGLE_CONNECTIONS_RESULT",
          apps: [],
          success: false,
          error: "Не удалось найти приложения. Возможно, страница не залогинена или Google изменил разметку.",
        });
      }
    } else {
      setTimeout(poll, 1500);
    }
  }

  // Give the SPA time to render
  setTimeout(poll, 3000);
})();
