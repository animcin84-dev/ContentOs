from database import engine, Consent, Service
from sqlalchemy.orm import sessionmaker
import json
import time

from analyzer import analyze_risk

SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Rescan all legacy ones with the fresh new prompt
consents = db.query(Consent).join(Service).filter(
    Service.category == "Legacy Integration"
).all()

print(f"Forcing re-scan for {len(consents)} legacy services with NEW EXPERT AI LOGIC...")
print("Running with 8s delay to perfectly comply with Groq/OpenRouter Rate Limits (6000 TPM).")

for i, c in enumerate(consents):
    svc = db.query(Service).get(c.service_id)
    scopes = json.loads(c.data_types)
    
    print(f"[{i+1}/{len(consents)}] AI Analyzing {svc.name}...")
    success = False
    
    # Retry loop for rate limits
    for attempt in range(3):
        try:
            res = analyze_risk(svc.domain, "Legacy Integration", scopes)
            c.risk_score = res.get("risk_score", 50)
            c.recommendation = res.get("recommendation", "Не удалось проанализировать.")
            db.commit()
            print(f"  -> Score: {c.risk_score} | {c.recommendation}")
            success = True
            break # Success, break retry loop
        except Exception as e:
            # Check if it was rate limit
            if "429" in str(e):
                print(f"  -> Rate Limit! Waiting 10 seconds before retry... (Attempt {attempt+1}/3)")
                time.sleep(10)
            else:
                print(f"  -> Error: {e}")
                time.sleep(5)
                break
                
    if success:
        time.sleep(6.5)  # Safe delay to stay under ~800 tokens * 8 requests = 6400 TPM

print("Done processing!")
db.close()
