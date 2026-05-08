from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from app.api.v1.auth import get_current_user
from app.db.models import User

router = APIRouter()

@router.get("/population")
async def population_risk(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = db.execute(text("""
        SELECT risk_tier, COUNT(*) AS count
        FROM (
            SELECT DISTINCT ON (patient_id) patient_id, risk_tier
            FROM risk_scores
            ORDER BY patient_id, score_date DESC
        ) latest
        GROUP BY risk_tier
        ORDER BY count DESC
    """)).fetchall()
    return [{"risk_tier": row[0], "count": row[1]} for row in result]

@router.get("/high-risk")
async def high_risk_patients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = db.execute(text("""
        SELECT p.id, p.first_name, p.last_name, p.mrn,
               rs.risk_score, rs.risk_tier, rs.score_date
        FROM patients p
        JOIN (
            SELECT DISTINCT ON (patient_id) patient_id,
                   risk_score, risk_tier, score_date
            FROM risk_scores
            ORDER BY patient_id, score_date DESC
        ) rs ON p.id = rs.patient_id
        WHERE rs.risk_tier IN ('HIGH', 'CRITICAL')
        ORDER BY rs.risk_score DESC
        LIMIT 50
    """)).fetchall()
    return [
        {
            "id": str(row[0]),
            "first_name": row[1],
            "last_name": row[2],
            "mrn": row[3],
            "risk_score": float(row[4]),
            "risk_tier": row[5],
            "score_date": str(row[6])
        } for row in result
    ]

@router.get("/trends")
async def risk_trends(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = db.execute(text("""
        SELECT DATE(score_date) AS date,
               AVG(risk_score) AS avg_risk,
               COUNT(*) AS total_predictions
        FROM risk_scores
        WHERE score_date >= NOW() - INTERVAL '30 days'
        GROUP BY DATE(score_date)
        ORDER BY date
    """)).fetchall()
    return [
        {
            "date": str(row[0]),
            "avg_risk": round(float(row[1]), 4),
            "total_predictions": row[2]
        } for row in result
    ]