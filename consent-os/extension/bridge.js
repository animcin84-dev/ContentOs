// Consent OS — Bridge Script
// This script runs on http://localhost:5173 (The Dashboard)
// It listens for events from the webpage and relays them to the extension's background script.

console.log("Consent OS: Extension Bridge Active.");

// 1. Dashboard -> Extension
window.addEventListener("message", (event) => {
  if (event.source !== window) return;

  if (event.data.type && event.data.type === "CONSENT_OS_REAL_REVOKE") {
    console.log("Consent OS Bridge: Relaying revoke request for ID:", event.data.externalId);
    chrome.runtime.sendMessage({
      type: "START_REAL_REVOKE",
      externalId: event.data.externalId,
      searchName: event.data.searchName
    });
  }

  if (event.data.type && event.data.type === "CHECK_EXTENSION_STATUS") {
      window.postMessage({ type: "CONSENT_OS_EXTENSION_READY" }, "*");
  }
});

// 2. Extension -> Dashboard
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg.type === "REVOKE_VERIFIED_BY_EXTENSION") {
        console.log("Consent OS Bridge: Received verification for ID:", msg.externalId);
        window.postMessage({
            type: "REVOKE_SUCCESS_FEEDBACK",
            externalId: msg.externalId,
            searchName: msg.searchName
        }, "*");
    }
});
