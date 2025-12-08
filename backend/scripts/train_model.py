"""
Script d'entraînement des modèles de détection de fraude
Supporte: Kaggle, SÉNTRA, ou les deux (hybride)
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
import argparse
from datetime import datetime
from src.ml.training.trainer import FraudModelTrainer
from src.ml.training.evaluator import FraudModelEvaluator
from src.core.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


def train_on_kaggle(output_dir: str = "./data/models/production"):
    """
    Entraîne un modèle sur le dataset Kaggle
    
    Args:
        output_dir: Dossier de sortie pour le modèle
        
    Returns:
        Tuple (trainer, metrics)
    """
    logger.info("="*70)
    logger.info("🔧 ENTRAÎNEMENT SUR DATASET KAGGLE")
    logger.info("="*70)
    
    # Charger les données
    logger.info("\n📥 Chargement des données Kaggle...")
    train_df = pd.read_csv("./data/processed/kaggle_train.csv")
    test_df = pd.read_csv("./data/processed/kaggle_test.csv")
    
    logger.info(f"   - Train: {len(train_df)} transactions")
    logger.info(f"   - Test: {len(test_df)} transactions")
    
    # Initialiser le trainer
    trainer = FraudModelTrainer(
        model_type='random_forest',
        use_smote=True,  # Important pour dataset très déséquilibré
        test_size=0.2
    )
    
    # Préparer les données (Kaggle = déjà preprocessées)
    X_train, y_train = trainer.prepare_data(train_df, is_kaggle=True)
    X_test, y_test = trainer.prepare_data(test_df, is_kaggle=True)
    
    # Entraînement
    logger.info("\n🚀 Entraînement du modèle...")
    history = trainer.train(X_train, y_train)
    
    # Évaluation
    logger.info("\n📊 Évaluation sur test set...")
    evaluator = FraudModelEvaluator()
    
    y_pred = trainer.model.predict(X_test)
    y_proba = trainer.model.get_fraud_probability(X_test)
    
    metrics = evaluator.evaluate(y_test, y_pred, y_proba)
    
    # Sauvegarder le modèle
    logger.info("\n💾 Sauvegarde du modèle...")
    model_path = trainer.save_model(output_dir)
    
    # Graphiques
    evaluator.plot_confusion_matrix(f"{output_dir}/kaggle_confusion_matrix.png")
    evaluator.plot_roc_curve(f"{output_dir}/kaggle_roc_curve.png")
    
    logger.info("\n" + evaluator.get_classification_report())
    
    return trainer, metrics


def train_on_sentra(output_dir: str = "./data/models/production"):
    """
    Entraîne un modèle sur le dataset SÉNTRA
    
    Args:
        output_dir: Dossier de sortie
        
    Returns:
        Tuple (trainer, metrics)
    """
    logger.info("="*70)
    logger.info("🔧 ENTRAÎNEMENT SUR DATASET SÉNTRA (BCEAO)")
    logger.info("="*70)
    
    # Charger les données
    logger.info("\n📥 Chargement des données SÉNTRA...")
    train_df = pd.read_csv("./data/processed/transactions_train.csv")
    test_df = pd.read_csv("./data/processed/transactions_test.csv")
    
    logger.info(f"   - Train: {len(train_df)} transactions")
    logger.info(f"   - Test: {len(test_df)} transactions")
    
    # Initialiser le trainer
    trainer = FraudModelTrainer(
        model_type='random_forest',
        use_smote=False,  # Dataset déjà plus équilibré
        test_size=0.2
    )
    
    # Préparer les données (SÉNTRA = extraction features nécessaire)
    X_train, y_train = trainer.prepare_data(train_df, is_kaggle=False)
    X_test, y_test = trainer.prepare_data(test_df, is_kaggle=False)
    
    # Entraînement
    logger.info("\n🚀 Entraînement du modèle...")
    history = trainer.train(X_train, y_train)
    
    # Évaluation
    logger.info("\n📊 Évaluation sur test set...")
    evaluator = FraudModelEvaluator()
    
    y_pred = trainer.model.predict(X_test)
    y_proba = trainer.model.get_fraud_probability(X_test)
    
    metrics = evaluator.evaluate(y_test, y_pred, y_proba)
    
    # Afficher features importantes
    logger.info("\n🔝 Top 10 Features Importantes:")
    feature_imp = trainer.model.get_feature_importances(10)
    for idx, row in feature_imp.iterrows():
        logger.info(f"   {idx+1}. {row['feature']}: {row['importance']:.4f}")
    
    # Sauvegarder
    logger.info("\n💾 Sauvegarde du modèle...")
    model_path = trainer.save_model(output_dir)
    
    # Graphiques
    evaluator.plot_confusion_matrix(f"{output_dir}/sentra_confusion_matrix.png")
    evaluator.plot_roc_curve(f"{output_dir}/sentra_roc_curve.png")
    
    logger.info("\n" + evaluator.get_classification_report())
    
    return trainer, metrics


def train_hybrid(output_dir: str = "./data/models/production"):
    """
    Entraîne sur les deux datasets et compare
    
    Args:
        output_dir: Dossier de sortie
        
    Returns:
        Dict avec résultats des deux modèles
    """
    logger.info("="*70)
    logger.info("🚀 ENTRAÎNEMENT HYBRIDE (KAGGLE + SÉNTRA)")
    logger.info("="*70)
    
    # Entraîner sur Kaggle
    logger.info("\n" + "="*70)
    logger.info("PARTIE 1/3 : ENTRAÎNEMENT KAGGLE")
    logger.info("="*70)
    trainer_kaggle, metrics_kaggle = train_on_kaggle(output_dir)
    
    # Entraîner sur SÉNTRA
    logger.info("\n" + "="*70)
    logger.info("PARTIE 2/3 : ENTRAÎNEMENT SÉNTRA")
    logger.info("="*70)
    trainer_sentra, metrics_sentra = train_on_sentra(output_dir)
    
    # Validation croisée : tester modèle Kaggle sur données SÉNTRA
    logger.info("\n" + "="*70)
    logger.info("PARTIE 3/3 : VALIDATION CROISÉE")
    logger.info("="*70)
    
    logger.info("\n🔄 Test du modèle Kaggle sur données SÉNTRA...")
    test_sentra = pd.read_csv("./data/processed/transactions_test.csv")
    
    # Préparer données SÉNTRA
    X_sentra_test, y_sentra_test = trainer_sentra.prepare_data(test_sentra, is_kaggle=False)
    
    # Attention: modèle Kaggle attend features Kaggle
    # On ne peut pas le tester directement sur features SÉNTRA (différentes)
    logger.info("⚠️  Les features sont différentes - validation croisée directe impossible")
    logger.info("💡 Utiliser transfer learning ou réentraînement serait nécessaire")
    
    # Comparaison finale
    logger.info("\n" + "="*70)
    logger.info("📊 COMPARAISON FINALE")
    logger.info("="*70)
    
    evaluator = FraudModelEvaluator()
    comparison = {
        'Kaggle': metrics_kaggle,
        'SÉNTRA': metrics_sentra
    }
    
    df_comparison = evaluator.compare_models(comparison)
    
    # Sauvegarder la comparaison
    df_comparison.to_csv(f"{output_dir}/model_comparison.csv")
    logger.info(f"\n✅ Comparaison sauvegardée: {output_dir}/model_comparison.csv")
    
    return {
        'kaggle': {'trainer': trainer_kaggle, 'metrics': metrics_kaggle},
        'sentra': {'trainer': trainer_sentra, 'metrics': metrics_sentra},
        'comparison': df_comparison
    }


def main():
    """Fonction principale"""
    
    parser = argparse.ArgumentParser(description='Entraîner un modèle de détection de fraude')
    parser.add_argument(
        '--dataset',
        type=str,
        choices=['kaggle', 'sentra', 'both'],
        default='sentra',
        help='Dataset à utiliser (kaggle, sentra, ou both)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='./data/models/production',
        help='Dossier de sortie pour les modèles'
    )
    
    args = parser.parse_args()
    
    logger.info("="*70)
    logger.info("🚀 SÉNTRA - ENTRAÎNEMENT MODÈLES ML")
    logger.info(f"   Dataset: {args.dataset}")
    logger.info(f"   Output: {args.output}")
    logger.info("="*70)
    
    # Créer dossier output
    Path(args.output).mkdir(parents=True, exist_ok=True)
    
    # Entraîner selon le choix
    start_time = datetime.now()
    
    if args.dataset == 'kaggle':
        trainer, metrics = train_on_kaggle(args.output)
    elif args.dataset == 'sentra':
        trainer, metrics = train_on_sentra(args.output)
    elif args.dataset == 'both':
        results = train_hybrid(args.output)
    
    total_time = (datetime.now() - start_time).total_seconds()
    
    logger.info("\n" + "="*70)
    logger.info("✅ ENTRAÎNEMENT TERMINÉ")
    logger.info("="*70)
    logger.info(f"   Temps total: {total_time:.2f}s")
    logger.info(f"   Modèles sauvegardés dans: {args.output}")
    logger.info("")
    logger.info("📝 Prochaines étapes:")
    logger.info("   1. Tester l'API: uvicorn src.api.main:app --reload")
    logger.info("   2. Faire une prédiction test")
    logger.info("   3. Déployer le modèle en production")


if __name__ == "__main__":
    main()