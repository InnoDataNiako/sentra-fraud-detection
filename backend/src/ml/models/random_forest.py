"""Modèle Random Forest pour la détection de fraude
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
import joblib
from src.core.logging import get_logger

logger = get_logger(__name__)


class FraudRandomForest:
    """Random Forest optimisé pour la détection de fraude"""
    
    def __init__(self, **kwargs):
        """
        Args:
            **kwargs: Hyperparamètres pour RandomForestClassifier
        """
        # Hyperparamètres par défaut optimisés pour la fraude
        default_params = {
            'n_estimators': 200,
            'max_depth': 15,
            'min_samples_split': 10,
            'min_samples_leaf': 5,
            'max_features': 'sqrt',
            'class_weight': 'balanced',  # Important pour classes déséquilibrées
            'random_state': 42,
            'n_jobs': -1,
            'verbose': 0
        }
        
        # Merger avec params fournis
        
        default_params.update(kwargs)
        
        self.model = RandomForestClassifier(**default_params)
        self.feature_importances_ = None
        self.feature_names_ = None
        self.is_fitted = False
        
        logger.info(f"Random Forest initialisé avec {default_params['n_estimators']} arbres")
    
    def fit(self, X: pd.DataFrame, y: pd.Series) -> 'FraudRandomForest':
        """
        Entraîne le modèle
        
        Args:
            X: Features d'entraînement
            y: Labels (0=légitime, 1=fraude)
            
        Returns:
            self
        """
        logger.info(f"Entraînement Random Forest sur {len(X)} échantillons")
        logger.info(f"   - Features: {X.shape[1]}")
        logger.info(f"   - Fraudes: {y.sum()} ({y.mean()*100:.2f}%)")
        
        # Entraînement
        self.model.fit(X, y)
        
        # Sauvegarder noms features et importances
        self.feature_names_ = X.columns.tolist()
        self.feature_importances_ = pd.DataFrame({
            'feature': self.feature_names_,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        self.is_fitted = True
        
        logger.info("✅ Random Forest entraîné avec succès")
        logger.info(f"   Top 5 features: {', '.join(self.feature_importances_['feature'].head(5).tolist())}")
        
        return self
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Prédit les labels (0 ou 1)
        
        Args:
            X: Features
            
        Returns:
            Array des prédictions
        """
        if not self.is_fitted:
            raise ValueError("Modèle non entraîné. Appeler fit() d'abord.")
        
        return self.model.predict(X)
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Prédit les probabilités de fraude
        
        Args:
            X: Features
            
        Returns:
            Array des probabilités [prob_légitime, prob_fraude]
        """
        if not self.is_fitted:
            raise ValueError("Modèle non entraîné. Appeler fit() d'abord.")
        
        return self.model.predict_proba(X)
    
    def get_fraud_probability(self, X: pd.DataFrame) -> np.ndarray:
        """
        Retourne uniquement la probabilité de fraude (colonne 1)
        
        Args:
            X: Features
            
        Returns:
            Array des probabilités de fraude
        """
        proba = self.predict_proba(X)
        return proba[:, 1]
    
    def get_feature_importances(self, top_n: int = 20) -> pd.DataFrame:
        """
        Retourne les features les plus importantes
        
        Args:
            top_n: Nombre de features à retourner
            
        Returns:
            DataFrame avec features et importances
        """
        if self.feature_importances_ is None:
            raise ValueError("Modèle non entraîné.")
        
        return self.feature_importances_.head(top_n)
    
    def tune_hyperparameters(
        self, 
        X: pd.DataFrame, 
        y: pd.Series,
        cv: int = 5,
        scoring: str = 'f1'
    ) -> Dict[str, Any]:
        """
        Optimise les hyperparamètres avec GridSearchCV
        
        Args:
            X: Features d'entraînement
            y: Labels
            cv: Nombre de folds pour cross-validation
            scoring: Métrique à optimiser
            
        Returns:
            Dictionnaire avec meilleurs paramètres
        """
        logger.info("🔧 Optimisation des hyperparamètres...")
        
        # Grille de recherche
        param_grid = {
            'n_estimators': [100, 200, 300],
            'max_depth': [10, 15, 20, None],
            'min_samples_split': [5, 10, 20],
            'min_samples_leaf': [2, 5, 10],
            'max_features': ['sqrt', 'log2']
        }
        
        # GridSearch
        grid_search = GridSearchCV(
            estimator=RandomForestClassifier(
                class_weight='balanced',
                random_state=42,
                n_jobs=-1
            ),
            param_grid=param_grid,
            cv=cv,
            scoring=scoring,
            n_jobs=-1,
            verbose=1
        )
        
        grid_search.fit(X, y)
        
        # Meilleurs paramètres
        best_params = grid_search.best_params_
        best_score = grid_search.best_score_
        
        logger.info(f"✅ Meilleurs paramètres trouvés (score: {best_score:.4f}):")
        for param, value in best_params.items():
            logger.info(f"   - {param}: {value}")
        
        # Mettre à jour le modèle
        self.model = grid_search.best_estimator_
        self.is_fitted = True
        
        return {
            'best_params': best_params,
            'best_score': best_score,
            'cv_results': grid_search.cv_results_
        }
    
    def save(self, filepath: str):
        """Sauvegarde le modèle"""
        if not self.is_fitted:
            raise ValueError("Modèle non entraîné.")
        
        joblib.dump(self, filepath)
        logger.info(f"✅ Random Forest sauvegardé: {filepath}")
    
    @staticmethod
    def load(filepath: str) -> 'FraudRandomForest':
        """Charge le modèle"""
        model = joblib.load(filepath)
        logger.info(f"✅ Random Forest chargé: {filepath}")
        return model
    
    def get_params(self) -> Dict[str, Any]:
        """Retourne les paramètres du modèle"""
        return self.model.get_params()
    
    def __repr__(self) -> str:
        status = "fitted" if self.is_fitted else "not fitted"
        n_features = len(self.feature_names_) if self.feature_names_ else 0
        return f"FraudRandomForest(n_estimators={self.model.n_estimators}, status={status}, n_features={n_features})"