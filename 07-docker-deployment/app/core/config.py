from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """
    Centralized configuration.
    Reads from .env file OR environment variables (env vars have priority).
    """
    
    # Ollama
    ollama_base_url: str = Field(default="http://localhost:11434")
    ollama_model: str = Field(default="qwen2.5:7b")
    ollama_temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    ollama_timeout: float = Field(default=300.0)
    
    # API
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_env: str = Field(default="development")
    
    # Logging
    log_level: str = Field(default="INFO")
    
    # Pydantic V2: указываем откуда читать конфиг
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,  # OLLAMA_BASE_URL и ollama_base_url — одно и то же
        extra="ignore"         # Игнорируем лишние переменные из .env
    )


# Singleton — создаём ОДИН раз при импорте
settings = Settings()

if __name__ == "__main__":
    # Для отладки — можно запустить и увидеть, что загрузилось
    print(settings.model_dump_json(indent=2))
