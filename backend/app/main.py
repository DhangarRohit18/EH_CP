"""
WebGuard Backend API Server
FastAPI Application Entry Point & Canonical Source of Truth
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import engine, Base
from .models import analysis as analysis_models, security as security_models
from .api import analysis, history, health, events, security_assessment

# Initialize Database Schema
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="WebGuard: Security Intelligence & Website Trust Platform",
    description="Dual-engine cybersecurity platform: Passive OSINT, Web Security Configuration, CVE Intelligence, and E-Commerce Trust Assessment.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware (permits Chrome extensions and Web UI)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 Routers
app.include_router(analysis.router, prefix=settings.API_V1_STR)
app.include_router(history.router, prefix=settings.API_V1_STR)
app.include_router(health.router, prefix=settings.API_V1_STR)
app.include_router(events.router, prefix=settings.API_V1_STR)
app.include_router(security_assessment.router, prefix=settings.API_V1_STR)
app.include_router(security_assessment.findings_router, prefix=settings.API_V1_STR)
app.include_router(security_assessment.scopes_router, prefix=settings.API_V1_STR)
app.include_router(security_assessment.assets_router, prefix=settings.API_V1_STR)
app.include_router(security_assessment.devsec_router, prefix=settings.API_V1_STR)

# Top-level Aliases for backwards compatibility & prompt API specification
app.include_router(health.router) # /health
app.include_router(analysis.router, prefix="/api") # /api/analyze
app.include_router(security_assessment.router, prefix="/api") # /api/security-assessments
app.include_router(security_assessment.findings_router, prefix="/api") # /api/findings
app.include_router(security_assessment.assets_router, prefix="/api") # /api/assets
app.include_router(history.router, prefix="/api") # /api/history

@app.get("/api/providers/status")
def providers_status(db = None):
    from .adapters.domain_adapter import domain_adapter
    from .adapters.price_adapter import price_adapter
    from .adapters.osint_adapter import osint_adapter
    from .adapters.cve_adapter import cve_adapter
    return {
        "status": "online",
        "providers": {
            "domain_intel": {"name": domain_adapter.name, "circuit_breaker": domain_adapter.circuit_breaker.state},
            "pricing_intel": {"name": price_adapter.name, "circuit_breaker": price_adapter.circuit_breaker.state},
            "passive_osint": {"name": osint_adapter.name, "circuit_breaker": osint_adapter.circuit_breaker.state},
            "cve_vulnerability": {"name": cve_adapter.name, "circuit_breaker": cve_adapter.circuit_breaker.state}
        }
    }

@app.get("/")
def root():
    return {
        "service": "WebGuard Security Intelligence Platform",
        "version": "2.0.0",
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health",
        "analyze_trust": f"{settings.API_V1_STR}/analyze",
        "analyze_security": f"{settings.API_V1_STR}/security-assessments",
        "findings": f"{settings.API_V1_STR}/findings",
        "scopes": f"{settings.API_V1_STR}/scopes",
        "assets": f"{settings.API_V1_STR}/assets",
        "developer_security": f"{settings.API_V1_STR}/developer-security",
        "events": f"{settings.API_V1_STR}/events"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
