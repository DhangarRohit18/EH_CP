"""
Explainability Engine
Generates transparent, mathematically grounded point additions and human-readable explanations.
"""

from typing import Dict, Any, List

def generate_explanations(factors: Dict[str, Any], is_demo_canonical: bool = False) -> List[Dict[str, Any]]:
    """
    Decomposes total score into individual point contributions.
    """
    explanations = []

    for key, f in factors.items():
        points = f["contribution"]
        weight_pct = int(f["weight"] * 100)
        
        severity = "info"
        if points >= 15:
            severity = "critical"
        elif points >= 8:
            severity = "warning"

        explanations.append({
            "factor": f["name"],
            "points": points,
            "explanation": f["reason"],
            "weight_percent": weight_pct,
            "severity": severity
        })

    # Sort descending by point impact
    return sorted(explanations, key=lambda x: x["points"], reverse=True)
