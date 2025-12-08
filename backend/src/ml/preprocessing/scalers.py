"""
Scalers pour la normalisation des features numériques
"""

import pandas as pd
import numpy as np
from typing import List, Optional
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, PowerTransformer  # AJOUT

import joblib
from src.core.logging import get_logger

logger = get_logger(__name__)


class FeatureScaler:
    """Scaler pour normaliser les features numériques"""
    
    def __init__(self, scaler_type: str = 'standard'):
        """
        Args:
            scaler_type: Type de scaler ('standard', 'minmax', 'robust')
        """
        self.scaler_type = scaler_type
        self.scaler = self._get_scaler(scaler_type)
        self.feature_names = []
        self.fitted = False
    
    def _get_scaler(self, scaler_type: str):
        """Retourne le scaler approprié"""
        scalers = {
            'standard': StandardScaler(),
            'minmax': MinMaxScaler(),
            'robust': RobustScaler(),
            'power': PowerTransformer(method='yeo-johnson')  # Nouveau

        }
        
        if scaler_type not in scalers:
            logger.warning(f"Type de scaler inconnu: {scaler_type}, utilisation de 'standard'")
            scaler_type = 'standard'
        
        return scalers[scaler_type]
    
    def fit(self, df: pd.DataFrame, numeric_columns: Optional[List[str]] = None):
        """
        Entraîne le scaler sur les données
        
        Args:
            df: DataFrame avec les données
            numeric_columns: Liste des colonnes à normaliser (auto-détection si None)
        """
        if numeric_columns is None:
            # Auto-détection des colonnes numériques
            numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        self.feature_names = numeric_columns
        
        logger.info(f"Entraînement {self.scaler_type} scaler sur {len(numeric_columns)} colonnes")
        
        # Fit sur les colonnes sélectionnées
        self.scaler.fit(df[numeric_columns])
        self.fitted = True
        
        logger.info("✅ Scaler entraîné")
    
    def transform(self, df: pd.DataFrame, inplace: bool = False) -> pd.DataFrame:
        """
        Normalise les features
        
        Args:
            df: DataFrame à transformer
            inplace: Si True, modifie df directement
            
        Returns:
            DataFrame transformé
        """
        if not self.fitted:
            raise ValueError("Scaler non entraîné. Appeler fit() d'abord.")
        
        df_scaled = df if inplace else df.copy()
        
        # Vérifier que toutes les colonnes existent
        missing_cols = set(self.feature_names) - set(df.columns)
        if missing_cols:
            logger.warning(f"Colonnes manquantes: {missing_cols}")
            # Utiliser seulement les colonnes disponibles
            available_cols = [col for col in self.feature_names if col in df.columns]
        else:
            available_cols = self.feature_names
        
        if available_cols:
            df_scaled[available_cols] = self.scaler.transform(df[available_cols])
        
        return df_scaled
    
    def fit_transform(self, df: pd.DataFrame, numeric_columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Entraîne et transforme en une seule étape
        
        Args:
            df: DataFrame avec les données
            numeric_columns: Liste des colonnes à normaliser
            
        Returns:
            DataFrame transformé
        """
        self.fit(df, numeric_columns)
        return self.transform(df)
    
    def inverse_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Inverse la normalisation
        
        Args:
            df: DataFrame normalisé
            
        Returns:
            DataFrame dans l'échelle originale
        """
        if not self.fitted:
            raise ValueError("Scaler non entraîné.")
        
        df_original = df.copy()
        df_original[self.feature_names] = self.scaler.inverse_transform(df[self.feature_names])
        return df_original
    
    def save(self, filepath: str):
        """Sauvegarde le scaler"""
        joblib.dump(self, filepath)
        logger.info(f"✅ Scaler sauvegardé: {filepath}")
    
    @staticmethod
    def load(filepath: str) -> 'FeatureScaler':
        """Charge le scaler"""
        scaler = joblib.load(filepath)
        logger.info(f"✅ Scaler chargé: {filepath}")
        return scaler


class PreprocessingPipeline:
    """Pipeline complet de preprocessing"""
    
    def __init__(self):
        self.feature_extractor = None
        self.encoders = None
        self.scaler = None
        self.feature_columns = []
        self.fitted = False
    
    def fit(self, df: pd.DataFrame, target_column: str = 'is_fraud'):
        """
        Entraîne le pipeline complet
        
        Args:
            df: DataFrame avec les données d'entraînement
            target_column: Nom de la colonne cible
        """
        logger.info("🔧 Entraînement du pipeline de preprocessing...")
        
        from .features import FraudFeatureExtractor
        from .encoders import CategoricalEncoder
        
        # 1. Feature extraction
        logger.info("1/3 Extraction features...")
        self.feature_extractor = FraudFeatureExtractor()
        features_df = self.feature_extractor.extract_features_dataframe(df)
        
        # 2. Encoding (si nécessaire)
        logger.info("2/3 Encodage variables catégorielles...")
        categorical_cols = features_df.select_dtypes(include=['object']).columns.tolist()
        if categorical_cols:
            self.encoders = CategoricalEncoder()
            features_df = self.encoders.fit_transform(features_df, categorical_cols)
        
        # 3. Scaling
        logger.info("3/3 Normalisation features...")
        numeric_cols = features_df.select_dtypes(include=[np.number]).columns.tolist()
        self.scaler = FeatureScaler(scaler_type='standard')
        features_df = self.scaler.fit_transform(features_df, numeric_cols)
        
        self.feature_columns = features_df.columns.tolist()
        self.fitted = True
        
        logger.info(f"✅ Pipeline entraîné - {len(self.feature_columns)} features")
        
        return features_df
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transforme de nouvelles données
        
        Args:
            df: DataFrame à transformer
            
        Returns:
            DataFrame avec features preprocessées
        """
        if not self.fitted:
            raise ValueError("Pipeline non entraîné. Appeler fit() d'abord.")
        
        # Feature extraction
        features_df = self.feature_extractor.extract_features_dataframe(df)
        
        # Encoding
        if self.encoders:
            features_df = self.encoders.transform(features_df)
        
        # Scaling
        features_df = self.scaler.transform(features_df)
        
        # S'assurer que toutes les colonnes attendues sont présentes
        missing_cols = set(self.feature_columns) - set(features_df.columns)
        if missing_cols:
            logger.warning(f"Colonnes manquantes: {missing_cols}, remplissage avec 0")
            for col in missing_cols:
                features_df[col] = 0
        
        return features_df[self.feature_columns]
    
    def fit_transform(self, df: pd.DataFrame, target_column: str = 'is_fraud') -> pd.DataFrame:
        """Entraîne et transforme en une seule étape"""
        return self.fit(df, target_column)
    
    def save(self, filepath: str):
        """Sauvegarde le pipeline complet"""
        joblib.dump(self, filepath)
        logger.info(f"✅ Pipeline sauvegardé: {filepath}")
    
    @staticmethod
    def load(filepath: str) -> 'PreprocessingPipeline':
        """Charge le pipeline"""
        pipeline = joblib.load(filepath)
        logger.info(f"✅ Pipeline chargé: {filepath}")
        return pipeline