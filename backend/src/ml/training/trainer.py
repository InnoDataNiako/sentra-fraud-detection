"""
Pipeline d'entraînement pour les modèles de détection de fraude
"""

import pandas as pd
import numpy as np
import joblib
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.pipeline import Pipeline as ImbPipeline

from src.ml.models.random_forest import FraudRandomForest
from src.ml.models.isolation_forest import FraudIsolationForest
from src.ml.preprocessing.features import FraudFeatureExtractor
from src.ml.preprocessing.scalers import FeatureScaler
from src.core.logging import get_logger

logger = get_logger(__name__)


class FraudModelTrainer:
    """Classe principale pour l'entraînement des modèles"""
    
    def __init__(
        self,
        model_type: str = 'random_forest',
        use_smote: bool = True,
        test_size: float = 0.2
    ):
        """
        Args:
            model_type: Type de modèle ('random_forest' ou 'isolation_forest')
            use_smote: Utiliser SMOTE pour rééquilibrer les classes
            test_size: Proportion du test set
        """
        self.model_type = model_type
        self.use_smote = use_smote
        self.test_size = test_size
        
        # Composants du pipeline
        self.feature_extractor = None
        self.scaler = None
        self.model = None
        self.sampler = None
        
        # Résultats
        self.training_history = {}
        self.feature_names = []
        
        logger.info(f"🔧 Trainer initialisé: {model_type}, SMOTE={use_smote}")
    
    def prepare_data(
        self,
        df: pd.DataFrame,
        is_kaggle: bool = False
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prépare les données pour l'entraînement
        
        Args:
            df: DataFrame avec les transactions
            is_kaggle: Si True, données Kaggle (pas d'extraction features)
            
        Returns:
            Tuple (X, y) - Features et labels
        """
        logger.info("🔧 Préparation des données...")
        
        if is_kaggle:
            # Dataset Kaggle: features déjà extraites (V1-V28, Time, Amount)
            feature_cols = [col for col in df.columns if col not in ['is_fraud', 'Class', 'Time']]
            X = df[feature_cols]
            y = df['is_fraud']
            
            # Normalisation
            self.scaler = FeatureScaler(scaler_type='standard')
            X = self.scaler.fit_transform(X)
            
            logger.info(f"   - Features Kaggle: {X.shape[1]}")
        else:
            # Dataset SÉNTRA: extraction de features nécessaire
            self.feature_extractor = FraudFeatureExtractor()
            X = self.feature_extractor.extract_features_dataframe(df)
            y = df['is_fraud']
            
            # Normalisation
            numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
            self.scaler = FeatureScaler(scaler_type='standard')
            X = self.scaler.fit_transform(X, numeric_cols)
            
            logger.info(f"   - Features extraites: {X.shape[1]}")
        
        self.feature_names = X.columns.tolist()
        
        logger.info(f"   - Samples: {len(X)}")
        logger.info(f"   - Fraudes: {y.sum()} ({y.mean()*100:.2f}%)")
        
        return X, y
    
    def handle_imbalance(
        self,
        X: pd.DataFrame,
        y: pd.Series
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Gère le déséquilibre des classes avec SMOTE + Undersampling
        
        Args:
            X: Features
            y: Labels
            
        Returns:
            Tuple (X_resampled, y_resampled)
        """
        if not self.use_smote:
            return X, y
        
        logger.info("⚖️ Rééquilibrage des classes...")
        logger.info(f"   Avant - Légitimes: {(y==0).sum()}, Fraudes: {(y==1).sum()}")
        
        # Stratégie: SMOTE (oversampling minoritaire) + Undersampling (majoritaire)
        # Objectif: ratio 1:3 (fraude:légitime)
        
        n_fraud = (y == 1).sum()
        n_legit = (y == 0).sum()
        target_fraud = n_fraud * 3  # Tripler les fraudes avec SMOTE
        target_legit = target_fraud * 3  # Ratio final 1:3
        
        # Pipeline de sampling
        self.sampler = ImbPipeline([
            ('smote', SMOTE(sampling_strategy={1: target_fraud}, random_state=42)),
            ('undersample', RandomUnderSampler(sampling_strategy={0: target_legit}, random_state=42))
        ])
        
        X_resampled, y_resampled = self.sampler.fit_resample(X, y)
        
        logger.info(f"   Après  - Légitimes: {(y_resampled==0).sum()}, Fraudes: {(y_resampled==1).sum()}")
        logger.info(f"   Ratio final: 1:{(y_resampled==0).sum() / (y_resampled==1).sum():.1f}")
        
        return pd.DataFrame(X_resampled, columns=X.columns), pd.Series(y_resampled)
    
    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None
    ) -> Dict[str, Any]:
        """
        Entraîne le modèle
        
        Args:
            X_train: Features d'entraînement
            y_train: Labels d'entraînement
            X_val: Features de validation (optionnel)
            y_val: Labels de validation (optionnel)
            
        Returns:
            Dictionnaire avec résultats d'entraînement
        """
        logger.info(f"🚀 Entraînement du modèle {self.model_type}...")
        
        start_time = datetime.now()
        
        # Rééquilibrage si nécessaire
        X_train_balanced, y_train_balanced = self.handle_imbalance(X_train, y_train)
        
        # Créer et entraîner le modèle
        if self.model_type == 'random_forest':
            self.model = FraudRandomForest(
                n_estimators=200,
                max_depth=15,
                min_samples_split=10,
                class_weight='balanced',
                random_state=42
            )
        elif self.model_type == 'isolation_forest':
            contamination = y_train.mean()  # Proportion de fraudes
            self.model = FraudIsolationForest(
                contamination=contamination,
                n_estimators=100,
                random_state=42
            )
        else:
            raise ValueError(f"Type de modèle inconnu: {self.model_type}")
        
        # Entraînement
        self.model.fit(X_train_balanced, y_train_balanced)
        
        training_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"✅ Modèle entraîné en {training_time:.2f}s")
        
        # Stocker l'historique
        self.training_history = {
            'model_type': self.model_type,
            'training_samples': len(X_train_balanced),
            'training_time_seconds': training_time,
            'use_smote': self.use_smote,
            'fraud_rate_original': y_train.mean(),
            'fraud_rate_balanced': y_train_balanced.mean(),
            'n_features': X_train.shape[1],
            'feature_names': self.feature_names,
            'timestamp': datetime.now().isoformat()
        }
        
        return self.training_history
    
    def save_model(self, output_dir: str = "./data/models/production"):
        """
        Sauvegarde le modèle et tous les composants
        
        Args:
            output_dir: Dossier de sortie
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Sauvegarder le modèle
        model_filename = f"{self.model_type}_{timestamp}.pkl"
        model_path = output_path / model_filename
        self.model.save(str(model_path))
        
        # Sauvegarder le scaler
        if self.scaler:
            scaler_path = output_path / f"scaler_{timestamp}.pkl"
            self.scaler.save(str(scaler_path))
        
        # Sauvegarder le feature extractor (si SÉNTRA)
        if self.feature_extractor:
            extractor_path = output_path / f"feature_extractor_{timestamp}.pkl"
            import joblib
            joblib.dump(self.feature_extractor, str(extractor_path))
        
        # Sauvegarder les métadonnées
        import json
        metadata = {
            **self.training_history,
            'model_path': str(model_path),
            'scaler_path': str(scaler_path) if self.scaler else None,
            'extractor_path': str(extractor_path) if self.feature_extractor else None
        }
        
        metadata_path = output_path / f"metadata_{timestamp}.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"✅ Modèle sauvegardé dans {output_path}")
        logger.info(f"   - Modèle: {model_filename}")
        logger.info(f"   - Métadonnées: metadata_{timestamp}.json")
        
        return str(model_path)
    
    @staticmethod
    def load_model(model_path: str) -> 'FraudModelTrainer':
        """
        Charge un modèle sauvegardé
        
        Args:
            model_path: Chemin vers le modèle
            
        Returns:
            Instance de FraudModelTrainer avec modèle chargé
        """
        import joblib
        
        trainer = FraudModelTrainer()
        trainer.model = joblib.load(model_path)
        
        # Charger scaler et extractor si disponibles
        model_dir = Path(model_path).parent
        timestamp = Path(model_path).stem.split('_')[-1]
        
        scaler_path = model_dir / f"scaler_{timestamp}.pkl"
        if scaler_path.exists():
            trainer.scaler = joblib.load(str(scaler_path))
        
        extractor_path = model_dir / f"feature_extractor_{timestamp}.pkl"
        if extractor_path.exists():
            trainer.feature_extractor = joblib.load(str(extractor_path))
        
        logger.info(f"✅ Modèle chargé: {model_path}")
        
        return trainer