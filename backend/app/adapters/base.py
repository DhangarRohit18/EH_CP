"""
WebGuard Common Evidence Provider Contract & Circuit Breaker
Defines unified interface for external intelligence and local observational adapters.
"""

import time
import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class ProviderStatus:
    SUCCESS = "SUCCESS"
    UNAVAILABLE = "UNAVAILABLE"
    STALE = "STALE"
    RATE_LIMITED = "RATE_LIMITED"
    ERROR = "ERROR"

class EvidenceResult(BaseModel):
    provider_name: str
    evidence_type: str
    status: str = ProviderStatus.SUCCESS
    confidence: float = 1.0 # 0.0 - 1.0
    retrieved_at: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    data: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None

class CircuitBreaker:
    """
    Prevents cascading provider failures by halting outbound calls
    after consecutive errors until a reset timeout expires.
    """
    def __init__(self, failure_threshold: int = 3, reset_timeout_seconds: float = 60.0):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout_seconds
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED" # CLOSED, OPEN, HALF_OPEN

    def record_success(self):
        self.failure_count = 0
        self.state = "CLOSED"

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

    def is_available(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.reset_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        return True # HALF_OPEN allows one trial request

    def can_execute(self) -> bool:
        return self.is_available()

class BaseEvidenceProvider:
    """
    Base class for all evidence collection adapters.
    """
    def __init__(self, name: str, cache_ttl_seconds: int = 600):
        self.name = name
        self.cache_ttl = cache_ttl_seconds
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.circuit_breaker = CircuitBreaker()

    def get_cached(self, key: str) -> Optional[EvidenceResult]:
        entry = self.cache.get(key)
        if not entry:
            return None
        if time.time() - entry["timestamp"] > self.cache_ttl:
            # Mark as stale if still useful, or evict
            result = entry["result"]
            result.status = ProviderStatus.STALE
            return result
        return entry["result"]

    def set_cache(self, key: str, result: EvidenceResult):
        self.cache[key] = {
            "result": result,
            "timestamp": time.time()
        }
