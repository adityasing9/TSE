import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv, set_key

# Ensure parent directories exist
DATA_DIR = Path.home() / ".examai"
DATA_DIR.mkdir(parents=True, exist_ok=True)
ENV_PATH = DATA_DIR / ".env"

# If local .env doesn't exist in DATA_DIR, copy from current directory or create it
if not ENV_PATH.exists():
    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.write(
            "# ExamAI CLI Configuration\n"
            "DB_HOST=localhost\n"
            "DB_PORT=3306\n"
            "DB_USER=root\n"
            "DB_PASSWORD=\n"
            "DB_NAME=examai\n"
            "OPENROUTER_API_KEY=\n"
            "GEMINI_API_KEY=\n"
            "OLLAMA_HOST=http://localhost:11434\n"
            "DEFAULT_PROVIDER=gemini\n"
            "OPENROUTER_MODEL=google/gemini-2.5-flash\n"
            "GEMINI_MODEL=gemini-2.5-flash\n"
            "OLLAMA_MODEL=llama3\n"
            "THEME=cyber\n"
            "LANGUAGE=english\n"
        )

# Load the environment from the home directory .env file
load_dotenv(dotenv_path=ENV_PATH)

class Settings(BaseSettings):
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "3306"))
    db_user: str = os.getenv("DB_USER", "root")
    db_password: str = os.getenv("DB_PASSWORD", "")
    db_name: str = os.getenv("DB_NAME", "examai")
    
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    
    default_provider: str = os.getenv("DEFAULT_PROVIDER", "gemini")  # gemini, openrouter, or ollama
    openrouter_model: str = os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3")
    
    theme: str = os.getenv("THEME", "cyber")
    language: str = os.getenv("LANGUAGE", "english")
    
    # We ignore standard environment variables from process env if needed
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore"
    )

def get_settings() -> Settings:
    """Returns the loaded settings instance."""
    return Settings()

def update_config_key(key: str, value: str) -> None:
    """Updates a configuration setting in the .env file and environment."""
    os.environ[key.upper()] = value
    set_key(str(ENV_PATH), key.upper(), value)
