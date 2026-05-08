from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Patient, RiskScore, AuditLog, User
from app.api.v1.auth import get_current_user
from app.ml.predictor import predictor
from sqlalchemy import text
import uuid

router = APIRouter()

@router.post("/predict/{patient_id}")
async def predict_risk(
    patient_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    features = build_features_for_patient(str(patient_id), db)
    result = predictor.predict(features)

    score_row = RiskScore(
        patient_id=patient_id,
        model_version=result['model_version'],
        risk_score=result['risk_score'],
        risk_tier=result['risk_tier'],
        readmission_30d=result['readmission_30d'],
        readmission_90d=result['readmission_90d'],
        mortality_risk=result['mortality_risk'],
    )
    db.add(score_row)
    db.add(AuditLog(
        user_id=current_user.id,
        action='PREDICT',
        resource_type='risk_score',
        patient_id=patient_id,
        response_code=200
    ))
    db.commit()
    db.refresh(score_row)
    return result

@router.get("/scores/{patient_id}")
async def get_risk_history(
    patient_id: uuid.UUID,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    scores = db.query(RiskScore)\
        .filter(RiskScore.patient_id == patient_id)\
        .order_by(RiskScore.score_date.desc())\
        .limit(limit).all()
    return [
        {
            "id": str(s.id),
            "risk_score": float(s.risk_score),
            "risk_tier": s.risk_tier,
            "readmission_30d": float(s.readmission_30d),
            "score_date": str(s.score_date),
            "model_version": s.model_version
        } for s in scores
    ]

def build_features_for_patient(patient_id: str, db: Session) -> dict:
    row = db.execute(
        text("SELECT * FROM patient_features WHERE patient_id = :pid"),
        {'pid': patient_id}
    ).fetchone()
    if row is None:
        return {col: 0 for col in predictor.features}
    return dict(row._mapping)