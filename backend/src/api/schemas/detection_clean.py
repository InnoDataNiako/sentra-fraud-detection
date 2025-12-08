"""
Schémas Pydantic complets pour la détection de fraude - Version production
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, timezone

class DetectionRequest(BaseModel):
    """Schéma pour une requête de détection de fraude"""
    transaction_id: Optional[str] = Field(default=None, description="ID de transaction")
    amount: float = Field(gt=0, le=100000000, description="Montant de la transaction (0 - 100M)")
    currency: str = Field(default="XOF", min_length=3, max_length=3, description="Code devise ISO")
    customer_id: str = Field(min_length=1, max_length=100, description="ID du client")
    merchant_id: Optional[str] = Field(default=None, max_length=100, description="ID du commerçant")
    transaction_type: str = Field(default="payment", description="Type de transaction")
    location: Optional[str] = Field(default=None, description="Localisation")
    ip_address: Optional[str] = Field(default=None, description="Adresse IP")
    device_id: Optional[str] = Field(default=None, description="ID du device")
    timestamp: Optional[datetime] = Field(default=None, description="Date/heure")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Données supplémentaires")

    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra={
            "example": {
                "transaction_id": "txn_clean_001",
                "amount": 25000.0,
                "currency": "XOF",
                "customer_id": "cust_clean_001",
                "merchant_id": "merch_clean_001",
                "transaction_type": "payment",
                "location": "Dakar, Sénégal",
                "ip_address": "196.200.1.100",
                "device_id": "device_clean_123",
                "timestamp": "2025-11-20T10:00:00Z"
            }
        }
    )


class FraudExplanation(BaseModel):
    """Explication détaillée de la détection"""
    top_features: Dict[str, float] = Field(description="Features les plus importantes")
    fraud_indicators: List[str] = Field(description="Indicateurs de fraude détectés")
    risk_factors: Dict[str, Any] = Field(description="Facteurs de risque")
    algorithm_confidence: float = Field(ge=0.0, le=1.0, description="Confiance de l'algorithme")

    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra={
            "example": {
                "top_features": {
                    "amount": 0.45,
                    "transaction_velocity": 0.32,
                    "location_risk": 0.18
                },
                "fraud_indicators": [
                    "Montant inhabituel pour ce client",
                    "Localisation inconnue",
                    "Haute vélocité de transactions"
                ],
                "risk_factors": {
                    "amount_zscore": 3.2,
                    "velocity_24h": 8,
                    "new_location": True
                },
                "algorithm_confidence": 0.92
            }
        }
    )


class DetectionResult(BaseModel):
    """Résultat complet de la détection de fraude"""
    transaction_id: str = Field(description="ID de la transaction analysée")
    detection_id: str = Field(description="ID unique de cette détection")
    is_fraud: bool = Field(description="Verdict: fraude ou légitime")
    fraud_probability: float = Field(ge=0.0, le=1.0, description="Probabilité de fraude (0-1)")
    risk_level: str = Field(description="Niveau de risque: low, medium, high, critical")
    fraud_types: List[str] = Field(default_factory=list, description="Types de fraude détectés")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Score de confiance")
    explanation: Optional[FraudExplanation] = Field(default=None, description="Explication détaillée")
    recommendation: str = Field(description="Action recommandée")
    should_block: bool = Field(description="Indique si la transaction doit être bloquée")
    processing_time_ms: float = Field(description="Temps de traitement en millisecondes")
    algorithm_version: str = Field(description="Version de l'algorithme")
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), 
    description="Date de détection")
    

    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra={
            "example": {
                "transaction_id": "txn_clean_001",
                "detection_id": "det_20251120_001",
                "is_fraud": True,
                "fraud_probability": 0.87,
                "risk_level": "high",
                "fraud_types": ["unusual_amount", "suspicious_location"],
                "confidence_score": 0.92,
                "explanation": {
                    "top_features": {
                        "amount": 0.45,
                        "transaction_velocity": 0.32,
                        "location_risk": 0.18
                    },
                    "fraud_indicators": [
                        "Montant 5x supérieur à la moyenne du client",
                        "Localisation jamais utilisée auparavant"
                    ],
                    "risk_factors": {
                        "amount_zscore": 4.2,
                        "velocity_24h": 12,
                        "new_location": True
                    },
                    "algorithm_confidence": 0.92
                },
                "recommendation": "Bloquer la transaction et contacter le client",
                "should_block": True,
                "processing_time_ms": 45.8,
                "algorithm_version": "v1.0.0",
                "detected_at": "2025-11-20T10:00:00.123Z"
            }
        }
    )


class DetectionResponse(BaseModel):
    """Schéma pour la réponse de détection de fraude"""
    transaction_id: str = Field(description="ID de la transaction analysée")
    is_fraud: bool = Field(description="Verdict: fraude ou légitime")
    fraud_probability: float = Field(ge=0.0, le=1.0, description="Probabilité de fraude (0-1)")
    risk_level: str = Field(description="Niveau de risque: low, medium, high, critical")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Score de confiance")
    recommendation: str = Field(description="Action recommandée")
    should_block: bool = Field(description="Indique si la transaction doit être bloquée")
    processing_time_ms: float = Field(description="Temps de traitement en millisecondes")
    algorithm_version: str = Field(description="Version de l'algorithme")
    algorithm_confidence: float = Field(ge=0.0, le=1.0, description="Confiance de l'algorithme")
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Date de détection")
    fraud_types: List[str] = Field(default_factory=list, description="Types de fraude détectés")
    explanation: Optional[FraudExplanation] = Field(default=None, description="Explication détaillée")

    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra={
            "example": {
                "transaction_id": "txn_clean_001",
                "is_fraud": True,
                "fraud_probability": 0.87,
                "risk_level": "high",
                "confidence_score": 0.92,
                "recommendation": "Bloquer la transaction et contacter le client",
                "should_block": True,
                "processing_time_ms": 45.8,
                "algorithm_version": "v1.0.0",
                "algorithm_confidence": 0.95,
                "detected_at": "2025-11-20T10:00:00.123Z",
                "fraud_types": ["unusual_amount", "suspicious_location"]
            }
        }
    )


class BatchDetectionRequest(BaseModel):
    """Requête pour détecter plusieurs transactions en batch"""
    transactions: List[DetectionRequest] = Field(min_length=1, max_length=1000)
    
    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra={
            "example": {
                "transactions": [
                    {
                        "transaction_id": "txn_batch_001",
                        "amount": 50000.0,
                        "currency": "XOF",
                        "customer_id": "cust_batch_001"
                    },
                    {
                        "transaction_id": "txn_batch_002",
                        "amount": 150000.0,
                        "currency": "XOF",
                        "customer_id": "cust_batch_002"
                    }
                ]
            }
        }
    )


class BatchDetectionResponse(BaseModel):
    results: List[DetectionResponse] = Field(description="Résultats pour chaque transaction")
    total_processed: int = Field(description="Nombre de transactions traitées")
    total_fraud: int = Field(description="Nombre de fraudes détectées")
    fraud_rate: float = Field(description="Taux de fraude en %")
    total_processing_time_ms: float = Field(description="Temps total de traitement")

    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra={
            "example": {
                "results": [
                    {
                        "transaction_id": "txn_batch_001",
                        "is_fraud": False,
                        "fraud_probability": 0.12
                    },
                    {
                        "transaction_id": "txn_batch_002",
                        "is_fraud": True,
                        "fraud_probability": 0.89
                    }
                ],
                "total_processed": 2,
                "total_fraud": 1,
                "fraud_rate": 50.0,
                "total_processing_time_ms": 89.5
            }
        }
    )


class AlertResponse(BaseModel):
    """Schéma pour une alerte de fraude"""
    alert_id: str = Field(description="ID unique de l'alerte")
    transaction_id: str = Field(description="ID de la transaction concernée")
    severity: str = Field(description="Sévérité: low, medium, high, critical")
    fraud_type: str = Field(description="Type de fraude")
    title: str = Field(description="Titre de l'alerte")
    description: Optional[str] = Field(default=None, description="Description détaillée")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Score de confiance")
    is_resolved: bool = Field(default=False, description="Indique si l'alerte est résolue")
    created_at: datetime = Field(description="Date de création")
    
    model_config = ConfigDict(
        protected_namespaces=(),
        from_attributes=True,
        json_schema_extra={
            "example": {
                "alert_id": "alert_clean_001",
                "transaction_id": "txn_clean_001",
                "severity": "high",
                "fraud_type": "unusual_amount",
                "title": "Montant Transaction Suspect",
                "description": "Transaction de 500,000 XOF détectée, 5x supérieur à la moyenne",
                "confidence_score": 0.87,
                "is_resolved": False,
                "created_at": "2025-11-20T10:00:00Z"
            }
        }
    )