


# """
# Configuration centralisée de l'application SÉNTRA
# Utilise Pydantic Settings pour la validation des variables d'environnement
# """

# from typing import List, Optional
# from pydantic import Field, field_validator
# from pydantic_settings import BaseSettings, SettingsConfigDict


# class Settings(BaseSettings):
#     """Configuration principale de l'application"""
    
#     # === APPLICATION ===
#     APP_NAME: str = "SÉNTRA Fraud Detection API"
#     APP_VERSION: str = "1.0.0"
#     APP_DESCRIPTION: str = "Système intelligent de détection de fraude"
#     ENVIRONMENT: str = Field(default="development", pattern="^(development|staging|production)$")
#     DEBUG: bool = True
    
#     # === API ===
#     # API_HOST: str = "0.0.0.0"
#     API_HOST: str = "localhost"  # 🔧 Changer de "0.0.0.0" à "localhost"
#     API_PORT: int = 8000
#     API_PREFIX: str = "/api/v1"
#     API_WORKERS: int = 4
    
#     # === SECURITY ===
#     SECRET_KEY: str
#     ALGORITHM: str = "HS256"
#     ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
#     # === CORS ===
#     ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

#     CORS_ALLOW_CREDENTIALS: bool = True
#     CORS_ALLOW_METHODS: str = "GET,POST,PUT,DELETE,OPTIONS"
#     CORS_ALLOW_HEADERS: str = "*"
    
#     # === DATABASE ===
#     DATABASE_URL: str
#     DB_ECHO: bool = False
#     DB_POOL_SIZE: int = 10
#     DB_MAX_OVERFLOW: int = 20
#     # ATTRIBUT AJOUTÉ pour résoudre l'AttributeError dans main.py
#     RUN_DB_SEEDING: bool = False 
    
#     # === REDIS ===
#     REDIS_URL: str = "redis://localhost:6379/0"
#     REDIS_PASSWORD: Optional[str] = None
#     REDIS_TTL: int = 3600
    
#     # === MACHINE LEARNING ===
#     ML_MODEL_PATH: str = "./data/models/production"
#     ML_MODEL_NAME: str = "fraud_model_v1.pkl"
#     ML_PREPROCESSING_PIPELINE: str = "preprocessing_pipeline.pkl"
#     ML_THRESHOLD: float = Field(default=0.85, ge=0.0, le=1.0)
#     ML_BATCH_SIZE: int = 32
    
#     # === LOGGING ===
#     LOG_LEVEL: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
#     LOG_FORMAT: str = Field(default="json", pattern="^(json|text)$")
#     LOG_FILE_PATH: str = "./logs/sentra.log"
#     LOG_ROTATION: str = "500 MB"
    
#     # === KAFKA ===
#     KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
#     KAFKA_TOPIC_TRANSACTIONS: str = "transactions"
#     KAFKA_TOPIC_ALERTS: str = "fraud_alerts"
#     KAFKA_ENABLED: bool = False
    
#     # === MONITORING ===
#     ENABLE_METRICS: bool = True
#     PROMETHEUS_PORT: int = 9090
    
#     # === EMAIL ===
#     SMTP_HOST: Optional[str] = None
#     SMTP_PORT: int = 587
#     SMTP_USER: Optional[str] = None
#     SMTP_PASSWORD: Optional[str] = None
#     ALERT_EMAIL_FROM: Optional[str] = None
#     ALERT_EMAIL_TO: Optional[str] = None
    
#     # === RATE LIMITING ===
#     RATE_LIMIT_ENABLED: bool = True
#     RATE_LIMIT_PER_MINUTE: int = 60
    
#     # Configuration du modèle Pydantic
#     model_config = SettingsConfigDict(
#         env_file=".env",
#         env_file_encoding="utf-8",
#         case_sensitive=True,
#         extra="ignore"
#     )
    
#     # === VALIDATORS ===
    
#     @field_validator("SECRET_KEY")
#     @classmethod
#     def validate_secret_key(cls, v: str) -> str:
#         """Valide que la clé secrète est suffisamment longue"""
#         if len(v) < 32:
#             raise ValueError("SECRET_KEY doit avoir au moins 32 caractères")
#         return v
    
#     @field_validator("DATABASE_URL")
#     @classmethod
#     def validate_database_url(cls, v: str) -> str:
#         """Valide le format de l'URL de base de données"""
#         if not v.startswith("postgresql://"):
#             raise ValueError("DATABASE_URL doit commencer par 'postgresql://'")
#         return v
    
#     # === PROPRIÉTÉS CALCULÉES ===
    
#     @property
#     def is_production(self) -> bool:
#         """Vérifie si l'environnement est production"""
#         return self.ENVIRONMENT == "production"
    
#     @property
#     def is_development(self) -> bool:
#         """Vérifie si l'environnement est développement"""
#         return self.ENVIRONMENT == "development"
    
#     @property
#     def allowed_origins_list(self) -> List[str]:
#         """Retourne la liste des origines CORS autorisées"""
#         return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
#     @property
#     def full_model_path(self) -> str:
#         """Retourne le chemin complet du modèle ML"""
#         return f"{self.ML_MODEL_PATH}/{self.ML_MODEL_NAME}"
    
#     @property
#     def full_preprocessing_path(self) -> str:
#         """Retourne le chemin complet du pipeline de preprocessing"""
#         return f"{self.ML_MODEL_PATH}/{self.ML_PREPROCESSING_PIPELINE}"


# # === INSTANCE GLOBALE ===
# settings = Settings()


# # === FONCTION HELPER ===
# def get_settings() -> Settings:
#     """
#     Fonction helper pour injecter les settings dans FastAPI
#     Usage: settings = Depends(get_settings)
#     """
#     return settings

"""
Configuration centralisée de l'application SÉNTRA
Utilise Pydantic Settings pour la validation des variables d'environnement
"""

import os
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration principale de l'application"""
    
    # === APPLICATION ===
    APP_NAME: str = "SÉNTRA Fraud Detection API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Système intelligent de détection de fraude"
    ENVIRONMENT: str = Field(default="development", pattern="^(development|staging|production)$")
    DEBUG: bool = True
    
    # === API ===
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    API_WORKERS: int = 4
    
    # === SECURITY ===
    SECRET_KEY: str = Field(default="default-secret-key-change-in-production-min-32-chars")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # === CORS ===
    ALLOWED_ORIGINS: str = Field(default="http://localhost:3000,http://localhost:5173")
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: str = "GET,POST,PUT,DELETE,OPTIONS,PATCH"
    CORS_ALLOW_HEADERS: str = "*"
    
    # === DATABASE ===
    DATABASE_URL: str = Field(default="postgresql://user:pass@localhost:5432/db")
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    RUN_DB_SEEDING: bool = False 
    
    # === REDIS ===
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None
    REDIS_TTL: int = 3600
    
    # === MACHINE LEARNING ===
    ML_MODEL_PATH: str = "./data/models/production"
    ML_MODEL_NAME: str = "fraud_model_v1.pkl"
    ML_PREPROCESSING_PIPELINE: str = "preprocessing_pipeline.pkl"
    ML_THRESHOLD: float = Field(default=0.85, ge=0.0, le=1.0)
    ML_BATCH_SIZE: int = 32
    
    # === LOGGING ===
    LOG_LEVEL: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    LOG_FORMAT: str = Field(default="json", pattern="^(json|text)$")
    LOG_FILE_PATH: str = "./logs/sentra.log"
    LOG_ROTATION: str = "500 MB"
    
    # === KAFKA ===
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_TRANSACTIONS: str = "transactions"
    KAFKA_TOPIC_ALERTS: str = "fraud_alerts"
    KAFKA_ENABLED: bool = False
    
    # === MONITORING ===
    ENABLE_METRICS: bool = True
    PROMETHEUS_PORT: int = 9090
    
    # === EMAIL ===
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    ALERT_EMAIL_FROM: Optional[str] = None
    ALERT_EMAIL_TO: Optional[str] = None
    
    # === RATE LIMITING ===
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Configuration du modèle Pydantic
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
        env_prefix="SENTRA_"
    )
    
    # === VALIDATORS ===
    
    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Valide que la clé secrète est suffisamment longue"""
        if len(v) < 32 and os.getenv("ENVIRONMENT") == "production":
            raise ValueError("SECRET_KEY doit avoir au moins 32 caractères en production")
        return v
    
    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Valide le format de l'URL de base de données"""
        if not v.startswith("postgresql://"):
            if os.getenv("ENVIRONMENT") == "production":
                raise ValueError("DATABASE_URL doit commencer par 'postgresql://'")
        return v
    
    # === PROPRIÉTÉS CALCULÉES ===
    
    @property
    def is_production(self) -> bool:
        """Vérifie si l'environnement est production"""
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        """Vérifie si l'environnement est développement"""
        return self.ENVIRONMENT == "development"
    
    @property
    def is_render(self) -> bool:
        """Vérifie si l'application tourne sur Render.com"""
        return os.getenv("RENDER", "").lower() in ["true", "yes", "1"]
    
    @property
    def render_external_url(self) -> str:
        """Récupère l'URL externe Render depuis les variables d'environnement"""
        return os.getenv("RENDER_EXTERNAL_URL", "")
    
    @property
    def render_service_name(self) -> str:
        """Récupère le nom du service Render"""
        return os.getenv("RENDER_SERVICE_NAME", "")

    @property
    def allowed_origins_list(self) -> List[str]:
        """Retourne la liste des origines CORS autorisées"""
        # Pour Render/Production
        if self.is_render or self.is_production:
            origins = [
                "https://sentra-frontend.onrender.com",
                "https://sentra-backend.onrender.com",
                "https://*.onrender.com",
            ]
            
            # Ajouter le frontend URL si défini
            frontend_url = os.getenv("FRONTEND_URL")
            if frontend_url:
                origins.append(frontend_url)
            
            return origins
        
        # Pour développement local
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
        
    @property
    def full_model_path(self) -> str:
        """Retourne le chemin complet du modèle ML"""
        return f"{self.ML_MODEL_PATH}/{self.ML_MODEL_NAME}"
    
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def fix_render_database_url(cls, v: str) -> str:
        """Corrige l'URL de base de données pour Render"""
        # Render utilise 'postgres://' mais SQLAlchemy veut 'postgresql://'
        if v and "postgres://" in v:
            corrected = v.replace("postgres://", "postgresql://", 1)
            print(f"🔧 URL DB corrigée: {corrected}")
            return corrected
        return v

    @property
    def full_preprocessing_path(self) -> str:
        """Retourne le chemin complet du pipeline de preprocessing"""
        return f"{self.ML_MODEL_PATH}/{self.ML_PREPROCESSING_PIPELINE}"
    

    @property
    def cors_allow_methods_list(self) -> List[str]:
        """Retourne la liste des méthodes CORS autorisées"""
        return [method.strip() for method in self.CORS_ALLOW_METHODS.split(",")]
    
    @property
    def cors_allow_headers_list(self) -> List[str]:
        """Retourne la liste des headers CORS autorisés"""
        return [header.strip() for header in self.CORS_ALLOW_HEADERS.split(",")]
        
# === INSTANCE GLOBALE ===
settings = Settings()


# === FONCTION HELPER ===
def get_settings() -> Settings:
    """
    Fonction helper pour injecter les settings dans FastAPI
    Usage: settings = Depends(get_settings)
    """
    return settings