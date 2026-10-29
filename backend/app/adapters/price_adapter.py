"""
WebGuard Price Evidence Provider Adapter
Analyzes observed storefront price against authenticated benchmark catalogs.
"""

from typing import Dict, Any, Optional
from .base import BaseEvidenceProvider, EvidenceResult, ProviderStatus

# Curated reference benchmark catalogs for common high-ticket luxury / tech items
RETAIL_BENCHMARK_CATALOG: Dict[str, Dict[str, Any]] = {
    "iphone 16 pro": {"mrp": 119999.0, "currency": "₹", "category": "electronics", "brand": "Apple"},
    "iphone 15 pro": {"mrp": 109999.0, "currency": "₹", "category": "electronics", "brand": "Apple"},
    "iphone 14": {"mrp": 59999.0, "currency": "₹", "category": "electronics", "brand": "Apple"},
    "rolex submariner": {"mrp": 850000.0, "currency": "₹", "category": "luxury_watches", "brand": "Rolex"},
    "air jordan 1": {"mrp": 16995.0, "currency": "₹", "category": "footwear", "brand": "Nike"},
    "macbook pro 14": {"mrp": 169900.0, "currency": "₹", "category": "electronics", "brand": "Apple"},
    "sony wh-1000xm5": {"mrp": 29990.0, "currency": "₹", "category": "electronics", "brand": "Sony"},
    "playstation 5": {"mrp": 54990.0, "currency": "₹", "category": "gaming", "brand": "Sony"},
}

class PriceEvidenceAdapter(BaseEvidenceProvider):
    def __init__(self):
        super().__init__(name="pricing_intel_provider", cache_ttl_seconds=3600)

    def evaluate_pricing(
        self,
        product_name: Optional[str],
        observed_price: Optional[float],
        currency: str = "₹",
        provided_ref_price: Optional[float] = None,
        provided_orig_price: Optional[float] = None
    ) -> EvidenceResult:
        evidence_data: Dict[str, Any] = {
            "observed_price": observed_price,
            "currency": currency,
            "reference_price": None,
            "reference_source": "unavailable",
            "product_match_confidence": 0.0,
            "discount_pct": 0.0,
            "is_evaluated": False,
        }

        if not self.circuit_breaker.can_execute():
            return EvidenceResult(
                provider_name=self.name,
                evidence_type="price_anomaly",
                status=ProviderStatus.UNAVAILABLE,
                confidence=0.0,
                data=evidence_data,
                error_message="Circuit breaker active (provider degraded)"
            )

        if observed_price is None or observed_price <= 0:
            return EvidenceResult(
                provider_name=self.name,
                evidence_type="price_anomaly",
                status=ProviderStatus.UNAVAILABLE,
                confidence=0.0,
                data=evidence_data,
                error_message="Observed price is missing or zero"
            )

        # 1. Use explicitly provided reference price if available
        if provided_ref_price and provided_ref_price > 0:
            ref_price = provided_ref_price
            evidence_data["reference_price"] = ref_price
            evidence_data["reference_source"] = "explicit_market_benchmark"
            evidence_data["product_match_confidence"] = 0.95
        elif provided_orig_price and provided_orig_price > observed_price:
            ref_price = provided_orig_price
            evidence_data["reference_price"] = ref_price
            evidence_data["reference_source"] = "merchant_strikethrough_price"
            evidence_data["product_match_confidence"] = 0.85
        else:
            # 2. Match against catalog if product name is present
            ref_price = None
            if product_name:
                p_lower = product_name.lower().strip()
                for key, item in RETAIL_BENCHMARK_CATALOG.items():
                    if key in p_lower:
                        ref_price = item["mrp"]
                        evidence_data["reference_price"] = ref_price
                        evidence_data["reference_source"] = f"authenticated_retail_benchmark ({item['brand']})"
                        evidence_data["product_match_confidence"] = 0.90
                        break

        # If still no reference price, honestly report unavailable rather than inventing a price
        if not ref_price:
            evidence_data["is_evaluated"] = False
            return EvidenceResult(
                provider_name=self.name,
                evidence_type="price_anomaly",
                status=ProviderStatus.UNAVAILABLE,
                confidence=0.30,
                data=evidence_data,
                error_message="No reliable reference benchmark found for comparison"
            )

        # Compute discount percentage
        evidence_data["is_evaluated"] = True
        if ref_price > observed_price:
            discount_pct = round(((ref_price - observed_price) / ref_price) * 100.0, 1)
            evidence_data["discount_pct"] = discount_pct

        return EvidenceResult(
            provider_name=self.name,
            evidence_type="price_anomaly",
            status=ProviderStatus.SUCCESS,
            confidence=evidence_data["product_match_confidence"],
            data=evidence_data
        )

price_adapter = PriceEvidenceAdapter()
