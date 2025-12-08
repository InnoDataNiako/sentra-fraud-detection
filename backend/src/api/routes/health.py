"""
Routes de santé de l'API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import psutil
import os

from src.database.connection import get_db
from src.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Vérifie la santé de l'API et de la base de données
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {}
    }
    
    try:
        # Test connexion base de données
        db.execute("SELECT 1")
        health_status["services"]["database"] = {
            "status": "healthy",
            "message": "Connexion PostgreSQL établie"
        }
    except Exception as e:
        health_status["services"]["database"] = {
            "status": "unhealthy",
            "message": f"Erreur connexion: {str(e)}"
        }
        health_status["status"] = "degraded"
    
    # Métriques système
    try:
        health_status["system"] = {
            "memory_usage": f"{psutil.virtual_memory().percent}%",
            "cpu_usage": f"{psutil.cpu_percent()}%",
            "disk_usage": f"{psutil.disk_usage('/').percent}%",
            "process_uptime": f"{psutil.Process(os.getpid()).create_time():.0f}"
        }
    except Exception as e:
        health_status["system"] = {
            "status": "unavailable",
            "error": str(e)
        }
    
    # Log selon le statut
    if health_status["status"] == "healthy":
        logger.info("✅ Health check: Tous les services sont opérationnels")
    else:
        logger.warning(f"⚠️ Health check: Statut dégradé - {health_status}")
    
    return health_status

@router.get("/health/ready")
async def readiness_probe(db: Session = Depends(get_db)):
    """
    Sonde de readiness pour Kubernetes/Load Balancer
    """
    try:
        # Vérification critique de la base de données
        db.execute("SELECT 1")
        return {
            "status": "ready",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Readiness probe failed: {e}")
        raise HTTPException(
            status_code=503,
            detail="Service non prêt - Base de données indisponible"
        )

@router.get("/health/live")
async def liveness_probe():
    """
    Sonde de liveness pour Kubernetes
    """
    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat()
    }