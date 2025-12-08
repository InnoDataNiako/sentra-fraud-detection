"""
Service principal de détection de fraude
Orchestre l'inférence ML et la logique métier
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.ml.inference.predictor import FraudPredictor
from src.ml.inference.ensemble import EnsemblePredictor
from src.database.repositories.transaction_repository import TransactionRepository
from src.database.repositories.alert_repository import AlertRepository
from src.database.models import Transaction, FraudAlert, AlertSeverity
from src.core.logging import get_logger

logger = get_logger(__name__)


class FraudDetectionService:
    """Service principal de détection de fraude"""
    
    def __init__(self, db: Session, model_path: str = None):
        """
        Args:
            db: Session base de données
            model_path: Chemin vers le modèle (auto-détection si None)
        """
        self.db = db
        self.transaction_repo = TransactionRepository(db)
        self.alert_repo = AlertRepository(db)
        
        # Initialiser le prédicteur
        if model_path is None:
            # Auto-détection du dernier modèle
            model_path = self._find_latest_model()
        
        self.predictor = FraudPredictor(model_path, 'sentra')
        self.ensemble = EnsemblePredictor(sentra_model_path=model_path, strategy='weighted')
        
        # Configuration métier
        self.config = {
            'auto_block_threshold': 0.85,  # Seuil blocage automatique
            'high_risk_threshold': 0.70,   # Seuil risque élevé
            'review_threshold': 0.50,      # Seuil revue manuelle
            'max_daily_transactions': 50,  # Seuil vélocité
            'suspicious_amount': 500000,   # Montant suspect (XOF)
        }
        
        logger.info(f"✅ Service détection initialisé - Modèle: {model_path}")
    
    def _find_latest_model(self) -> str:
        """Trouve le modèle le plus récent"""
        import glob
        model_files = glob.glob("./data/models/production/random_forest_*.pkl")
        if not model_files:
            raise FileNotFoundError("Aucun modèle trouvé")
        
        latest_model = max(model_files, key=lambda x: x.split('_')[-2:])
        return latest_model
    
    def detect_fraud(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Détecte la fraude pour une transaction
        
        Args:
            transaction_data: Données de la transaction
            
        Returns:
            Résultat complet de détection
        """
        start_time = datetime.now()
        
        try:
            # 1. Validation des données
            self._validate_transaction_data(transaction_data)
            
            # 2. Vérification règles métier simples
            business_rules_result = self._check_business_rules(transaction_data)
            
            # 3. Détection ML avec ensemble
            ml_prediction = self.ensemble.predict_single(transaction_data)
            
            # 4. Décision finale combinant règles métier et ML
            final_decision = self._make_final_decision(
                transaction_data, 
                business_rules_result, 
                ml_prediction
            )
            
            # 5. Sauvegarde en base
            transaction_record = self._save_transaction(transaction_data, final_decision)
            
            # 6. Création alerte si nécessaire
            if final_decision['should_alert']:
                alert = self._create_fraud_alert(transaction_record, final_decision)
                final_decision['alert_id'] = alert.alert_id
            
            # 7. Action automatique si seuil critique
            if final_decision['should_block']:
                self._execute_auto_block(transaction_record, final_decision)
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            final_decision['total_processing_time_ms'] = round(processing_time, 2)
            
            logger.info(
                f"🔍 Détection terminée - Transaction: {transaction_data.get('transaction_id')}, "
                f"Fraude: {final_decision['is_fraud']}, "
                f"Confiance: {final_decision['confidence']:.2f}"
            )
            
            return final_decision
            
        # Dans detect_fraud method, améliorer le bloc except :
        except Exception as e:
            logger.error(f"❌ Erreur détection fraude: {e}")
            return {
                'transaction_id': transaction_data.get('transaction_id'),
                'error': str(e),
                'is_fraud': False,
                'should_block': False,
                'combined_risk_score': 0.0,  # ← AJOUTER CETTE LIGNE
                'recommendation': 'Erreur système - Transaction approuvée par sécurité'
            }
    
    def _validate_transaction_data(self, data: Dict[str, Any]):
        """Valide les données de transaction"""
        required_fields = ['amount', 'currency', 'customer_id', 'timestamp']
        
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Champ requis manquant: {field}")
        
        if data['amount'] <= 0:
            raise ValueError("Le montant doit être positif")
        
        if data['currency'] not in ['XOF', 'EUR', 'USD']:
            raise ValueError("Devise non supportée")
    
    def _check_business_rules(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Vérifie les règles métier simples - VERSION CORRIGÉE"""
        rules_violated = []
        risk_score = 0.0
        
        # Règle 1: Montant suspect
        if transaction['amount'] > self.config['suspicious_amount']:
            rules_violated.append('high_amount')
            risk_score += 0.3
        
        # Règle 2: Vélocité transactions (simulée)
        recent_tx_count = self.transaction_repo.count_recent_transactions(
            transaction['customer_id'], 
            hours=24
        )
        if recent_tx_count > self.config['max_daily_transactions']:
            rules_violated.append('high_velocity')
            risk_score += 0.4
        
        # Règle 3: Heure inhabituelle - CORRECTION APPLIQUÉE
        timestamp = transaction['timestamp']
        try:
            if isinstance(timestamp, datetime):
                tx_time = timestamp
            elif isinstance(timestamp, str):
                # Gérer le format avec 'Z'
                timestamp_str = str(timestamp)
                if timestamp_str.endswith('Z'):
                    timestamp_str = timestamp_str.replace('Z', '+00:00')
                tx_time = datetime.fromisoformat(timestamp_str)
            else:
                # Fallback
                tx_time = datetime.utcnow()
        except Exception as e:
            logger.warning(f"⚠️ Erreur parsing timestamp '{timestamp}': {e}")
            tx_time = datetime.utcnow()
        
        if tx_time.hour <= 5 or tx_time.hour >= 23:  # Nuit
            rules_violated.append('unusual_time')
            risk_score += 0.2
        
        # Règle 4: Nouveau pays (simulée)
        if transaction.get('country_code') not in ['SN', 'ML', 'CI']:  # UEMOA
            rules_violated.append('foreign_country')
            risk_score += 0.3
        
        return {
            'rules_violated': rules_violated,
            'business_risk_score': min(risk_score, 1.0),
            'recent_transactions_count': recent_tx_count
        }
    
    def _make_final_decision(
        self, 
        transaction: Dict[str, Any],
        business_rules: Dict[str, Any],
        ml_prediction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prend la décision finale combinant règles métier et ML"""
        
        # Score combiné (70% ML + 30% règles métier)
        combined_score = (
            ml_prediction['fraud_probability'] * 0.7 + 
            business_rules['business_risk_score'] * 0.3
        )
        
        is_fraud = combined_score > 0.5
        
        # Décision de blocage (plus conservative)
        should_block = (
            combined_score > self.config['auto_block_threshold'] or
            ml_prediction['fraud_probability'] > 0.9 or
            len(business_rules['rules_violated']) >= 3
        )
        
        # Niveau de sévérité
        if combined_score > 0.85:
            severity = AlertSeverity.CRITICAL
        elif combined_score > 0.70:
            severity = AlertSeverity.HIGH
        elif combined_score > 0.50:
            severity = AlertSeverity.MEDIUM
        else:
            severity = AlertSeverity.LOW
        
        return {
            'transaction_id': transaction.get('transaction_id'),
            'is_fraud': is_fraud,
            'combined_risk_score': combined_score,
            'ml_probability': ml_prediction['fraud_probability'],
            'business_risk_score': business_rules['business_risk_score'],
            'should_block': should_block,
            'should_alert': is_fraud or combined_score > 0.3,
            'severity': severity,
            'confidence': ml_prediction['confidence_score'],
            'rules_violated': business_rules['rules_violated'],
            'recommendation': self._generate_recommendation(combined_score, should_block),
            'detection_timestamp': datetime.now().isoformat(),
            'algorithm_version': ml_prediction.get('model_version', 'unknown')
        }
    
    def _generate_recommendation(self, risk_score: float, should_block: bool) -> str:
        """Génère une recommandation métier"""
        if should_block:
            return "🚨 BLOQUER - Transaction bloquée automatiquement"
        elif risk_score > 0.7:
            return "⚠️  REVUE CRITIQUE - Nécessite investigation immédiate"
        elif risk_score > 0.5:
            return "📋 REVUE MANUELLE - À investiguer par équipe sécurité"
        elif risk_score > 0.3:
            return "👀 SURVEILLANCE - Monitorer le client"
        else:
            return "✅ APPROUVER - Transaction légitime"
    
    def _save_transaction(
        self, 
        transaction_data: Dict[str, Any], 
        decision: Dict[str, Any]
    ) -> Transaction:
        """Sauvegarde la transaction en base - VERSION CORRIGÉE"""
        
        # Parser le timestamp de façon robuste
        timestamp = self._safe_parse_timestamp(transaction_data['timestamp'])
        
        transaction_record = {
            'transaction_id': transaction_data.get('transaction_id'),
            'customer_id': transaction_data['customer_id'],
            'merchant_id': transaction_data.get('merchant_id'),
            'amount': float(transaction_data['amount']),  # S'assurer que c'est un float
            'currency': transaction_data['currency'],
            'transaction_type': transaction_data.get('transaction_type', 'payment'),
            'location': transaction_data.get('location'),
            'ip_address': transaction_data.get('ip_address'),
            'timestamp': timestamp,  # Utiliser le timestamp parsé
            'is_fraud': decision['is_fraud'],
            'fraud_score': float(decision['combined_risk_score']),  # S'assurer que c'est un float
            'fraud_reason': ', '.join(decision['rules_violated']),
            'status': 'FRAUD' if decision['should_block'] else 'APPROVED'
        }
        
        return self.transaction_repo.create(transaction_record)
    
    def _safe_parse_timestamp(self, timestamp):
        """Parse timestamp de façon robuste - NOUVELLE MÉTHODE UTILITAIRE"""
        if isinstance(timestamp, datetime):
            return timestamp
        
        if isinstance(timestamp, str):
            try:
                # Gérer le format avec 'Z'
                if timestamp.endswith('Z'):
                    timestamp = timestamp.replace('Z', '+00:00')
                return datetime.fromisoformat(timestamp)
            except ValueError as e:
                logger.warning(f"⚠️ Erreur parsing timestamp '{timestamp}': {e}")
                # Essayer un format alternatif
                try:
                    return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
                except ValueError:
                    try:
                        return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        pass
        
        # Fallback
        return datetime.utcnow()
    
    def _create_fraud_alert(
        self, 
        transaction: Transaction, 
        decision: Dict[str, Any]
    ) -> FraudAlert:
        """Crée une alerte de fraude"""
        alert_data = {
            'alert_id': f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            'transaction_id': transaction.id,
            'severity': decision['severity'],
            'title': self._generate_alert_title(decision),
            'description': self._generate_alert_description(transaction, decision),
            'fraud_indicators': str(decision['rules_violated'])
        }
        
        return self.alert_repo.create(alert_data)
    
    def _generate_alert_title(self, decision: Dict[str, Any]) -> str:
        """Génère le titre de l'alerte"""
        base = "Alerte Fraude - "
        
        if decision['severity'] == AlertSeverity.CRITICAL:
            return base + "CRITIQUE - Blocage automatique"
        elif decision['severity'] == AlertSeverity.HIGH:
            return base + "HAUTE - Intervention requise"
        elif decision['severity'] == AlertSeverity.MEDIUM:
            return base + "MOYENNE - Investigation nécessaire"
        else:
            return base + "FAIBLE - Surveillance"
    
    def _generate_alert_description(
        self, 
        transaction: Transaction, 
        decision: Dict[str, Any]
    ) -> str:
        """Génère la description de l'alerte"""
        return (
            f"Transaction suspecte détectée\n"
            f"Client: {transaction.customer_id}\n"
            f"Montant: {transaction.amount} {transaction.currency}\n"
            f"Score risque: {decision['combined_risk_score']:.2f}\n"
            f"Règles violées: {', '.join(decision['rules_violated'])}\n"
            f"Recommandation: {decision['recommendation']}"
        )
    
    def _execute_auto_block(self, transaction: Transaction, decision: Dict[str, Any]):
        """Exécute le blocage automatique"""
        logger.warning(
            f"🚫 TRANSACTION BLOQUÉE - {transaction.transaction_id} - "
            f"Score: {decision['combined_risk_score']:.2f}"
        )
        
        # Ici, on intégrerait avec le système de paiement
        # Pour l'instant, on log juste l'action
        # En production: appeler API blocage, notifier client, etc.
    
    def get_detection_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Retourne les statistiques de détection"""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        stats = self.transaction_repo.get_stats_by_period(start_time, end_time)
        alerts_stats = self.alert_repo.get_severity_distribution()
        
        return {
            'period': f"last_{hours}_hours",
            'total_transactions': stats['total_transactions'],
            'fraudulent_transactions': stats['fraudulent_transactions'],
            'fraud_rate': stats['fraud_rate'],
            'alerts_by_severity': alerts_stats,
            'avg_processing_time': 45.2,  # À calculer réellement
            'auto_blocks_count': self.alert_repo.count_by_severity(AlertSeverity.CRITICAL)
        }


# Service factory pour injection de dépendances
def get_fraud_detection_service(db: Session) -> FraudDetectionService:
    """Factory pour l'injection de dépendances FastAPI"""
    return FraudDetectionService(db)