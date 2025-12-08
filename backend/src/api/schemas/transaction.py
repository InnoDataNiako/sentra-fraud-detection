# """
# Schémas Pydantic pour les transactions
# """

# from typing import Optional, Dict, Any, List
# from datetime import datetime
# from pydantic import BaseModel, Field, field_validator, ConfigDict


# class TransactionBase(BaseModel):
#     """Schéma de base pour une transaction"""
#     amount: float = Field(..., gt=0, description="Montant de la transaction (doit être > 0)")
#     currency: str = Field("XOF", min_length=3, max_length=3, description="Code devise ISO (ex: XOF, EUR)")
#     customer_id: str = Field(..., min_length=1, max_length=100, description="Identifiant unique du client")
#     merchant_id: Optional[str] = Field(None, max_length=100, description="Identifiant du commerçant")
    
#     # Détails transaction
#     transaction_type: Optional[str] = Field(None, description="Type: transfer, payment, withdrawal")
#     payment_method: Optional[str] = Field(None, description="Méthode: card, mobile, bank_transfer")
    
#     # Localisation
#     location: Optional[str] = Field(None, max_length=200, description="Localisation (ville, pays)")
#     ip_address: Optional[str] = Field(None, max_length=45, description="Adresse IP")
#     device_id: Optional[str] = Field(None, max_length=100, description="ID du device")
    
#     # Métadonnées additionnelles
#     metadata: Optional[Dict[str, Any]] = Field(None, description="Données supplémentaires en JSON")
    
#     @field_validator("currency")
#     @classmethod
#     def validate_currency(cls, v: str) -> str:
#         """Valide que la devise est en majuscules"""
#         return v.upper()
    
#     @field_validator("amount")
#     @classmethod
#     def validate_amount(cls, v: float) -> float:
#         """Valide que le montant est raisonnable"""
#         if v > 100_000_000:  # 100 millions
#             raise ValueError("Le montant ne peut pas dépasser 100 millions")
#         return round(v, 2)


# class TransactionCreate(TransactionBase):
#     """Schéma pour créer une nouvelle transaction"""
#     transaction_id: Optional[str] = Field(None, description="ID personnalisé (auto-généré si omis)")
    
#     model_config = ConfigDict(
#         json_schema_extra={
#             "example": {
#                 "transaction_id": "txn_20251114_001",
#                 "amount": 150000.0,
#                 "currency": "XOF",
#                 "customer_id": "cust_12345",
#                 "merchant_id": "merch_789",
#                 "transaction_type": "payment",
#                 "payment_method": "mobile",
#                 "location": "Dakar, Sénégal",
#                 "ip_address": "196.168.1.1",
#                 "device_id": "device_abc123"
#             }
#         }
#     )


# class TransactionResponse(TransactionBase):
#     """Schéma pour la réponse d'une transaction"""
#     id: int = Field(..., description="ID interne de la base de données")
#     transaction_id: str = Field(..., description="Identifiant unique de la transaction")
#     timestamp: datetime = Field(..., description="Date et heure de la transaction")
#     status: str = Field(..., description="Statut: pending, approved, rejected, under_review")
    
#     # Détection fraude
#     is_fraud: bool = Field(..., description="Indique si c'est une fraude")
#     # fraud_probability: float = Field(..., ge=0.0, le=1.0, description="Probabilité de fraude (0-1)")
#     fraud_score: float = Field(..., description="Score technique")
#     fraud_types: Optional[List[str]] = Field(None, description="Types de fraude détectés")
    
#     # Timestamps
#     processed_at: Optional[datetime] = Field(None, description="Date de traitement")
#     created_at: datetime = Field(..., description="Date de création")
#     updated_at: Optional[datetime] = Field(None, description="Date de mise à jour")
    
#     model_config = ConfigDict(
#         from_attributes=True,  # Permet de créer depuis un modèle SQLAlchemy
#         json_schema_extra={
#             "example": {
#                 "id": 1,
#                 "transaction_id": "txn_20251114_001",
#                 "amount": 150000.0,
#                 "currency": "XOF",
#                 "customer_id": "cust_12345",
#                 "merchant_id": "merch_789",
#                 "transaction_type": "payment",
#                 "payment_method": "mobile",
#                 "location": "Dakar, Sénégal",
#                 "ip_address": "196.168.1.1",
#                 "device_id": "device_abc123",
#                 "timestamp": "2025-11-14T08:00:00Z",
#                 "status": "approved",
#                 "is_fraud": False,
#                 "fraud_probability": 0.12,
#                 "fraud_types": None,
#                 "processed_at": "2025-11-14T08:00:01Z",
#                 "created_at": "2025-11-14T08:00:00Z",
#                 "updated_at": None
#             }
#         }
#     )

# from enum import Enum

# class TransactionStatus(str, Enum):
#     PENDING = "pending"
#     APPROVED = "approved"
#     REJECTED = "rejected"
#     FRAUD = "fraud"

# # Puis dans tes schémas :
# status: TransactionStatus = Field(..., description="Statut de la transaction")


# class TransactionUpdate(BaseModel):
#     """Schéma pour mettre à jour une transaction"""
#     status: Optional[str] = Field(None, description="Nouveau statut")
#     is_fraud: Optional[bool] = Field(None, description="Marquer comme fraude")
#     metadata: Optional[Dict[str, Any]] = Field(None, description="Métadonnées à ajouter")
    
#     model_config = ConfigDict(
#         json_schema_extra={
#             "example": {
#                 "status": "under_review",
#                 "is_fraud": True,
#                 "metadata": {"reviewed_by": "admin_01", "notes": "Suspect"}
#             }
#         }
#     )


# class TransactionListResponse(BaseModel):
#     """Schéma pour une liste de transactions"""
#     transactions: List[TransactionResponse] = Field(..., description="Liste des transactions")
#     total: int = Field(..., description="Nombre total de transactions")
    
#     model_config = ConfigDict(
#         json_schema_extra={
#             "example": {
#                 "transactions": [
#                     {
#                         "id": 1,
#                         "transaction_id": "txn_001",
#                         "amount": 50000.0,
#                         "currency": "XOF",
#                         "is_fraud": False,
#                         "fraud_probability": 0.05
#                     }
#                 ],
#                 "total": 1
#             }
#         }
#     )


# class TransactionStats(BaseModel):
#     """Schéma pour les statistiques d'un client"""
#     customer_id: str = Field(..., description="ID du client")
#     total_transactions: int = Field(..., description="Nombre total de transactions")
#     total_amount: float = Field(..., description="Montant total")
#     avg_amount: float = Field(..., description="Montant moyen")
#     fraud_count: int = Field(..., description="Nombre de fraudes")
#     fraud_rate: float = Field(..., description="Taux de fraude en %")
#     last_transaction_date: Optional[datetime] = Field(None, description="Date dernière transaction")
    
#     model_config = ConfigDict(
#         json_schema_extra={
#             "example": {
#                 "customer_id": "cust_12345",
#                 "total_transactions": 150,
#                 "total_amount": 12500000.0,
#                 "avg_amount": 83333.33,
#                 "fraud_count": 2,
#                 "fraud_rate": 1.33,
#                 "last_transaction_date": "2025-11-14T08:00:00Z"
#             }
#         }
#     )


"""
Schémas Pydantic pour les transactions
Alignés avec les modèles SQLAlchemy
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum


class TransactionStatus(str, Enum):
    """Statut de transaction - aligné avec SQLAlchemy"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    FRAUD = "fraud"


class TransactionBase(BaseModel):
    """Schéma de base pour une transaction"""
    amount: float = Field(..., gt=0, description="Montant de la transaction (doit être > 0)")
    currency: str = Field("XOF", min_length=3, max_length=3, description="Code devise ISO (ex: XOF, EUR)")
    customer_id: str = Field(..., min_length=1, max_length=100, description="Identifiant unique du client")
    merchant_id: Optional[str] = Field(None, max_length=100, description="Identifiant du commerçant")
    
    # Détails transaction
    transaction_type: Optional[str] = Field(None, description="Type: transfer, payment, withdrawal")
    
    # Localisation
    location: Optional[str] = Field(None, max_length=255, description="Localisation (ville, pays)")
    country_code: Optional[str] = Field(None, max_length=2, description="Code pays ISO")
    ip_address: Optional[str] = Field(None, max_length=45, description="Adresse IP")
    
    # Métadonnées additionnelles
    metadata: Optional[Dict[str, Any]] = Field(None, description="Données supplémentaires en JSON")
    
    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Valide que la devise est en majuscules"""
        return v.upper()
    
    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        """Valide que le montant est raisonnable"""
        if v > 100_000_000:  # 100 millions
            raise ValueError("Le montant ne peut pas dépasser 100 millions")
        return round(v, 2)
    
    @field_validator("country_code")
    @classmethod
    def validate_country_code(cls, v: Optional[str]) -> Optional[str]:
        """Valide le code pays"""
        if v is not None:
            return v.upper()
        return v


class TransactionCreate(TransactionBase):
    """Schéma pour créer une nouvelle transaction"""
    transaction_id: Optional[str] = Field(None, description="ID personnalisé (auto-généré si omis)")
    timestamp: Optional[datetime] = Field(None, description="Date/heure de la transaction (maintenant si omis)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "transaction_id": "txn_20251114_001",
                "amount": 150000.0,
                "currency": "XOF",
                "customer_id": "cust_12345",
                "merchant_id": "merch_789",
                "transaction_type": "payment",
                "location": "Dakar, Sénégal",
                "country_code": "SN",
                "ip_address": "196.168.1.1",
                "timestamp": "2025-11-14T08:00:00Z"
            }
        }
    )


class TransactionResponse(TransactionBase):
    """Schéma pour la réponse d'une transaction - Aligné avec SQLAlchemy"""
    id: int = Field(..., description="ID interne de la base de données")
    transaction_id: str = Field(..., description="Identifiant unique de la transaction")
    timestamp: datetime = Field(..., description="Date et heure de la transaction")
    status: TransactionStatus = Field(..., description="Statut de la transaction")
    
    # Détection fraude - Champs alignés avec SQLAlchemy
    is_fraud: bool = Field(..., description="Indique si c'est une fraude")
    fraud_score: float = Field(..., ge=0.0, le=1.0, description="Score de fraude (0-1)")
    fraud_reason: Optional[str] = Field(None, description="Raison de la détection de fraude")
    
    # Timestamps de la base
    created_at: datetime = Field(..., description="Date de création en base")
    updated_at: Optional[datetime] = Field(None, description="Date de mise à jour en base")
    
    model_config = ConfigDict(
        from_attributes=True,  # Permet de créer depuis un modèle SQLAlchemy
        json_schema_extra={
            "example": {
                "id": 1,
                "transaction_id": "txn_20251114_001",
                "amount": 150000.0,
                "currency": "XOF",
                "customer_id": "cust_12345",
                "merchant_id": "merch_789",
                "transaction_type": "payment",
                "location": "Dakar, Sénégal",
                "country_code": "SN",
                "ip_address": "196.168.1.1",
                "timestamp": "2025-11-14T08:00:00Z",
                "status": "approved",
                "is_fraud": False,
                "fraud_score": 0.12,
                "fraud_reason": None,
                "created_at": "2025-11-14T08:00:00Z",
                "updated_at": None
            }
        }
    )


class TransactionUpdate(BaseModel):
    """Schéma pour mettre à jour une transaction"""
    status: Optional[TransactionStatus] = Field(None, description="Nouveau statut")
    is_fraud: Optional[bool] = Field(None, description="Marquer comme fraude")
    fraud_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Nouveau score de fraude")
    fraud_reason: Optional[str] = Field(None, description="Raison de la fraude")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Métadonnées à ajouter")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "under_review",
                "is_fraud": True,
                "fraud_score": 0.85,
                "fraud_reason": "Montant suspect pour ce client",
                "metadata": {"reviewed_by": "admin_01", "notes": "Suspect"}
            }
        }
    )


class TransactionListResponse(BaseModel):
    """Schéma pour une liste de transactions"""
    transactions: List[TransactionResponse] = Field(..., description="Liste des transactions")
    total: int = Field(..., description="Nombre total de transactions")
    page: int = Field(..., description="Page actuelle")
    page_size: int = Field(..., description="Taille de la page")
    total_pages: int = Field(..., description="Nombre total de pages")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "transactions": [
                    {
                        "id": 1,
                        "transaction_id": "txn_001",
                        "amount": 50000.0,
                        "currency": "XOF",
                        "customer_id": "cust_12345",
                        "is_fraud": False,
                        "fraud_score": 0.05,
                        "status": "approved"
                    }
                ],
                "total": 1,
                "page": 1,
                "page_size": 50,
                "total_pages": 1
            }
        }
    )


class TransactionStats(BaseModel):
    """Schéma pour les statistiques d'un client"""
    customer_id: str = Field(..., description="ID du client")
    total_transactions: int = Field(..., description="Nombre total de transactions")
    total_amount: float = Field(..., description="Montant total")
    avg_amount: float = Field(..., description="Montant moyen")
    fraud_count: int = Field(..., description="Nombre de fraudes")
    fraud_rate: float = Field(..., description="Taux de fraude en %")
    last_transaction_date: Optional[datetime] = Field(None, description="Date dernière transaction")
    avg_fraud_score: float = Field(..., description="Score de fraude moyen")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "customer_id": "cust_12345",
                "total_transactions": 150,
                "total_amount": 12500000.0,
                "avg_amount": 83333.33,
                "fraud_count": 2,
                "fraud_rate": 1.33,
                "last_transaction_date": "2025-11-14T08:00:00Z",
                "avg_fraud_score": 0.15
            }
        }
    )


class TransactionAnalysis(BaseModel):
    """Schéma pour l'analyse détaillée d'une transaction"""
    transaction: TransactionResponse = Field(..., description="Transaction analysée")
    customer_history: TransactionStats = Field(..., description="Historique du client")
    risk_factors: List[str] = Field(..., description="Facteurs de risque identifiés")
    recommendation: str = Field(..., description="Recommandation")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "transaction": {
                    "id": 1,
                    "transaction_id": "txn_001",
                    "amount": 500000.0,
                    "customer_id": "cust_12345",
                    "is_fraud": True,
                    "fraud_score": 0.87
                },
                "customer_history": {
                    "customer_id": "cust_12345",
                    "total_transactions": 15,
                    "total_amount": 750000.0,
                    "avg_amount": 50000.0,
                    "fraud_count": 0,
                    "fraud_rate": 0.0,
                    "last_transaction_date": "2025-11-13T10:00:00Z",
                    "avg_fraud_score": 0.08
                },
                "risk_factors": [
                    "Montant 10x supérieur à la moyenne",
                    "Transaction dans un nouveau pays",
                    "Heure inhabituelle"
                ],
                "recommendation": "Bloquer et vérifier l'identité du client"
            }
        }
    )