"""
Script pour télécharger et préparer le dataset Kaggle Credit Card Fraud
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from src.core.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


def download_kaggle_dataset():
    """
    Télécharge le dataset Kaggle via l'API
    Nécessite : pip install kaggle
    Configuration : ~/.kaggle/kaggle.json avec tes credentials
    """
    try:
        import kaggle
        
        logger.info("📥 Téléchargement du dataset Kaggle...")
        
        # Télécharger le dataset
        kaggle.api.dataset_download_files(
            'mlg-ulb/creditcardfraud',
            path='./data/raw/',
            unzip=True
        )
        
        logger.info("✅ Dataset téléchargé dans data/raw/")
        return True
        
    except ImportError:
        logger.warning("⚠️ Module 'kaggle' non installé")
        logger.info("Installation: pip install kaggle")
        logger.info("Puis configurer: ~/.kaggle/kaggle.json")
        return False
    except Exception as e:
        logger.error(f"❌ Erreur téléchargement: {e}")
        logger.info("💡 Alternative: Télécharger manuellement depuis https://www.kaggle.com/mlg-ulb/creditcardfraud")
        return False


def prepare_kaggle_data():
    """Prépare le dataset Kaggle pour l'entraînement"""
    
    logger.info("🔧 Préparation du dataset Kaggle...")
    
    # Charger les données
    kaggle_path = Path("./data/raw/creditcard.csv")
    
    if not kaggle_path.exists():
        logger.error(f"❌ Fichier non trouvé: {kaggle_path}")
        logger.info("💡 Télécharge-le manuellement depuis Kaggle et place-le dans data/raw/")
        return None
    
    df = pd.read_csv(kaggle_path)
    
    logger.info(f"✅ Dataset chargé: {len(df)} transactions")
    logger.info(f"   - Colonnes: {df.shape[1]}")
    logger.info(f"   - Fraudes: {df['Class'].sum()} ({df['Class'].mean()*100:.3f}%)")
    
    # Le dataset Kaggle a des features PCA (V1-V28) + Time + Amount
    # On va normaliser Amount et créer quelques features supplémentaires
    
    # Normaliser Amount (log scale)
    df['Amount_log'] = np.log1p(df['Amount'])
    
    # Features temporelles (Time est en secondes depuis première transaction)
    df['Hour'] = (df['Time'] / 3600) % 24
    df['Day'] = (df['Time'] / 86400).astype(int)
    
    # Renommer la colonne cible pour cohérence
    df = df.rename(columns={'Class': 'is_fraud'})
    
    # Split train/test (80/20)
    train_df, test_df = train_test_split(
        df, 
        test_size=0.2, 
        random_state=42,
        stratify=df['is_fraud']  # Garder la même proportion de fraude
    )
    
    # Sauvegarder
    output_dir = Path("./data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    train_path = output_dir / "kaggle_train.csv"
    test_path = output_dir / "kaggle_test.csv"
    
    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)
    
    logger.info(f"✅ Données préparées:")
    logger.info(f"   - Train: {train_path} ({len(train_df)} lignes)")
    logger.info(f"   - Test: {test_path} ({len(test_df)} lignes)")
    logger.info(f"   - Train fraudes: {train_df['is_fraud'].sum()} ({train_df['is_fraud'].mean()*100:.3f}%)")
    logger.info(f"   - Test fraudes: {test_df['is_fraud'].sum()} ({test_df['is_fraud'].mean()*100:.3f}%)")
    
    return train_df, test_df


def compare_datasets():
    """Compare les caractéristiques des deux datasets"""
    
    logger.info("\n" + "="*70)
    logger.info("📊 COMPARAISON DES DATASETS")
    logger.info("="*70)
    
    # Charger les deux datasets
    sentra_path = Path("./data/processed/transactions_train.csv")
    kaggle_path = Path("./data/processed/kaggle_train.csv")
    
    if not sentra_path.exists() or not kaggle_path.exists():
        logger.warning("⚠️ Datasets manquants pour la comparaison")
        return
    
    sentra_df = pd.read_csv(sentra_path)
    kaggle_df = pd.read_csv(kaggle_path)
    
    logger.info("\n📈 STATISTIQUES COMPARATIVES:")
    logger.info(f"\n{'Métrique':<30} {'SÉNTRA (BCEAO)':<20} {'Kaggle':<20}")
    logger.info("-" * 70)
    
    # Taille
    logger.info(f"{'Nombre transactions':<30} {len(sentra_df):<20} {len(kaggle_df):<20}")
    
    # Taux de fraude
    sentra_fraud_rate = sentra_df['is_fraud'].mean() * 100
    kaggle_fraud_rate = kaggle_df['is_fraud'].mean() * 100
    logger.info(f"{'Taux de fraude (%)':<30} {sentra_fraud_rate:<20.2f} {kaggle_fraud_rate:<20.3f}")
    
    # Nombre de fraudes
    logger.info(f"{'Nombre de fraudes':<30} {sentra_df['is_fraud'].sum():<20} {kaggle_df['is_fraud'].sum():<20}")
    
    # Colonnes
    logger.info(f"{'Nombre de features':<30} {sentra_df.shape[1]:<20} {kaggle_df.shape[1]:<20}")
    
    logger.info("\n💡 OBSERVATIONS:")
    logger.info("   - Kaggle: Dataset PCA anonymisé (features V1-V28)")
    logger.info("   - SÉNTRA: Features interprétables (montant, localisation, etc.)")
    logger.info("   - Kaggle: Très déséquilibré (0.17% fraude)")
    logger.info("   - SÉNTRA: Plus équilibré (2.5% fraude, réaliste pour Afrique)")


def main():
    """Fonction principale"""
    
    logger.info("="*70)
    logger.info("📥 TÉLÉCHARGEMENT ET PRÉPARATION DATASET KAGGLE")
    logger.info("="*70)
    
    # Option 1 : Télécharger automatiquement (si API Kaggle configurée)
    logger.info("\n1️⃣ Tentative de téléchargement automatique...")
    success = download_kaggle_dataset()
    
    if not success:
        logger.info("\n" + "="*70)
        logger.info("📋 TÉLÉCHARGEMENT MANUEL REQUIS")
        logger.info("="*70)
        logger.info("\n🔗 Étapes:")
        logger.info("   1. Va sur: https://www.kaggle.com/mlg-ulb/creditcardfraud")
        logger.info("   2. Clique sur 'Download' (nécessite compte Kaggle gratuit)")
        logger.info("   3. Extrais creditcard.csv")
        logger.info("   4. Place-le dans: backend/data/raw/creditcard.csv")
        logger.info("   5. Relance ce script")
        logger.info("\n⏸️  Script en pause - Télécharge le fichier puis relance")
        return
    
    # Option 2 : Préparer les données
    logger.info("\n2️⃣ Préparation des données...")
    prepare_kaggle_data()
    
    # Option 3 : Comparaison
    logger.info("\n3️⃣ Comparaison des datasets...")
    compare_datasets()
    
    logger.info("\n" + "="*70)
    logger.info("✅ CONFIGURATION TERMINÉE")
    logger.info("="*70)
    logger.info("\n📝 Prochaines étapes:")
    logger.info("   1. Entraîner sur Kaggle: python scripts/train_model.py --dataset kaggle")
    logger.info("   2. Entraîner sur SÉNTRA: python scripts/train_model.py --dataset sentra")
    logger.info("   3. Entraîner sur les deux: python scripts/train_model.py --dataset both")


if __name__ == "__main__":
    main()