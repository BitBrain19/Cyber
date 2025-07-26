from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    """
    Application configuration settings, loaded from environment variables or defaults.
    Organized by category: server, security, database, ML, monitoring, etc.
    """
    # Application
    APP_NAME: str = "SecurityAI Backend"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://app.securityai.com"
    ]
    
    # Allowed Hosts
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Database - PostgreSQL
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "securityai"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "securityai"
    POSTGRES_URL: Optional[str] = None
    
    # Database - InfluxDB
    INFLUXDB_URL: str = "http://localhost:8086"
    INFLUXDB_TOKEN: str = "your-influxdb-token"
    INFLUXDB_ORG: str = "securityai"
    INFLUXDB_BUCKET: str = "security_events"
    
    # Database - Elasticsearch
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    ELASTICSEARCH_USERNAME: str = "elastic"
    ELASTICSEARCH_PASSWORD: str = "password"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_PASSWORD: Optional[str] = None
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_EVENTS: str = "security_events"
    KAFKA_TOPIC_LOGS: str = "security_logs"
    KAFKA_TOPIC_THREAT_INTEL: str = "threat_intelligence"
    
    # ML Pipeline
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"
    ML_MODELS_PATH: str = "./models"
    MODEL_RETRAIN_INTERVAL_HOURS: int = 168  # Weekly
    
    # Security Intelligence APIs
    VIRUSTOTAL_API_KEY: Optional[str] = None
    ALIENVAULT_OTX_API_KEY: Optional[str] = None
    MITRE_ATTACK_URL: str = "https://attack.mitre.org/versions/v13/enterprise/enterprise.json"
    
    # AWS S3 (for backups and cold storage)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: str = "securityai-backups"
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    PROMETHEUS_PORT: int = 9090
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "./uploads"
    
    # Circuit Breaker
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 5
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT: int = 60
    
    # Gemini Integration
    USE_GEMINI_FOR_LOGS: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Build PostgreSQL URL if not provided
        if not self.POSTGRES_URL:
            self.POSTGRES_URL = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        
        # Set environment-specific settings
        if self.ENVIRONMENT == "production":
            self.DEBUG = False
            self.LOG_LEVEL = "WARNING"
        elif self.ENVIRONMENT == "development":
            self.DEBUG = True
            self.LOG_LEVEL = "DEBUG"

# Create settings instance
settings = Settings()

# Validate required settings for production
if settings.ENVIRONMENT == "production":
    required_settings = [
        "SECRET_KEY",
        "POSTGRES_PASSWORD",
        "INFLUXDB_TOKEN",
        "ELASTICSEARCH_PASSWORD"
    ]
    
    missing_settings = [setting for setting in required_settings 
                       if not getattr(settings, setting) or getattr(settings, setting) == "password"]
    
    if missing_settings:
        raise ValueError(f"Missing required settings for production: {missing_settings}") 