"""
Script ETL pour charger les transactions depuis les fichiers CSV vers la base de données.
Nécessite la librairie 'pandas'.
"""
import pandas as pd
from sqlalchemy.orm import Session  # 🔧 AJOUTER CET IMPORT
from datetime import datetime
import os
import logging
from pathlib import Path
import random  # 🔧 AJOUTER CET IMPORT

from src.database.models import Transaction, TransactionStatus  # 🔧 AJOUTER TransactionStatus
from src.core.config import settings

logger = logging.getLogger(__name__)

# Définition du chemin de base pour les fichiers de données
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"

def load_transactions_from_csv(db: Session, train_file: str = "transactions_train.csv", test_file: str = "transactions_test.csv"):
    """
    Charge les transactions à partir des fichiers CSV (train et test) dans la base de données.
    """
    
    train_path = DATA_DIR / train_file
    test_path = DATA_DIR / test_file
    
    if not train_path.exists() or not test_path.exists():
        logger.error(f"Fichiers de données non trouvés. Vérifiez les chemins : {train_path} et {test_path}")
        return 0

    logger.info(f"Chargement des fichiers train ({train_file}) et test ({test_file})...")

    try:
        # 1. Extraction et Concaténation
        df_train = pd.read_csv(train_path)
        df_test = pd.read_csv(test_path)
        df_full = pd.concat([df_train, df_test], ignore_index=True)
        
        logger.info(f"Total des transactions chargées: {len(df_full)}")
        
        # 2. Transformation : Préparation pour SQLAlchemy
        
        # 🔧 CORRECTION : Mapping des colonnes selon votre structure réelle
        column_mapping = {
            'transaction_id': 'transaction_id',
            'amount': 'amount', 
            'currency': 'currency',
            'customer_id': 'customer_id',
            'merchant_id': 'merchant_id',
            'transaction_type': 'transaction_type',
            'location': 'location',
            'ip_address': 'ip_address',
            'timestamp': 'timestamp',
            'is_fraud': 'is_fraud'
        }
        
        df_full.rename(columns=column_mapping, inplace=True)
        
        # 🔧 CORRECTION : Conversion du timestamp
        df_full['timestamp'] = pd.to_datetime(df_full['timestamp'])
        
        # 🔧 CORRECTION : Ajout des colonnes manquantes avec valeurs par défaut
        if 'country_code' not in df_full.columns:
            # Extraire le code pays de la localisation
            def extract_country_code(location):
                if 'Sénégal' in location:
                    return 'SN'
                elif 'Togo' in location:
                    return 'TG'
                elif 'Bénin' in location:
                    return 'BJ'
                elif 'Guinée-Bissau' in location:
                    return 'GW'
                elif 'Burkina Faso' in location:
                    return 'BF'
                else:
                    return 'SN'
            
            df_full['country_code'] = df_full['location'].apply(extract_country_code)
        
        if 'fraud_score' not in df_full.columns:
            # Générer un score de fraude réaliste
            df_full['fraud_score'] = df_full['is_fraud'].apply(
                lambda x: round(0.8 + 0.2 * random.random(), 3) if x else round(0.1 + 0.2 * random.random(), 3)
            )
        
        if 'fraud_reason' not in df_full.columns:
            df_full['fraud_reason'] = df_full['is_fraud'].apply(
                lambda x: "Comportement suspect détecté" if x else None
            )
        
        # Définir le statut en fonction de is_fraud
        def get_status(is_fraud):
            return TransactionStatus.FRAUD if is_fraud else TransactionStatus.APPROVED
        
        df_full['status'] = df_full['is_fraud'].apply(get_status)
        
        # Sélection des colonnes finales pour le modèle Transaction
        required_columns = [
            'transaction_id', 'timestamp', 'amount', 'currency', 'customer_id', 'merchant_id',
            'transaction_type', 'location', 'country_code', 'ip_address', 'is_fraud', 
            'fraud_score', 'fraud_reason', 'status'
        ]
        
        # Garder seulement les colonnes disponibles
        available_columns = [col for col in required_columns if col in df_full.columns]
        df_ready = df_full[available_columns]
        
        # Conversion du DataFrame en dictionnaire de lignes pour l'insertion
        transactions_data = df_ready.to_dict('records')

        # 3. Chargement (Load)
        
        # Création des objets Transaction
        transaction_objects = []
        for data in transactions_data:
            try:
                transaction_objects.append(Transaction(**data))
            except Exception as e:
                logger.warning(f"Erreur avec transaction {data.get('transaction_id')}: {e}")
                continue
        
        # Insertion en masse
        db.add_all(transaction_objects)
        db.commit()
        
        total_loaded = len(transaction_objects)
        logger.info(f"✅ Chargement réussi de {total_loaded} transactions réelles dans la base de données.")
        return total_loaded

    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erreur critique lors du chargement des transactions : {e}")
        import traceback
        traceback.print_exc()
        return 0