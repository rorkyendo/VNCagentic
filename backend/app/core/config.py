from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    SECRET_KEY: str = "change-this-in-production"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/vncagentic"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # LLM Provider Configuration
    API_PROVIDER: str = "comet"  # comet, anthropic, openai, ollama
    
    # CometAPI Configuration
    COMET_API_BASE_URL: str = "https://api.cometapi.com/v1"
    COMET_API_KEY: str = os.getenv("COMET_API_KEY", "")
    COMET_MODEL: str = "cometapi-3-7-sonnet"
    COMET_MAX_TOKENS: int = 1024
    
    # Original Anthropic Configuration
    ANTHROPIC_API_URL: str = "https://api.anthropic.com/v1"
    
    # OpenAI Configuration (Alternative)
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_MAX_TOKENS: int = 4096
    
    # Ollama Configuration (Local/Free)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama2"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Anthropic API
    ANTHROPIC_API_KEY: str = ""
    
    # Agent Configuration
    MAX_SESSIONS: int = 10
    SESSION_TIMEOUT_MINUTES: int = 60
    MAX_OUTPUT_TOKENS: int = 4096
    DEFAULT_MODEL: str = "claude-sonnet-4-20250514"
    
    # VNC Configuration
    VNC_PASSWORD: str = "vncpassword"
    VNC_DISPLAY: str = ":1"
    WIDTH: int = 1024
    HEIGHT: int = 768
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
