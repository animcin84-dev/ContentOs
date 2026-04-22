// Consent OS — Automated Revoker Script

(function () {
  console.log("Consent OS: Auto-revoker active...");

  chrome.storage.local.get(['consentOsTarget', 'consentOsTargetId'], (res) => {
      const targetName = res.consentOsTarget;
      
      // We don't care about targetId for routing, we strictly use URL checking
      chrome.storage.local.remove(['consentOsTarget', 'consentOsTargetId']);

      // ── MIGHTY BOT HUD ─────────────────────────────
      const hud = document.createElement('div');
      hud.style.cssText = `
        position: fixed; top: 20px; right: 20px; z-index: 999999;
        background: rgba(15, 23, 42, 0.95); backdrop-filter: blur(10px);
        border: 1px solid rgba(99, 130, 255, 0.4); border-radius: 12px;
        padding: 16px 20px; color: #fff; font-family: system-ui, sans-serif;
        box-shadow: 0 10px 30px rgba(0,0,0,0.6); font-size: 14px;
        transition: all 0.3s ease;
      `;
      document.body.appendChild(hud);

      function updateHUD(text, type='info') {
          console.log("Consent OS:", text);
          const icon = type === 'error' ? '❌' : type === 'success' ? '✅' : type === 'warning' ? '⚠️' : '🤖';
          const color = type === 'error' ? '#ef4444' : type === 'success' ? '#22c55e' : type === 'warning' ? '#eab308' : '#60a5fa';
          hud.innerHTML = `<div style="font-weight: 600; color: ${color}; margin-bottom: 4px;">Consent OS ${icon}</div>
                           <div style="color: #cbd5e1; font-size: 13px;">${text}</div>`;
      }
      
      updateHUD("Инициализация сканера...");
      // ────────────────────────────────────────────────

      const MAX_ATTEMPTS = 30;
      let attempts = 0;
      let searchInterval;

      function deepClick(el) {
          const clickOpts = { bubbles: true, cancelable: true, view: window };
          el.dispatchEvent(new MouseEvent('mousedown', clickOpts));
          el.dispatchEvent(new MouseEvent('mouseup', clickOpts));
          el.dispatchEvent(new MouseEvent('click', clickOpts));
          el.click();
      }

      // --- Search-and-Destroy Mode Logic ---
      function executeSearchAndDestroy() {
         updateHUD(`Ищу приложение: <b style="color:white">"${targetName}"</b>...`, 'info');
         searchInterval = setInterval(() => {
            attempts++;
            if (attempts > MAX_ATTEMPTS) {
                clearInterval(searchInterval);
                updateHUD(`Не могу найти приложение "${targetName}" на странице.`, 'error');
                chrome.runtime.sendMessage({ type: "REVOKE_FAILED" });
                setTimeout(() => window.close(), 4000);
                return;
            }

            let foundEl = null;
            const cleanTarget = targetName.toLowerCase().replace(/\s+/g, ' ').trim();

            // Match exact structure from content_scanner.js
            document.querySelectorAll('a[href*="/connections/app/"]').forEach(a => {
                const nameEl = a.querySelector('h3, h2, [role="heading"], span');
                const name = nameEl ? nameEl.textContent : a.textContent;
                const elText = name.toLowerCase().replace(/\s+/g, ' ').trim();
                
                if (elText === cleanTarget || elText.includes(cleanTarget) || cleanTarget.includes(elText)) {
                    foundEl = a;
                }
            });

            if (foundEl) {
                clearInterval(searchInterval);
                updateHUD(`Успех! Нашел ссылку. Вхожу в профиль...`, 'success');
                
                deepClick(foundEl);
                attempts = 0; 
                setTimeout(() => findAndClickRemove(true), 3000); // Wait for SPA redirect
            } else {
                 updateHUD(`Скроллю страницу вниз (Попытка ${attempts}/${MAX_ATTEMPTS})`, 'info');
                 window.scrollBy(0, 1000);
                 const links = document.querySelectorAll('a[href*="/connections/app/"]');
                 if (links.length > 0) links[links.length - 1].scrollIntoView({behavior: "smooth", block: "end"});
            }
         }, 1000);
      }

      // --- Standard Revoke Mode Logic ---
      function findAndClickRemove(isFallbackPhase = false) {
        updateHUD(`Ищу кнопку удаления (Попытка ${attempts})...`, 'info');
        
        const allElements = Array.from(document.querySelectorAll('*')).filter(el => el.children.length === 0);
        const removeBtn = allElements.find(btn => {
            const text = btn.textContent.trim().toLowerCase();
            if (!text || text.length > 60) return false;
            
            const keywords = [
                'remove access', 'delete connection', 'отменить доступ', 'удалить связь', 
                'удалить все связи', 'отмена всех связей', 'удалить приложение', 'отключить',
                'прекратить доступ', 'supprimer l\'accès', 'zugriff entfernen', 'quitar acceso'
            ];
            return keywords.some(kw => text.includes(kw));
        });

        if (removeBtn) {
          updateHUD(`Кнопка найдена! Нажимаю...`, 'success');
          const realBtn = removeBtn.closest('button, [role="button"]') || removeBtn;
          deepClick(realBtn);
          
          attempts = 0;
          setTimeout(confirmRemoval, 1500);
          return;
        }

        attempts++;
        if (attempts < MAX_ATTEMPTS) {
          // Fallback logic
          if (!isFallbackPhase && attempts > 8 && targetName) {
              updateHUD(`Кнопка не найдена (устаревший ID). Возврат в общий список сервисов...`, 'warning');
              attempts = 0;
              history.back(); // Soft navigate to list instead of hard reload
              setTimeout(executeSearchAndDestroy, 2000);
              return;
          }
          setTimeout(() => findAndClickRemove(isFallbackPhase), 1000);
        } else {
          updateHUD(`ОШИБКА: Кнопка удаления физически отсутствует.`, 'error');
          chrome.runtime.sendMessage({ type: "REVOKE_FAILED" });
        }
      }

      function confirmRemoval() {
        updateHUD(`Ожидаю модальное окно подтверждения...`, 'info');
        
        const allElements = Array.from(document.querySelectorAll('*')).filter(el => el.children.length === 0);
        const confirmBtn = allElements.find(btn => {
            const text = btn.textContent.trim().toLowerCase();
            if (!text || text.length > 50) return false;
            const keywords = ['confirm', 'remove', 'ok', 'удалить', 'подтвердить', 'confirmer', 'bestätigen', 'confirmar'];
            return keywords.some(kw => text === kw || text.includes(kw));
        });

        if (confirmBtn) {
          updateHUD(`Подтверждаю удаление!`, 'success');
          const realBtn = confirmBtn.closest('button, [role="button"]') || confirmBtn;
          deepClick(realBtn);
          
          updateHUD(`🎉 Официально отвязано! Возвращаемся в Дашборд...`, 'success');
          
          setTimeout(() => {
            chrome.runtime.sendMessage({ 
                type: "REVOKE_COMPLETED", 
                success: true,
                externalId: targetName, // Ensure we pass something truthy
                searchName: targetName
            });
            setTimeout(() => window.close(), 1000);
          }, 3500);
        } else {
            setTimeout(confirmRemoval, 500);
        }
      }

      // Route the flow based on ACTUAL URL, bypassing any Google redirects
      const isDetailsPage = window.location.href.includes('/connections/app/');
      if (isDetailsPage) {
          findAndClickRemove(false);
      } else {
          if (!targetName) {
              updateHUD(`Критическая ошибка: отсутствует имя сервиса в памяти.`, 'error');
              return;
          }
          executeSearchAndDestroy();
      }
  });
})();
