"""
Isolation Forest pour la détection d'anomalies
Modèle non supervisé complémentaire au Random Forest
"""

import numpy as np
import pandas as pd
from typing import Optional
from sklearn.ensemble import IsolationForest
import joblib
from src.core.logging import get_logger

logger = get_logger(__name__)


class FraudIsolationForest:
    """Isolation Forest pour détecter les anomalies (transactions suspectes)"""
    
    def __init__(self, contamination: float = 0.028, **kwargs):
        """
        Args:
            contamination: Proportion attendue d'anomalies (0.028 = 2.8% selon BCEAO)
            **kwargs: Autres paramètres pour IsolationForest
        """
        default_params = {
            'n_estimators': 100,
            'max_samples': 256,
            'contamination': contamination,
            'random_state': 42,
            'n_jobs': -1,
            'verbose': 0
        }
        
        default_params.update(kwargs)
        
        self.model = IsolationForest(**default_params)
        self.is_fitted = False
        self.threshold = None
        
        logger.info(f"Isolation Forest initialisé (contamination: {contamination*100}%)")
    
    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> 'FraudIsolationForest':
        """
        Entraîne le modèle (non supervisé, y est ignoré)
        
        Args:
            X: Features d'entraînement
            y: Ignoré (non supervisé)
            
        Returns:
            self
        """
        logger.info(f"Entraînement Isolation Forest sur {len(X)} échantillons")
        
        self.model.fit(X)
        
        # Calculer le threshold
        scores = self.model.decision_function(X)
        self.threshold = np.percentile(scores, self.model.contamination * 100)
        
        self.is_fitted = True
        
        logger.info("✅ Isolation Forest entraîné avec succès")
        logger.info(f"   Threshold: {self.threshold:.4f}")
        
        return self
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Prédit les anomalies (-1 = anomalie, 1 = normal)
        
        Args:
            X: Features
            
        Returns:
            Array des prédictions (-1 ou 1)
        """
        if not self.is_fitted:
            raise ValueError("Modèle non entraîné. Appeler fit() d'abord.")
        
        return self.model.predict(X)
    
    def predict_binary(self, X: pd.DataFrame) -> np.ndarray:
        """
        Prédit en format binaire (0 = normal, 1 = anomalie)
        
        Args:
            X: Features
            
        Returns:
            Array des prédictions (0 ou 1)
        """
        predictions = self.predict(X)
        # Convertir -1 -> 1 (anomalie) et 1 -> 0 (normal)
        return np.where(predictions == -1, 1, 0)
    
    def decision_function(self, X: pd.DataFrame) -> np.ndarray:
        """
        Retourne les scores d'anomalie (plus négatif = plus anormal)
        
        Args:
            X: Features
            
        Returns:
            Array des scores
        """
        if not self.is_fitted:
            raise ValueError("Modèle non entraîné.")
        
        return self.model.decision_function(X)
    
    def get_anomaly_score(self, X: pd.DataFrame) -> np.ndarray:
        """
        Retourne un score d'anomalie normalisé entre 0 et 1
        0 = normal, 1 = très anormal
        
        Args:
            X: Features
            
        Returns:
            Array des scores normalisés
        """
        scores = self.decision_function(X)
        
        # Normaliser entre 0 et 1
        # Plus le score est négatif, plus c'est anormal
        # On inverse et normalise
        min_score = scores.min()
        max_score = scores.max()
        
        if max_score - min_score == 0:
            return np.zeros(len(scores))
        
        normalized = (max_score - scores) / (max_score - min_score)
        return normalized
    
    def save(self, filepath: str):
        """Sauvegarde le modèle"""
        if not self.is_fitted:
            raise ValueError("Modèle non entraîné.")
        
        joblib.dump(self, filepath)
        logger.info(f"✅ Isolation Forest sauvegardé: {filepath}")
    
    @staticmethod
    def load(filepath: str) -> 'FraudIsolationForest':
        """Charge le modèle"""
        model = joblib.load(filepath)
        logger.info(f"✅ Isolation Forest chargé: {filepath}")
        return model
    
    def __repr__(self) -> str:
        status = "fitted" if self.is_fitted else "not fitted"
        contamination = self.model.contamination * 100
        return f"FraudIsolationForest(contamination={contamination:.1f}%, status={status})"