from typing import List, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import json


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Redis Configuration
    REDIS_URL: str
    
    # Google Cloud Configuration
    GOOGLE_CLOUD_PROJECT: str
    GOOGLE_APPLICATION_CREDENTIALS: str
    GCS_BUCKET_NAME: str
    
    # Vertex AI Configuration
    VERTEX_AI_LOCATION: str = "us-central1"
    
    # Gemini API Configuration
    GEMINI_API_KEY: str
    
    # Application Configuration
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(",")]
        return v
    
    # File Upload Configuration
    MAX_UPLOAD_SIZE_MB: int = 10240
    ALLOWED_EXTENSIONS: str = ".csv,.json,.jpg,.jpeg,.png,.txt"
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",")]
    
    # Training Configuration
    MAX_TRAINING_HOURS: int = 24
    MAX_ITERATIONS: int = 5
    MAX_CONCURRENT_PROJECTS_PER_USER: int = 5
    
    # Security Configuration
    DATA_RETENTION_DAYS: int = 90
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"
    
    @property
    def max_upload_size_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024


settings = Settings()
