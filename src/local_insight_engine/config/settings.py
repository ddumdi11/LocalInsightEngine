"""
Application settings and configuration.
"""

import os
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings using Pydantic for validation."""
    
    # General settings
    app_name: str = "LocalInsightEngine"
    app_version: str = "0.1.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # File processing settings
    max_file_size_mb: int = Field(default=50, env="MAX_FILE_SIZE_MB")
    supported_formats: list[str] = Field(
        default=["pdf", "txt", "epub", "mobi"], 
        env="SUPPORTED_FORMATS"
    )
    
    # Text processing settings
    chunk_size: int = Field(default=1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, env="CHUNK_OVERLAP")
    
    # NER settings
    spacy_model: str = Field(default="de_core_news_sm", env="SPACY_MODEL")
    
    # External API settings
    llm_api_key: Optional[str] = Field(default=None, env="LLM_API_KEY")
    llm_model: str = Field(default="claude-3-sonnet-20240229", env="LLM_MODEL")
    llm_base_url: Optional[str] = Field(default=None, env="LLM_BASE_URL")
    
    # Storage settings
    data_dir: Path = Field(
        default=Path.home() / ".local_insight_engine",
        env="DATA_DIR"
    )
    cache_dir: Path = Field(
        default=Path.home() / ".local_insight_engine" / "cache",
        env="CACHE_DIR"
    )
    
    # Security settings
    max_api_requests_per_minute: int = Field(default=20, env="MAX_API_REQUESTS")
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)