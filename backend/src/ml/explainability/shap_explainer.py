"""
Explainability avec SHAP pour comprendre les décisions du modèle
"""

import shap
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any, List, Optional
import joblib
from pathlib import Path
from src.core.logging import get_logger

logger = get_logger(__name__)


class SHAPExplainer:
    """
    Explainability avec SHAP pour comprendre les prédictions de fraude
    """
    
    def __init__(self, model, feature_names: List[str], model_type: str = 'random_forest'):
        """
        Args:
            model: Modèle ML entraîné
            feature_names: Noms des features
            model_type: Type de modèle ('random_forest', 'ensemble')
        """
        self.model = model
        self.feature_names = feature_names
        self.model_type = model_type
        self.explainer = None
        self._init_explainer()
        
        logger.info(f"✅ SHAP Explainer initialisé pour {model_type}")
    
    def _init_explainer(self):
        """Initialise l'explainer SHAP approprié"""
        try:
            if hasattr(self.model, 'predict_proba'):
                # Tree-based models
                self.explainer = shap.TreeExplainer(self.model)
            else:
                # Fallback: KernelExplainer (plus lent mais universel)
                self.explainer = shap.KernelExplainer(
                    self.model.predict_proba, 
                    shap.sample(np.zeros((1, len(self.feature_names))), 100)
                )
        except Exception as e:
            logger.warning(f"SHAP TreeExplainer échoué, utilisation Kernel: {e}")
            self.explainer = shap.KernelExplainer(
                self.model.predict_proba, 
                shap.sample(np.zeros((1, len(self.feature_names))), 100)
            )
    
    def explain_prediction(self, features: pd.DataFrame, transaction_id: str = 'unknown') -> Dict[str, Any]:
        """
        Explique une prédiction individuelle
        
        Args:
            features: DataFrame avec une seule ligne (la transaction)
            transaction_id: ID de la transaction pour le logging
            
        Returns:
            Dictionnaire avec explication détaillée
        """
        if self.explainer is None:
            raise ValueError("Explainer SHAP non initialisé")
        
        logger.info(f"🔍 Explication SHAP pour {transaction_id}")
        
        # Calculer les valeurs SHAP
        shap_values = self.explainer.shap_values(features)
        
        # Pour Random Forest, shap_values est une liste [class_0, class_1]
        if isinstance(shap_values, list) and len(shap_values) == 2:
            shap_values = shap_values[1]  # Prendre la classe "fraude"
        
        # Valeur de base et prédiction
        base_value = self.explainer.expected_value
        if isinstance(base_value, np.ndarray) and len(base_value) == 2:
            base_value = base_value[1]  # Classe "fraude"
        
        prediction = self.model.predict_proba(features)[0, 1]
        
        # Features les plus influentes (top 10)
        feature_impacts = []
        for i in range(len(self.feature_names)):
            impact = float(shap_values[0, i]) if len(shap_values.shape) > 1 else float(shap_values[i])
            feature_impacts.append({
                'feature': self.feature_names[i],
                'impact': impact,
                'value': float(features.iloc[0, i]) if i < features.shape[1] else 0.0
            })
        
        # Trier par impact absolu
        feature_impacts.sort(key=lambda x: abs(x['impact']), reverse=True)
        top_features = feature_impacts[:10]
        
        # Construire l'explication
        explanation = {
            'transaction_id': transaction_id,
            'prediction_probability': float(prediction),
            'base_value': float(base_value),
            'top_positive_features': [
                {**feat, 'direction': 'positive'} 
                for feat in top_features if feat['impact'] > 0
            ][:5],
            'top_negative_features': [
                {**feat, 'direction': 'negative'} 
                for feat in top_features if feat['impact'] < 0
            ][:5],
            'fraud_indicators': self._generate_fraud_indicators(top_features),
            'explanation_summary': self._generate_summary(top_features, prediction)
        }
        
        return explanation
    
    def _generate_fraud_indicators(self, top_features: List[Dict]) -> List[str]:
        """Génère des indicateurs de fraude en langage naturel"""
        indicators = []
        
        for feat in top_features:
            feature_name = feat['feature']
            impact = feat['impact']
            value = feat['value']
            
            if impact > 0:  # Contribue à la fraude
                if 'amount' in feature_name:
                    if value > 100000:  # Montant élevé
                        indicators.append(f"Montant élevé ({value:,.0f} XOF)")
                    elif 'zscore' in feature_name and value > 2:
                        indicators.append(f"Montant anormal (z-score: {value:.1f})")
                
                elif 'velocity' in feature_name or 'count' in feature_name:
                    if value > 5:
                        indicators.append(f"Haute vélocité transactions ({value} opérations)")
                
                elif 'night' in feature_name and value == 1:
                    indicators.append("Transaction de nuit")
                
                elif 'location_risk' in feature_name and value > 0.7:
                    indicators.append(f"Localisation à risque (score: {value:.2f})")
        
        return indicators[:5]  # Limiter à 5 indicateurs
    
    def _generate_summary(self, top_features: List[Dict], probability: float) -> str:
        """Génère un résumé en langage naturel"""
        if probability < 0.3:
            return "Transaction légitime - Aucun indicateur de fraude significatif"
        
        positive_impacts = [f for f in top_features if f['impact'] > 0]
        
        if not positive_impacts:
            return "Transaction légitime - Facteurs neutres ou favorables"
        
        # Prendre le top 3 des features positives
        top_3 = positive_impacts[:3]
        reasons = []
        
        for feat in top_3:
            name = feat['feature']
            if 'amount' in name:
                reasons.append("montant anormal")
            elif 'velocity' in name:
                reasons.append("fréquence transactions suspecte")
            elif 'location' in name:
                reasons.append("localisation à risque")
            elif 'night' in name:
                reasons.append("horaire inhabituel")
            elif 'device' in name:
                reasons.append("nouvel appareil")
            else:
                reasons.append(f"comportement inhabituel ({name})")
        
        if probability > 0.7:
            severity = "élevé"
            action = "nécessite une investigation immédiate"
        elif probability > 0.5:
            severity = "modéré" 
            action = "recommandé de mettre en revue"
        else:
            severity = "faible"
            action = "surveillance recommandée"
        
        return f"Risque de fraude {severity} détecté. Principales raisons: {', '.join(reasons)}. {action}."
    
    def plot_waterfall(self, features: pd.DataFrame, transaction_id: str, save_path: Optional[str] = None):
        """
        Génère un graphique waterfall SHAP
        
        Args:
            features: Features de la transaction
            transaction_id: ID pour le titre
            save_path: Chemin de sauvegarde (optionnel)
        """
        if self.explainer is None:
            raise ValueError("Explainer non initialisé")
        
        shap_values = self.explainer.shap_values(features)
        if isinstance(shap_values, list):
            shap_values = shap_values[1]  # Classe fraude
        
        plt.figure(figsize=(10, 8))
        shap.waterfall_plot(
            shap.Explanation(
                values=shap_values[0] if len(shap_values.shape) > 1 else shap_values,
                base_values=self.explainer.expected_value[1] if isinstance(self.explainer.expected_value, np.ndarray) else self.explainer.expected_value,
                data=features.iloc[0],
                feature_names=self.feature_names
            ),
            show=False
        )
        plt.title(f"Explication SHAP - Transaction {transaction_id}", fontsize=14)
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300, facecolor='white')
            logger.info(f"✅ Waterfall plot sauvegardé: {save_path}")
        
        plt.close()
    
    def plot_feature_importance(self, save_path: Optional[str] = None):
        """
        Graphique d'importance globale des features
        """
        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
        else:
            # Estimation avec SHAP
            logger.warning("Utilisation SHAP pour importance features")
            return
        
        # Créer DataFrame
        imp_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importances
        }).sort_values('importance', ascending=True)
        
        # Graphique
        plt.figure(figsize=(10, 8))
        plt.barh(imp_df['feature'][-15:], imp_df['importance'][-15:])
        plt.xlabel('Importance')
        plt.title('Importance des Features - Modèle Random Forest')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
            logger.info(f"✅ Feature importance sauvegardé: {save_path}")
        
        plt.close()
    
    def save_explanation_report(self, explanation: Dict[str, Any], output_path: str):
        """
        Sauvegarde un rapport d'explication complet
        
        Args:
            explanation: Résultat de explain_prediction()
            output_path: Chemin de sortie
        """
        import json
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(explanation, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Rapport d'explication sauvegardé: {output_path}")


class FraudExplanationAPI:
    """
    API simplifiée pour l'explication des prédictions
    """
    
    def __init__(self, predictor, feature_names: List[str]):
        self.predictor = predictor
        self.explainer = SHAPExplainer(predictor.model, feature_names)
    
    def explain_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Explique une transaction complète (prédiction + explication)
        """
        # Faire la prédiction
        prediction_result = self.predictor.predict_single(transaction)
        
        # Préparer les features
        if self.predictor.model_type == 'sentra':
            features = self.predictor._prepare_sentra_features(transaction)
        else:
            features = self.predictor._prepare_kaggle_features(transaction)
        
        # Générer l'explication
        explanation = self.explainer.explain_prediction(
            features, 
            transaction.get('transaction_id', 'unknown')
        )
        
        # Combiner les résultats
        return {
            **prediction_result,
            'explanation': explanation
        }