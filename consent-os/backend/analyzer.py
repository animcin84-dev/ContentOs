import os
import json

GROQ_KEY = os.getenv("GROQ_API_KEY", "")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")

def run_ai(client, model: str, prompt: str) -> dict:
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a cynical, expert cyber-security hacker. "
                    "You analyze OAuth permissions. "
                    "You MUST output ONLY valid JSON with exactly two keys: "
                    "'risk_score' (integer 0-100) and 'recommendation'. "
                    "DO NOT output markdown, no explanations, JUST JSON."
                )
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        response_format={"type": "json_object"}
    )
    content = resp.choices[0].message.content.strip()
    return json.loads(content)


def analyze_risk(domain: str, category: str, scopes: list[str]) -> dict:
    # Очищаем права до нормального вида
    clean_scopes = []
    has_critical = False
    
    for s in scopes:
        s_low = s.lower()
        if "drive" in s_low or "gmail" in s_low or "mail" in s_low.split("/")[-1] or "contacts" in s_low:
            has_critical = True
            
        if "/" in s and ("googleapis" in s or "google" in s):
            clean_scopes.append(s.split("/auth/")[-1] if "/auth/" in s else s.split("/")[-1])
        else:
            clean_scopes.append(s)

    scopes_text = ", ".join(clean_scopes)

    prompt = f"""Ты — опытный инженер по кибербезопасности. 
Я даю тебе название сервиса: "{domain}"
Он запрашивает права доступа к Google: [{scopes_text}]

Оцени уровень угрозы (risk_score от 0 до 100) и напиши ОЧЕНЬ короткую, человечную, дерзкую рекомендацию на русском языке (максимум 2 предложения).
НИКАКИХ шаблонных фраз типа "Нам неизвестно", "Учитывая что это Legacy Integration", "Предоставление доступа может позволить". Пиши прямо, как друг-айтишник.

ПРАВИЛА ОЦЕНКИ (ОБЯЗАТЕЛЬНЫ К ИСПОЛНЕНИЮ):

1. Если в правах ЕСТЬ ТОЛЬКО "google_account_access" (это просто вход по кнопке 'Войти через Гугл'):
   - Если "{domain}" — это известный мировой сервис, крупный бренд, нормальная игра или популярный тул (например GitHub, Meta, Coursera, Twitch, Patreon, Epic Games, Subway Surfers, 2GIS, Mail.Ru, Chess.com, Figma, Wokwi, ChatGPT) -> СТАВЬ РИСК ровно 10 или 15. Рекомендация: "✅ Обычный безопасный вход через Google у популярного сервиса."
   - Если "{domain}" — это что-то странное, длинные цифры, сомнительные слова (например "1031123-xxx.apps...", "3dwallpaper", "hack", "freefollowers") -> СТАВЬ РИСК 60-70. Рекомендация: "⚠️ Сомнительный ноунейм-сервис висит в твоем аккаунте. Лучше отозвать."

2. Если в правах есть "drive" (гугл диск), "gmail" (почта), "contacts" (контакты) или "admin":
   - СТАВЬ РИСК 90-100! (Если только это не системное приложение).
   - Рекомендация: "🚨 КРАСНАЯ ТРЕВОГА! Они могут читать твои личные файлы и переписки. Срочно удалять!"

ФОРМАТ ОТВЕТА (ТОЛЬКО JSON):
{{"risk_score": 15, "recommendation": "✅ Безопасный вход. Популярный сервис (GitHub), можно смело оставлять."}}
"""

    errors = []

    # Попытка 1 — Groq (Llama 3.1 8b)
    if GROQ_KEY:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=GROQ_KEY, base_url="https://api.groq.com/openai/v1")
            res = run_ai(client, "llama-3.1-8b-instant", prompt)
            return {
                "risk_score": min(100, max(0, int(res.get("risk_score", 50)))),
                "recommendation": res.get("recommendation", "Нет рекомендаций")
            }
        except Exception as e:
            errors.append(f"Groq: {e}")

    # Попытка 2 — OpenRouter
    if OPENROUTER_KEY:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENROUTER_KEY, base_url="https://openrouter.ai/api/v1")
            res = run_ai(client, "meta-llama/llama-3.2-3b-instruct:free", prompt)
            return {
                "risk_score": min(100, max(0, int(res.get("risk_score", 50)))),
                "recommendation": res.get("recommendation", "Нет рекомендаций")
            }
        except Exception as e:
            errors.append(f"OpenRouter: {e}")

    raise Exception("Все AI недоступны: " + str(errors))
