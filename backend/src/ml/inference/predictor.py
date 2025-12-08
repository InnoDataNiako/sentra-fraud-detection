# """
# Classe générique de prédiction pour la détection de fraude
# Supporte les modèles Kaggle et SÉNTRA
# """

# import pandas as pd
# import numpy as np
# import joblib
# from typing import Dict, Any, Optional, List
# from pathlib import Path
# from datetime import datetime
# from src.core.logging import get_logger

# logger = get_logger(__name__)


# class FraudPredictor:
#     """
#     Prédicteur générique pour la détection de fraude
#     Charge et utilise un modèle entraîné
#     """
    
#     def __init__(self, model_path: str, model_type: str = 'sentra'):
#         """
#         Args:
#             model_path: Chemin vers le modèle (.pkl)
#             model_type: Type de modèle ('sentra' ou 'kaggle')
#         """
#         self.model_path = model_path
#         self.model_type = model_type
#         self.model = None
#         self.scaler = None
#         self.feature_extractor = None
#         self.metadata = None
        
#         self._load_model()
        
#         logger.info(f"✅ Prédicteur {model_type} initialisé")
    
#     def _load_model(self):
#         """Charge le modèle et ses dépendances"""
        
#         model_path = Path(self.model_path)
        
#         if not model_path.exists():
#             raise FileNotFoundError(f"Modèle non trouvé: {self.model_path}")
        
#         # Charger le modèle principal
#         self.model = joblib.load(str(model_path))
#         logger.info(f"   - Modèle chargé: {model_path.name}")
        
#         # Extraire timestamp du nom de fichier
#         # Ex: random_forest_20251117_193806.pkl -> 20251117_193806
#         timestamp = '_'.join(model_path.stem.split('_')[-2:])
#         model_dir = model_path.parent
        
#         # Charger le scaler
#         scaler_path = model_dir / f"scaler_{timestamp}.pkl"
#         if scaler_path.exists():
#             self.scaler = joblib.load(str(scaler_path))
#             logger.info(f"   - Scaler chargé")
        
#         # Charger le feature extractor (SÉNTRA uniquement)
#         if self.model_type == 'sentra':
#             extractor_path = model_dir / f"feature_extractor_{timestamp}.pkl"
#             if extractor_path.exists():
#                 self.feature_extractor = joblib.load(str(extractor_path))
#                 logger.info(f"   - Feature extractor chargé")
        
#         # Charger les métadonnées
#         metadata_path = model_dir / f"metadata_{timestamp}.json"
#         if metadata_path.exists():
#             import json
#             with open(metadata_path, 'r') as f:
#                 self.metadata = json.load(f)
#             logger.info(f"   - Métadonnées chargées")
    
#     def predict_single(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
#         """
#         Prédit si une transaction est frauduleuse
        
#         Args:
#             transaction: Dictionnaire avec les données de la transaction
            
#         Returns:
#             Dictionnaire avec le résultat de la prédiction
#         """
#         start_time = datetime.now()
        
#         # Préparer les données
#         if self.model_type == 'sentra':
#             # Extraction de features pour SÉNTRA
#             features = self._prepare_sentra_features(transaction)
#         else:
#             # Features Kaggle (déjà extraites)
#             features = self._prepare_kaggle_features(transaction)
        
#         # Prédiction
#         prediction = self.model.predict(features)[0]
#         probability = self.model.get_fraud_probability(features)[0]
        
#         # Temps de traitement
#         processing_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        
#         # Déterminer le niveau de risque
#         risk_level = self._get_risk_level(probability)
        
#         # Construire le résultat
#         result = {
#             'transaction_id': transaction.get('transaction_id', 'unknown'),
#             'is_fraud': bool(prediction),
#             'fraud_probability': float(probability),
#             'risk_level': risk_level,
#             'confidence_score': float(probability if prediction else 1 - probability),
#             'model_type': self.model_type,
#             'ml_model_version': self.metadata.get('model_type', 'unknown') if self.metadata else 'unknown',  # Renommé
#             'processing_time_ms': round(processing_time_ms, 2),
#             'timestamp': datetime.now().isoformat()
#         }
        
#         # Ajouter recommandation
#         result['recommendation'] = self._get_recommendation(probability, prediction)
#         result['should_block'] = prediction and probability > 0.8
        
#         logger.info(f"Prédiction {self.model_type}: fraud={prediction}, proba={probability:.4f}")
        
#         return result
    
#     def _prepare_sentra_features(self, transaction: Dict[str, Any]) -> pd.DataFrame:
#         """Prépare les features pour le modèle SÉNTRA"""
        
#         # Créer DataFrame
#         df = pd.DataFrame([transaction])
        
#         # Extraction de features
#         if self.feature_extractor:
#             features = self.feature_extractor.extract_features(transaction)
#             features_df = pd.DataFrame([features])
#         else:
#             # Fallback: utiliser directement les données
#             features_df = df
        
#         # Normalisation
#         if self.scaler:
#             features_df = self.scaler.transform(features_df)
        
#         return features_df
    
#     def _prepare_kaggle_features(self, transaction: Dict[str, Any]) -> pd.DataFrame:
#         """Prépare les features pour le modèle Kaggle"""
        
#         # Pour Kaggle, on attend que les features V1-V28, Time, Amount soient déjà présentes
#         df = pd.DataFrame([transaction])
        
#         # Normalisation
#         if self.scaler:
#             df = self.scaler.transform(df)
        
#         return df
    
#     def _get_risk_level(self, probability: float) -> str:
#         """Détermine le niveau de risque"""
#         if probability < 0.3:
#             return 'low'
#         elif probability < 0.6:
#             return 'medium'
#         elif probability < 0.85:
#             return 'high'
#         else:
#             return 'critical'
    
#     def _get_recommendation(self, probability: float, is_fraud: bool) -> str:
#         """Génère une recommandation d'action"""
#         if not is_fraud:
#             return "Approuver la transaction"
        
#         if probability > 0.9:
#             return "Bloquer immédiatement et contacter le client"
#         elif probability > 0.7:
#             return "Bloquer et demander authentification supplémentaire"
#         elif probability > 0.5:
#             return "Mettre en revue manuelle"
#         else:
#             return "Surveiller et logger"
    
#     def predict_batch(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#         """
#         Prédit sur un batch de transactions
        
#         Args:
#             transactions: Liste de transactions
            
#         Returns:
#             Liste de résultats
#         """
#         results = []
#         for transaction in transactions:
#             try:
#                 result = self.predict_single(transaction)
#                 results.append(result)
#             except Exception as e:
#                 logger.error(f"Erreur prédiction: {e}")
#                 results.append({
#                     'transaction_id': transaction.get('transaction_id', 'unknown'),
#                     'error': str(e)
#                 })
        
#         return results
    
#     def get_model_info(self) -> Dict[str, Any]:
#         """Retourne les informations du modèle"""
#         info = {
#             'model_type': self.model_type,
#             'model_path': str(self.model_path),
#             'has_scaler': self.scaler is not None,
#             'has_feature_extractor': self.feature_extractor is not None,
#         }
        
#         if self.metadata:
#             info.update({
#                 'training_date': self.metadata.get('timestamp'),
#                 'training_samples': self.metadata.get('training_samples'),
#                 'n_features': self.metadata.get('n_features'),
#             })
        
#         return info


# """ DEUXIEME """


# """
# Classe générique de prédiction pour la détection de fraude
# Supporte les modèles Kaggle et SÉNTRA
# """

# import pandas as pd
# import numpy as np
# import joblib
# from typing import Dict, Any, Optional, List
# from pathlib import Path
# from datetime import datetime
# from src.core.logging import get_logger

# logger = get_logger(__name__)


# class FraudPredictor:
#     """
#     Prédicteur générique pour la détection de fraude
#     Charge et utilise un modèle entraîné
#     """
    
#     def __init__(self, model_path: str, model_type: str = 'sentra'):
#         """
#         Args:
#             model_path: Chemin vers le modèle (.pkl)
#             model_type: Type de modèle ('sentra' ou 'kaggle')
#         """
#         self.model_path = model_path
#         self.model_type = model_type
#         self.model = None
#         self.scaler = None
#         self.feature_extractor = None
#         self.metadata = None
        
#         self._load_model()
        
#         logger.info(f"✅ Prédicteur {model_type} initialisé")
    
#     def _load_model(self):
#         """Charge le modèle et ses dépendances"""
        
#         model_path = Path(self.model_path)
        
#         if not model_path.exists():
#             raise FileNotFoundError(f"Modèle non trouvé: {self.model_path}")
        
#         # Charger le modèle principal
#         self.model = joblib.load(str(model_path))
#         logger.info(f"   - Modèle chargé: {model_path.name}")
        
#         # Extraire timestamp du nom de fichier
#         # Ex: random_forest_20251117_193806.pkl -> 20251117_193806
#         timestamp = '_'.join(model_path.stem.split('_')[-2:])
#         model_dir = model_path.parent
        
#         # Charger le scaler
#         scaler_path = model_dir / f"scaler_{timestamp}.pkl"
#         if scaler_path.exists():
#             self.scaler = joblib.load(str(scaler_path))
#             logger.info(f"   - Scaler chargé")
        
#         # Charger le feature extractor (SÉNTRA uniquement)
#         if self.model_type == 'sentra':
#             extractor_path = model_dir / f"feature_extractor_{timestamp}.pkl"
#             if extractor_path.exists():
#                 self.feature_extractor = joblib.load(str(extractor_path))
#                 logger.info(f"   - Feature extractor chargé")
        
#         # Charger les métadonnées
#         metadata_path = model_dir / f"metadata_{timestamp}.json"
#         if metadata_path.exists():
#             import json
#             with open(metadata_path, 'r') as f:
#                 self.metadata = json.load(f)
#             logger.info(f"   - Métadonnées chargées")
#     def predict_single(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
#         """
#         Prédit si une transaction est frauduleuse
#         """
#         start_time = datetime.now()
        
#         # Préparer les données
#         if self.model_type == 'sentra':
#             features = self._prepare_sentra_features(transaction)
#         else:
#             features = self._prepare_kaggle_features(transaction)
        
#         # ⚠️ CORRECTION ICI : Utiliser predict_proba au lieu de get_fraud_probability
#         try:
#             # Prédiction binaire
#             prediction = self.model.predict(features)[0]
            
#             # Probabilité (si le modèle le supporte)
#             if hasattr(self.model, 'predict_proba'):
#                 probabilities = self.model.predict_proba(features)[0]
#                 if len(probabilities) == 2:  # Classification binaire
#                     probability = float(probabilities[1])  # Classe 1 = fraude
#                 else:
#                     probability = float(probabilities[0])
#             elif hasattr(self.model, 'decision_function'):
#                 # Pour Isolation Forest, SVM, etc.
#                 score = self.model.decision_function(features)[0]
#                 # Convertir score en probabilité approximative
#                 probability = 1 / (1 + np.exp(-score))
#             else:
#                 # Fallback
#                 probability = 0.5 if prediction == 1 else 0.1
            
#         except Exception as e:
#             logger.error(f"Erreur prédiction: {e}")
#             # Valeurs par défaut en cas d'erreur
#             prediction = 0
#             probability = 0.1
        
#         # Temps de traitement
#         processing_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        
#         # Déterminer le niveau de risque
#         risk_level = self._get_risk_level(probability)
        
#         # Construire le résultat
#         result = {
#             'transaction_id': transaction.get('transaction_id', 'unknown'),
#             'is_fraud': bool(prediction),
#             'fraud_probability': float(probability),
#             'risk_level': risk_level,
#             'confidence_score': float(probability if prediction else 1 - probability),
#             'model_type': self.model_type,
#             'model_version': self.metadata.get('model_type', 'unknown') if self.metadata else 'unknown',
#             'processing_time_ms': round(processing_time_ms, 2),
#             'timestamp': datetime.now().isoformat()
#         }
        
#         # Ajouter recommandation
#         result['recommendation'] = self._get_recommendation(probability, prediction)
#         result['should_block'] = prediction and probability > 0.8
        
#         logger.info(f"Prédiction {self.model_type}: fraud={prediction}, proba={probability:.4f}")
        
#         return result
#     def _prepare_sentra_features(self, transaction: Dict[str, Any]) -> np.ndarray:
#         """Prépare les features pour le modèle SÉNTRA"""
        
#         # 🔧 CORRECTION : Créer une copie pour ne pas modifier l'original
#         tx_data = transaction.copy()
        
#         # 🔧 CORRECTION : Parser le timestamp AVANT l'extraction
#         if 'timestamp' in tx_data and isinstance(tx_data['timestamp'], str):
#             tx_time = datetime.fromisoformat(tx_data['timestamp'].replace('Z', '+00:00'))
            
#             # Ajouter les features temporelles en tant qu'entiers
#             tx_data['hour'] = int(tx_time.hour)
#             tx_data['day_of_week'] = int(tx_time.weekday())
#             tx_data['is_weekend'] = int(tx_time.weekday() >= 5)
#             tx_data['is_night'] = int(tx_time.hour <= 5 or tx_time.hour >= 23)
#             tx_data['month'] = int(tx_time.month)
#             tx_data['day'] = int(tx_time.day)
        
#         # 🔧 CORRECTION : S'assurer que amount est un float
#         if 'amount' in tx_data:
#             tx_data['amount'] = float(tx_data['amount'])
        
#         # Extraction de features
#         if self.feature_extractor:
#             features = self.feature_extractor.extract_features(tx_data)
#             if isinstance(features, dict):
#                 # Convertir dict -> DataFrame
#                 features_df = pd.DataFrame([features])
#             else:
#                 features_df = pd.DataFrame([features])
#         else:
#             # Fallback: utiliser directement les données
#             features_df = pd.DataFrame([tx_data])
        
#         # Normalisation
#         if self.scaler:
#             features_array = self.scaler.transform(features_df)
#             return features_array
        
#         return features_df.values
    
#     def _prepare_kaggle_features(self, transaction: Dict[str, Any]) -> np.ndarray:
#         """Prépare les features pour le modèle Kaggle"""
        
#         # Pour Kaggle, on attend que les features V1-V28, Time, Amount soient déjà présentes
#         df = pd.DataFrame([transaction])
        
#         # Normalisation
#         if self.scaler:
#             features_array = self.scaler.transform(df)
#             return features_array
        
#         return df.values
    
#     def _get_risk_level(self, probability: float) -> str:
#         """Détermine le niveau de risque"""
#         if probability < 0.3:
#             return 'low'
#         elif probability < 0.6:
#             return 'medium'
#         elif probability < 0.85:
#             return 'high'
#         else:
#             return 'critical'
    
#     def _get_recommendation(self, probability: float, is_fraud: bool) -> str:
#         """Génère une recommandation d'action"""
#         if not is_fraud:
#             return "Approuver la transaction"
        
#         if probability > 0.9:
#             return "Bloquer immédiatement et contacter le client"
#         elif probability > 0.7:
#             return "Bloquer et demander authentification supplémentaire"
#         elif probability > 0.5:
#             return "Mettre en revue manuelle"
#         else:
#             return "Surveiller et logger"
    
#     def predict_batch(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#         """
#         Prédit sur un batch de transactions
        
#         Args:
#             transactions: Liste de transactions
            
#         Returns:
#             Liste de résultats
#         """
#         results = []
#         for transaction in transactions:
#             try:
#                 result = self.predict_single(transaction)
#                 results.append(result)
#             except Exception as e:
#                 logger.error(f"Erreur prédiction: {e}")
#                 results.append({
#                     'transaction_id': transaction.get('transaction_id', 'unknown'),
#                     'error': str(e)
#                 })
        
#         return results
    
#     def get_model_info(self) -> Dict[str, Any]:
#         """Retourne les informations du modèle"""
#         info = {
#             'model_type': self.model_type,
#             'model_path': str(self.model_path),
#             'has_scaler': self.scaler is not None,
#             'has_feature_extractor': self.feature_extractor is not None,
#         }
        
#         if self.metadata:
#             info.update({
#                 'training_date': self.metadata.get('timestamp'),
#                 'training_samples': self.metadata.get('training_samples'),
#                 'n_features': self.metadata.get('n_features'),
#             })
        
#         return info



""" TROISIEME """


"""
Classe générique de prédiction pour la détection de fraude
Supporte les modèles Kaggle et SÉNTRA
"""

import pandas as pd
import numpy as np
import joblib
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
from src.core.logging import get_logger

logger = get_logger(__name__)


class FraudPredictor:
    """
    Prédicteur générique pour la détection de fraude
    Charge et utilise un modèle entraîné
    """
    
    def __init__(self, model_path: str, model_type: str = 'sentra'):
        """
        Args:
            model_path: Chemin vers le modèle (.pkl)
            model_type: Type de modèle ('sentra' ou 'kaggle')
        """
        self.model_path = model_path
        self.model_type = model_type
        self.model = None
        self.scaler = None
        self.feature_extractor = None
        self.metadata = None
        
        self._load_model()
        
        logger.info(f"✅ Prédicteur {model_type} initialisé")
    
    def _load_model(self):
        """Charge le modèle et ses dépendances"""
        
        model_path = Path(self.model_path)
        
        if not model_path.exists():
            raise FileNotFoundError(f"Modèle non trouvé: {self.model_path}")
        
        # Charger le modèle principal
        self.model = joblib.load(str(model_path))
        logger.info(f"   - Modèle chargé: {model_path.name}")
        
        # Extraire timestamp du nom de fichier
        # Ex: random_forest_20251117_193806.pkl -> 20251117_193806
        timestamp = '_'.join(model_path.stem.split('_')[-2:])
        model_dir = model_path.parent
        
        # Charger le scaler
        scaler_path = model_dir / f"scaler_{timestamp}.pkl"
        if scaler_path.exists():
            self.scaler = joblib.load(str(scaler_path))
            logger.info(f"   - Scaler chargé")
        
        # Charger le feature extractor (SÉNTRA uniquement)
        if self.model_type == 'sentra':
            extractor_path = model_dir / f"feature_extractor_{timestamp}.pkl"
            if extractor_path.exists():
                self.feature_extractor = joblib.load(str(extractor_path))
                logger.info(f"   - Feature extractor chargé")
        
        # Charger les métadonnées
        metadata_path = model_dir / f"metadata_{timestamp}.json"
        if metadata_path.exists():
            import json
            with open(metadata_path, 'r') as f:
                self.metadata = json.load(f)
            logger.info(f"   - Métadonnées chargées")
    
    def predict_single(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prédit si une transaction est frauduleuse
        """
        start_time = datetime.now()
        
        try:
            # Préparer les données
            if self.model_type == 'sentra':
                features = self._prepare_sentra_features(transaction)
            else:
                features = self._prepare_kaggle_features(transaction)
            
            # ⚠️ CORRECTION ICI : Utiliser predict_proba au lieu de get_fraud_probability
            try:
                # Prédiction binaire
                prediction = self.model.predict(features)[0]
                
                # Probabilité (si le modèle le supporte)
                if hasattr(self.model, 'predict_proba'):
                    probabilities = self.model.predict_proba(features)[0]
                    if len(probabilities) == 2:  # Classification binaire
                        probability = float(probabilities[1])  # Classe 1 = fraude
                    else:
                        probability = float(probabilities[0])
                elif hasattr(self.model, 'decision_function'):
                    # Pour Isolation Forest, SVM, etc.
                    score = self.model.decision_function(features)[0]
                    # Convertir score en probabilité approximative
                    probability = 1 / (1 + np.exp(-score))
                else:
                    # Fallback
                    probability = 0.5 if prediction == 1 else 0.1
                
            except Exception as e:
                logger.error(f"Erreur prédiction ML: {e}")
                # Valeurs par défaut en cas d'erreur
                prediction = 0
                probability = 0.1
            
            # Temps de traitement
            processing_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            # Déterminer le niveau de risque
            risk_level = self._get_risk_level(probability)
            
            # Construire le résultat
            result = {
                'transaction_id': transaction.get('transaction_id', 'unknown'),
                'is_fraud': bool(prediction),
                'fraud_probability': float(probability),
                'risk_level': risk_level,
                'confidence_score': float(probability if prediction else 1 - probability),
                'model_type': self.model_type,
                'model_version': self.metadata.get('model_type', 'unknown') if self.metadata else 'unknown',
                'processing_time_ms': round(processing_time_ms, 2),
                'timestamp': datetime.now().isoformat()
            }
            
            # Ajouter recommandation
            result['recommendation'] = self._get_recommendation(probability, prediction)
            result['should_block'] = prediction and probability > 0.8
            
            logger.info(f"Prédiction {self.model_type}: fraud={prediction}, proba={probability:.4f}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur complète prédiction: {e}")
            # Retourner un résultat minimal en cas d'erreur
            return {
                'transaction_id': transaction.get('transaction_id', 'unknown'),
                'is_fraud': False,
                'fraud_probability': 0.1,
                'risk_level': 'low',
                'confidence_score': 0.9,
                'model_type': self.model_type,
                'model_version': 'error',
                'processing_time_ms': 0.0,
                'timestamp': datetime.now().isoformat(),
                'recommendation': 'Erreur système - Transaction approuvée',
                'should_block': False,
                'error': str(e)
            }
    
    def _prepare_sentra_features(self, transaction: Dict[str, Any]) -> np.ndarray:
        """Prépare les features pour le modèle SÉNTRA"""
        
        # 🔧 CORRECTION : Créer une copie pour ne pas modifier l'original
        tx_data = transaction.copy()
        
        # 🔧 CORRECTION : Parser le timestamp AVANT l'extraction - VERSION CORRIGÉE
        if 'timestamp' in tx_data:
            timestamp = tx_data['timestamp']
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
                    tx_time = datetime.utcnow()
                
                # Ajouter les features temporelles en tant qu'entiers
                tx_data['hour'] = int(tx_time.hour)
                tx_data['day_of_week'] = int(tx_time.weekday())
                tx_data['is_weekend'] = int(tx_time.weekday() >= 5)
                tx_data['is_night'] = int(tx_time.hour <= 5 or tx_time.hour >= 23)
                tx_data['month'] = int(tx_time.month)
                tx_data['day'] = int(tx_time.day)
                
            except Exception as e:
                logger.warning(f"⚠️ Erreur parsing timestamp '{timestamp}' dans predictor: {e}")
                # Valeurs par défaut
                tx_time = datetime.utcnow()
                tx_data['hour'] = 12
                tx_data['day_of_week'] = 3
                tx_data['is_weekend'] = 0
                tx_data['is_night'] = 0
                tx_data['month'] = tx_time.month
                tx_data['day'] = tx_time.day
        
        # 🔧 CORRECTION : S'assurer que amount est un float
        if 'amount' in tx_data:
            try:
                tx_data['amount'] = float(tx_data['amount'])
            except (ValueError, TypeError):
                tx_data['amount'] = 0.0
        
        # 🔧 CORRECTION : Extraire l'ID numérique du customer_id si nécessaire
        if 'customer_id' in tx_data and isinstance(tx_data['customer_id'], str):
            # Essayer d'extraire un numéro si format "cust_123"
            import re
            match = re.search(r'\d+', tx_data['customer_id'])
            if match:
                tx_data['customer_id_numeric'] = int(match.group())
            else:
                # Fallback : utiliser un hash
                tx_data['customer_id_numeric'] = hash(tx_data['customer_id']) % 10000
        
        # Extraction de features
        if self.feature_extractor:
            try:
                features = self.feature_extractor.extract_features(tx_data)
                if isinstance(features, dict):
                    # Convertir dict -> DataFrame
                    features_df = pd.DataFrame([features])
                else:
                    features_df = pd.DataFrame([features])
            except Exception as e:
                logger.error(f"❌ Erreur extraction features: {e}")
                # Fallback: utiliser directement les données
                features_df = pd.DataFrame([tx_data])
        else:
            # Fallback: utiliser directement les données
            features_df = pd.DataFrame([tx_data])
        
        # Normalisation
        if self.scaler:
            try:
                features_array = self.scaler.transform(features_df)
                return features_array
            except Exception as e:
                logger.error(f"❌ Erreur normalisation: {e}")
                return features_df.values
        
        return features_df.values
    
    def _prepare_kaggle_features(self, transaction: Dict[str, Any]) -> np.ndarray:
        """Prépare les features pour le modèle Kaggle"""
        
        # Pour Kaggle, on attend que les features V1-V28, Time, Amount soient déjà présentes
        df = pd.DataFrame([transaction])
        
        # Normalisation
        if self.scaler:
            try:
                features_array = self.scaler.transform(df)
                return features_array
            except Exception as e:
                logger.error(f"❌ Erreur normalisation Kaggle: {e}")
                return df.values
        
        return df.values
    
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
        """Génère une recommandation d'action"""
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
        """
        Prédit sur un batch de transactions
        
        Args:
            transactions: Liste de transactions
            
        Returns:
            Liste de résultats
        """
        results = []
        for transaction in transactions:
            try:
                result = self.predict_single(transaction)
                results.append(result)
            except Exception as e:
                logger.error(f"Erreur prédiction batch: {e}")
                results.append({
                    'transaction_id': transaction.get('transaction_id', 'unknown'),
                    'error': str(e)
                })
        
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """Retourne les informations du modèle"""
        info = {
            'model_type': self.model_type,
            'model_path': str(self.model_path),
            'has_scaler': self.scaler is not None,
            'has_feature_extractor': self.feature_extractor is not None,
        }
        
        if self.metadata:
            info.update({
                'training_date': self.metadata.get('timestamp'),
                'training_samples': self.metadata.get('training_samples'),
                'n_features': self.metadata.get('n_features'),
            })
        
        return info