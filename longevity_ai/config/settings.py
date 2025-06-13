"""
Application configuration management using Pydantic Settings.
Handles environment variables, validation, and configuration hierarchy.
"""
import os
from functools import lru_cache
from typing import List, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support and validation."""
    
    # ==========================================
    # Application Information
    # ==========================================
    app_name: str = Field(default="Longevity AI Assistant")
    app_version: str = Field(default="0.1.0")
    environment: str = Field(default="development")
    debug: bool = Field(default=False)
    
    # ==========================================
    # API Configuration
    # ==========================================
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000, ge=1, le=65535)
    api_workers: int = Field(default=1, ge=1, le=32)
    
    # ==========================================
    # OpenAI Configuration
    # ==========================================
    openai_api_key: str = Field(..., description="OpenAI API key", min_length=10)
    openai_model: str = Field(default="gpt-4o-mini")
    openai_embedding_model: str = Field(default="text-embedding-3-small")
    openai_temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    openai_max_tokens: int = Field(default=1000, ge=1, le=4000)
    
    # ==========================================
    # Supabase Configuration
    # ==========================================
    supabase_url: str = Field(..., description="Supabase project URL")
    supabase_key: str = Field(..., description="Supabase anon key", min_length=10)
    supabase_table_name: str = Field(default="longevity_knowledge")
    
    # ==========================================
    # Vector Store Configuration
    # ==========================================
    embedding_dimensions: int = Field(default=1536, ge=1, le=3072)
    chunk_size: int = Field(default=1000, ge=100, le=4000)
    chunk_overlap: int = Field(default=200, ge=0, le=1000)
    max_chunks_per_doc: int = Field(default=50, ge=1, le=200)
    
    # ==========================================
    # Retrieval Configuration
    # ==========================================
    default_top_k: int = Field(default=5, ge=1, le=20)
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    max_context_length: int = Field(default=4000, ge=1000, le=8000)
    
    # ==========================================
    # Security & Rate Limiting
    # ==========================================
    allowed_origins: List[str] = Field(default=["*"])
    api_key_header: str = Field(default="X-API-Key")
    rate_limit_requests: int = Field(default=100, ge=1)
    rate_limit_window: int = Field(default=3600, ge=60)  # seconds
    
    # ==========================================
    # Logging Configuration
    # ==========================================
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")
    log_file: Optional[str] = Field(default=None)
    
    # ==========================================
    # Data Paths
    # ==========================================
    data_dir: str = Field(default="data")
    raw_data_dir: str = Field(default="data/raw")
    processed_data_dir: str = Field(default="data/processed")
    embeddings_dir: str = Field(default="data/embeddings")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"
        
    # ==========================================
    # Validators
    # ==========================================
    
    @validator('environment')
    def validate_environment(cls, v):
        """Validate environment setting."""
        allowed = ['development', 'staging', 'production', 'testing']
        if v.lower() not in allowed:
            raise ValueError(f'Environment must be one of: {allowed}')
        return v.lower()
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """Validate log level."""
        allowed = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in allowed:
            raise ValueError(f'Log level must be one of: {allowed}')
        return v.upper()
    
    @validator('log_format')
    def validate_log_format(cls, v):
        """Validate log format."""
        allowed = ['json', 'text', 'console']
        if v.lower() not in allowed:
            raise ValueError(f'Log format must be one of: {allowed}')
        return v.lower()
    
    @validator('openai_api_key')
    def validate_openai_key(cls, v):
        """Basic validation for OpenAI API key format."""
        if not v.startswith('sk-'):
            raise ValueError('OpenAI API key must start with "sk-"')
        return v
    
    @validator('supabase_url')
    def validate_supabase_url(cls, v):
        """Basic validation for Supabase URL format."""
        if not v.startswith('https://'):
            raise ValueError('Supabase URL must start with "https://"')
        if not '.supabase.co' in v:
            raise ValueError('Supabase URL must contain ".supabase.co"')
        return v
    
    @validator('chunk_overlap')
    def validate_chunk_overlap(cls, v, values):
        """Ensure chunk overlap is less than chunk size."""
        if 'chunk_size' in values and v >= values['chunk_size']:
            raise ValueError('Chunk overlap must be less than chunk size')
        return v
    
    # ==========================================
    # Properties
    # ==========================================
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.environment == "testing"
    
    @property
    def database_url(self) -> str:
        """Get formatted database URL."""
        return f"{self.supabase_url}/rest/v1/"
    
    @property
    def full_table_name(self) -> str:
        """Get full table name with any prefixes."""
        return f"public.{self.supabase_table_name}"
    
    # ==========================================
    # Methods
    # ==========================================
    
    def get_data_path(self, filename: str, subdir: str = "processed") -> str:
        """Get full path for a data file."""
        if subdir == "raw":
            return os.path.join(self.raw_data_dir, filename)
        elif subdir == "processed":
            return os.path.join(self.processed_data_dir, filename)
        elif subdir == "embeddings":
            return os.path.join(self.embeddings_dir, filename)
        else:
            return os.path.join(self.data_dir, subdir, filename)
    
    def ensure_data_directories(self) -> None:
        """Ensure all data directories exist."""
        directories = [
            self.data_dir,
            self.raw_data_dir,
            self.processed_data_dir,
            self.embeddings_dir,
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience function for testing
def get_test_settings(**overrides) -> Settings:
    """Get settings for testing with overrides."""
    test_env = {
        'environment': 'testing',
        'debug': True,
        'log_level': 'DEBUG',
        'supabase_table_name': 'test_longevity_knowledge',
        **overrides
    }
    return Settings(**test_env)