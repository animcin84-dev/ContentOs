// ============================================================
// Consent OS — Content Script
// Автоматически запускается на КАЖДОЙ странице
// Три реальных метода обнаружения трекеров
// ============================================================

const TRACKER_DB = {
  // Analytics
  'google-analytics.com': { name: 'Google Analytics', cat: 'Аналитика', data: ['Поведение', 'Устройство', 'Локация'], risk: 55 },
  'googletagmanager.com': { name: 'Google Tag Manager', cat: 'Аналитика', data: ['Всё что передадут', 'Скрипты'], risk: 60 },
  'analytics.google.com': { name: 'Google Analytics 4', cat: 'Аналитика', data: ['Клики', 'Страницы', 'Время'], risk: 55 },
  'mc.yandex.ru': { name: 'Yandex Metrica', cat: 'Аналитика', data: ['Запись экрана', 'Клики', 'Карта скроллинга'], risk: 75 },
  'counter.yadro.ru': { name: 'Yadro Analytics', cat: 'Аналитика', data: ['Поведение', 'IP'], risk: 50 },
  // Ad networks
  'doubleclick.net': { name: 'DoubleClick (Google Ads)', cat: 'Реклама', data: ['Профиль', 'История покупок', 'Интересы'], risk: 85 },
  'googlesyndication.com': { name: 'Google AdSense', cat: 'Реклама', data: ['Контекст страницы', 'Поведение'], risk: 70 },
  'connect.facebook.net': { name: 'Meta Pixel / Facebook SDK', cat: 'Реклама', data: ['Биометрия', 'Покупки', 'Контакты'], risk: 95 },
  'facebook.com': { name: 'Facebook', cat: 'Социальные', data: ['Биометрия', 'Связи', 'pH'], risk: 90 },
  'instagram.com': { name: 'Instagram (Meta)', cat: 'Социальные', data: ['Фото', 'Биометрия лица', 'Контакты'], risk: 92 },
  // Yandex
  'yandex.ru': { name: 'Yandex', cat: 'Экосистема', data: ['Поиск', 'Локация', 'Почта'], risk: 70 },
  'yandex.kz': { name: 'Yandex KZ', cat: 'Экосистема', data: ['Поиск', 'Локация'], risk: 68 },
  'zen.yandex.ru': { name: 'Яндекс Дзен', cat: 'Контент', data: ['Интересы', 'Время чтения'], risk: 55 },
  // Payments
  'kaspi.kz': { name: 'Kaspi.kz', cat: 'Финансы', data: ['Транзакции', 'Кредитный профиль', 'Покупки', 'Локация'], risk: 82 },
  'epay.kkb.kz': { name: 'Halyk ePayment', cat: 'Финансы', data: ['Транзакции', 'Карты'], risk: 75 },
  'freedompay.kz': { name: 'Freedom Pay', cat: 'Финансы', data: ['Транзакции'], risk: 72 },
  // Government KZ
  'egov.kz': { name: 'eGov.kz', cat: 'Государство', data: ['ИИН', 'Документы', 'Семья', 'Налоги'], risk: 35 },
  'elicense.kz': { name: 'eLicense KZ', cat: 'Государство', data: ['Лицензии', 'Бизнес данные'], risk: 30 },
  // CDN / Social
  'cdnjs.cloudflare.com': { name: 'Cloudflare CDN', cat: 'Инфраструктура', data: ['IP', 'Запросы'], risk: 20 },
  'jsdelivr.net': { name: 'jsDelivr CDN', cat: 'Инфраструктура', data: ['IP'], risk: 15 },
  'twitter.com': { name: 'Twitter / X', cat: 'Социальные', data: ['Интересы', 'Связи'], risk: 78 },
  'platform.twitter.com': { name: 'Twitter Widget', cat: 'Социальные', data: ['Поведение', 'Связи'], risk: 78 },
  'linkedin.com': { name: 'LinkedIn', cat: 'Профессиональные', data: ['Карьера', 'Резюме', 'Сеть контактов'], risk: 65 },
  // Russian services
  'vk.com': { name: 'ВКонтакте', cat: 'Социальные', data: ['Связи', 'Интересы', 'Локация'], risk: 80 },
  'ok.ru': { name: 'Одноклассники', cat: 'Социальные', data: ['Связи', 'Фото'], risk: 72 },
  'mail.ru': { name: 'Mail.ru', cat: 'Экосистема', data: ['Почта', 'Интересы', 'Поведение'], risk: 78 },
  // KZ local
  'kolesa.kz': { name: 'Kolesa.kz', cat: 'Объявления', data: ['Телефон', 'Email', 'Поиск авто'], risk: 45 },
  'krisha.kz': { name: 'Krisha.kz', cat: 'Недвижимость', data: ['Телефон', 'Email', 'Интересы'], risk: 42 },
  'olx.kz': { name: 'OLX Kazakhstan', cat: 'Объявления', data: ['Телефон', 'Email', 'Покупки'], risk: 48 },
  'hh.kz': { name: 'HeadHunter KZ', cat: 'Карьера', data: ['Резюме', 'Навыки', 'Зарплата'], risk: 55 },
  // Hotjar / UX tracking
  'hotjar.com': { name: 'Hotjar', cat: 'UX Аналитика', data: ['Запись экрана', 'Тепловые карты', 'Клики'], risk: 88 },
  'static.hotjar.com': { name: 'Hotjar', cat: 'UX Аналитика', data: ['Запись экрана', 'Клики'], risk: 88 },
  // Sentry / crash
  'sentry.io': { name: 'Sentry', cat: 'Мониторинг', data: ['Ошибки', 'Стек', 'Email при ошибке'], risk: 38 },
  'ingest.sentry.io': { name: 'Sentry Ingest', cat: 'Мониторинг', data: ['Ошибки', 'Стек'], risk: 38 },
  // Misc
  'cloudflare.com': { name: 'Cloudflare', cat: 'Инфраструктура', data: ['IP', 'Bot защита'], risk: 18 },
  'recaptcha.net': { name: 'reCAPTCHA', cat: 'Безопасность', data: ['Поведение мыши', 'Биометрия'], risk: 45 },
  'google.com': { name: 'Google', cat: 'Экосистема', data: ['Поиск', 'Локация', 'Всё', 'История'], risk: 65 },
  'googleapis.com': { name: 'Google APIs', cat: 'Инфраструктура', data: ['Сервисы Google', 'Авторизация'], risk: 40 },
  'gstatic.com': { name: 'Google Static', cat: 'Инфраструктура', data: ['Ресурсы Google'], risk: 30 },
  'amplitude.com': { name: 'Amplitude', cat: 'Аналитика продукта', data: ['События', 'Воронка', 'Ретеншн'], risk: 72 },
  'mixpanel.com': { name: 'Mixpanel', cat: 'Аналитика продукта', data: ['События', 'Пользовательские потоки'], risk: 70 },
  'segment.io': { name: 'Segment', cat: 'Аналитика', data: ['Все пользовательские данные → передаются 100+ сервисам'], risk: 90 },
  'intercom.io': { name: 'Intercom', cat: 'Поддержка', data: ['История переписки', 'Email', 'Поведение'], risk: 60 },
  'zendesk.com': { name: 'Zendesk', cat: 'Поддержка', data: ['Email', 'Обращения', 'История'], risk: 55 },
};

// Inline script patterns
const INLINE_PATTERNS = [
  { re: /gtag\s*\(/,         domain: 'google-analytics.com', name: 'Google Analytics (inline)' },
  { re: /fbq\s*\(/,          domain: 'connect.facebook.net', name: 'Meta Pixel (inline)' },
  { re: /ym\s*\(/,           domain: 'mc.yandex.ru',         name: 'Yandex Metrica (inline)' },
  { re: /_ym_uid/,           domain: 'mc.yandex.ru',         name: 'Yandex Metrica UID' },
  { re: /amplitude\.init/,   domain: 'amplitude.com',        name: 'Amplitude (inline)' },
  { re: /mixpanel\.init/,    domain: 'mixpanel.com',         name: 'Mixpanel (inline)' },
  { re: /Intercom\s*\(/,     domain: 'intercom.io',          name: 'Intercom (inline)' },
  { re: /hotjar\.init/,      domain: 'hotjar.com',           name: 'Hotjar (inline)' },
  { re: /analytics\.js/,     domain: 'google-analytics.com', name: 'GA Analytics.js' },
];

function extractDomain(url) {
  try {
    return new URL(url).hostname.replace(/^www\./, '');
  } catch { return null; }
}

function matchTracker(domain) {
  if (!domain) return null;
  // Direct match
  if (TRACKER_DB[domain]) return { domain, ...TRACKER_DB[domain] };
  // Subdomain match
  for (const key of Object.keys(TRACKER_DB)) {
    if (domain.endsWith('.' + key) || domain === key) {
      return { domain, ...TRACKER_DB[key] };
    }
  }
  return null;
}

function scanPage() {
  const found = {};
  const pageDomain = location.hostname.replace(/^www\./, '');

  // METHOD 1: Network resource entries
  try {
    const entries = performance.getEntriesByType('resource');
    for (const e of entries) {
      const d = extractDomain(e.name);
      if (!d || d === pageDomain) continue;
      const t = matchTracker(d);
      if (t && !found[t.domain]) found[t.domain] = t;
    }
  } catch(e) {}

  // METHOD 2: <script>, <img>, <iframe>, <link> src attributes
  try {
    const selectors = 'script[src], img[src], iframe[src], link[href]';
    document.querySelectorAll(selectors).forEach(el => {
      const url = el.src || el.href;
      if (!url) return;
      const d = extractDomain(url);
      if (!d || d === pageDomain) continue;
      const t = matchTracker(d);
      if (t && !found[t.domain]) found[t.domain] = t;
    });
  } catch(e) {}

  // METHOD 3: Inline script pattern matching
  try {
    document.querySelectorAll('script:not([src])').forEach(el => {
      const code = el.textContent || '';
      for (const pat of INLINE_PATTERNS) {
        if (pat.re.test(code)) {
          const base = matchTracker(pat.domain) || { domain: pat.domain, name: pat.name, cat: 'Аналитика', data: [], risk: 50 };
          if (!found[base.domain]) found[base.domain] = base;
        }
      }
    });
  } catch(e) {}

  return Object.values(found);
}

// Run scan and send to background
const trackers = scanPage();

if (trackers.length > 0 || true) {
  chrome.runtime.sendMessage({
    type: 'PAGE_SCAN',
    payload: {
      url: location.href,
      domain: location.hostname.replace(/^www\./, ''),
      title: document.title,
      trackers,
      ts: Date.now()
    }
  });
}
