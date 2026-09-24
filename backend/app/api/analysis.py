"""
Analysis API Router
Endpoint: POST /api/v1/analyze
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models.analysis import AnalyzeRequest, AnalyzeResponse, Analysis, FactorResultModel, DetectedSignalModel
from ..database import get_db
from ..engine.risk_engine import compute_risk

router = APIRouter(prefix="/analyze", tags=["Analysis"])

@router.post("", response_model=AnalyzeResponse)
def analyze_storefront(request: AnalyzeRequest, db: Session = Depends(get_db)):
    payload_dict = request.model_dump()
    result = compute_risk(payload_dict)

    # Persist record in database
    try:
        db_analysis = Analysis(
            id=result["id"],
            url=result["url"],
            domain=result["domain"],
            product_name=result["product_name"],
            price=result["price"],
            currency=result["currency"],
            risk_score=result["risk_score"],
            risk_level=result["risk_level"],
            recommendation=result["recommendation"]
        )
        db.add(db_analysis)

        # Persist factors
        for f_key, f_val in result["factors"].items():
            db_factor = FactorResultModel(
                analysis_id=result["id"],
                factor_name=f_key,
                raw_score=f_val["raw_score"],
                weight=f_val["weight"],
                contribution=f_val["contribution"],
                explanation=f_val["reason"]
            )
            db.add(db_factor)

        # Persist detected signals
        for sig in result["detected_signals"]:
            db_sig = DetectedSignalModel(
                analysis_id=result["id"],
                category=sig["category"],
                severity=sig["severity"],
                message=sig["message"],
                rule_triggered=sig.get("rule_triggered")
            )
            db.add(db_sig)

        db.commit()
    except Exception as e:
        db.rollback()
        # Non-fatal DB write error; still return the computed risk result
        print(f"[WebGuard DB Error] Could not persist analysis: {e}")

    return result
