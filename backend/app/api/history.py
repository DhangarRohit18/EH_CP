"""
History API Router
Endpoints:
- GET /api/v1/history
- GET /api/v1/history/{id}
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.analysis import Analysis, HistoryItemSchema

router = APIRouter(prefix="/history", tags=["History"])

@router.get("", response_model=List[HistoryItemSchema])
def get_history(
    limit: int = Query(50, ge=1, le=200),
    risk_level: Optional[str] = None,
    domain: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Analysis)
    if risk_level:
        query = query.filter(Analysis.risk_level == risk_level.upper())
    if domain:
        query = query.filter(Analysis.domain.contains(domain.lower()))

    records = query.order_by(Analysis.created_at.desc()).limit(limit).all()

    items = []
    for r in records:
        top_reasons = [f.explanation for f in r.factors[:3]] if r.factors else []
        items.append({
            "id": r.id,
            "url": r.url,
            "domain": r.domain,
            "product_name": r.product_name,
            "price": r.price,
            "currency": r.currency,
            "risk_score": r.risk_score,
            "risk_level": r.risk_level,
            "created_at": r.created_at.isoformat() + "Z" if r.created_at else "",
            "top_reasons": top_reasons
        })
    return items

@router.get("/{analysis_id}")
def get_analysis_detail(analysis_id: str, db: Session = Depends(get_db)):
    record = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis record not found.")

    return {
        "id": record.id,
        "url": record.url,
        "domain": record.domain,
        "product_name": record.product_name,
        "price": record.price,
        "currency": record.currency,
        "risk_score": record.risk_score,
        "risk_level": record.risk_level,
        "recommendation": record.recommendation,
        "created_at": record.created_at.isoformat() + "Z" if record.created_at else "",
        "factors": [{
            "factor_name": f.factor_name,
            "raw_score": f.raw_score,
            "weight": f.weight,
            "contribution": f.contribution,
            "explanation": f.explanation
        } for f in record.factors],
        "signals": [{
            "category": s.category,
            "severity": s.severity,
            "message": s.message,
            "rule_triggered": s.rule_triggered
        } for s in record.signals]
    }
