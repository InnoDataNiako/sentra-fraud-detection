"""
Évaluation des modèles de détection de fraude
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
    precision_recall_curve,
    roc_curve
)
import matplotlib.pyplot as plt
import seaborn as sns
from src.core.logging import get_logger

logger = get_logger(__name__)


class FraudModelEvaluator:
    """Évaluateur de performance pour modèles de détection de fraude"""
    
    def __init__(self):
        self.metrics = {}
        self.y_true = None
        self.y_pred = None
        self.y_proba = None
    
    def evaluate(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_proba: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        Évalue les performances du modèle
        
        Args:
            y_true: Labels réels
            y_pred: Prédictions binaires (0 ou 1)
            y_proba: Probabilités de fraude (optionnel)
            
        Returns:
            Dictionnaire avec toutes les métriques
        """
        logger.info("📊 Évaluation des performances...")
        
        self.y_true = y_true
        self.y_pred = y_pred
        self.y_proba = y_proba
        
        # Métriques de base
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, zero_division=0),
            'recall': recall_score(y_true, y_pred, zero_division=0),
            'f1_score': f1_score(y_true, y_pred, zero_division=0)
        }
        
        # AUC-ROC si probabilités disponibles
        if y_proba is not None:
            metrics['auc_roc'] = roc_auc_score(y_true, y_proba)
        
        # Matrice de confusion
        cm = confusion_matrix(y_true, y_pred)
        tn, fp, fn, tp = cm.ravel()
        
        metrics.update({
            'true_negatives': int(tn),
            'false_positives': int(fp),
            'false_negatives': int(fn),
            'true_positives': int(tp),
            'total_samples': len(y_true),
            'total_frauds': int(y_true.sum()),
            'total_legitimate': int((y_true == 0).sum())
        })
        
        # Métriques métier importantes
        metrics['false_positive_rate'] = fp / (fp + tn) if (fp + tn) > 0 else 0
        metrics['false_negative_rate'] = fn / (fn + tp) if (fn + tp) > 0 else 0
        metrics['detection_rate'] = tp / (tp + fn) if (tp + fn) > 0 else 0
        
        # Coût business (exemple avec coûts fictifs)
        cost_fp = 10  # Coût d'une fausse alerte (investigation)
        cost_fn = 100  # Coût d'une fraude non détectée
        metrics['estimated_cost'] = (fp * cost_fp) + (fn * cost_fn)
        
        self.metrics = metrics
        
        # Afficher résumé
        self._print_summary()
        
        return metrics
    
    def _print_summary(self):
        """Affiche un résumé des performances"""
        logger.info("="*70)
        logger.info("📈 RÉSULTATS D'ÉVALUATION")
        logger.info("="*70)
        
        m = self.metrics
        
        logger.info(f"\n🎯 Métriques Principales:")
        logger.info(f"   - Accuracy:  {m['accuracy']:.4f}")
        logger.info(f"   - Precision: {m['precision']:.4f}")
        logger.info(f"   - Recall:    {m['recall']:.4f}")
        logger.info(f"   - F1-Score:  {m['f1_score']:.4f}")
        if 'auc_roc' in m:
            logger.info(f"   - AUC-ROC:   {m['auc_roc']:.4f}")
        
        logger.info(f"\n📊 Matrice de Confusion:")
        logger.info(f"   - True Positives (TP):  {m['true_positives']}")
        logger.info(f"   - True Negatives (TN):  {m['true_negatives']}")
        logger.info(f"   - False Positives (FP): {m['false_positives']}")
        logger.info(f"   - False Negatives (FN): {m['false_negatives']}")
        
        logger.info(f"\n💼 Métriques Métier:")
        logger.info(f"   - Taux Faux Positifs: {m['false_positive_rate']:.4f} ({m['false_positive_rate']*100:.2f}%)")
        logger.info(f"   - Taux Faux Négatifs: {m['false_negative_rate']:.4f} ({m['false_negative_rate']*100:.2f}%)")
        logger.info(f"   - Taux Détection:     {m['detection_rate']:.4f} ({m['detection_rate']*100:.2f}%)")
        logger.info(f"   - Coût Estimé:        {m['estimated_cost']:.0f} unités")
        
        logger.info("="*70)
    
    def get_classification_report(self) -> str:
        """
        Génère un rapport de classification détaillé
        
        Returns:
            Rapport texte
        """
        if self.y_true is None or self.y_pred is None:
            raise ValueError("Appeler evaluate() d'abord")
        
        target_names = ['Légitime', 'Fraude']
        report = classification_report(
            self.y_true,
            self.y_pred,
            target_names=target_names,
            digits=4
        )
        
        return report
    
    def plot_confusion_matrix(self, save_path: Optional[str] = None):
        """
        Affiche la matrice de confusion
        
        Args:
            save_path: Chemin pour sauvegarder l'image (optionnel)
        """
        if self.y_true is None or self.y_pred is None:
            raise ValueError("Appeler evaluate() d'abord")
        
        cm = confusion_matrix(self.y_true, self.y_pred)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(
            cm,
            annot=True,
            fmt='d',
            cmap='Blues',
            xticklabels=['Légitime', 'Fraude'],
            yticklabels=['Légitime', 'Fraude']
        )
        plt.title('Matrice de Confusion')
        plt.ylabel('Valeur Réelle')
        plt.xlabel('Prédiction')
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
            logger.info(f"✅ Matrice de confusion sauvegardée: {save_path}")
        
        plt.close()
    
    def plot_roc_curve(self, save_path: Optional[str] = None):
        """
        Affiche la courbe ROC
        
        Args:
            save_path: Chemin pour sauvegarder l'image (optionnel)
        """
        if self.y_proba is None:
            logger.warning("⚠️ Probabilités non disponibles, impossible de tracer ROC")
            return
        
        fpr, tpr, thresholds = roc_curve(self.y_true, self.y_proba)
        auc = roc_auc_score(self.y_true, self.y_proba)
        
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, label=f'ROC Curve (AUC = {auc:.4f})', linewidth=2)
        plt.plot([0, 1], [0, 1], 'k--', label='Random')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Courbe ROC - Détection de Fraude')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
            logger.info(f"✅ Courbe ROC sauvegardée: {save_path}")
        
        plt.close()
    
    def plot_precision_recall_curve(self, save_path: Optional[str] = None):
        """
        Affiche la courbe Precision-Recall
        
        Args:
            save_path: Chemin pour sauvegarder l'image (optionnel)
        """
        if self.y_proba is None:
            logger.warning("⚠️ Probabilités non disponibles")
            return
        
        precision, recall, thresholds = precision_recall_curve(self.y_true, self.y_proba)
        
        plt.figure(figsize=(8, 6))
        plt.plot(recall, precision, linewidth=2)
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title('Courbe Precision-Recall')
        plt.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
            logger.info(f"✅ Courbe P-R sauvegardée: {save_path}")
        
        plt.close()
    
    def find_optimal_threshold(self, metric: str = 'f1') -> float:
        """
        Trouve le seuil optimal pour maximiser une métrique
        
        Args:
            metric: Métrique à optimiser ('f1', 'precision', 'recall')
            
        Returns:
            Seuil optimal
        """
        if self.y_proba is None:
            raise ValueError("Probabilités nécessaires")
        
        thresholds = np.arange(0.0, 1.0, 0.01)
        best_threshold = 0.5
        best_score = 0.0
        
        for threshold in thresholds:
            y_pred_temp = (self.y_proba >= threshold).astype(int)
            
            if metric == 'f1':
                score = f1_score(self.y_true, y_pred_temp, zero_division=0)
            elif metric == 'precision':
                score = precision_score(self.y_true, y_pred_temp, zero_division=0)
            elif metric == 'recall':
                score = recall_score(self.y_true, y_pred_temp, zero_division=0)
            else:
                raise ValueError(f"Métrique inconnue: {metric}")
            
            if score > best_score:
                best_score = score
                best_threshold = threshold
        
        logger.info(f"✅ Seuil optimal ({metric}): {best_threshold:.2f} (score: {best_score:.4f})")
        
        return best_threshold
    
    def compare_models(self, results: Dict[str, Dict[str, Any]]):
        """
        Compare plusieurs modèles
        
        Args:
            results: Dict {nom_modèle: métriques}
        """
        logger.info("="*70)
        logger.info("🔍 COMPARAISON DES MODÈLES")
        logger.info("="*70)
        
        df = pd.DataFrame(results).T
        
        # Afficher tableau comparatif
        logger.info(f"\n{df.to_string()}")
        
        # Identifier le meilleur
        best_model = df['f1_score'].idxmax()
        logger.info(f"\n🏆 Meilleur modèle (F1): {best_model}")
        
        return df