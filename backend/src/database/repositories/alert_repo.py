"""
Repository pour la gestion des alertes de fraude
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.database.models import FraudAlert, AlertSeverity
from src.core.logging import get_logger

logger = get_logger(__name__)


class AlertRepository:
    """Repository pour les opérations CRUD sur les alertes"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, alert_data: dict) -> FraudAlert:
        """
        Crée une nouvelle alerte de fraude
        
        Args:
            alert_data: Dictionnaire avec les données de l'alerte
            
        Returns:
            FraudAlert créée
        """
        alert = FraudAlert(**alert_data)
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        
        logger.warning(f"Alerte de fraude créée: {alert.alert_id} - Severity: {alert.severity}")
        return alert
    
    def get_by_id(self, alert_id: int) -> Optional[FraudAlert]:
        """Récupère une alerte par son ID"""
        return self.db.query(FraudAlert).filter(FraudAlert.id == alert_id).first()
    
    def get_by_alert_id(self, alert_id: str) -> Optional[FraudAlert]:
        """Récupère une alerte par son alert_id unique"""
        return self.db.query(FraudAlert).filter(
            FraudAlert.alert_id == alert_id
        ).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[FraudAlert]:
        """Récupère toutes les alertes avec pagination"""
        return self.db.query(FraudAlert).order_by(
            FraudAlert.created_at.desc()
        ).offset(skip).limit(limit).all()
    
    def get_unreviewed(self, skip: int = 0, limit: int = 100) -> List[FraudAlert]:
        """Récupère les alertes non examinées"""
        return self.db.query(FraudAlert).filter(
            FraudAlert.is_reviewed == False
        ).order_by(FraudAlert.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_by_severity(
        self, 
        severity: AlertSeverity, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[FraudAlert]:
        """Récupère les alertes par niveau de gravité"""
        return self.db.query(FraudAlert).filter(
            FraudAlert.severity == severity
        ).order_by(FraudAlert.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_critical_unreviewed(self, limit: int = 50) -> List[FraudAlert]:
        """Récupère les alertes critiques non examinées"""
        return self.db.query(FraudAlert).filter(
            FraudAlert.severity == AlertSeverity.CRITICAL,
            FraudAlert.is_reviewed == False
        ).order_by(FraudAlert.created_at.desc()).limit(limit).all()
    
    def update(self, alert_id: int, update_data: dict) -> Optional[FraudAlert]:
        """Met à jour une alerte"""
        alert = self.get_by_id(alert_id)
        if not alert:
            return None
        
        for key, value in update_data.items():
            setattr(alert, key, value)
        
        alert.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(alert)
        
        logger.info(f"Alerte mise à jour: {alert.alert_id}")
        return alert
    
    def mark_as_reviewed(
        self, 
        alert_id: int, 
        reviewed_by: str, 
        resolution: str
    ) -> Optional[FraudAlert]:
        """Marque une alerte comme examinée"""
        return self.update(alert_id, {
            "is_reviewed": True,
            "reviewed_by": reviewed_by,
            "reviewed_at": datetime.utcnow(),
            "resolution": resolution
        })
    
    def delete(self, alert_id: int) -> bool:
        """Supprime une alerte"""
        alert = self.get_by_id(alert_id)
        if not alert:
            return False
        
        self.db.delete(alert)
        self.db.commit()
        
        logger.warning(f"Alerte supprimée: {alert.alert_id}")
        return True
    
    # === STATISTIQUES ===
    
    def count_total(self) -> int:
        """Compte le nombre total d'alertes"""
        return self.db.query(func.count(FraudAlert.id)).scalar()
    
    def count_unreviewed(self) -> int:
        """Compte le nombre d'alertes non examinées"""
        return self.db.query(func.count(FraudAlert.id)).filter(
            FraudAlert.is_reviewed == False
        ).scalar()
    
    def count_by_severity(self, severity: AlertSeverity) -> int:
        """Compte les alertes par niveau de gravité"""
        return self.db.query(func.count(FraudAlert.id)).filter(
            FraudAlert.severity == severity
        ).scalar()
    
    def get_severity_distribution(self) -> dict:
        """Retourne la distribution des alertes par gravité"""
        return {
            "critical": self.count_by_severity(AlertSeverity.CRITICAL),
            "high": self.count_by_severity(AlertSeverity.HIGH),
            "medium": self.count_by_severity(AlertSeverity.MEDIUM),
            "low": self.count_by_severity(AlertSeverity.LOW),
        }