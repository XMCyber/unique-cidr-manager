"""
Configuration management for the CIDR Manager application.

This module handles all configuration settings using environment variables
with sensible defaults and validation.
"""

import os
import logging
from functools import lru_cache
from typing import Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Server configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    debug: bool = Field(default=False, description="Debug mode")
    
    # Git configuration
    access_token: str = Field(..., description="GitHub access token")
    occupied_repo: str = Field(..., description="GitHub repository for occupied CIDRs")
    occupied_file: str = Field(default="occupied-range.json", description="Occupied CIDRs filename")
    git_dest_dir: str = Field(default="infra", description="Local git repository directory")
    
    # Git committer information
    committer_name: str = Field(default="Unique CIDR Manager", description="Git committer name")
    committer_email: str = Field(default="cidr@manager.dev", description="Git committer email")
    
    # Application configuration
    log_level: str = Field(default="INFO", description="Logging level")
    max_reason_length: int = Field(default=100, description="Maximum length for reason field")
    
    # CORS configuration
    allowed_origins: str = Field(default="*", description="Comma-separated list of allowed origins for CORS")
    
    @property
    def https_remote_url(self) -> str:
        """Construct the HTTPS remote URL for Git operations."""
        return f"https://{self.access_token}@github.com/{self.occupied_repo}"
    
    @property
    def cors_origins(self) -> list:
        """Parse allowed origins from comma-separated string."""
        if self.allowed_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]
    
    @validator('access_token')
    def validate_access_token(cls, v):
        """Validate GitHub access token is provided."""
        if not v:
            raise ValueError("GitHub access token is required")
        return v
    
    @validator('occupied_repo')
    def validate_occupied_repo(cls, v):
        """Validate repository format."""
        if not v or '/' not in v:
            raise ValueError("Repository must be in format 'owner/repo'")
        return v
    
    @validator('port')
    def validate_port(cls, v):
        """Validate port number."""
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,  # Keep exact case for env vars
        "extra": "ignore"
    }

@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings (cached).
    
    Returns:
        Settings: Application configuration
        
    Raises:
        ValueError: If required environment variables are missing or invalid
    """
    try:
        settings = Settings()
        
        # Configure logging based on settings
        logging.basicConfig(
            level=getattr(logging, settings.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Set Git Python to quiet mode
        os.environ["GIT_PYTHON_REFRESH"] = "quiet"
        
        logger.info(f"Configuration loaded successfully")
        logger.info(f"Server will run on {settings.host}:{settings.port}")
        logger.info(f"Git repository: {settings.occupied_repo}")
        logger.info(f"Debug mode: {settings.debug}")
        
        return settings
        
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        logger.error("Please ensure all required environment variables are set:")
        logger.error("- access_token: GitHub personal access token")
        logger.error("- occupied_repo: GitHub repository in format 'owner/repo'")
        logger.error("Note: Variable names are case-sensitive and must be lowercase (same as original system)")
        raise

def validate_environment() -> bool:
    """
    Validate that all required environment variables are present.
    
    Returns:
        bool: True if environment is valid
        
    Raises:
        SystemExit: If required variables are missing
    """
    # Use EXACT same environment variable names as original system
    required_vars = ['access_token', 'occupied_repo']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error("Missing required environment variables:")
        for var in missing_vars:
            logger.error(f"  - {var}")
        logger.error("\nPlease set these variables and restart the application.")
        logger.error("Note: Variable names are case-sensitive and must be lowercase (same as original system)")
        return False
    
    return True

def get_version() -> str:
    """Get application version."""
    return "3.0.0"

def get_app_info() -> dict:
    """Get application information for health checks and documentation."""
    settings = get_settings()
    return {
        "name": "CIDR Manager",
        "version": get_version(),
        "description": "A comprehensive CIDR management system for network address allocation",
        "host": settings.host,
        "port": settings.port,
        "debug": settings.debug,
        "repository": settings.occupied_repo
    }
