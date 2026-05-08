from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.session import get_db
from app.db.models import Patient, AuditLog, User
from app.api.v1.auth import get_current_user
import uuid

router = APIRouter()

@router.get("/")
async def list_patients(
    search: str = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Patient).filter(Patient.is_active == True)
    if search:
        query = query.filter(
            or_(
                Patient.first_name.ilike(f"%{search}%"),
                Patient.last_name.ilike(f"%{search}%"),
                Patient.mrn.ilike(f"%{search}%")
            )
        )
    total = query.count()
    patients = query.offset(skip).limit(limit).all()
    return {"total": total, "patients": [
        {
            "id": str(p.id),
            "mrn": p.mrn,
            "first_name": p.first_name,
            "last_name": p.last_name,
            "date_of_birth": str(p.date_of_birth),
            "gender": p.gender,
            "insurance_type": p.insurance_type,
            "is_active": p.is_active
        } for p in patients
    ]}

@router.get("/{patient_id}")
async def get_patient(
    patient_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    db.add(AuditLog(
        user_id=current_user.id,
        action='READ',
        resource_type='patients',
        patient_id=patient_id,
        response_code=200
    ))
    db.commit()
    return {
        "id": str(patient.id),
        "mrn": patient.mrn,
        "first_name": patient.first_name,
        "last_name": patient.last_name,
        "date_of_birth": str(patient.date_of_birth),
        "gender": patient.gender,
        "race": patient.race,
        "insurance_type": patient.insurance_type,
        "is_active": patient.is_active,
        "created_at": str(patient.created_at)
    }