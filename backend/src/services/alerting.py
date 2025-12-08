"""
Service de gestion des alertes de fraude
Gère le workflow d'investigation et les notifications
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from src.database.repositories.alert_repository import AlertRepository
from src.database.models import FraudAlert, AlertSeverity
from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)


class AlertingService:
    """Service de gestion des alertes de fraude"""
    
    def __init__(self, db: Session):
        self.db = db
        self.alert_repo = AlertRepository(db)
        
        # Configuration des notifications
        self.notification_config = {
            'email_enabled': settings.SMTP_HOST is not None,
            'sms_enabled': False,  # À implémenter avec service SMS
            'webhook_enabled': False,  # À implémenter
            'critical_threshold': AlertSeverity.HIGH
        }
    
    def create_alert(
        self,
        transaction_id: int,
        severity: AlertSeverity,
        title: str,
        description: str,
        fraud_indicators: str
    ) -> FraudAlert:
        """
        Crée une nouvelle alerte de fraude
        
        Args:
            transaction_id: ID de la transaction concernée
            severity: Niveau de sévérité
            title: Titre de l'alerte
            description: Description détaillée
            fraud_indicators: Indicateurs de fraude
            
        Returns:
            Alerte créée
        """
        alert_data = {
            'alert_id': f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            'transaction_id': transaction_id,
            'severity': severity,
            'title': title,
            'description': description,
            'fraud_indicators': fraud_indicators
        }
        
        alert = self.alert_repo.create(alert_data)
        
        # Notifications automatiques selon sévérité
        self._handle_alert_notifications(alert)
        
        logger.info(f"🚨 Alerte créée: {alert.alert_id} - {severity.value}")
        
        return alert
    
    def _handle_alert_notifications(self, alert: FraudAlert):
        """Gère les notifications selon la sévérité"""
        try:
            # Notification pour alertes CRITICAL et HIGH
            if alert.severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]:
                self._send_immediate_notification(alert)
            
            # Notification email pour toutes les alertes MEDIUM+
            if (alert.severity.value >= AlertSeverity.MEDIUM.value and 
                self.notification_config['email_enabled']):
                self._send_email_notification(alert)
            
            # Log pour toutes les alertes
            logger.warning(
                f"📢 Alerte {alert.severity.value}: {alert.title} - "
                f"Transaction: {alert.transaction_id}"
            )
                
        except Exception as e:
            logger.error(f"❌ Erreur notification alerte {alert.alert_id}: {e}")
    
    def _send_immediate_notification(self, alert: FraudAlert):
        """Notification immédiate pour alertes critiques"""
        # Ici, on intégrerait avec:
        # - Slack/Teams webhooks
        # - SMS aux responsables
        # - Appels système
        
        message = (
            f"🚨 ALERTE FRAUDE {alert.severity.value.upper()} 🚨\n"
            f"ID: {alert.alert_id}\n"
            f"Titre: {alert.title}\n"
            f"Transaction: {alert.transaction_id}\n"
            f"Description: {alert.description}\n"
            f"Créée: {alert.created_at}"
        )
        
        # Pour l'instant, on log juste
        # En production: envoyer vers système de notification
        logger.critical(f"NOTIFICATION IMMÉDIATE: {message}")
    
    def _send_email_notification(self, alert: FraudAlert):
        """Envoie une notification email"""
        if not self.notification_config['email_enabled']:
            return
        
        try:
            # Configuration email
            smtp_host = settings.SMTP_HOST
            smtp_port = settings.SMTP_PORT
            smtp_user = settings.SMTP_USER
            smtp_password = settings.SMTP_PASSWORD
            
            if not all([smtp_host, smtp_user, smtp_password]):
                logger.warning("Configuration email incomplète")
                return
            
            # Création du message
            msg = MIMEMultipart()
            msg['From'] = settings.ALERT_EMAIL_FROM
            msg['To'] = settings.ALERT_EMAIL_TO
            msg['Subject'] = f"🚨 SÉNTRA - Alerte Fraude {alert.severity.value}"
            
            # Corps du message
            body = f"""
            <h2>Alerte de Fraude Détectée - SÉNTRA</h2>
            
            <p><strong>ID Alerte:</strong> {alert.alert_id}</p>
            <p><strong>Sévérité:</strong> {alert.severity.value.upper()}</p>
            <p><strong>Titre:</strong> {alert.title}</p>
            <p><strong>Transaction ID:</strong> {alert.transaction_id}</p>
            <p><strong>Description:</strong></p>
            <pre>{alert.description}</pre>
            <p><strong>Indicateurs de Fraude:</strong> {alert.fraud_indicators}</p>
            <p><strong>Date de Création:</strong> {alert.created_at}</p>
            
            <hr>
            <p><em>Cet email a été généré automatiquement par le système SÉNTRA</em></p>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Envoi
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
            
            logger.info(f"📧 Email notification sent for alert {alert.alert_id}")
            
        except Exception as e:
            logger.error(f"❌ Erreur envoi email alerte {alert.alert_id}: {e}")
    
    def get_pending_alerts(
        self, 
        severity: Optional[AlertSeverity] = None,
        limit: int = 50
    ) -> List[FraudAlert]:
        """
        Récupère les alertes en attente d'investigation
        
        Args:
            severity: Filtrer par sévérité
            limit: Nombre max d'alertes
            
        Returns:
            Liste d'alertes non examinées
        """
        if severity:
            return self.alert_repo.get_by_severity(severity, limit=limit)
        else:
            return self.alert_repo.get_unreviewed(limit=limit)
    
    def mark_alert_reviewed(
        self, 
        alert_id: int, 
        reviewed_by: str,
        resolution: str,
        is_confirmed_fraud: bool
    ) -> Optional[FraudAlert]:
        """
        Marque une alerte comme examinée
        
        Args:
            alert_id: ID de l'alerte
            reviewed_by: Nom de l'analyste
            resolution: Résolution de l'incident
            is_confirmed_fraud: Si la fraude a été confirmée
            
        Returns:
            Alerte mise à jour
        """
        alert = self.alert_repo.mark_as_reviewed(
            alert_id, 
            reviewed_by, 
            resolution
        )
        
        if alert and is_confirmed_fraud:
            # Mettre à jour la transaction associée
            from src.database.repositories.transaction_repository import TransactionRepository
            tx_repo = TransactionRepository(self.db)
            tx_repo.mark_as_fraud(
                alert.transaction_id,
                fraud_score=0.95,  # Score de confirmation
                reason=f"Confirmé par {reviewed_by}: {resolution}"
            )
            
            logger.info(f"✅ Fraude confirmée - Alerte {alert.alert_id}")
        
        return alert
    
    def get_alert_stats(self) -> Dict[str, Any]:
        """
        Retourne les statistiques des alertes
        
        Returns:
            Statistiques des alertes
        """
        total = self.alert_repo.count_total()
        unreviewed = self.alert_repo.count_unreviewed()
        distribution = self.alert_repo.get_severity_distribution()
        
        return {
            'total_alerts': total,
            'unreviewed_alerts': unreviewed,
            'reviewed_alerts': total - unreviewed,
            'distribution_by_severity': distribution,
            'review_rate': (total - unreviewed) / total if total > 0 else 0
        }
    
    def escalate_alert(self, alert_id: int, reason: str) -> Optional[FraudAlert]:
        """
        Escalade une alerte vers un niveau supérieur
        
        Args:
            alert_id: ID de l'alerte
            reason: Raison de l'escalade
            
        Returns:
            Alerte mise à jour
        """
        alert = self.alert_repo.get_by_id(alert_id)
        if not alert:
            return None
        
        # Logique d'escalade
        if alert.severity == AlertSeverity.LOW:
            new_severity = AlertSeverity.MEDIUM
        elif alert.severity == AlertSeverity.MEDIUM:
            new_severity = AlertSeverity.HIGH
        elif alert.severity == AlertSeverity.HIGH:
            new_severity = AlertSeverity.CRITICAL
        else:
            new_severity = alert.severity  # Déjà au maximum
        
        if new_severity != alert.severity:
            alert = self.alert_repo.update(alert_id, {
                'severity': new_severity,
                'description': f"{alert.description}\n\n🚨 ESCALADE: {reason}"
            })
            
            logger.warning(
                f"📈 Alerte {alert.alert_id} escaladée de {alert.severity} à {new_severity}"
            )
            
            # Renotifier pour alerte escaladée
            self._handle_alert_notifications(alert)
        
        return alert


# Service factory
def get_alerting_service(db: Session) -> AlertingService:
    """Factory pour l'injection de dépendances"""
    return AlertingService(db)