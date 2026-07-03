from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    postgres_db: str = "neuroflow"
    postgres_user: str = "neuroflow"
    postgres_password: str = "neuroflow_secret"
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    
    redis_password: str = "redis_secret"
    redis_host: str = "redis"
    redis_port: int = 6379
    
    mlflow_tracking_uri: str = "http://mlflow:5000"
    
    class Config:
        env_file = "../.env"

settings = Settings()
