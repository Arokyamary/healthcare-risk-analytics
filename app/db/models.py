from sqlalchemy import Column, String, Boolean, Date, DateTime, Numeric, SmallInteger, Integer, Text, BigInteger, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Patient(Base):
    __tablename__ = 'patients'
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    mrn = Column(String(20), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(10))
    race = Column(String(50))
    zip_code = Column(String(10))
    insurance_type = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    risk_scores = relationship("RiskScore", back_populates="patient")

class RiskScore(Base):
    __tablename__ = 'risk_scores'
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    patient_id = Column(UUID(as_uuid=True), ForeignKey('patients.id'), nullable=False)
    model_version = Column(String(50), nullable=False)
    score_date = Column(DateTime(timezone=True), server_default=func.now())
    risk_score = Column(Numeric(6, 4), nullable=False)
    risk_tier = Column(String(20), nullable=False)
    readmission_30d = Column(Numeric(6, 4))
    readmission_90d = Column(Numeric(6, 4))
    mortality_risk = Column(Numeric(6, 4))
    top_features = Column(JSONB)
    confidence = Column(Numeric(5, 4))
    notes = Column(Text)
    patient = relationship("Patient", back_populates="risk_scores")

class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(Text, nullable=False)
    full_name = Column(String(200))
    role = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AuditLog(Base):
    __tablename__ = 'audit_log'
    id = Column(BigInteger, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100))
    resource_id = Column(UUID(as_uuid=True))
    patient_id = Column(UUID(as_uuid=True), ForeignKey('patients.id'))
    ip_address = Column(INET)
    response_code = Column(SmallInteger)
    created_at = Column(DateTime(timezone=True), server_default=func.now())