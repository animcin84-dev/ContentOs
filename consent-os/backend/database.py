from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text, Enum, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime
import json

SQLALCHEMY_DATABASE_URL = "sqlite:///./consent.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    consents = relationship("Consent", back_populates="user", cascade="all, delete")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete")


class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    domain = Column(String, unique=True, nullable=False)
    logo_emoji = Column(String, default="🌐")
    description = Column(Text)
    category = Column(String, default="Other")  # e.g. Delivery, Education, Health
    external_id = Column(String, nullable=True) # Unique ID from the source (e.g. Google App ID)

    consents = relationship("Consent", back_populates="service")


class Consent(Base):
    __tablename__ = "consents"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    data_types = Column(Text, default="[]")   # JSON list: ["email", "location"]
    risk_score = Column(Integer, default=0)
    recommendation = Column(String, nullable=True)
    status = Column(String, default="active")  # 'active', 'revoked'
    verified_revoke = Column(Boolean, default=False) # Confirmed by extension
    granted_at = Column(DateTime, default=datetime.utcnow)
    last_seen_at = Column(DateTime, default=datetime.utcnow)  # Updated on every re-auth
    revoked_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="consents")
    service = relationship("Service", back_populates="consents")

    def data_types_list(self):
        try:
            return json.loads(self.data_types)
        except Exception:
            return []


class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)   # "granted" | "revoked" | "login" | "scan"
    service_id = Column(Integer, ForeignKey("services.id"), nullable=True)
    detail = Column(Text, default="")
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")
    service = relationship("Service")


def create_tables():
    Base.metadata.create_all(bind=engine)
    # Safe migrations — add missing columns without wiping data
    _safe_migrate()


def _safe_migrate():
    """Add missing columns to existing tables. Safe to call every startup."""
    import sqlite3
    conn = sqlite3.connect("./consent.db")
    cur = conn.cursor()

    # Get existing consent columns
    cur.execute("PRAGMA table_info(consents)")
    consent_cols = {row[1] for row in cur.fetchall()}

    cur.execute("PRAGMA table_info(services)")
    service_cols = {row[1] for row in cur.fetchall()}

    migrations = [
        ("recommendation", "ALTER TABLE consents ADD COLUMN recommendation TEXT", consent_cols, "consents"),
        ("last_seen_at",   "ALTER TABLE consents ADD COLUMN last_seen_at DATETIME", consent_cols, "consents"),
        ("verified_revoke","ALTER TABLE consents ADD COLUMN verified_revoke BOOLEAN DEFAULT 0", consent_cols, "consents"),
        ("external_id",    "ALTER TABLE services ADD COLUMN external_id TEXT", service_cols, "services"),
    ]
    for col, sql, target_cols, table_name in migrations:
        if col not in target_cols:
            cur.execute(sql)
            print(f"✅ Migration applied: added {table_name}.{col}")

    conn.commit()
    conn.close()



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
