"""
Configuration management for ML Inference Service.
Loads settings from environment variables with sensible defaults.
"""

from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """ML Service configuration."""
    
    # Service
    service_name: str = "ml-inference"
    service_version: str = "1.0.0"
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Models
    model_path: str = "models/expense_category_model.pkl"
    vectorizer_path: str = "models/tfidf_vectorizer.pkl"
    model_preload: bool = True
    
    # Performance
    workers: int = 1
    timeout: int = 30
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Validation
    max_description_length: int = 500
    min_description_length: int = 1
    
    class Config:
        env_prefix = "ML_SERVICE_"
        case_sensitive = False
        env_file = ".env"


# Global settings instance
settings = Settings()
