from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/lente_cidada"
    REDIS_URL: str = "redis://localhost:6379/0"
    GEMINI_API_KEY: str = ""
    # Local dev/testing: disable real API calls when true
    GEMINI_MOCK: bool = False
    # Vertex / GenAI endpoint configuration
    GOOGLE_GENAI_USE_VERTEXAI: bool = False
    GOOGLE_CLOUD_PROJECT: str | None = None
    GOOGLE_CLOUD_LOCATION: str | None = None
    # Optional explicit Gemini/GenAI base URL (useful for proxies or overrides)
    GEMINI_API_ENDPOINT: str | None = None
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
