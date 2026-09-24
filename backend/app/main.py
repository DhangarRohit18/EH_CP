"""
WebGuard Backend API Server
FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import engine, Base
from .api import analysis, history, health

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="WebGuard: Explainable E-Commerce Fraud Risk Engine",
    description="Multi-factor defensive cybersecurity assessment before entering payment credentials.",
    version="1.0.0",
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

# Register API Routers
app.include_router(analysis.router, prefix=settings.API_V1_STR)
app.include_router(history.router, prefix=settings.API_V1_STR)
app.include_router(health.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "message": "WebGuard Fraud Risk Engine Online",
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health",
        "analyze": f"{settings.API_V1_STR}/analyze"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
