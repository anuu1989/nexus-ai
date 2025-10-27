"""
Core Configuration Module
========================
Centralized configuration management for NexusAI
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class AppConfig:
    """Main application configuration"""
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'ai-assistant-secret-key-2024')
    PORT: int = int(os.getenv('PORT', 5000))
    DEBUG: bool = os.getenv('DEBUG', 'True').lower() == 'true'
    WORKERS: int = int(os.getenv('WORKERS', 4))

@dataclass
class AIConfig:
    """AI provider configuration"""
    GROQ_API_KEY: Optional[str] = os.getenv('GROQ_API_KEY')
    OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')
    ANTHROPIC_API_KEY: Optional[str] = os.getenv('ANTHROPIC_API_KEY')
    GOOGLE_API_KEY: Optional[str] = os.getenv('GOOGLE_API_KEY')
    HUGGINGFACE_API_KEY: Optional[str] = os.getenv('HUGGINGFACE_API_KEY')
    OLLAMA_BASE_URL: str = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')

@dataclass
class DatabaseConfig:
    """Database configuration"""
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///nexusai.db')
    DATABASE_POOL_SIZE: int = int(os.getenv('DATABASE_POOL_SIZE', 10))

# Global configuration instances
app_config = AppConfig()
ai_config = AIConfig()
db_config = DatabaseConfig()

def get_app_config() -> AppConfig:
    """Get application configuration"""
    return app_config

def get_ai_config() -> AIConfig:
    """Get AI configuration"""
    return ai_config

def get_db_config() -> DatabaseConfig:
    """Get database configuration"""
    return db_config