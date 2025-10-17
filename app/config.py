from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    API_RATE_LIMIT: int = 1000  # requests per day
    API_RATE_WINDOW: int = 86400  # seconds in a day
    REDIS_URL: str = "redis://redis:6379/0"
    DATABASE_URL: str = "postgresql+psycopg2://user:password@db:5432/apidb"
    BILLING_UNIT_PRICE: float = 0.01

    # Database pool tuning
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 40
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800  # seconds

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
