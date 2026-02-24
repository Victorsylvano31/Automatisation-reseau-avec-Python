from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "NRE Platform V2"
    
    # Base de données locale (SQLite ne nécessite pas d'installation séparée)
    DATABASE_URL: str = "sqlite:///./nre_platform.db"
    
    # Configuration Celery "Eager" (Exécute les tâches de manière synchrone pendant le Dev sans besoin de Redis)
    CELERY_TASK_ALWAYS_EAGER: bool = True
    
    # Fallback Credentials
    DEFAULT_USERNAME: str = "admin"
    DEFAULT_PASSWORD: str = "cisco"
    
    class Config:
        env_file = ".env"

settings = Settings()
