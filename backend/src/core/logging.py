# """
# Configuration du système de logging pour SÉNTRA
# Utilise Loguru pour des logs structurés et performants
# """

# import sys
# from pathlib import Path
# from loguru import logger
# from .config import settings


# def setup_logging() -> None:
#     """Configure le système de logging de l'application"""
    
#     # Supprimer le handler par défaut
#     logger.remove()
    
#     # === CONSOLE LOGGING ===
#     if settings.LOG_FORMAT == "json":
#         # Format JSON pour production (parsing facile)
#         logger.add(
#             sys.stdout,
#             format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
#             level=settings.LOG_LEVEL,
#             colorize=True,
#             serialize=settings.is_production,  # JSON seulement en production
#         )
#     else:
#         # Format texte pour développement (lisible)
#         logger.add(
#             sys.stdout,
#             format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
#             level=settings.LOG_LEVEL,
#             colorize=True,
#         )
    
#     # === FILE LOGGING ===
#     log_path = Path(settings.LOG_FILE_PATH)
#     log_path.parent.mkdir(parents=True, exist_ok=True)
    
#     logger.add(
#         settings.LOG_FILE_PATH,
#         rotation=settings.LOG_ROTATION,
#         retention="30 days",
#         compression="zip",
#         level=settings.LOG_LEVEL,
#         format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
#         serialize=True,  # JSON pour fichiers
#         enqueue=True,    # Asynchrone pour performance
#     )
    
#     # === ERROR FILE LOGGING ===
#     logger.add(
#         log_path.parent / "errors.log",
#         rotation="100 MB",
#         retention="60 days",
#         compression="zip",
#         level="ERROR",
#         format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
#         serialize=True,
#         enqueue=True,
#         backtrace=True,   # Stack trace complet
#         diagnose=True,    # Variables locales
#     )
    
#     logger.info(f"🚀 Logging configuré - Niveau: {settings.LOG_LEVEL}, Format: {settings.LOG_FORMAT}")


# def get_logger(name: str):
#     """
#     Retourne un logger avec contexte
    
#     Usage:
#         from src.core.logging import get_logger
#         logger = get_logger(__name__)
#         logger.info("Message")
#     """
#     return logger.bind(module=name)


# # === HELPERS POUR LOGGING STRUCTURÉ ===

# def log_api_request(method: str, path: str, status_code: int, duration_ms: float):
#     """Log une requête API avec métriques"""
#     logger.info(
#         "API Request",
#         extra={
#             "method": method,
#             "path": path,
#             "status_code": status_code,
#             "duration_ms": round(duration_ms, 2),
#         }
#     )


# def log_fraud_detection(
#     transaction_id: str,
#     is_fraud: bool,
#     confidence: float,
#     processing_time_ms: float
# ):
#     """Log une détection de fraude"""
#     logger.info(
#         f"Fraud Detection: {'FRAUD' if is_fraud else 'LEGIT'}",
#         extra={
#             "transaction_id": transaction_id,
#             "is_fraud": is_fraud,
#             "confidence": round(confidence, 4),
#             "processing_time_ms": round(processing_time_ms, 2),
#         }
#     )


# def log_ml_prediction(model_name: str, prediction_time_ms: float, features_count: int):
#     """Log une prédiction ML"""
#     logger.debug(
#         "ML Prediction",
#         extra={
#             "model": model_name,
#             "prediction_time_ms": round(prediction_time_ms, 2),
#             "features_count": features_count,
#         }
#     )


# def log_database_query(query_type: str, table: str, duration_ms: float):
#     """Log une requête base de données"""
#     logger.debug(
#         "Database Query",
#         extra={
#             "query_type": query_type,
#             "table": table,
#             "duration_ms": round(duration_ms, 2),
#         }
#     )


"""
Configuration du système de logging pour SÉNTRA
Utilise Loguru pour des logs structurés et performants
"""

import sys
from pathlib import Path
from loguru import logger
from .config import settings


def setup_logging() -> None:
    """Configure le système de logging de l'application"""
    
    # Supprimer le handler par défaut
    logger.remove()
    
    # === CONSOLE LOGGING ===
    if settings.LOG_FORMAT == "json":
        # Format JSON pour production (parsing facile)
        logger.add(
            sys.stdout,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
            level=settings.LOG_LEVEL,
            colorize=True,
            serialize=settings.is_production,
        )
    else:
        # Format texte pour développement (lisible)
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=settings.LOG_LEVEL,
            colorize=True,
        )
    
    # === FILE LOGGING ===
    log_path = Path(settings.LOG_FILE_PATH)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        settings.LOG_FILE_PATH,
        rotation=settings.LOG_ROTATION,
        retention="30 days",
        compression="zip",
        level=settings.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        serialize=True, 
        enqueue=True, 
    )
    
    # === ERROR FILE LOGGING ===
    logger.add(
        log_path.parent / "errors.log",
        rotation="100 MB",
        retention="60 days",
        compression="zip",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        serialize=True,
        enqueue=True,
        backtrace=True, 
        diagnose=True, 
    )
    
    logger.info(f"🚀 Logging configuré - Niveau: {settings.LOG_LEVEL}, Format: {settings.LOG_FORMAT}")


def get_logger(name: str):
    """
    Retourne un logger avec contexte
    
    Usage:
        from src.core.logging import get_logger
        logger = get_logger(__name__)
        logger.info("Message")
    """
    return logger.bind(module=name)


# === HELPERS POUR LOGGING STRUCTURÉ ===

def log_api_request(method: str, path: str, status_code: int, duration_ms: float):
    """Log une requête API avec métriques"""
    logger.info(
        "API Request",
        extra={
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": round(duration_ms, 2),
        }
    )


def log_fraud_detection(
    transaction_id: str,
    is_fraud: bool,
    confidence: float,
    processing_time_ms: float
):
    """Log une détection de fraude"""
    logger.info(
        f"Fraud Detection: {'FRAUD' if is_fraud else 'LEGIT'}",
        extra={
            "transaction_id": transaction_id,
            "is_fraud": is_fraud,
            "confidence": round(confidence, 4),
            "processing_time_ms": round(processing_time_ms, 2),
        }
    )


def log_ml_prediction(model_name: str, prediction_time_ms: float, features_count: int):
    """Log une prédiction ML"""
    logger.debug(
        "ML Prediction",
        extra={
            "model": model_name,
            "prediction_time_ms": round(prediction_time_ms, 2),
            "features_count": features_count,
        }
    )


def log_database_query(query_type: str, table: str, duration_ms: float):
    """Log une requête base de données"""
    logger.debug(
        "Database Query",
        extra={
            "query_type": query_type,
            "table": table,
            "duration_ms": round(duration_ms, 2),
        }
    )