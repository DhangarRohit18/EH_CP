"""
History & Audit Trail API Router
Endpoints:
- GET /api/v1/history
- GET /api/v1/history/{id}
- DELETE /api/v1/history/{id}
- DELETE /api/v1/history
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.analysis import Analysis, HistoryItemSchema

router = APIRouter(prefix="/history", tags=["Audit History"])

@router.get("", response_model=List[HistoryItemSchema])
def get_history(
    limit: int = Query(50, ge=1, le=200, description="Max records to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    risk_level: Optional[str] = Query(None, description="Filter by risk tier (LOW, MEDIUM, HIGH, CRITICAL)"),
    domain: Optional[str] = Query(None, description="Substring search on domain name"),
    db: Session = Depends(get_db)
):
    query = db.query(Analysis)
    if risk_level:
        query = query.filter(Analysis.risk_level == risk_level.upper())
    if domain:
        query = query.filter(Analysis.domain.contains(domain.lower()))

    records = query.order_by(Analysis.created_at.desc()).offset(offset).limit(limit).all()

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
            "evidence_coverage": r.evidence_coverage or 1.0,
            "latency_ms": r.latency_ms or 0.0,
            "created_at": r.created_at.isoformat() + "Z" if r.created_at else "",
            "top_reasons": top_reasons,
            "is_pre_payment_triggered": r.is_pre_payment_triggered or False
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
        "normalized_domain": record.normalized_domain,
        "product_name": record.product_name,
        "price": record.price,
        "currency": record.currency,
        "risk_score": record.risk_score,
        "risk_level": record.risk_level,
        "evidence_coverage": record.evidence_coverage,
        "latency_ms": record.latency_ms,
        "model_version": record.model_version,
        "recommendation": record.recommendation,
        "is_pre_payment_triggered": record.is_pre_payment_triggered,
        "created_at": record.created_at.isoformat() + "Z" if record.created_at else "",
        "factors": [{
            "factor_name": f.factor_name,
            "raw_score": f.raw_score,
            "weight": f.weight,
            "contribution": f.contribution,
            "confidence": f.confidence,
            "status": f.status,
            "explanation": f.explanation,
            "missing_evidence": f.missing_evidence
        } for f in record.factors],
        "signals": [{
            "category": s.category,
            "severity": s.severity,
            "message": s.message,
            "rule_triggered": s.rule_triggered
        } for s in record.signals]
    }

@router.delete("/{analysis_id}")
def delete_single_analysis(analysis_id: str, db: Session = Depends(get_db)):
    record = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis record not found.")

    db.delete(record)
    db.commit()
    return {"message": f"Analysis '{analysis_id}' deleted successfully."}

@router.delete("")
def clear_all_history(db: Session = Depends(get_db)):
    """
    Transactionally deletes all persisted analysis runs and cascaded relationships.
    """
    deleted_count = db.query(Analysis).delete(synchronize_session=False)
    db.commit()
    return {"message": f"Successfully deleted {deleted_count} analysis record(s)."}
