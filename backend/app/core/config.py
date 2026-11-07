import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")

    PROJECT_NAME: str = "BizGuard AI"
    API_V1_STR: str = "/api/v1"
    
    # Database - Supports PostgreSQL or local SQLite async fallback
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./bizguard.db"
    )
    
    # Multi-Agent Switch Protocol
    SWITCH_BUS_URL: str = os.getenv("SWITCH_BUS_URL", "ws://127.0.0.1:8765/switch-bus")
    SWITCH_AGENT_ID: str = os.getenv("SWITCH_AGENT_ID", "bizguard-orchestrator-01")
    
    # Mattermost Webhook
    MATTERMOST_WEBHOOK_URL: Optional[str] = os.getenv("MATTERMOST_WEBHOOK_URL", None)
    MATTERMOST_CHANNEL: str = os.getenv("MATTERMOST_CHANNEL", "#bizguard-war-room")
    
    # LLM Reasoning Provider
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY", None)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    DEFAULT_LLM_PROVIDER: str = os.getenv("DEFAULT_LLM_PROVIDER", "anthropic")
    
settings = Settings()
