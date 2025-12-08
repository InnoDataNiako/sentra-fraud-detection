"""
Prédicteur ensemble combinant les modèles   SÉNTRA
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime
from .predictor import FraudPredictor
from src.core.logging import get_logger

logger = get_logger(__name__)


class EnsemblePredictor:
    """
    Combine les prédictions de plusieurs modèles
    Stratégies: voting, weighted average, context-based
    """
    
    def __init__(
        self,
        kaggle_model_path: Optional[str] = None,
        sentra_model_path: Optional[str] = None,
        strategy: str = 'weighted',
        weights: Optional[Dict[str, float]] = None
    ):
        """
        Args:
            kaggle_model_path: Chemin modèle Kaggle
            sentra_model_path: Chemin modèle SÉNTRA
            strategy: Stratégie de combinaison ('voting', 'weighted', 'context')
            weights: Poids pour weighted average {'kaggle': 0.6, 'sentra': 0.4}
        """
        self.strategy = strategy
        self.weights = weights or {'kaggle': 0.6, 'sentra': 0.4}
        
        # Charger les prédicteurs
        self.predictors = {}
        
        if kaggle_model_path:
            self.predictors['kaggle'] = FraudPredictor(kaggle_model_path, 'kaggle')
            logger.info("✅ Prédicteur Kaggle chargé")
        
        if sentra_model_path:
            self.predictors['sentra'] = FraudPredictor(sentra_model_path, 'sentra')
            logger.info("✅ Prédicteur SÉNTRA chargé")
        
        if not self.predictors:
            raise ValueError("Au moins un modèle doit être fourni")
        
        logger.info(f"🔀 Ensemble initialisé - Stratégie: {strategy}")
    
    def predict_single(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prédit avec ensemble de modèles
        
        Args:
            transaction: Données transaction
            
        Returns:
            Résultat combiné
        """
        start_time = datetime.now()
        
        # Obtenir prédictions de chaque modèle
        predictions = {}
        for name, predictor in self.predictors.items():
            try:
                pred = predictor.predict_single(transaction)
                predictions[name] = pred
            except Exception as e:
                logger.error(f"Erreur prédiction {name}: {e}")
                continue
        
        if not predictions:
            raise ValueError("Aucune prédiction réussie")
        
        # Combiner selon la stratégie
        if self.strategy == 'voting':
            result = self._voting_strategy(predictions, transaction)
        elif self.strategy == 'weighted':
            result = self._weighted_strategy(predictions, transaction)
        elif self.strategy == 'context':
            result = self._context_strategy(predictions, transaction)
        else:
            # Fallback: weighted par défaut
            result = self._weighted_strategy(predictions, transaction)
        
        # Ajouter métadonnées ensemble
        result['ensemble'] = {
            'strategy': self.strategy,
            'models_used': list(predictions.keys()),
            'individual_predictions': {
                name: {
                    'is_fraud': pred['is_fraud'],
                    'probability': pred['fraud_probability']
                }
                for name, pred in predictions.items()
            }
        }
        
        processing_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        result['processing_time_ms'] = round(processing_time_ms, 2)
        
        return result
    
    def _voting_strategy(
        self,
        predictions: Dict[str, Dict],
        transaction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Vote majoritaire : si >= 50% des modèles disent fraude, c'est fraude
        """
        fraud_votes = sum(1 for pred in predictions.values() if pred['is_fraud'])
        total_votes = len(predictions)
        
        is_fraud = fraud_votes >= (total_votes / 2)
        
        # Moyenne des probabilités
        avg_probability = np.mean([pred['fraud_probability'] for pred in predictions.values()])
        
        return {
            'transaction_id': transaction.get('transaction_id', 'unknown'),
            'is_fraud': is_fraud,
            'fraud_probability': float(avg_probability),
            'risk_level': self._get_risk_level(avg_probability),
            'confidence_score': float(avg_probability if is_fraud else 1 - avg_probability),
            'model_type': 'ensemble_voting',
            'recommendation': self._get_recommendation(avg_probability, is_fraud),
            'should_block': is_fraud and avg_probability > 0.8,
            'votes': f"{fraud_votes}/{total_votes}",
            'timestamp': datetime.now().isoformat()
        }
    
    def _weighted_strategy(
        self,
        predictions: Dict[str, Dict],
        transaction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Moyenne pondérée des probabilités
        Par défaut: Kaggle 60%, SÉNTRA 40%
        """
        weighted_prob = 0.0
        total_weight = 0.0
        
        for name, pred in predictions.items():
            weight = self.weights.get(name, 1.0)
            weighted_prob += pred['fraud_probability'] * weight
            total_weight += weight
        
        final_probability = weighted_prob / total_weight if total_weight > 0 else 0
        is_fraud = final_probability > 0.5
        
        return {
            'transaction_id': transaction.get('transaction_id', 'unknown'),
            'is_fraud': is_fraud,
            'fraud_probability': float(final_probability),
            'risk_level': self._get_risk_level(final_probability),
            'confidence_score': float(final_probability if is_fraud else 1 - final_probability),
            'model_type': 'ensemble_weighted',
            'recommendation': self._get_recommendation(final_probability, is_fraud),
            'should_block': is_fraud and final_probability > 0.8,
            'weights_used': self.weights,
            'timestamp': datetime.now().isoformat()
        }
    
    def _context_strategy(
        self,
        predictions: Dict[str, Dict],
        transaction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Sélection basée sur le contexte de la transaction
        - Si Mobile Money + zone UEMOA → Priorité SÉNTRA
        - Sinon → Priorité Kaggle
        """
        # Déterminer le contexte
        payment_method = transaction.get('payment_method', '').lower()
        location = transaction.get('location', '').lower()
        
        is_mobile_money = 'mobile' in payment_method
        is_uemoa = any(country in location for country in [
            'sénégal', 'senegal', 'côte', 'ivoire', 'mali', 'burkina',
            'niger', 'togo', 'benin', 'bissau', 'dakar', 'abidjan'
        ])
        
        # Choisir le modèle principal
        if is_mobile_money and is_uemoa and 'sentra' in predictions:
            primary = 'sentra'
            primary_weight = 0.7
            logger.info("Context: Mobile Money UEMOA → Priorité SÉNTRA")
        elif 'kaggle' in predictions:
            primary = 'kaggle'
            primary_weight = 0.7
            logger.info("Context: Standard → Priorité Kaggle")
        else:
            # Fallback
            primary = list(predictions.keys())[0]
            primary_weight = 1.0
        
        # Calculer probabilité pondérée
        final_probability = predictions[primary]['fraud_probability'] * primary_weight
        
        # Ajouter contribution des autres modèles
        secondary_weight = (1 - primary_weight) / max(len(predictions) - 1, 1)
        for name, pred in predictions.items():
            if name != primary:
                final_probability += pred['fraud_probability'] * secondary_weight
        
        is_fraud = final_probability > 0.5
        
        return {
            'transaction_id': transaction.get('transaction_id', 'unknown'),
            'is_fraud': is_fraud,
            'fraud_probability': float(final_probability),
            'risk_level': self._get_risk_level(final_probability),
            'confidence_score': float(final_probability if is_fraud else 1 - final_probability),
            'model_type': 'ensemble_context',
            'primary_model': primary,
            'context': {
                'is_mobile_money': is_mobile_money,
                'is_uemoa': is_uemoa
            },
            'recommendation': self._get_recommendation(final_probability, is_fraud),
            'should_block': is_fraud and final_probability > 0.8,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_risk_level(self, probability: float) -> str:
        """Détermine le niveau de risque"""
        if probability < 0.3:
            return 'low'
        elif probability < 0.6:
            return 'medium'
        elif probability < 0.85:
            return 'high'
        else:
            return 'critical'
    
    def _get_recommendation(self, probability: float, is_fraud: bool) -> str:
        """Génère une recommandation"""
        if not is_fraud:
            return "Approuver la transaction"
        
        if probability > 0.9:
            return "Bloquer immédiatement et contacter le client"
        elif probability > 0.7:
            return "Bloquer et demander authentification supplémentaire"
        elif probability > 0.5:
            return "Mettre en revue manuelle"
        else:
            return "Surveiller et logger"
    
    def predict_batch(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prédictions en batch"""
        return [self.predict_single(tx) for tx in transactions]
    
    def get_ensemble_info(self) -> Dict[str, Any]:
        """Informations sur l'ensemble"""
        return {
            'strategy': self.strategy,
            'models': {
                name: predictor.get_model_info()
                for name, predictor in self.predictors.items()
            },
            'weights': self.weights if self.strategy == 'weighted' else None
        }