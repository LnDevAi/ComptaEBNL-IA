import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    app_name: str = "ComptaOHADA-IA"
    app_version: str = "2.0.0"
    description: str = "Plateforme de comptabilité OHADA avec IA intégrée"
    debug: bool = False
    
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/comptaohada"
    database_url_test: str = "postgresql://user:password@localhost:5432/comptaohada_test"
    
    # Security
    secret_key: str = "ComptaOHADA-IA-Secret-Key-2024-SYSCEBNL-OHADA-v2"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # CORS
    cors_origins: list = ["http://localhost:3000", "https://app.comptaohada.ai"]
    
    # AI Configuration
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4-turbo-preview"
    
    # OCR Configuration
    tesseract_path: Optional[str] = None  # Path to tesseract executable
    
    # Email Configuration
    mail_username: Optional[str] = None
    mail_password: Optional[str] = None
    mail_from: str = "noreply@comptaohada.ai"
    mail_port: int = 587
    mail_server: str = "smtp.gmail.com"
    mail_from_name: str = "ComptaOHADA-IA"
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379"
    
    # Stripe Configuration
    stripe_secret_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    
    # File Storage
    upload_path: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    # OHADA Configuration
    syscebnl_version: str = "2024"
    ohada_countries: list = [
        "BJ", "BF", "CM", "CF", "TD", "KM", "CI", "CD", 
        "GQ", "GA", "GN", "GW", "ML", "NE", "CG", "SN", "TG"
    ]
    
    # Subscription Plans
    subscription_plans: dict = {
        "starter": {
            "name": "Starter",
            "price": 0,
            "currency": "EUR",
            "max_organizations": 1,
            "max_entries_per_month": 50,
            "features": ["basic_reports", "email_support"]
        },
        "professional": {
            "name": "Professional", 
            "price": 50,
            "currency": "EUR",
            "max_organizations": 5,
            "max_entries_per_month": -1,  # Unlimited
            "features": ["ai_assistant", "priority_support", "advanced_reports"]
        },
        "enterprise": {
            "name": "Enterprise",
            "price": -1,  # Custom pricing
            "currency": "EUR", 
            "max_organizations": -1,  # Unlimited
            "max_entries_per_month": -1,  # Unlimited
            "features": ["custom_api", "dedicated_support", "training", "sla"]
        }
    }
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class DevelopmentSettings(Settings):
    debug: bool = True
    database_url: str = "sqlite:///./comptaohada_dev.db"
    log_level: str = "DEBUG"


class ProductionSettings(Settings):
    debug: bool = False
    log_level: str = "WARNING"


class TestSettings(Settings):
    database_url: str = "sqlite:///./test_comptaohada.db"
    testing: bool = True


def get_settings() -> Settings:
    environment = os.getenv("ENVIRONMENT", "development")
    
    if environment == "development":
        return DevelopmentSettings()
    elif environment == "production":
        return ProductionSettings()
    elif environment == "testing":
        return TestSettings()
    else:
        return DevelopmentSettings()


settings = get_settings()
