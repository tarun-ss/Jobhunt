"""
Configuration settings for JobHunter AI
Loads environment variables and provides centralized config access
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # LLM Configuration
    google_api_key: str  # Google Gemini API key
    llm_model: str = "gemini-2.0-flash-exp"  # or gemini-1.5-pro
    
    # Database URLs (Optional - can use SQLite)
    postgres_url: str = "sqlite:///jobhunter.db"
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: Optional[str] = None
    neo4j_url: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    redis_url: str = "redis://localhost:6379/0"
    
    # Job Scraping APIs
    jsearch_api_key: Optional[str] = None
    adzuna_api_key: Optional[str] = None
    adzuna_app_id: Optional[str] = None
    
    # Email Configuration
    gmail_client_id: Optional[str] = None
    gmail_client_secret: Optional[str] = None
    gmail_refresh_token: Optional[str] = None
    
    # MCP Server
    mcp_server_url: str = "http://localhost:8000"
    mcp_server_port: int = 8000
    mcp_oauth_client_id: Optional[str] = None
    mcp_oauth_client_secret: Optional[str] = None
    
    # API Server
    api_host: str = "0.0.0.0"
    api_port: int = 8080
    api_workers: int = 4
    api_secret_key: str = "default_secret_key_change_me"
    
    # Observability
    langsmith_api_key: Optional[str] = None
    langsmith_project: str = "jobhunter-ai"
    
    # Feature Flags
    enable_daily_updates: bool = True
    enable_ghost_job_detection: bool = True
    enable_auto_application: bool = False
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_day: int = 1000
    
    # ML Models
    ghost_job_model_path: str = "ml_models/ghost_job_detector/model.pkl"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/jobhunter.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
