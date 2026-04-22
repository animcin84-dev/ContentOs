from pydantic import BaseModel, EmailStr, field_validator
from typing import List, Optional
from datetime import datetime


# ── Auth ────────────────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: str
    name: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str
    email: str


class UserOut(BaseModel):
    id: int
    email: str
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── Services ────────────────────────────────────────────────────────────────────
class ServiceOut(BaseModel):
    id: int
    name: str
    domain: str
    logo_emoji: str
    description: Optional[str]
    category: str
    external_id: Optional[str]

    class Config:
        from_attributes = True


# ── Consents ────────────────────────────────────────────────────────────────────
class ConsentOut(BaseModel):
    id: int
    service: ServiceOut
    data_types: List[str]
    risk_score: int
    recommendation: Optional[str] = None
    status: str
    verified_revoke: bool
    granted_at: datetime
    revoked_at: Optional[datetime]

    class Config:
        from_attributes = True


# ── Audit Log ───────────────────────────────────────────────────────────────────
class AuditLogOut(BaseModel):
    id: int
    action: str
    detail: str
    timestamp: datetime
    service: Optional[ServiceOut]

    class Config:
        from_attributes = True


# ── Extension Track ─────────────────────────────────────────────────────────────
class TrackConsentRequest(BaseModel):
    domain: str
    scopes: str

class VerifyRevokeRequest(BaseModel):
    external_id: Optional[str] = None
    search_name: Optional[str] = None
