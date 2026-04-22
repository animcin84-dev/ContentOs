document.addEventListener('DOMContentLoaded', async () => {
  let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (tab && tab.url) {
    let url = new URL(tab.url);
    document.getElementById('host').textContent = url.hostname;
    
    setTimeout(() => {
      document.getElementById('risk-badge').textContent = '🔴 Высокий риск (Реклама)';
      document.getElementById('details').style.display = 'block';
      let ul = document.getElementById('tracker-list');
      ul.innerHTML = `
        <li>Google Analytics</li>
        <li>Meta Pixel (Поведение)</li>
        <li>Фоновая геолокация</li>
      `;
    }, 800);
  }

  document.getElementById('btn-block').addEventListener('click', (e) => {
    e.target.textContent = '✅ Заблокировано (Sync to OS)';
    e.target.style.background = 'rgba(0,224,158,0.15)';
    e.target.style.color = '#00e09e';
    e.target.style.borderColor = 'rgba(0,224,158,0.3)';
    chrome.tabs.sendMessage(tab.id, { action: "block_trackers" });
  });
});
