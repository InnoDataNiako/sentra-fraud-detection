"""
Encodeurs pour les variables catégorielles
"""

import pandas as pd
import numpy as np
from typing import Dict, List
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
import joblib
from src.core.logging import get_logger

logger = get_logger(__name__)


class CategoricalEncoder:
    """Encodeur pour les variables catégorielles"""
    
    def __init__(self):
        self.label_encoders = {}
        self.onehot_encoders = {}
        self.fitted = False
    
    def fit(self, df: pd.DataFrame, categorical_columns: List[str]):
        """
        Entraîne les encodeurs sur les données
        
        Args:
            df: DataFrame avec les données
            categorical_columns: Liste des colonnes catégorielles
        """
        logger.info(f"Entraînement encodeurs sur {len(categorical_columns)} colonnes")
        
        for col in categorical_columns:
            if col in df.columns:
                # Label Encoding
                le = LabelEncoder()
                le.fit(df[col].fillna('unknown'))
                self.label_encoders[col] = le
        
        self.fitted = True
        logger.info("✅ Encodeurs entraînés")
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transforme les colonnes catégorielles
        
        Args:
            df: DataFrame à transformer
            
        Returns:
            DataFrame transformé
        """
        if not self.fitted:
            raise ValueError("Encodeurs non entraînés. Appeler fit() d'abord.")
        
        df_encoded = df.copy()
        
        for col, encoder in self.label_encoders.items():
            if col in df_encoded.columns:
                # Gérer les valeurs inconnues
                df_encoded[col] = df_encoded[col].fillna('unknown')
                df_encoded[col] = df_encoded[col].apply(
                    lambda x: x if x in encoder.classes_ else 'unknown'
                )
                df_encoded[f'{col}_encoded'] = encoder.transform(df_encoded[col])
        
        return df_encoded
    
    def fit_transform(self, df: pd.DataFrame, categorical_columns: List[str]) -> pd.DataFrame:
        """
        Entraîne et transforme en une seule étape
        
        Args:
            df: DataFrame avec les données
            categorical_columns: Liste des colonnes catégorielles
            
        Returns:
            DataFrame transformé
        """
        self.fit(df, categorical_columns)
        return self.transform(df)
    
    def save(self, filepath: str):
        """Sauvegarde les encodeurs"""
        joblib.dump(self, filepath)
        logger.info(f"✅ Encodeurs sauvegardés: {filepath}")
    
    @staticmethod
    def load(filepath: str) -> 'CategoricalEncoder':
        """Charge les encodeurs"""
        encoder = joblib.load(filepath)
        logger.info(f"✅ Encodeurs chargés: {filepath}")
        return encoder


class LocationEncoder:
    """Encodeur spécialisé pour les localisations"""
    
    def __init__(self):
        self.location_risk_scores = {}
        self.fitted = False
    
    def fit(self, df: pd.DataFrame, location_column: str = 'location', fraud_column: str = 'is_fraud'):
        """
        Calcule les scores de risque par localisation
        
        Args:
            df: DataFrame avec les données
            location_column: Nom de la colonne localisation
            fraud_column: Nom de la colonne fraude
        """
        logger.info(f"Calcul des scores de risque par localisation")
        
        if location_column in df.columns and fraud_column in df.columns:
            # Calculer le taux de fraude par localisation
            location_stats = df.groupby(location_column)[fraud_column].agg(['mean', 'count'])
            
            # Smooth le score avec un prior bayésien
            global_fraud_rate = df[fraud_column].mean()
            min_samples = 10
            
            location_stats['risk_score'] = (
                (location_stats['mean'] * location_stats['count'] + 
                 global_fraud_rate * min_samples) / 
                (location_stats['count'] + min_samples)
            )
            
            self.location_risk_scores = location_stats['risk_score'].to_dict()
            self.fitted = True
            
            logger.info(f"✅ Scores calculés pour {len(self.location_risk_scores)} localisations")
    
    def transform(self, df: pd.DataFrame, location_column: str = 'location') -> pd.DataFrame:
        """
        Ajoute les scores de risque par localisation
        
        Args:
            df: DataFrame à transformer
            location_column: Nom de la colonne localisation
            
        Returns:
            DataFrame avec colonne 'location_risk_score'
        """
        if not self.fitted:
            raise ValueError("Encodeur non entraîné. Appeler fit() d'abord.")
        
        df_transformed = df.copy()
        
        # Score par défaut pour localisations inconnues (moyenne)
        default_score = np.mean(list(self.location_risk_scores.values())) if self.location_risk_scores else 0.5
        
        df_transformed['location_risk_score'] = df_transformed[location_column].map(
            self.location_risk_scores
        ).fillna(default_score)
        
        return df_transformed
    
    def fit_transform(self, df: pd.DataFrame, location_column: str = 'location', fraud_column: str = 'is_fraud') -> pd.DataFrame:
        """Entraîne et transforme en une seule étape"""
        self.fit(df, location_column, fraud_column)
        return self.transform(df, location_column)
    
    def save(self, filepath: str):
        """Sauvegarde l'encodeur"""
        joblib.dump(self, filepath)
        logger.info(f"✅ Encodeur localisation sauvegardé: {filepath}")
    
    @staticmethod
    def load(filepath: str) -> 'LocationEncoder':
        """Charge l'encodeur"""
        encoder = joblib.load(filepath)
        logger.info(f"✅ Encodeur localisation chargé: {filepath}")
        return encoder