"""
WebGuard Assessment Scope Validation & Authorization Engine
Enforces strict backend target validation.
Rejects unauthorized scanning requests and out-of-scope destinations.
"""

from typing import Tuple, Optional
from sqlalchemy.orm import Session
from ..models.security import AssessmentScopeModel
from .domain_parser import normalize_domain, parse_registrable_domain

def is_domain_in_authorized_scope(domain: str, db: Session) -> Tuple[bool, Optional[str]]:
    """
    Checks if a domain or its registrable apex domain belongs to an active, authorized assessment scope.
    Returns (is_authorized, authorized_by_or_reason)
    """
    norm_dom = normalize_domain(domain)
    _, sld, tld = parse_registrable_domain(norm_dom)
    apex = f"{sld}.{tld}" if sld and tld else norm_dom

    # Query exact domain or apex scope
    scope = db.query(AssessmentScopeModel).filter(
        AssessmentScopeModel.is_authorized == True,
        (AssessmentScopeModel.domain == norm_dom) | (AssessmentScopeModel.domain == apex)
    ).first()

    if scope:
        return True, f"Authorized under scope #{scope.id} ({scope.domain}) by {scope.authorized_by}"

    return False, f"Domain '{norm_dom}' is not registered in the approved assessment scope inventory."

def register_scope_domain(domain: str, description: str, authorized_by: str, db: Session) -> AssessmentScopeModel:
    """
    Adds a new domain to the authorized assessment scope.
    """
    norm = normalize_domain(domain)
    existing = db.query(AssessmentScopeModel).filter(AssessmentScopeModel.domain == norm).first()
    if existing:
        existing.is_authorized = True
        existing.description = description
        existing.authorized_by = authorized_by
        db.commit()
        db.refresh(existing)
        return existing

    new_scope = AssessmentScopeModel(
        domain=norm,
        description=description,
        is_authorized=True,
        authorized_by=authorized_by
    )
    db.add(new_scope)
    db.commit()
    db.refresh(new_scope)
    return new_scope
