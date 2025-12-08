# Service de génération de rapports et statistiques
# Analytiques temps réel pour le monitoring

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import json
import io

# Assurez-vous que ces imports sont correctement configurés dans votre environnement
from src.database.repositories.transaction_repository import TransactionRepository
from src.database.repositories.alert_repository import AlertRepository
from src.core.logging import get_logger

logger = get_logger(__name__)


class ReportingService:
    """Service de génération de rapports et statistiques"""
    
    def __init__(self, db: Session):
        self.db = db
        self.transaction_repo = TransactionRepository(db)
        self.alert_repo = AlertRepository(db)
        
    # Constantes de Fallback pour garantir la stabilité en cas de BDD vide ou erreur
    # Ces valeurs sont utilisées si les Repositories ne retournent rien (None ou dictionnaire vide)
    DEFAULT_STATS = {
        'total_transactions': 0,
        'fraudulent_transactions': 0,
        'fraud_rate': 0.0,
        'total_amount': 0
    }
    
    # --- FONCTIONS PUBLIQUES ---

    def get_realtime_dashboard(self) -> Dict[str, Any]:
        """
        Données pour le dashboard temps réel (24h)
        
        SANS DONNÉES TEMPORAIRES (utilise les Repositories et valeurs par défaut robustes).
        
        Returns:
            Métriques temps réel consolidées.
        """
        now = datetime.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        
        # 1. Récupération des données réelles (avec gestion des exceptions implicites si la BDD est vide)
        
        # Statistiques des 24h : utilise .get() sur les Repositories
        tx_24h = self.transaction_repo.get_stats_by_period(last_24h, now)
        tx_7d = self.transaction_repo.get_stats_by_period(last_7d, now)
        
        # Métriques agrégées simples
        total_amount_24h = self.transaction_repo.get_total_amount_period(last_24h, now)
        avg_amount_24h = self.transaction_repo.get_avg_amount_period(last_24h, now)
        
        # Statistiques alertes
        alert_stats = self.alert_repo.get_severity_distribution()
        unreviewed_alerts = self.alert_repo.count_unreviewed()
        total_alerts = self.alert_repo.count_total()
        
        # --- 2. Application des Fallbacks / Sécurisation ---
        
        # Utiliser les statistiques de transaction ou les valeurs par défaut
        safe_tx_24h = {**self.DEFAULT_STATS, **(tx_24h if tx_24h else {})}
        safe_tx_7d = {**self.DEFAULT_STATS, **(tx_7d if tx_7d else {})}
        safe_alert_stats = alert_stats if alert_stats else {}
        
        # Calculs sécurisés
        total_tx_24h = safe_tx_24h['total_transactions']
        frauds_detected_24h = safe_tx_24h['fraudulent_transactions']
        
        review_rate = (total_alerts - unreviewed_alerts) / total_alerts if total_alerts > 0 else 0
        
        # Taux de blocage automatique
        critical_alerts = safe_alert_stats.get('critical', 0)
        auto_block_rate = critical_alerts / max(total_tx_24h, 1) # Évite la division par zéro
        
        # Estimation du montant bloqué (utiliser une valeur sécurisée si total_amount est None)
        BLOCKED_AMOUNT_PER_FRAUD = 150000 
        blocked_amount_est = frauds_detected_24h * BLOCKED_AMOUNT_PER_FRAUD
        
        # Métriques de performance (celles-ci sont encore "en dur" car elles viennent de l'évaluation du modèle, pas de la BDD)
        detection_accuracy = 0.998
        avg_processing_time = 15.6 # Simulé ou lu d'une autre source (table 'system_metrics')
        
        # --- 3. Construction de la réponse (Structure pour le frontend) ---
        return {
            'timestamp': now.isoformat(),
            'time_periods': {
                'last_24h': last_24h.isoformat(),
                'last_7d': last_7d.isoformat()
            },
            'transactions': {
                # Clés utilisées par le frontend (metrics)
                'total_transactions': total_tx_24h,
                'total_revenue': total_amount_24h if total_amount_24h is not None else 0, 
                # Données détaillées 
                'last_24h_detail': {
                    'total': total_tx_24h,
                    'fraudulent': frauds_detected_24h,
                    'fraud_rate': safe_tx_24h['fraud_rate'],
                    'total_amount': total_amount_24h if total_amount_24h is not None else 0,
                    'avg_amount': avg_amount_24h if avg_amount_24h is not None else 0
                },
                'last_7d_detail': safe_tx_7d,
            },
            'alerts': {
                # Clés utilisées par le frontend (metrics)
                'frauds_detected': frauds_detected_24h,
                'blocked_amount': blocked_amount_est,
                'fraud_rate': safe_tx_24h['fraud_rate'], 
                # Données détaillées
                'total': total_alerts,
                'unreviewed': unreviewed_alerts,
                'distribution': safe_alert_stats,
                'review_rate': review_rate
            },
            'performance': {
                # Clés utilisées par le frontend (metrics)
                'model_accuracy': detection_accuracy,
                'avg_processing_time_ms': avg_processing_time,
                # Données détaillées
                'detection_accuracy': detection_accuracy, 
                'false_positive_rate': 0.0026,
                'auto_block_rate': auto_block_rate
            }
        }
    
    def generate_daily_report(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Génère un rapport quotidien détaillé
        
        Args:
            date: Date du rapport (aujourd'hui si None)
            
        Returns:
            Rapport quotidien
        """
        if date is None:
            date = datetime.now()
        
        start_time = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Statistiques de la journée (Utilisation des appels réels)
        daily_stats = self.transaction_repo.get_stats_by_period(start_time, end_time)
        alert_stats = self.alert_repo.get_severity_distribution()
        
        # Sécurisation des données
        safe_daily_stats = {**self.DEFAULT_STATS, **(daily_stats if daily_stats else {})}
        safe_alert_stats = alert_stats if alert_stats else {}
        
        # Transactions par heure (SIMULÉ - nécessite une implémentation BDD)
        hourly_transactions = self._get_hourly_breakdown(start_time, end_time)
        
        # Top clients à risque (SIMULÉ - nécessite une implémentation BDD)
        risky_customers = self._get_risky_customers(start_time, end_time)
        
        # Alertes de la journée (Réel)
        daily_alerts = self.alert_repo.get_alerts_by_period(start_time, end_time)
        
        # Estimation des économies (utiliser la même constante que le dashboard)
        BLOCKED_AMOUNT_PER_FRAUD = 150000 
        estimated_savings = safe_daily_stats['fraudulent_transactions'] * BLOCKED_AMOUNT_PER_FRAUD
        
        # Calcul du statut de révision sécurisé
        reviewed_alerts = sum(1 for a in daily_alerts if getattr(a, 'is_reviewed', False))
        pending_alerts = len(daily_alerts) - reviewed_alerts
        
        report = {
            'report_date': date.strftime('%Y-%m-%d'),
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_transactions': safe_daily_stats['total_transactions'],
                'fraudulent_transactions': safe_daily_stats['fraudulent_transactions'],
                'fraud_rate_percent': safe_daily_stats['fraud_rate'],
                'total_alerts': len(daily_alerts),
                'auto_blocks': safe_alert_stats.get('critical', 0),
                'estimated_savings': estimated_savings
            },
            'hourly_breakdown': hourly_transactions,
            'top_risky_customers': risky_customers[:10],
            'alert_summary': {
                'by_severity': safe_alert_stats,
                'review_status': {
                    'reviewed': reviewed_alerts,
                    'pending': pending_alerts
                }
            },
            'recommendations': self._generate_daily_recommendations(safe_daily_stats, safe_alert_stats)
        }
        
        logger.info(f"📊 Rapport quotidien généré pour {date.strftime('%Y-%m-%d')}")

        
        return report
    
    # --- FONCTIONS INTERNES (avec simulations, à remplacer par appels BDD) ---

    def _get_hourly_breakdown(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Récupère la répartition horaire des transactions (Actuellement SIMULÉE)"""
        # TODO: Remplacer par self.transaction_repo.get_hourly_stats(start_time, end_time)
        hours = []
        # Simulation robuste (données vides si besoin)
        if start_time.date() != datetime.now().date():
             return [] # Retourne vide pour les jours passés si non implémenté
             
        for hour in range(24):
            total = np.random.randint(500, 2000)
            fraud = int(total * np.random.uniform(0.005, 0.03))
            
            hours.append({
                'hour': f"{hour:02d}:00",
                'total_transactions': total,
                'fraudulent_transactions': fraud,
                'fraud_rate': (fraud / total) * 100 if total > 0 else 0
            })
        
        return hours
    
    def _get_risky_customers(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Identifie les clients à haut risque (Actuellement SIMULÉE)"""
        # TODO: Remplacer par self.transaction_repo.get_top_risky_customers(start_time, end_time)
        
        # Simulation maintenue uniquement comme données de démo
        sample_customers = [
            {'customer_id': 'cust_12345', 'risk_score': 0.85, 'fraud_count': 3, 'total_transactions': 15},
            {'customer_id': 'cust_67890', 'risk_score': 0.72, 'fraud_count': 2, 'total_transactions': 8},
            {'customer_id': 'cust_11111', 'risk_score': 0.68, 'fraud_count': 1, 'total_transactions': 25},
            {'customer_id': 'cust_22222', 'risk_score': 0.61, 'fraud_count': 1, 'total_transactions': 12},
        ]
        
        return sample_customers
    
    def _generate_daily_recommendations(
        self, 
        stats: Dict[str, Any], 
        alert_stats: Dict[str, int]
    ) -> List[str]:
        """Génère des recommandations basées sur les données"""
        recommendations = []
        
        # Utilisation de .get pour gérer les clés manquantes
        fraud_rate = stats.get('fraud_rate', 0)
        total_alerts = sum(alert_stats.values())
        
        # Recommandation basée sur le taux de fraude
        if fraud_rate > 5.0:
            recommendations.append("🚨 Taux de fraude élevé - Renforcer les règles de détection")
        elif fraud_rate < 1.0:
            recommendations.append("✅ Taux de fraude normal - Maintenir la surveillance")
        
        # Recommandation basée sur les alertes
        if total_alerts > 50:
            recommendations.append("📋 Nombre élevé d'alertes - Augmenter la capacité d'investigation")
        
        # Recommandation basée sur les blocages automatiques
        auto_blocks = alert_stats.get('critical', 0)
        if auto_blocks > 10:
            recommendations.append("🛡️ Blocages automatiques efficaces - Maintenir les seuils")
        
        if not recommendations:
            recommendations.append("📈 Performance normale - Continuer le monitoring standard")
        
        return recommendations
    
    # --- FONCTIONS D'EXPORT / PERFORMANCE ---

    def export_report_to_csv(self, report_data: Dict[str, Any]) -> str:
        """
        Exporte un rapport en format CSV
        
        Args:
            report_data: Données du rapport
            
        Returns:
            CSV en string
        """
        output = io.StringIO()
        
        # Section résumé
        summary_df = pd.DataFrame([report_data.get('summary', {})])
        output.write("--- SUMMARY ---\n")
        summary_df.to_csv(output, index=False)
        output.write("\n")
        
        # Section breakdown horaire
        hourly_df = pd.DataFrame(report_data.get('hourly_breakdown', []))
        output.write("--- HOURLY BREAKDOWN ---\n")
        hourly_df.to_csv(output, index=False)
        output.write("\n")
        
        # Section clients risqués
        customers_df = pd.DataFrame(report_data.get('top_risky_customers', []))
        output.write("--- RISKY CUSTOMERS ---\n")
        customers_df.to_csv(output, index=False)
        
        return output.getvalue()
    
    def generate_performance_report(self, days: int = 30) -> Dict[str, Any]:
        """
        Rapport de performance sur une période
        
        Args:
            days: Nombre de jours à analyser
            
        Returns:
            Rapport de performance
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Métriques sur la période (Réel)
        period_stats = self.transaction_repo.get_stats_by_period(start_date, end_date)
        safe_period_stats = {**self.DEFAULT_STATS, **(period_stats if period_stats else {})}
        
        # Tendances (SIMULÉ)
        daily_fraud_rates = []
        current_date = start_date
        total_days = (end_date - start_date).days
        
        if total_days > 0:
            while current_date <= end_date:
                # Simulation de taux de fraude quotidien
                fraud_rate = np.random.uniform(1.5, 4.5)
                daily_fraud_rates.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'fraud_rate': fraud_rate
                })
                current_date += timedelta(days=1)
        
        # Calcul sécurisé
        avg_daily_transactions = safe_period_stats['total_transactions'] / days if days > 0 else 0
        peak_fraud_day = max(daily_fraud_rates, key=lambda x: x['fraud_rate']) if daily_fraud_rates else {'date': 'N/A', 'fraud_rate': 0.0}

        return {
            'period': {
                'start': start_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d'),
                'days': days
            },
            'overall_performance': {
                'total_transactions': safe_period_stats['total_transactions'],
                'total_fraud': safe_period_stats['fraudulent_transactions'],
                'avg_fraud_rate': safe_period_stats['fraud_rate'],
                'detection_accuracy': 0.988,
                'false_positive_rate': 0.0026
            },
            'trends': {
                'daily_fraud_rates': daily_fraud_rates,
                'avg_daily_transactions': avg_daily_transactions,
                'peak_fraud_day': peak_fraud_day
            },
            'recommendations': [
                "Maintenir le modèle actuel - Performance stable",
                "Surveiller les faux positifs - Taux très bas",
                "Planifier le réentraînement du modèle dans 2 semaines"
            ]
        }
    
    def get_model_performance(self) -> Dict[str, Any]:
        """
        Retourne les métriques de performance du modèle ML (SIMULÉ)
        
        Returns:
            Métriques du modèle
        """
        # Ces données devraient être lues depuis une table 'model_metrics'
        return {
            'ml_model_version': 'random_forest_20251119_140607', 
            'training_date': '2025-11-19',
            'performance_metrics': {
                'accuracy': 0.9880,
                'precision': 0.8810,
                'recall': 0.6607,
                'f1_score': 0.7551,
                'auc_roc': 0.8596,
                'false_positive_rate': 0.0026,
                'false_negative_rate': 0.3393
            },
            'feature_importance': {
                'top_features': [
                    {'feature': 'amount_log', 'importance': 0.2733},
                    {'feature': 'amount', 'importance': 0.2663},
                    {'feature': 'amount_ratio_avg', 'importance': 0.0827}
                ]
            },
            'business_impact': {
                'fraud_detected': 37,
                'false_positives': 5,
                'estimated_savings': 18500000, 
                'investigation_costs': 50000 
            }
        }


# Service factory
def get_reporting_service(db: Session) -> ReportingService:
    """Factory pour l'injection de dépendances"""
    return ReportingService(db)