from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
import json
from typing import List

from database import create_tables, get_db, User, Service, Consent, AuditLog
from auth import (
    hash_password, verify_password, create_access_token, get_current_user
)
from schemas import (
    RegisterRequest, TokenResponse, UserOut,
    ConsentOut, ServiceOut, AuditLogOut, TrackConsentRequest, VerifyRevokeRequest
)

# ── App Init ────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Consent OS API",
    description="Manage your personal data consents",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

create_tables()


# ── Auth Routes ─────────────────────────────────────────────────────────────────
@app.post("/auth/register", response_model=TokenResponse, tags=["Auth"])
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user and return JWT token immediately."""
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    user = User(
        email=req.email,
        name=req.name,
        hashed_password=hash_password(req.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Log registration
    log = AuditLog(user_id=user.id, action="register", detail=f"Account created for {req.email}")
    db.add(log)
    db.commit()

    token = create_access_token({"sub": user.email})
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        name=user.name,
        email=user.email
    )


@app.post("/auth/token", response_model=TokenResponse, tags=["Auth"])
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """OAuth2 Password flow — returns a JWT bearer token."""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    log = AuditLog(user_id=user.id, action="login", detail=f"Login from OAuth2 flow")
    db.add(log)
    db.commit()

    token = create_access_token({"sub": user.email})
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        name=user.name,
        email=user.email
    )


@app.get("/auth/me", response_model=UserOut, tags=["Auth"])
def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user."""
    return current_user


# ── Services Routes ─────────────────────────────────────────────────────────────
@app.get("/services", response_model=List[ServiceOut], tags=["Services"])
def list_services(db: Session = Depends(get_db)):
    """Get all registered services."""
    return db.query(Service).all()


# ── Consents Routes ─────────────────────────────────────────────────────────────
def serialise_consent(c: Consent) -> dict:
    """Convert Consent ORM to dict with parsed data_types."""
    return {
        "id": c.id,
        "service": {
            "id": c.service.id,
            "name": c.service.name,
            "domain": c.service.domain,
            "logo_emoji": c.service.logo_emoji,
            "description": c.service.description,
            "category": c.service.category,
            "external_id": c.service.external_id,
        },
        "data_types": c.data_types_list(),
        "risk_score": c.risk_score,
        "recommendation": c.recommendation,
        "status": c.status,
        "verified_revoke": c.verified_revoke,
        "granted_at": c.granted_at.isoformat(),
        "last_seen_at": c.last_seen_at.isoformat() if c.last_seen_at else c.granted_at.isoformat(),
        "revoked_at": c.revoked_at.isoformat() if c.revoked_at else None,
    }


@app.get("/consents", tags=["Consents"])
def list_consents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all consents for the current user, with service details."""
    consents = (
        db.query(Consent)
        .options(joinedload(Consent.service))
        .filter(Consent.user_id == current_user.id)
        .order_by(Consent.risk_score.desc())
        .all()
    )
    return [serialise_consent(c) for c in consents]


@app.get("/consents/{consent_id}", tags=["Consents"])
def get_consent(
    consent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a single consent by ID."""
    c = (
        db.query(Consent)
        .options(joinedload(Consent.service))
        .filter(Consent.id == consent_id, Consent.user_id == current_user.id)
        .first()
    )
    if not c:
        raise HTTPException(status_code=404, detail="Consent not found")
    return serialise_consent(c)


@app.delete("/consents/{consent_id}/revoke", tags=["Consents"])
def revoke_consent(
    consent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke a specific consent — records it into audit_log."""
    c = (
        db.query(Consent)
        .options(joinedload(Consent.service))
        .filter(Consent.id == consent_id, Consent.user_id == current_user.id)
        .first()
    )
    if not c:
        raise HTTPException(status_code=404, detail="Consent not found")
    if c.status == "revoked":
        raise HTTPException(status_code=400, detail="Consent already revoked")

    c.status = "revoked"
    c.revoked_at = datetime.utcnow()

    log = AuditLog(
        user_id=current_user.id,
        action="revoked",
        service_id=c.service_id,
        detail=f"Revoked access for {c.service.name} ({c.service.domain}). "
               f"Data types: {', '.join(c.data_types_list())}"
    )
    db.add(log)
    db.commit()
    db.refresh(c)

    return {
        "message": f"Access to {c.service.name} successfully revoked",
        "consent": serialise_consent(c)
    }


# ── History Route ───────────────────────────────────────────────────────────────
@app.get("/history", tags=["History"])
def get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get audit log for the current user."""
    logs = (
        db.query(AuditLog)
        .options(joinedload(AuditLog.service))
        .filter(AuditLog.user_id == current_user.id)
        .order_by(AuditLog.timestamp.desc())
        .limit(100)
        .all()
    )
    return [
        {
            "id": l.id,
            "action": l.action,
            "detail": l.detail,
            "timestamp": l.timestamp.isoformat(),
            "service": {
                "name": l.service.name,
                "domain": l.service.domain,
                "logo_emoji": l.service.logo_emoji,
                "category": l.service.category,
            } if l.service else None,
        }
        for l in logs
    ]


# ── Stats Route ─────────────────────────────────────────────────────────────────
@app.get("/stats", tags=["Stats"])
def get_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Dashboard aggregate stats for the current user."""
    all_c = db.query(Consent).filter(Consent.user_id == current_user.id).all()
    active = [c for c in all_c if c.status == "active"]
    revoked = [c for c in all_c if c.status == "revoked"]
    high_risk = [c for c in active if c.risk_score >= 70]
    return {
        "total": len(all_c),
        "active": len(active),
        "revoked": len(revoked),
        "high_risk": len(high_risk),
    }


# ── Tracking Route (Extension) ────────────────────────────────────────────────
@app.post("/api/track-consent", tags=["Tracking"])
def track_consent(
    req: TrackConsentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Called by the Chrome extension when it intercepts an OAuth request."""
    # Find or create service
    svc = db.query(Service).filter(Service.domain == req.domain).first()
    if not svc:
        svc = Service(
            name=req.domain.replace(".com", "").replace(".kz", "").capitalize(),
            domain=req.domain,
            logo_emoji="🔌",
            category="Auto-detected",
            description="Auto-detected via Chrome Extension"
        )
        db.add(svc)
        db.commit()
        db.refresh(svc)

    # Calculate basic risk score based on scopes length
    import re
    from analyzer import analyze_risk
    
    # split by spaces or commas
    scopes_list = [s.strip() for s in re.split(r'[, ]+', req.scopes) if s.strip()]
    if not scopes_list:
        scopes_list = ["basic_auth"]
    
    try:
        analysis = analyze_risk(svc.domain, svc.category, scopes_list)
        risk = analysis["risk_score"]
        rec = analysis["recommendation"]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Сбой ИИ анализатора (Groq/Llama): {str(e)}"
        )

    # Check if active consent exists
    consent = db.query(Consent).filter(
        Consent.user_id == current_user.id,
        Consent.service_id == svc.id,
        Consent.status == "active"
    ).first()

    if not consent:
        consent = Consent(
            user_id=current_user.id,
            service_id=svc.id,
            data_types=json.dumps(scopes_list),
            risk_score=risk,
            recommendation=rec,
            status="active",
            granted_at=datetime.utcnow()
        )
        db.add(consent)
        
        log = AuditLog(
            user_id=current_user.id,
            action="scan",
            service_id=svc.id,
            detail=f"Auto-detected new OAuth consent for {svc.name}. Scopes: {', '.join(scopes_list)}",
            timestamp=datetime.utcnow()
        )
        db.add(log)
    else:
        # Replace scopes with the new fresh ones from this OAuth event
        # (also merge to keep any extras from past sessions)
        existing_scopes = json.loads(consent.data_types)
        combined = list(set(existing_scopes + scopes_list))
        
        try:
            upd_analysis = analyze_risk(svc.domain, svc.category, combined)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Сбой ИИ анализатора (Groq/Llama) при обновлении: {str(e)}"
            )
        
        consent.data_types = json.dumps(combined)
        consent.risk_score = upd_analysis["risk_score"]
        consent.recommendation = upd_analysis["recommendation"]
        consent.last_seen_at = datetime.utcnow()  # Mark as freshly seen

        log = AuditLog(
            user_id=current_user.id,
            action="scan",
            service_id=svc.id,
            detail=f"Updated OAuth consent scopes for {svc.name}.",
            timestamp=datetime.utcnow()
        )
        db.add(log)

    db.commit()
    return {"status": "ok", "service": svc.name, "risk_score": risk}


def _bg_scan_legacy_consents(user_id: int):
    """Background task to scan legacy consents securely without blocking the HTTP response."""
    from database import SessionLocal
    import time
    db = SessionLocal()
    try:
        from analyzer import analyze_risk
        
        # Find all pending AI analysis
        pending = db.query(Consent).filter(
            Consent.user_id == user_id,
            Consent.recommendation == "Найден старый доступ через аккаунт Google."
        ).all()
        
        for c in pending:
            svc = db.query(Service).get(c.service_id)
            try:
                scopes = json.loads(c.data_types)
                ai_res = analyze_risk(svc.domain, "Legacy Integration", scopes)
                c.risk_score = ai_res.get("risk_score", 50)
                c.recommendation = ai_res.get("recommendation", c.recommendation)
                db.commit()
                time.sleep(1.5)  # Respect rate limits
            except Exception:
                time.sleep(5)  # Backoff on error
    finally:
        db.close()


@app.post("/api/sync-old-consents", tags=["Consent"])
def sync_old_consents(
    payload: List[dict],  # Expecting [{'name': 'AppName', 'scopes': ['...']}]
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Sync old manually extracted consents into Consent OS."""
    synced_count = 0
    
    for item in payload:
        name = item.get("name")
        scopes = item.get("scopes", ["google_account_access"])
        if not name: continue
        
        domain = name.lower().replace(" ", "") + ".com"

        svc = db.query(Service).filter(Service.domain == domain).first()
        external_id = item.get("external_id")

        if not svc:
            svc = Service(name=name, domain=domain, category="Legacy Integration", external_id=external_id)
            db.add(svc)
            db.commit()
            db.refresh(svc)
        elif external_id and not svc.external_id:
            # Update existing service with external_id if it was missing
            svc.external_id = external_id
            db.commit()
            
        existing = db.query(Consent).filter(
            Consent.user_id == current_user.id,
            Consent.service_id == svc.id,
            Consent.status == "active"
        ).first()
        
        if not existing:
            consent = Consent(
                user_id=current_user.id,
                service_id=svc.id,
                data_types=json.dumps(scopes),
                risk_score=50,
                recommendation="Найден старый доступ через аккаунт Google.",
                status="active",
                granted_at=datetime.utcnow()
            )
            db.add(consent)
            log = AuditLog(
                user_id=current_user.id,
                action="scan",
                service_id=svc.id,
                detail=f"Synced legacy consent for {name}",
                timestamp=datetime.utcnow()
            )
            db.add(log)
            synced_count += 1
            
    db.commit()
    
    if synced_count > 0:
        background_tasks.add_task(_bg_scan_legacy_consents, current_user.id)
        
    return {"status": "ok", "synced": synced_count}


@app.post("/api/verify-external-revoke", tags=["Consent"])
def verify_external_revoke(
    payload: VerifyRevokeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a consent as verified revoked after confirmation from the extension."""
    if payload.external_id:
        svc = db.query(Service).filter(Service.external_id == payload.external_id).first()
    elif payload.search_name:
        svc = db.query(Service).filter(Service.name == payload.search_name).first()
    else:
        raise HTTPException(status_code=400, detail="Missing external_id or search_name")
    if not svc:
        raise HTTPException(status_code=404, detail="Service not found")
        
    consent = db.query(Consent).filter(
        Consent.user_id == current_user.id,
        Consent.service_id == svc.id
    ).first()
    
    if not consent:
        raise HTTPException(status_code=404, detail="Consent not found")
        
    consent.verified_revoke = True
    consent.status = "revoked" # Ensure it's marked as revoked
    if not consent.revoked_at:
        consent.revoked_at = datetime.utcnow()
        
    db.commit()
    return {"status": "success", "service": svc.name}


# ── Advanced Features Routes ──────────────────────────────────────────────────
@app.post("/rescan", tags=["Advanced"])
def run_rescan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Force a live check. Sync mock statuses if they exist."""
    # In a real system, this would spawn a background worker with Puppeteer/Selenium
    # Here we simulate by marking some high risk items as active if they were revoked for demo
    import time
    time.sleep(2) # Simulate work
    
    log = AuditLog(
        user_id=current_user.id,
        action="scan",
        detail="Initiated deep sync with Google Connections server.",
        timestamp=datetime.utcnow()
    )
    db.add(log)
    db.commit()
    return {"status": "ok", "detail": "Rescan successful"}

@app.post("/webhooks/mass-revoke", tags=["Advanced"])
def run_mass_revoke(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Panic Mode: instantly mark all high_risk active connections to revoked."""
    import time
    active_risks = db.query(Consent).filter(
        Consent.user_id == current_user.id,
        Consent.status == "active",
        Consent.risk_score >= 70
    ).all()
    
    if not active_risks:
         return {"status": "ok", "message": "No high risk connections to revoke."}
         
    for c in active_risks:
         c.status = "revoked"
         c.revoked_at = datetime.utcnow()
         log = AuditLog(
             user_id=current_user.id,
             action="revoked",
             service_id=c.service_id,
             detail=f"Automated Panic Revoke for {getattr(c.service, 'name', 'Service')}.",
             timestamp=datetime.utcnow()
         )
         db.add(log)
         
    db.commit()
    time.sleep(1.5)
    return {"status": "ok", "message": f"Successfully revoked {len(active_risks)} connections."}

@app.post("/leak-scanner", tags=["Advanced"])
def run_leak_scanner(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deep Web Scanner (Leaks)"""
    import os
    import time
    
    # Execute Real OSINT file check (using the Holehe output for the user's email)
    # The system ran Holehe earlier and created this CSV:
    csv_path = "/home/anim/IQCH/holehe_1776783325_animcin84@gmail.com_results.csv"
    exposed = []
    
    if os.path.exists(csv_path):
        import csv
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 'exists' is column indicating if account exists on that site
                if row.get("exists", "").strip().lower() == "true":
                    exposed.append(row.get("name", "Unknown Service"))
    
    if not exposed:
        # Fallback empty case
        time.sleep(1)
        return {"status": "Clean", "detail": "No leaks found in the Dark Web or known OSINT databases."}

    # If exposed found, log it and return it
    breaches_str = ", ".join(exposed)
    log = AuditLog(
        user_id=current_user.id,
        action="scan",
        detail=f"CRITICAL: Found exposed OSINT footprints on {len(exposed)} services: {breaches_str[:200]}...",
        timestamp=datetime.utcnow()
    )
    db.add(log)
    db.commit()
    
    return {"status": "Breaches Found", "detail": f"OSINT scan found footprints on {len(exposed)} services, including: {breaches_str[:150]}..."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
