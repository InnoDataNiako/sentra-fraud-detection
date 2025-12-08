"""
Schémas Pydantic communs et réutilisables
"""

from typing import Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field


class HealthCheck(BaseModel):
    """Schéma pour le health check de l'API"""
    status: str = Field(..., description="Statut de l'API (healthy, unhealthy)")
    version: str = Field(..., description="Version de l'API")
    environment: str = Field(..., description="Environnement (dev, staging, prod)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Services status
    database: str = Field(..., description="Statut de la base de données")
    redis: Optional[str] = Field(None, description="Statut de Redis")
    ml_model: str = Field(..., description="Statut du modèle ML")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "environment": "development",
                "timestamp": "2025-11-14T08:00:00Z",
                "database": "connected",
                "redis": "connected",
                "ml_model": "loaded"
            }
        }


class ErrorResponse(BaseModel):
    """Schéma pour les réponses d'erreur"""
    error: str = Field(..., description="Type d'erreur")
    message: str = Field(..., description="Message d'erreur détaillé")
    details: Optional[Dict[str, Any]] = Field(None, description="Détails supplémentaires")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    path: Optional[str] = Field(None, description="Chemin de la requête")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Le montant doit être positif",
                "details": {"field": "amount", "value": -100},
                "timestamp": "2025-11-14T08:00:00Z",
                "path": "/api/v1/detect"
            }
        }


class SuccessResponse(BaseModel):
    """Schéma pour les réponses de succès génériques"""
    success: bool = Field(True, description="Indique le succès de l'opération")
    message: str = Field(..., description="Message de confirmation")
    data: Optional[Dict[str, Any]] = Field(None, description="Données retournées")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Opération réussie",
                "data": {"id": "txn_12345"},
                "timestamp": "2025-11-14T08:00:00Z"
            }
        }


class PaginationParams(BaseModel):
    """Paramètres de pagination"""
    page: int = Field(1, ge=1, description="Numéro de page")
    page_size: int = Field(50, ge=1, le=1000, description="Nombre d'éléments par page")
    
    @property
    def offset(self) -> int:
        """Calcule l'offset pour la requête SQL"""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """Retourne la limite pour la requête SQL"""
        return self.page_size


class PaginatedResponse(BaseModel):
    """Schéma pour les réponses paginées"""
    items: list = Field(..., description="Liste des éléments")
    total: int = Field(..., description="Nombre total d'éléments")
    page: int = Field(..., description="Page actuelle")
    page_size: int = Field(..., description="Taille de la page")
    total_pages: int = Field(..., description="Nombre total de pages")
    has_next: bool = Field(..., description="Indique s'il y a une page suivante")
    has_previous: bool = Field(..., description="Indique s'il y a une page précédente")
    
    @classmethod
    def create(cls, items: list, total: int, page: int, page_size: int):
        """Factory method pour créer une réponse paginée"""
        total_pages = (total + page_size - 1) // page_size
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1
        )


class Statistics(BaseModel):
    """Schéma pour les statistiques globales"""
    total_transactions: int = Field(..., description="Nombre total de transactions")
    total_fraud: int = Field(..., description="Nombre total de fraudes détectées")
    fraud_rate: float = Field(..., description="Taux de fraude en pourcentage")
    avg_amount: float = Field(..., description="Montant moyen des transactions")
    avg_detection_time_ms: Optional[float] = Field(None, description="Temps moyen de détection")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_transactions": 10000,
                "total_fraud": 250,
                "fraud_rate": 2.5,
                "avg_amount": 150000.0,
                "avg_detection_time_ms": 45.2
            }
        }