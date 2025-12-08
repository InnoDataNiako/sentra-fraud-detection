"""
Script pour initialiser la base de données SÉNTRA
Crée toutes les tables et insère des données de test
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from src.database.connection import init_db, check_db_connection, engine
from src.database.models import Base
from src.core.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


def create_tables():
    """Crée toutes les tables dans la base de données"""
    logger.info("🔨 Création des tables...")
    
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tables créées avec succès:")
        
        # Liste les tables créées
        for table_name in Base.metadata.tables.keys():
            logger.info(f"   - {table_name}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Erreur lors de la création des tables: {e}")
        return False


def drop_tables():
    """Supprime toutes les tables (DANGER!)"""
    logger.warning("⚠️  SUPPRESSION DE TOUTES LES TABLES...")
    response = input("Êtes-vous sûr ? (oui/non): ")
    
    if response.lower() == "oui":
        try:
            Base.metadata.drop_all(bind=engine)
            logger.warning("❌ Toutes les tables ont été supprimées")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur lors de la suppression: {e}")
            return False
    else:
        logger.info("Opération annulée")
        return False


def main():
    """Point d'entrée principal"""
    logger.info("=" * 60)
    logger.info("🚀 SÉNTRA - Initialisation de la base de données")
    logger.info("=" * 60)
    
    # Vérifier la connexion
    if not check_db_connection():
        logger.error("❌ Impossible de se connecter à la base de données")
        logger.error("Vérifiez que PostgreSQL est démarré et que DATABASE_URL est correct")
        sys.exit(1)
    
    # Menu
    print("\nOptions disponibles:")
    print("1. Créer les tables")
    print("2. Supprimer toutes les tables (DANGER!)")
    print("3. Recréer toutes les tables (drop + create)")
    print("4. Quitter")
    
    choice = input("\nVotre choix (1-4): ")
    
    if choice == "1":
        if create_tables():
            logger.info("✅ Base de données initialisée avec succès!")
    
    elif choice == "2":
        drop_tables()
    
    elif choice == "3":
        if drop_tables():
            create_tables()
            logger.info("✅ Base de données réinitialisée avec succès!")
    
    elif choice == "4":
        logger.info("Au revoir!")
    
    else:
        logger.error("Choix invalide")
        sys.exit(1)


if __name__ == "__main__":
    main()