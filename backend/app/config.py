import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "WebGuard Fraud Risk Engine"
    API_V1_STR: str = "/api/v1"
    PORT: int = 8001
    HOST: str = "0.0.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Database: SQLite fallback by default for instant local execution
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./webguard.db")
    
    # External threat intelligence APIs (Optional, mocks used when absent)
    WHOIS_API_KEY: str = os.getenv("WHOIS_API_KEY", "")
    THREAT_INTEL_API_KEY: str = os.getenv("THREAT_INTEL_API_KEY", "")
    PRICE_API_KEY: str = os.getenv("PRICE_API_KEY", "")
    
    # ML settings
    ENABLE_ISOLATION_FOREST: bool = True
    
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

settings = Settings()
