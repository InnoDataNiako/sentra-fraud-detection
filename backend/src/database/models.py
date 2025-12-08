# """
# Modèles SQLAlchemy pour la base de données SÉNTRA
# Définit les tables : Transaction, FraudAlert, User, AuditLog
# """

# from datetime import datetime
# from sqlalchemy import (
#     Column, Integer, String, Float, Boolean, DateTime,
#     ForeignKey, Text, Enum as SQLEnum, Index
# )
# from sqlalchemy.orm import relationship
# import enum

# from .connection import Base


# # === ENUMS ===
# class TransactionStatus(str, enum.Enum):
#     """Statut d'une transaction"""
#     PENDING = "pending"
#     APPROVED = "approved"
#     REJECTED = "rejected"
#     FRAUD = "fraud"


# class AlertSeverity(str, enum.Enum):
#     """Niveau de gravité d'une alerte"""
#     LOW = "low"
#     MEDIUM = "medium"
#     HIGH = "high"
#     CRITICAL = "critical"


# # === MODÈLES ===
# class Transaction(Base):
#     """Modèle pour les transactions financières"""
    
#     __tablename__ = "transactions"
    
#     # Clé primaire
#     id = Column(Integer, primary_key=True, index=True)
    
#     # Identifiants
#     transaction_id = Column(String(100), unique=True, index=True, nullable=False)
#     customer_id = Column(String(100), index=True, nullable=False)
#     merchant_id = Column(String(100), index=True, nullable=False)
    
#     # Détails transaction
#     amount = Column(Float, nullable=False)
#     currency = Column(String(3), default="XOF")  # Franc CFA
#     transaction_type = Column(String(50))  # payment, transfer, withdrawal
    
#     # Informations géographiques
#     location = Column(String(255))
#     country_code = Column(String(2))
#     ip_address = Column(String(45))
    
#     # Informations temporelles
#     timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
#     # Détection de fraude
#     is_fraud = Column(Boolean, default=False, index=True)
#     fraud_score = Column(Float, default=0.0)  # Score entre 0 et 1
#     fraud_reason = Column(Text)  # Explication de la détection
    
#     # Statut
#     status = Column(
#         SQLEnum(TransactionStatus),
#         default=TransactionStatus.PENDING,
#         nullable=False
#     )
    
#     # Métadonnées
#     created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
#     # Relations
#     alerts = relationship("FraudAlert", back_populates="transaction", cascade="all, delete-orphan")
    
#     # Index composites pour performance
#     __table_args__ = (
#         Index('idx_customer_timestamp', 'customer_id', 'timestamp'),
#         Index('idx_merchant_timestamp', 'merchant_id', 'timestamp'),
#         Index('idx_fraud_score', 'fraud_score'),
#     )
    
#     def __repr__(self):
#         return f"<Transaction(id={self.transaction_id}, amount={self.amount}, fraud={self.is_fraud})>"


# class FraudAlert(Base):
#     """Modèle pour les alertes de fraude"""
    
#     __tablename__ = "fraud_alerts"
    
#     # Clé primaire
#     id = Column(Integer, primary_key=True, index=True)
    
#     # Identifiant unique
#     alert_id = Column(String(100), unique=True, index=True, nullable=False)
    
#     # Relation avec transaction
#     transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    
#     # Détails de l'alerte
#     severity = Column(
#         SQLEnum(AlertSeverity),
#         default=AlertSeverity.MEDIUM,
#         nullable=False,
#         index=True
#     )
    
#     title = Column(String(255), nullable=False)
#     description = Column(Text)
#     fraud_indicators = Column(Text)  # JSON string des indicateurs
    
#     # Réponse à l'alerte
#     is_reviewed = Column(Boolean, default=False, index=True)
#     reviewed_by = Column(String(100))
#     reviewed_at = Column(DateTime)
#     resolution = Column(Text)  # Action prise
    
#     # Métadonnées
#     created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
#     # Relations
#     transaction = relationship("Transaction", back_populates="alerts")
    
#     def __repr__(self):
#         return f"<FraudAlert(id={self.alert_id}, severity={self.severity})>"


# class User(Base):
#     """Modèle pour les utilisateurs du système (admin, analysts)"""
    
#     __tablename__ = "users"
    
#     # Clé primaire
#     id = Column(Integer, primary_key=True, index=True)
    
#     # Informations utilisateur
#     username = Column(String(100), unique=True, index=True, nullable=False)
#     email = Column(String(255), unique=True, index=True, nullable=False)
#     full_name = Column(String(255))
    
#     # Authentification
#     hashed_password = Column(String(255), nullable=False)
    
#     # Rôle et permissions
#     role = Column(String(50), default="analyst")  # admin, analyst, viewer
#     is_active = Column(Boolean, default=True, index=True)
#     is_superuser = Column(Boolean, default=False)
    
#     # Métadonnées
#     created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
#     last_login = Column(DateTime)
    
#     def __repr__(self):
#         return f"<User(username={self.username}, role={self.role})>"


# class AuditLog(Base):
#     """Modèle pour les logs d'audit (traçabilité des actions)"""
    
#     __tablename__ = "audit_logs"
    
#     # Clé primaire
#     id = Column(Integer, primary_key=True, index=True)
    
#     # Qui a fait l'action
#     user_id = Column(Integer, ForeignKey("users.id"))
#     username = Column(String(100), index=True)
    
#     # Détails de l'action
#     action = Column(String(100), nullable=False, index=True)  # CREATE, UPDATE, DELETE
#     resource = Column(String(100), nullable=False)  # transaction, alert, user
#     resource_id = Column(String(100))
    
#     # Contexte
#     ip_address = Column(String(45))
#     user_agent = Column(Text)
    
#     # Changements
#     old_values = Column(Text)  # JSON des anciennes valeurs
#     new_values = Column(Text)  # JSON des nouvelles valeurs
    
#     # Métadonnées
#     timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
#     def __repr__(self):
#         return f"<AuditLog(action={self.action}, resource={self.resource}, user={self.username})>"


# class ModelMetrics(Base):
#     """Modèle pour stocker les métriques des modèles ML"""
    
#     __tablename__ = "model_metrics"
    
#     # Clé primaire
#     id = Column(Integer, primary_key=True, index=True)
    
#     # Identifiant du modèle
#     model_name = Column(String(100), nullable=False, index=True)
#     model_version = Column(String(50), nullable=False)
    
#     # Métriques de performance
#     accuracy = Column(Float)
#     precision = Column(Float)
#     recall = Column(Float)
#     f1_score = Column(Float)
#     auc_roc = Column(Float)
    
#     # Métriques business
#     false_positive_rate = Column(Float)
#     false_negative_rate = Column(Float)
#     total_predictions = Column(Integer, default=0)
#     fraud_detected = Column(Integer, default=0)
    
#     # Métriques système
#     avg_prediction_time_ms = Column(Float)
    
#     # Métadonnées
#     measured_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
#     def __repr__(self):
#         return f"<ModelMetrics(model={self.model_name}, f1={self.f1_score})>"


"""
Modèles SQLAlchemy pour la base de données SÉNTRA
Définit les tables : Transaction, FraudAlert, User, AuditLog
"""

from datetime import datetime
from typing import Dict, Any
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime,
    ForeignKey, Text, Enum as SQLEnum, Index, JSON
)
from sqlalchemy.orm import relationship
import enum

from .connection import Base


# === ENUMS ===
class TransactionStatus(str, enum.Enum):
    """Statut d'une transaction"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    FRAUD = "fraud"


class AlertSeverity(str, enum.Enum):
    """Niveau de gravité d'une alerte"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# === MODÈLES ===
class Transaction(Base):
    """Modèle pour les transactions financières"""
    
    __tablename__ = "transactions"
    
    # Clé primaire
    id = Column(Integer, primary_key=True, index=True)
    
    # Identifiants
    transaction_id = Column(String(100), unique=True, index=True, nullable=False)
    customer_id = Column(String(100), index=True, nullable=False)
    merchant_id = Column(String(100), index=True, nullable=False)
    
    # Détails transaction
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="XOF")  # Franc CFA
    transaction_type = Column(String(50))  # payment, transfer, withdrawal
    
    # Informations géographiques
    location = Column(String(255))
    country_code = Column(String(2))
    ip_address = Column(String(45))
    
    # Informations temporelles
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Détection de fraude
    is_fraud = Column(Boolean, default=False, index=True)
    fraud_score = Column(Float, default=0.0)  # Score entre 0 et 1
    fraud_reason = Column(Text)  # Explication de la détection
    
    # Statut
    status = Column(
        SQLEnum(TransactionStatus),
        default=TransactionStatus.PENDING,
        nullable=False
    )
    
    # Métadonnées - 🔧 CORRECTION : Changer le nom pour éviter le conflit
    transaction_metadata = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    alerts = relationship("FraudAlert", back_populates="transaction", cascade="all, delete-orphan")
    
    # Index composites pour performance
    __table_args__ = (
        Index('idx_customer_timestamp', 'customer_id', 'timestamp'),
        Index('idx_merchant_timestamp', 'merchant_id', 'timestamp'),
        Index('idx_fraud_score', 'fraud_score'),
    )
    
    def __repr__(self):
        return f"<Transaction(id={self.transaction_id}, amount={self.amount}, fraud={self.is_fraud})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'objet SQLAlchemy en dictionnaire pour Pydantic"""
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'amount': float(self.amount) if self.amount else 0.0,
            'currency': self.currency,
            'customer_id': self.customer_id,
            'merchant_id': self.merchant_id,
            'transaction_type': self.transaction_type,
            'location': self.location,
            'country_code': self.country_code,
            'ip_address': self.ip_address,
            'timestamp': self.timestamp,
            'status': self.status,
            'is_fraud': self.is_fraud,
            'fraud_score': float(self.fraud_score) if self.fraud_score else 0.0,
            'fraud_reason': self.fraud_reason,
            'metadata': self.transaction_metadata if self.transaction_metadata else {},  # 🔧 CORRECTION : mapper vers metadata
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }


class FraudAlert(Base):
    """Modèle pour les alertes de fraude"""
    
    __tablename__ = "fraud_alerts"
    
    # Clé primaire
    id = Column(Integer, primary_key=True, index=True)
    
    # Identifiant unique
    alert_id = Column(String(100), unique=True, index=True, nullable=False)
    
    # Relation avec transaction
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    
    # Détails de l'alerte
    severity = Column(
        SQLEnum(AlertSeverity),
        default=AlertSeverity.MEDIUM,
        nullable=False,
        index=True
    )
    
    title = Column(String(255), nullable=False)
    description = Column(Text)
    fraud_indicators = Column(Text)  # JSON string des indicateurs
    
    # Réponse à l'alerte
    is_reviewed = Column(Boolean, default=False, index=True)
    reviewed_by = Column(String(100))
    reviewed_at = Column(DateTime)
    resolution = Column(Text)  # Action prise
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    transaction = relationship("Transaction", back_populates="alerts")
    
    def __repr__(self):
        return f"<FraudAlert(id={self.alert_id}, severity={self.severity})>"


class User(Base):
    """Modèle pour les utilisateurs du système (admin, analysts)"""
    
    __tablename__ = "users"
    
    # Clé primaire
    id = Column(Integer, primary_key=True, index=True)
    
    # Informations utilisateur
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255))
    
    # Authentification
    hashed_password = Column(String(255), nullable=False)
    
    # Rôle et permissions
    role = Column(String(50), default="analyst")  # admin, analyst, viewer
    is_active = Column(Boolean, default=True, index=True)
    is_superuser = Column(Boolean, default=False)
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime)
    
    def __repr__(self):
        return f"<User(username={self.username}, role={self.role})>"


class AuditLog(Base):
    """Modèle pour les logs d'audit (traçabilité des actions)"""
    
    __tablename__ = "audit_logs"
    
    # Clé primaire
    id = Column(Integer, primary_key=True, index=True)
    
    # Qui a fait l'action
    user_id = Column(Integer, ForeignKey("users.id"))
    username = Column(String(100), index=True)
    
    # Détails de l'action
    action = Column(String(100), nullable=False, index=True)  # CREATE, UPDATE, DELETE
    resource = Column(String(100), nullable=False)  # transaction, alert, user
    resource_id = Column(String(100))
    
    # Contexte
    ip_address = Column(String(45))
    user_agent = Column(Text)
    
    # Changements
    old_values = Column(Text)  # JSON des anciennes valeurs
    new_values = Column(Text)  # JSON des nouvelles valeurs
    
    # Métadonnées
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<AuditLog(action={self.action}, resource={self.resource}, user={self.username})>"


class ModelMetrics(Base):
    """Modèle pour stocker les métriques des modèles ML"""
    
    __tablename__ = "model_metrics"
    
    # Clé primaire
    id = Column(Integer, primary_key=True, index=True)
    
    # Identifiant du modèle
    model_name = Column(String(100), nullable=False, index=True)
    model_version = Column(String(50), nullable=False)
    
    # Métriques de performance
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    auc_roc = Column(Float)
    
    # Métriques business
    false_positive_rate = Column(Float)
    false_negative_rate = Column(Float)
    total_predictions = Column(Integer, default=0)
    fraud_detected = Column(Integer, default=0)
    
    # Métriques système
    avg_prediction_time_ms = Column(Float)
    
    # Métadonnées
    measured_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<ModelMetrics(model={self.model_name}, f1={self.f1_score})>"