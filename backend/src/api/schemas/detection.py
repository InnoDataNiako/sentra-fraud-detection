# """
# Schémas Pydantic pour la détection de fraude
# """

# from typing import Optional, Dict, Any, List
# from datetime import datetime
# from pydantic import BaseModel, Field, ConfigDict


# class DetectionRequest(BaseModel):
#     """Schéma pour une requête de détection de fraude"""
#     transaction_id: Optional[str] = Field(None, description="ID de transaction (auto-généré si omis)")
#     amount: float = Field(..., gt=0, description="Montant de la transaction")
#     currency: str = Field("XOF", min_length=3, max_length=3, description="Code devise")
#     customer_id: str = Field(..., description="ID du client")
#     merchant_id: Optional[str] = Field(None, description="ID du commerçant")
    
#     # Contexte
#     transaction_type: Optional[str] = Field("payment", description="Type de transaction")
#     payment_method: Optional[str] = Field("mobile", description="Méthode de paiement")
#     location: Optional[str] = Field(None, description="Localisation")
#     ip_address: Optional[str] = Field(None, description="Adresse IP")
#     device_id: Optional[str] = Field(None, description="ID du device")
#     timestamp: Optional[datetime] = Field(None, description="Date/heure (maintenant si omis)")
    
#     # Métadonnées
#     metadata: Optional[Dict[str, Any]] = Field(None, description="Données supplémentaires")
    
#     model_config = ConfigDict(
#         protected_namespaces=(),  # AJOUTE CETTE LIGNE
#         json_schema_extra={
#             "example": {
#                 "transaction_id": "txn_test_001",
#                 "amount": 500000.0,
#                 "currency": "XOF",
#                 "customer_id": "cust_12345",
#                 "merchant_id": "merch_789",
#                 "transaction_type": "payment",
#                 "payment_method": "mobile",
#                 "location": "Dakar, Sénégal",
#                 "ip_address": "196.168.1.1",
#                 "device_id": "device_abc123",
#                 "timestamp": "2025-11-14T08:00:00Z"
#             }
#         }
#     )

# class FraudExplanation(BaseModel):
#     """Explication détaillée de la détection"""
#     top_features: Dict[str, float] = Field(..., description="Features les plus importantes (SHAP)")
#     fraud_indicators: List[str] = Field(..., description="Indicateurs de fraude détectés")
#     risk_factors: Dict[str, Any] = Field(..., description="Facteurs de risque")
    
#     # CORRECTION : Renommer ce champ aussi
#     ml_confidence: float = Field(..., ge=0.0, le=1.0, description="Confiance du modèle")  # Avant: model_confidence
    
#     model_config = ConfigDict(
#         protected_namespaces=(),  # CORRECTION ici aussi
#         json_schema_extra={
#             "example": {
#                 "top_features": {
#                     "amount": 0.45,
#                     "transaction_velocity": 0.32,
#                     "location_risk": 0.18
#                 },
#                 "fraud_indicators": [
#                     "Montant inhabituel pour ce client",
#                     "Localisation inconnue",
#                     "Haute vélocité de transactions"
#                 ],
#                 "risk_factors": {
#                     "amount_zscore": 3.2,
#                     "velocity_24h": 8,
#                     "new_location": True
#                 },
#                 "ml_confidence": 0.92
#             }
#         }
#     )


# class DetectionResult(BaseModel):
#     """Résultat complet de la détection de fraude"""
#     # Identifiants
#     transaction_id: str = Field(..., description="ID de la transaction analysée")
#     detection_id: str = Field(..., description="ID unique de cette détection")
    
#     # Résultat principal
#     is_fraud: bool = Field(..., description="Verdict: fraude ou légitime")
#     fraud_probability: float = Field(..., ge=0.0, le=1.0, description="Probabilité de fraude (0-1)")
#     risk_level: str = Field(..., description="Niveau de risque: low, medium, high, critical")
    
#     # Classification détaillée
#     fraud_types: List[str] = Field(default=[], description="Types de fraude détectés")
#     confidence_score: float = Field(..., ge=0.0, le=1.0, description="Score de confiance")
    
#     # Explication
#     explanation: Optional[FraudExplanation] = Field(None, description="Explication détaillée")
    
#     # Recommandation
#     recommendation: str = Field(..., description="Action recommandée")
#     should_block: bool = Field(..., description="Indique si la transaction doit être bloquée")
    
#     # Métriques de performance
#     processing_time_ms: float = Field(..., description="Temps de traitement en millisecondes")
#     ml_model_version: str = Field(..., description="Version du modèle utilisé")  # Renommé

#     # Timestamps
#     detected_at: datetime = Field(default_factory=datetime.utcnow, description="Date de détection")
    
#     model_config = ConfigDict(
#         protected_namespaces=(),  # AJOUTE CETTE LIGNE
#         json_schema_extra={
#             "example": {
#                 "transaction_id": "txn_test_001",
#                 "detection_id": "det_20251114_001",
#                 "is_fraud": True,
#                 "fraud_probability": 0.87,
#                 "risk_level": "high",
#                 "fraud_types": ["unusual_amount", "suspicious_location"],
#                 "confidence_score": 0.92,
#                 "explanation": {
#                     "top_features": {
#                         "amount": 0.45,
#                         "transaction_velocity": 0.32,
#                         "location_risk": 0.18
#                     },
#                     "fraud_indicators": [
#                         "Montant 5x supérieur à la moyenne du client",
#                         "Localisation jamais utilisée auparavant"
#                     ],
#                     "risk_factors": {
#                         "amount_zscore": 4.2,
#                         "velocity_24h": 12,
#                         "new_location": True
#                     },
#                     "ml_confidence": 0.92

#                 },
#                 "recommendation": "Bloquer la transaction et contacter le client",
#                 "should_block": True,
#                 "processing_time_ms": 45.8,
#                 "ml_model_version": "v1.0.0",
#                 "detected_at": "2025-11-14T08:00:00.123Z"
#             }
#         }
#     )

# class DetectionResponse(BaseModel):
#     """Schéma pour la réponse de détection de fraude"""
    
#     transaction_id: str = Field(..., description="ID de la transaction analysée")
#     is_fraud: bool = Field(..., description="Verdict: fraude ou légitime")
#     fraud_probability: float = Field(..., ge=0.0, le=1.0, description="Probabilité de fraude (0-1)")
#     risk_level: str = Field(..., description="Niveau de risque: low, medium, high, critical")
#     confidence_score: float = Field(..., ge=0.0, le=1.0, description="Score de confiance")
#     recommendation: str = Field(..., description="Action recommandée")
#     should_block: bool = Field(..., description="Indique si la transaction doit être bloquée")
#     processing_time_ms: float = Field(..., description="Temps de traitement en millisecondes")
    
#     # CORRECTION : Renommer les champs qui causent le conflit
#     ml_model_version: str = Field(..., description="Version du modèle utilisé")  # Avant: model_version
#     ml_confidence: float = Field(..., ge=0.0, le=1.0, description="Confiance du modèle")  # Avant: model_confidence
    
#     detected_at: datetime = Field(default_factory=datetime.utcnow, description="Date de détection")
    
#     # Champs optionnels pour compatibilité
#     fraud_types: List[str] = Field(default=[], description="Types de fraude détectés")
#     explanation: Optional[FraudExplanation] = Field(None, description="Explication détaillée")
    
#     model_config = ConfigDict(
#         protected_namespaces=(),  # CORRECTION : Désactiver la protection des namespaces
#         json_schema_extra={
#             "example": {
#                 "transaction_id": "txn_test_001",
#                 "is_fraud": True,
#                 "fraud_probability": 0.87,
#                 "risk_level": "high",
#                 "confidence_score": 0.92,
#                 "recommendation": "Bloquer la transaction et contacter le client",
#                 "should_block": True,
#                 "processing_time_ms": 45.8,
#                 "ml_model_version": "v1.0.0",
#                 "ml_confidence": 0.95,
#                 "detected_at": "2025-11-14T08:00:00.123Z",
#                 "fraud_types": ["unusual_amount", "suspicious_location"]
#             }
#         }
#     )



# class BatchDetectionRequest(BaseModel):
#     """Requête pour détecter plusieurs transactions en batch"""
#     transactions: List[DetectionRequest] = Field(..., min_length=1, max_length=1000)
    
#     model_config = ConfigDict(
#         protected_namespaces=(),  # AJOUTE CETTE LIGNE
#         json_schema_extra={
#             "example": {
#                 "transactions": [
#                     {
#                         "transaction_id": "txn_001",
#                         "amount": 50000.0,
#                         "currency": "XOF",
#                         "customer_id": "cust_123"
#                     },
#                     {
#                         "transaction_id": "txn_002",
#                         "amount": 150000.0,
#                         "currency": "XOF",
#                         "customer_id": "cust_456"
#                     }
#                 ]
#             }
#         }
#     )


# class BatchDetectionResponse(BaseModel):
#     """Réponse pour la détection en batch"""
#     results: List[DetectionResult] = Field(..., description="Résultats pour chaque transaction")
#     total_processed: int = Field(..., description="Nombre de transactions traitées")
#     total_fraud: int = Field(..., description="Nombre de fraudes détectées")
#     fraud_rate: float = Field(..., description="Taux de fraude en %")
#     total_processing_time_ms: float = Field(..., description="Temps total de traitement")
    
#     model_config = ConfigDict(
#         protected_namespaces=(),  # AJOUTE CETTE LIGNE
#         json_schema_extra={
#             "example": {
#                 "results": [
#                     {
#                         "transaction_id": "txn_001",
#                         "is_fraud": False,
#                         "fraud_probability": 0.12
#                     },
#                     {
#                         "transaction_id": "txn_002",
#                         "is_fraud": True,
#                         "fraud_probability": 0.89
#                     }
#                 ],
#                 "total_processed": 2,
#                 "total_fraud": 1,
#                 "fraud_rate": 50.0,
#                 "total_processing_time_ms": 89.5
#             }
#         }
#     )


# class AlertResponse(BaseModel):
#     """Schéma pour une alerte de fraude"""
#     alert_id: str = Field(..., description="ID unique de l'alerte")
#     transaction_id: str = Field(..., description="ID de la transaction concernée")
#     severity: str = Field(..., description="Sévérité: low, medium, high, critical")
#     fraud_type: str = Field(..., description="Type de fraude")
#     title: str = Field(..., description="Titre de l'alerte")
#     description: Optional[str] = Field(None, description="Description détaillée")
#     confidence_score: float = Field(..., ge=0.0, le=1.0, description="Score de confiance")
#     is_resolved: bool = Field(False, description="Indique si l'alerte est résolue")
#     created_at: datetime = Field(..., description="Date de création")
    
#     model_config = ConfigDict(
#         protected_namespaces=(),  # AJOUTE CETTE LIGNE
#         from_attributes=True,
#         json_schema_extra={
#             "example": {
#                 "alert_id": "alert_001",
#                 "transaction_id": "txn_test_001",
#                 "severity": "high",
#                 "fraud_type": "unusual_amount",
#                 "title": "Montant Transaction Suspect",
#                 "description": "Transaction de 500,000 XOF détectée, 5x supérieur à la moyenne",
#                 "confidence_score": 0.87,
#                 "is_resolved": False,
#                 "created_at": "2025-11-14T08:00:00Z"
#             }
#         }
#     )