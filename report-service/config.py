"""
Configuration for Report Service
Handles all settings for chart generation, PDF settings, and deployment
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Service Configuration
    SERVICE_NAME: str = "Report Service"
    SERVICE_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Server Configuration
    HOST: str = os.getenv('HOST', '0.0.0.0')
    PORT: int = int(os.getenv('PORT', 8001))
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.resolve()
    TEMPLATES_DIR: Path = BASE_DIR / 'templates'
    CHARTS_TEMP_DIR: Path = BASE_DIR / 'temp' / 'charts'
    
    # Chart Configuration
    CHART_DPI: int = 100
    CHART_WIDTH: int = 8
    CHART_HEIGHT: int = 6
    CHART_COLORS: list = [
        '#e74c3c', '#e67e22', '#f39c12', '#d35400', 
        '#c0392b', '#a93226', '#7f8c8d', '#34495e',
        '#16a085', '#27ae60', '#2980b9', '#8e44ad'
    ]
    
    # PDF Configuration
    PDF_PAGE_SIZE: str = 'A4'  # A4 or letter
    PDF_MARGIN_TOP: float = 0.5  # inches
    PDF_MARGIN_BOTTOM: float = 0.5
    PDF_MARGIN_LEFT: float = 0.75
    PDF_MARGIN_RIGHT: float = 0.75
    PDF_FONT_DEFAULT: str = 'Helvetica'
    PDF_FONT_BOLD: str = 'Helvetica-Bold'
    
    # Jinja2 Template Configuration
    TEMPLATE_AUTO_RELOAD: bool = True
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    # CORS Configuration (for frontend access)
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://expense-traker-frontend.vercel.app",
        "https://expense-tracker-api.railway.app"
    ]
    
    # Backend Service Integration
    BACKEND_BASE_URL: str = os.getenv(
        'BACKEND_BASE_URL', 
        'http://localhost:9000'
    )
    
    class Config:
        env_file = '.env'
        case_sensitive = True


# Create singleton settings instance
settings = Settings()

# Ensure required directories exist
settings.CHARTS_TEMP_DIR.mkdir(parents=True, exist_ok=True)
settings.TEMPLATES_DIR.mkdir(exist_ok=True)
