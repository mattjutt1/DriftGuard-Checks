"""
Application configuration module using Pydantic settings.
"""
from typing import List, Optional
from pydantic import BaseSettings, validator
import os


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Database
    database_url: str = "sqlite:///./promptevolver.db"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # JWT
    secret_key: str = "your-super-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:7b-instruct-q4_0"
    
    # PromptWizard
    promptwizard_mutate_refine_iterations: int = 3
    promptwizard_mutation_rounds: int = 3
    promptwizard_seen_set_size: int = 25
    promptwizard_few_shot_count: int = 3
    promptwizard_generate_reasoning: bool = True
    promptwizard_generate_expert_identity: bool = True
    promptwizard_temperature: float = 0.7
    promptwizard_max_tokens: int = 1024
    
    # API
    api_v1_str: str = "/api/v1"
    project_name: str = "PromptEvolver"
    version: str = "1.0.0"
    description: str = "AI-powered prompt optimization using PromptWizard framework"
    
    # CORS
    backend_cors_origins: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    @validator("backend_cors_origins", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_burst: int = 10
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    @property
    def promptwizard_config(self) -> dict:
        """Get PromptWizard configuration as dictionary."""
        return {
            "mutate_refine_iterations": self.promptwizard_mutate_refine_iterations,
            "mutation_rounds": self.promptwizard_mutation_rounds,
            "seen_set_size": self.promptwizard_seen_set_size,
            "few_shot_count": self.promptwizard_few_shot_count,
            "generate_reasoning": self.promptwizard_generate_reasoning,
            "generate_expert_identity": self.promptwizard_generate_expert_identity,
            "temperature": self.promptwizard_temperature,
            "max_tokens": self.promptwizard_max_tokens
        }
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()