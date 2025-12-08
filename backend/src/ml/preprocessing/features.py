# """
# Feature Engineering pour la détection de fraude
# Extraction et création de features pertinentes
# """

# import pandas as pd
# import numpy as np
# from typing import Dict, Any, Optional
# from datetime import datetime, timedelta
# from src.core.logging import get_logger

# logger = get_logger(__name__)


# class FraudFeatureExtractor:
#     """Extracteur de features pour la détection de fraude"""
    
#     def __init__(self):
#         self.feature_names = []
    
#     def extract_features(self, transaction: Dict[str, Any], historical_data: Optional[pd.DataFrame] = None) -> Dict[str, float]:
#         """
#         Extrait toutes les features d'une transaction
        
#         Args:
#             transaction: Dictionnaire contenant les données de la transaction
#             historical_data: DataFrame avec l'historique des transactions du client
            
#         Returns:
#             Dict[str, float]: Dictionnaire des features extraites
#         """
#         features = {}
        
#         # === FEATURES BASIQUES ===
#         features.update(self._extract_basic_features(transaction))
        
#         # === FEATURES TEMPORELLES ===
#         features.update(self._extract_temporal_features(transaction))
        
#         # === FEATURES COMPORTEMENTALES (si historique disponible) ===
#         if historical_data is not None and len(historical_data) > 0:
#             features.update(self._extract_behavioral_features(transaction, historical_data))
#         else:
#             # Features par défaut si pas d'historique
#             features.update(self._get_default_behavioral_features())
        
#         # === FEATURES DÉRIVÉES ===
#         features.update(self._extract_derived_features(transaction, features))
        
#         self.feature_names = list(features.keys())
#         return features
    
#     def _extract_basic_features(self, transaction: Dict[str, Any]) -> Dict[str, float]:
#         """Extrait les features de base de la transaction"""
#         features = {}
        
#         # Montant
#         features['amount'] = float(transaction.get('amount', 0))
#         features['amount_log'] = np.log1p(features['amount'])  # Log pour réduire skewness
        
#         # Montant binné (catégories de montant)
#         if features['amount'] < 10000:
#             features['amount_category'] = 0  # Petit
#         elif features['amount'] < 50000:
#             features['amount_category'] = 1  # Moyen
#         elif features['amount'] < 200000:
#             features['amount_category'] = 2  # Grand
#         else:
#             features['amount_category'] = 3  # Très grand
        
#         # Type de transaction (encodé)
#         tx_type = transaction.get('transaction_type', 'payment')
#         features['is_transfer'] = 1 if tx_type == 'transfer' else 0
#         features['is_withdrawal'] = 1 if tx_type == 'withdrawal' else 0
#         features['is_payment'] = 1 if tx_type == 'payment' else 0
        
#         # Méthode de paiement
#         payment_method = transaction.get('payment_method', 'mobile')
#         features['is_card'] = 1 if payment_method == 'card' else 0
#         features['is_mobile'] = 1 if payment_method == 'mobile' else 0
#         features['is_bank_transfer'] = 1 if payment_method == 'bank_transfer' else 0
        
#         # Présence de merchant
#         features['has_merchant'] = 1 if transaction.get('merchant_id') else 0
        
#         return features
    

#     def _extract_advanced_features(self, transaction: Dict, historical_data: pd.DataFrame) -> Dict:
#         """Features avancées pour améliorer la détection"""
#         features = {}
        
#         # 1. Distance depuis lieu habituel (si géoloc disponible)
#         if 'latitude' in transaction and 'longitude' in transaction:
#             usual_location = historical_data[['latitude', 'longitude']].mean()
#             current_location = [transaction['latitude'], transaction['longitude']]
#             features['distance_from_usual_km'] = self._calculate_distance(usual_location, current_location)
        
#         # 2. Similarité device (même device que transactions précédentes)
#         current_device = transaction.get('device_id')
#         if current_device and len(historical_data) > 0:
#             usual_devices = historical_data['device_id'].unique()
#             features['is_new_device'] = 0 if current_device in usual_devices else 1
        
#         # 3. Pattern horaire inhabituel pour ce client
#         if len(historical_data) > 0:
#             usual_hours = historical_data['hour'].mode()
#             current_hour = features.get('hour', 12)
#             features['unusual_hour'] = 0 if current_hour in usual_hours else 1
        
#         return features

#     def _calculate_distance(self, loc1: list, loc2: list) -> float:
#         """Calcule la distance entre deux points géographiques (simplifié)"""
#         # Formule haversine simplifiée pour la démo
#         lat1, lon1 = loc1
#         lat2, lon2 = loc2
#         return np.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2) * 111  # Approximation en km
        
    
#     def _extract_temporal_features(self, transaction: Dict[str, Any]) -> Dict[str, float]:
#         """Extrait les features temporelles"""
#         features = {}
        
#         # Timestamp
#         timestamp = transaction.get('timestamp')
#         if timestamp:
#             if isinstance(timestamp, str):
#                 timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
#             # Heure de la journée
#             features['hour'] = timestamp.hour
#             features['is_night'] = 1 if (timestamp.hour >= 22 or timestamp.hour <= 6) else 0
#             features['is_business_hours'] = 1 if (9 <= timestamp.hour <= 17) else 0
            
#             # Jour de la semaine
#             features['day_of_week'] = timestamp.weekday()
#             features['is_weekend'] = 1 if timestamp.weekday() >= 5 else 0
            
#             # Jour du mois
#             features['day_of_month'] = timestamp.day
#             features['is_month_start'] = 1 if timestamp.day <= 5 else 0
#             features['is_month_end'] = 1 if timestamp.day >= 25 else 0
#         else:
#             # Valeurs par défaut
#             features['hour'] = 12
#             features['is_night'] = 0
#             features['is_business_hours'] = 1
#             features['day_of_week'] = 3
#             features['is_weekend'] = 0
#             features['day_of_month'] = 15
#             features['is_month_start'] = 0
#             features['is_month_end'] = 0
        
#         return features
    
#     def _extract_behavioral_features(self, transaction: Dict[str, Any], historical_data: pd.DataFrame) -> Dict[str, float]:
#         """Extrait les features comportementales basées sur l'historique"""
#         features = {}
        
#         current_amount = transaction.get('amount', 0)
        
#         if len(historical_data) > 0:
#             # Statistiques sur les montants
#             amounts = historical_data['amount']
#             features['avg_amount'] = amounts.mean()
#             features['std_amount'] = amounts.std() if len(amounts) > 1 else 0
#             features['min_amount'] = amounts.min()
#             features['max_amount'] = amounts.max()
            
#             # Z-score du montant actuel
#             if features['std_amount'] > 0:
#                 features['amount_zscore'] = abs((current_amount - features['avg_amount']) / features['std_amount'])
#             else:
#                 features['amount_zscore'] = 0
            
#             # Ratio par rapport à la moyenne
#             if features['avg_amount'] > 0:
#                 features['amount_ratio_avg'] = current_amount / features['avg_amount']
#             else:
#                 features['amount_ratio_avg'] = 1.0
            
#             # Vélocité (nombre de transactions récentes)
#             now = datetime.utcnow()
#             # historical_data['timestamp'] = pd.to_datetime(historical_data['timestamp'])

#             historical_data = historical_data.copy()
#             historical_data.loc[:, 'timestamp'] = pd.to_datetime(historical_data['timestamp'])
#             # Transactions dans les dernières 24h
#             last_24h = historical_data[historical_data['timestamp'] >= now - timedelta(hours=24)]
#             features['tx_count_24h'] = len(last_24h)
#             features['tx_amount_24h'] = last_24h['amount'].sum() if len(last_24h) > 0 else 0
            
#             # Transactions dans les 7 derniers jours
#             last_7d = historical_data[historical_data['timestamp'] >= now - timedelta(days=7)]
#             features['tx_count_7d'] = len(last_7d)
#             features['tx_amount_7d'] = last_7d['amount'].sum() if len(last_7d) > 0 else 0
            
#             # Fréquence moyenne
#             if len(historical_data) > 1:
#                 time_diffs = historical_data['timestamp'].diff().dt.total_seconds()
#                 features['avg_time_between_tx'] = time_diffs.mean() / 3600  # en heures
#             else:
#                 features['avg_time_between_tx'] = 24.0
            
#             # Nouveauté du client
#             features['customer_age_days'] = (now - historical_data['timestamp'].min()).days
#             features['total_transactions'] = len(historical_data)
            
#         else:
#             features.update(self._get_default_behavioral_features())
        
#         return features
    
#     def _get_default_behavioral_features(self) -> Dict[str, float]:
#         """Features par défaut pour les nouveaux clients"""
#         return {
#             'avg_amount': 50000.0,
#             'std_amount': 20000.0,
#             'min_amount': 0.0,
#             'max_amount': 50000.0,
#             'amount_zscore': 0.0,
#             'amount_ratio_avg': 1.0,
#             'tx_count_24h': 0,
#             'tx_amount_24h': 0.0,
#             'tx_count_7d': 0,
#             'tx_amount_7d': 0.0,
#             'avg_time_between_tx': 24.0,
#             'customer_age_days': 0,
#             'total_transactions': 0,
#         }
    
#     def _extract_derived_features(self, transaction: Dict[str, Any], features: Dict[str, float]) -> Dict[str, float]:
#         """Crée des features dérivées basées sur les features existantes"""
#         derived = {}
        
#         # Indicateur de risque basé sur vélocité
#         if features['tx_count_24h'] > 5:
#             derived['high_velocity'] = 1
#         else:
#             derived['high_velocity'] = 0
        
#         # Indicateur montant anormal
#         if features['amount_zscore'] > 3:
#             derived['unusual_amount'] = 1
#         else:
#             derived['unusual_amount'] = 0
        
#         # Indicateur nouveau client
#         if features['customer_age_days'] < 7:
#             derived['is_new_customer'] = 1
#         else:
#             derived['is_new_customer'] = 0
        
#         # Score de risque combiné (simple)
#         risk_score = 0
#         risk_score += features['is_night'] * 0.2
#         risk_score += derived['high_velocity'] * 0.3
#         risk_score += derived['unusual_amount'] * 0.4
#         risk_score += derived['is_new_customer'] * 0.1
#         derived['risk_score'] = min(risk_score, 1.0)
        
#         return derived
    
#     def get_feature_names(self) -> list:
#         """Retourne la liste des noms de features"""
#         return self.feature_names
    
#     def extract_features_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
#         """
#         Extrait les features pour un DataFrame entier
        
#         Args:
#             df: DataFrame avec les transactions
            
#         Returns:
#             DataFrame avec les features extraites
#         """
#         features_list = []
        
#         for idx, row in df.iterrows():
#             transaction = row.to_dict()
            
#             # Récupérer l'historique du client (transactions précédentes)
#             customer_id = transaction.get('customer_id')
#             historical = df[(df['customer_id'] == customer_id) & (df.index < idx)]
            
#             # Extraire features
#             features = self.extract_features(transaction, historical)
#             features_list.append(features)
        
#         features_df = pd.DataFrame(features_list)
#         logger.info(f"✅ Features extraites: {features_df.shape[1]} features pour {len(df)} transactions")
        
#         return features_df




"""
Feature Engineering pour la détection de fraude
Extraction et création de features pertinentes
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from src.core.logging import get_logger

logger = get_logger(__name__)


class FraudFeatureExtractor:
    """Extracteur de features pour la détection de fraude"""
    
    def __init__(self):
        self.feature_names = []
    
    def extract_features(self, transaction: Dict[str, Any], historical_data: Optional[pd.DataFrame] = None) -> Dict[str, float]:
        """
        Extrait toutes les features d'une transaction
        
        Args:
            transaction: Dictionnaire contenant les données de la transaction
            historical_data: DataFrame avec l'historique des transactions du client
            
        Returns:
            Dict[str, float]: Dictionnaire des features extraites
        """
        features = {}
        
        # === FEATURES BASIQUES ===
        features.update(self._extract_basic_features(transaction))
        
        # === FEATURES TEMPORELLES ===
        features.update(self._extract_temporal_features(transaction))
        
        # === FEATURES COMPORTEMENTALES (si historique disponible) ===
        if historical_data is not None and len(historical_data) > 0:
            features.update(self._extract_behavioral_features(transaction, historical_data))
        else:
            # Features par défaut si pas d'historique
            features.update(self._get_default_behavioral_features())
        
        # === FEATURES DÉRIVÉES ===
        features.update(self._extract_derived_features(transaction, features))
        
        self.feature_names = list(features.keys())
        return features
    
    def _extract_basic_features(self, transaction: Dict[str, Any]) -> Dict[str, float]:
        """Extrait les features de base de la transaction"""
        features = {}
        
        # Montant
        features['amount'] = float(transaction.get('amount', 0))
        features['amount_log'] = float(np.log1p(features['amount']))  # Log pour réduire skewness
        
        # Montant binné (catégories de montant)
        if features['amount'] < 10000:
            features['amount_category'] = 0  # Petit
        elif features['amount'] < 50000:
            features['amount_category'] = 1  # Moyen
        elif features['amount'] < 200000:
            features['amount_category'] = 2  # Grand
        else:
            features['amount_category'] = 3  # Très grand
        
        # Type de transaction (encodé)
        tx_type = str(transaction.get('transaction_type', 'payment')).lower()
        features['is_transfer'] = 1 if tx_type == 'transfer' else 0
        features['is_withdrawal'] = 1 if tx_type == 'withdrawal' else 0
        features['is_payment'] = 1 if tx_type == 'payment' else 0
        
        # Méthode de paiement
        payment_method = str(transaction.get('payment_method', 'mobile')).lower()
        features['is_card'] = 1 if payment_method == 'card' else 0
        features['is_mobile'] = 1 if payment_method == 'mobile' else 0
        features['is_bank_transfer'] = 1 if payment_method == 'bank_transfer' else 0
        
        # Présence de merchant
        features['has_merchant'] = 1 if transaction.get('merchant_id') else 0
        
        return features
    
    def _extract_advanced_features(self, transaction: Dict, historical_data: pd.DataFrame) -> Dict:
        """Features avancées pour améliorer la détection"""
        features = {}
        
        # 1. Distance depuis lieu habituel (si géoloc disponible)
        if 'latitude' in transaction and 'longitude' in transaction:
            usual_location = historical_data[['latitude', 'longitude']].mean()
            current_location = [transaction['latitude'], transaction['longitude']]
            features['distance_from_usual_km'] = float(self._calculate_distance(usual_location, current_location))
        
        # 2. Similarité device (même device que transactions précédentes)
        current_device = transaction.get('device_id')
        if current_device and len(historical_data) > 0:
            usual_devices = historical_data['device_id'].unique()
            features['is_new_device'] = 0 if current_device in usual_devices else 1
        
        # 3. Pattern horaire inhabituel pour ce client
        if len(historical_data) > 0:
            usual_hours = historical_data['hour'].mode()
            current_hour = features.get('hour', 12)
            features['unusual_hour'] = 0 if current_hour in usual_hours.values else 1
        
        return features

    def _calculate_distance(self, loc1: list, loc2: list) -> float:
        """Calcule la distance entre deux points géographiques (simplifié)"""
        # Formule haversine simplifiée pour la démo
        lat1, lon1 = loc1
        lat2, lon2 = loc2
        return float(np.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2) * 111)  # Approximation en km
    
    def _extract_temporal_features(self, transaction: Dict[str, Any]) -> Dict[str, float]:
        """Extrait les features temporelles"""
        features = {}
        
        # Timestamp
        timestamp = transaction.get('timestamp')
        if timestamp:
            # 🔧 CORRECTION : Gérer tous les types de timestamp
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            elif isinstance(timestamp, (int, float)):
                # Si c'est un timestamp Unix
                timestamp = datetime.fromtimestamp(timestamp)
            elif not isinstance(timestamp, datetime):
                # Fallback : utiliser l'heure actuelle
                timestamp = datetime.now()
            
            # 🔧 CORRECTION : Convertir explicitement en int/float
            features['hour'] = int(timestamp.hour)
            features['is_night'] = int(1 if (timestamp.hour >= 22 or timestamp.hour <= 6) else 0)
            features['is_business_hours'] = int(1 if (9 <= timestamp.hour <= 17) else 0)
            
            # Jour de la semaine
            features['day_of_week'] = int(timestamp.weekday())
            features['is_weekend'] = int(1 if timestamp.weekday() >= 5 else 0)
            
            # Jour du mois
            features['day_of_month'] = int(timestamp.day)
            features['is_month_start'] = int(1 if timestamp.day <= 5 else 0)
            features['is_month_end'] = int(1 if timestamp.day >= 25 else 0)
        else:
            # Valeurs par défaut
            features['hour'] = 12
            features['is_night'] = 0
            features['is_business_hours'] = 1
            features['day_of_week'] = 3
            features['is_weekend'] = 0
            features['day_of_month'] = 15
            features['is_month_start'] = 0
            features['is_month_end'] = 0
        
        return features
    
    def _extract_behavioral_features(self, transaction: Dict[str, Any], historical_data: pd.DataFrame) -> Dict[str, float]:
        """Extrait les features comportementales basées sur l'historique"""
        features = {}
        
        current_amount = float(transaction.get('amount', 0))
        
        if len(historical_data) > 0:
            # 🔧 CORRECTION : Copier le DataFrame pour éviter les warnings
            hist_df = historical_data.copy()
            
            # Statistiques sur les montants
            amounts = hist_df['amount'].astype(float)
            features['avg_amount'] = float(amounts.mean())
            features['std_amount'] = float(amounts.std() if len(amounts) > 1 else 0)
            features['min_amount'] = float(amounts.min())
            features['max_amount'] = float(amounts.max())
            
            # Z-score du montant actuel
            if features['std_amount'] > 0:
                features['amount_zscore'] = float(abs((current_amount - features['avg_amount']) / features['std_amount']))
            else:
                features['amount_zscore'] = 0.0
            
            # Ratio par rapport à la moyenne
            if features['avg_amount'] > 0:
                features['amount_ratio_avg'] = float(current_amount / features['avg_amount'])
            else:
                features['amount_ratio_avg'] = 1.0
            
            # 🔧 CORRECTION : Gérer la conversion du timestamp de manière sûre
            try:
                # Convertir la colonne timestamp en datetime
                hist_df['timestamp'] = pd.to_datetime(hist_df['timestamp'], errors='coerce')
                
                # Vélocité (nombre de transactions récentes)
                now = datetime.utcnow()
                
                # Transactions dans les dernières 24h
                last_24h = hist_df[hist_df['timestamp'] >= now - timedelta(hours=24)]
                features['tx_count_24h'] = int(len(last_24h))
                features['tx_amount_24h'] = float(last_24h['amount'].sum() if len(last_24h) > 0 else 0)
                
                # Transactions dans les 7 derniers jours
                last_7d = hist_df[hist_df['timestamp'] >= now - timedelta(days=7)]
                features['tx_count_7d'] = int(len(last_7d))
                features['tx_amount_7d'] = float(last_7d['amount'].sum() if len(last_7d) > 0 else 0)
                
                # Fréquence moyenne
                if len(hist_df) > 1:
                    time_diffs = hist_df['timestamp'].diff().dt.total_seconds()
                    features['avg_time_between_tx'] = float(time_diffs.mean() / 3600) if not time_diffs.isna().all() else 24.0
                else:
                    features['avg_time_between_tx'] = 24.0
                
                # Nouveauté du client
                min_timestamp = hist_df['timestamp'].min()
                if pd.notna(min_timestamp):
                    features['customer_age_days'] = int((now - min_timestamp).days)
                else:
                    features['customer_age_days'] = 0
                    
            except Exception as e:
                logger.warning(f"⚠️ Erreur lors du calcul des features temporelles: {e}")
                # Utiliser des valeurs par défaut
                features['tx_count_24h'] = 0
                features['tx_amount_24h'] = 0.0
                features['tx_count_7d'] = 0
                features['tx_amount_7d'] = 0.0
                features['avg_time_between_tx'] = 24.0
                features['customer_age_days'] = 0
            
            features['total_transactions'] = int(len(hist_df))
            
        else:
            features.update(self._get_default_behavioral_features())
        
        return features
    
    def _get_default_behavioral_features(self) -> Dict[str, float]:
        """Features par défaut pour les nouveaux clients"""
        return {
            'avg_amount': 50000.0,
            'std_amount': 20000.0,
            'min_amount': 0.0,
            'max_amount': 50000.0,
            'amount_zscore': 0.0,
            'amount_ratio_avg': 1.0,
            'tx_count_24h': 0,
            'tx_amount_24h': 0.0,
            'tx_count_7d': 0,
            'tx_amount_7d': 0.0,
            'avg_time_between_tx': 24.0,
            'customer_age_days': 0,
            'total_transactions': 0,
        }
    
    def _extract_derived_features(self, transaction: Dict[str, Any], features: Dict[str, float]) -> Dict[str, float]:
        """Crée des features dérivées basées sur les features existantes"""
        derived = {}
        
        # Indicateur de risque basé sur vélocité
        derived['high_velocity'] = int(1 if features.get('tx_count_24h', 0) > 5 else 0)
        
        # Indicateur montant anormal
        derived['unusual_amount'] = int(1 if features.get('amount_zscore', 0) > 3 else 0)
        
        # Indicateur nouveau client
        derived['is_new_customer'] = int(1 if features.get('customer_age_days', 0) < 7 else 0)
        
        # Score de risque combiné (simple)
        risk_score = 0.0
        risk_score += features.get('is_night', 0) * 0.2
        risk_score += derived['high_velocity'] * 0.3
        risk_score += derived['unusual_amount'] * 0.4
        risk_score += derived['is_new_customer'] * 0.1
        derived['risk_score'] = float(min(risk_score, 1.0))
        
        return derived
    
    def get_feature_names(self) -> list:
        """Retourne la liste des noms de features"""
        return self.feature_names
    
    def extract_features_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extrait les features pour un DataFrame entier
        
        Args:
            df: DataFrame avec les transactions
            
        Returns:
            DataFrame avec les features extraites
        """
        features_list = []
        
        for idx, row in df.iterrows():
            transaction = row.to_dict()
            
            # Récupérer l'historique du client (transactions précédentes)
            customer_id = transaction.get('customer_id')
            historical = df[(df['customer_id'] == customer_id) & (df.index < idx)]
            
            # Extraire features
            features = self.extract_features(transaction, historical)
            features_list.append(features)
        
        features_df = pd.DataFrame(features_list)
        logger.info(f"✅ Features extraites: {features_df.shape[1]} features pour {len(df)} transactions")
        
        return features_df