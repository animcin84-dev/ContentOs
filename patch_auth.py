import codecs

with codecs.open("index.html", "r", "utf-8") as f:
    html = f.read()

toast_css = """
/* TOAST NOTIFICATIONS */
.toast-container { position: fixed; bottom: 24px; right: 24px; z-index: 9999; display: flex; flex-direction: column; gap: 8px; pointer-events: none; }
.toast { background: var(--bg-card); border: 1px solid var(--border); padding: 14px 20px; border-radius: 12px; font-size: 13px; font-weight: 500; display: flex; align-items: center; gap: 10px; animation: slideInTip 0.3s forwards; box-shadow: 0 4px 20px rgba(0,0,0,0.5); pointer-events: auto; color: white; }
@keyframes slideInTip { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
"""
if "toast-container" not in html[:html.find("</style>")]:
    html = html.replace('</style>', toast_css + '\n</style>')

if '<div class="toast-container" id="toast-container"></div>' not in html:
    html = html.replace('</body>', '<div class="toast-container" id="toast-container"></div>\n</body>')

js_functions = """
function showToast(msg, type='error') {
  let container = document.getElementById('toast-container');
  if(!container) return;
  const el = document.createElement('div');
  el.className = 'toast';
  el.style.borderLeft = `4px solid ${type==='success'?'var(--accent-green)':'var(--risk-red)'}`;
  el.innerHTML = msg;
  container.appendChild(el);
  setTimeout(()=>el.remove(), 4000);
}
"""
if "function showToast" not in html:
    html = html.replace('// 1. STORAGE & CRYPTO', js_functions + '\n// 1. STORAGE & CRYPTO')

html = html.replace('return alert("Заполните поля")', 'return showToast("Заполните поля")')
html = html.replace('return alert("Пользователь существует")', 'return showToast("Пользователь уже существует! Перейдите во вкладку Вход.")')
html = html.replace('return alert("Пользователь не найден")', 'return showToast("Пользователь не найден! Зарегистрируйтесь.")')
html = html.replace('return alert("Неверный пароль")', 'return showToast("Неверный пароль!")')
html = html.replace("alert('Введите ключи API!')", "showToast('Введите ключи API!')")
html = html.replace("alert('Ошибка Gmail API. Проверьте OAuth Scope.')", "showToast('Ошибка Gmail API. Проверьте OAuth Scope.')")

html = html.replace("const email = document.getElementById('auth-email-up').value;", "const email = document.getElementById('auth-email-up').value.trim();")
html = html.replace("const email = document.getElementById('auth-email-in').value;", "const email = document.getElementById('auth-email-in').value.trim();")

with codecs.open("index.html", "w", "utf-8") as f:
    f.write(html)

print("Patched.")
