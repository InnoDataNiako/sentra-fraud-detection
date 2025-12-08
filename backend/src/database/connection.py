"""
Configuration de la connexion à la base de données PostgreSQL
Gestion du pool de connexions et sessions SQLAlchemy
"""

from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)

# === BASE POUR LES MODÈLES ===
Base = declarative_base()

# === ENGINE SQLALCHEMY ===
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,  # Affiche les requêtes SQL si True
    pool_pre_ping=True,     # Vérifie la connexion avant utilisation
    poolclass=QueuePool,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_recycle=3600,      # Recycle les connexions après 1h
)

# === SESSION FACTORY ===
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# === EVENT LISTENERS ===
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Event déclenché lors de la connexion"""
    logger.debug("Nouvelle connexion PostgreSQL établie")


@event.listens_for(engine, "close")
def receive_close(dbapi_conn, connection_record):
    """Event déclenché lors de la fermeture"""
    logger.debug("Connexion PostgreSQL fermée")


# === DEPENDENCY INJECTION POUR FASTAPI ===
def get_db() -> Generator[Session, None, None]:
    """
    Dependency pour obtenir une session de base de données
    
    Usage dans FastAPI:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# === FONCTIONS UTILITAIRES ===
def init_db() -> None:
    """
    Initialise la base de données (crée toutes les tables)
    À utiliser uniquement en développement
    """
    logger.info("Initialisation de la base de données...")
    Base.metadata.create_all(bind=engine)
    logger.info(" Base de données initialisée avec succès")


def drop_all_tables() -> None:
    """
    Supprime toutes les tables (DANGER!)
    À utiliser uniquement en développement
    """
    logger.warning("⚠️ SUPPRESSION DE TOUTES LES TABLES...")
    Base.metadata.drop_all(bind=engine)
    logger.warning("❌ Toutes les tables ont été supprimées")


def check_db_connection() -> bool:
    """
    Vérifie que la connexion à la base de données fonctionne
    
    Returns:
        bool: True si la connexion fonctionne, False sinon
    """
    try:
        with engine.connect() as conn:
            from sqlalchemy import text  # ✅ IMPORT AJOUTÉ
            conn.execute(text("SELECT 1"))  # ✅ CORRECTION ICI
        logger.info("✅ Connexion à la base de données OK")
        return True
    except Exception as e:
        logger.error(f"❌ Erreur de connexion à la base de données: {e}")
        return False