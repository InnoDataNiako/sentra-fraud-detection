"""
Fonctions pour peupler la base de données, utilisant désormais le script ETL
pour charger les données réelles à partir des fichiers CSV.
"""

from sqlalchemy.orm import Session
import logging

# On importe la fonction de chargement des transactions depuis le nouveau fichier ETL
# NOTE: Cette fonction est définie dans src/etl/load_transactions.py
from src.etl.load_transactions import load_transactions_from_csv
# On importe le modèle de Transaction pour la vérification
from src.database.models import Transaction

logger = logging.getLogger(__name__)

def seed_db(db: Session):
    """
    Charge les transactions réelles depuis les fichiers CSV si la table est vide.
    Cette fonction est appelée au démarrage de l'application (via main.py).
    
    Args:
        db: Session SQLAlchemy pour interagir avec la base de données.
    """
    
    # 1. Vérification : Si des transactions existent, on saute le seeding.
    if db.query(Transaction).count() > 0:
        logger.info("La table 'transaction' contient déjà des données. Le seeding est ignoré.")
        db.close()
        return

    logger.info("Démarrage du chargement des transactions réelles depuis les fichiers CSV...")

    # 2. Appel du script ETL pour charger les transactions
    # Le script load_transactions_from_csv gère l'extraction, la transformation
    # et l'insertion des données dans la base (Load).
    total_loaded = load_transactions_from_csv(db)

    if total_loaded > 0:
        logger.info(f"Seeding terminé avec succès. {total_loaded} transactions chargées.")
    else:
        logger.warning("Le chargement ETL a échoué ou aucun fichier n'a été chargé. Vérifiez les chemins d'accès aux CSV.")
        
    db.close()