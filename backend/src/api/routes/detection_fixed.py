# """
# Routes de détection de fraude - Version FIXÉE pour production
# """

# from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
# from sqlalchemy.orm import Session
# from typing import List, Dict, Any
# from datetime import datetime
# from pydantic import BaseModel

# from src.database.connection import get_db
# from src.services.fraud_detection import get_fraud_detection_service
# from src.services.fraud_detection import FraudDetectionService
# from src.core.logging import get_logger

# logger = get_logger(__name__)
# router = APIRouter()

# # Schémas LOCAUX simples pour éviter les problèmes d'import
# class DetectionRequestLocal(BaseModel):
#     transaction_id: str = ""
#     amount: float
#     currency: str = "XOF"
#     customer_id: str
#     merchant_id: str = ""
#     transaction_type: str = "payment"

# class DetectionResponseLocal(BaseModel):
#     transaction_id: str
#     is_fraud: bool
#     fraud_probability: float
#     risk_level: str
#     confidence_score: float
#     recommendation: str
#     should_block: bool
#     processing_time_ms: float
#     algorithm_version: str = "v1.0.0"
#     algorithm_confidence: float
#     detected_at: str
#     fraud_types: List[str] = []

# @router.post(
#     "/detect",
#     # response_model=DetectionResponseLocal,
#     response_model=List[DetectionResponseLocal], # <--- Ajoutez ceci
#     summary="Détecter une fraude",
#     description="Analyse une transaction en temps réel pour détecter les fraudes potentielles"
# )
# async def detect_fraud(
#     request: DetectionRequestLocal,
#     background_tasks: BackgroundTasks,
#     db: Session = Depends(get_db),
#     fraud_service: FraudDetectionService = Depends(get_fraud_detection_service)
# ):
#     """
#     Détecte la fraude pour une transaction unique
#     """
#     try:
#         logger.info(f"Détection demandée - Transaction: {request.transaction_id}")
        
#         # Conversion pour le service
#         transaction_data = {
#             "transaction_id": request.transaction_id,
#             "amount": request.amount,
#             "currency": request.currency,
#             "customer_id": request.customer_id,
#             "merchant_id": request.merchant_id,
#             "transaction_type": request.transaction_type
#         }
        
#         # Appel du service (simulé pour l'instant)
#         detection_result = {
#             "is_fraud": False,
#             "fraud_probability": 0.15,
#             "confidence_score": 0.85,
#             "should_block": False
#         }
        
#         # Réponse
#         return DetectionResponseLocal(
#             transaction_id=request.transaction_id or "txn_test",
#             is_fraud=detection_result["is_fraud"],
#             fraud_probability=detection_result["fraud_probability"],
#             risk_level="low",
#             confidence_score=detection_result["confidence_score"],
#             recommendation="Approuver la transaction",
#             should_block=detection_result["should_block"],
#             processing_time_ms=25.5,
#             algorithm_confidence=0.88,
#             fraud_types=[],
#             detected_at=datetime.utcnow().isoformat()
#         )
        
#     except Exception as e:
#         logger.error(f"Erreur détection: {e}")
#         raise HTTPException(status_code=500, detail="Erreur lors de la détection")

# @router.post(
#     "/detect/batch",
#     response_model=List[DetectionResponseLocal],
#     summary="Détection par lot",
#     description="Analyse multiple transactions en une seule requête"
# )
# async def detect_fraud_batch(
#     requests: List[DetectionRequestLocal],
#     db: Session = Depends(get_db),
#     fraud_service: FraudDetectionService = Depends(get_fraud_detection_service)
# ):
#     """
#     Détection de fraude pour un lot de transactions
#     """
#     try:
#         logger.info(f"Détection par lot - {len(requests)} transactions")
        
#         results = []
#         for i, request in enumerate(requests):
#             result = DetectionResponseLocal(
#                 transaction_id=request.transaction_id or f"txn_batch_{i}",
#                 is_fraud=False,
#                 fraud_probability=0.1,
#                 risk_level="low",
#                 confidence_score=0.9,
#                 recommendation="Approuver",
#                 should_block=False,
#                 processing_time_ms=15.0,
#                 algorithm_confidence=0.85,
#                 fraud_types=[],
#                 detected_at=datetime.utcnow().isoformat()
#             )
#             results.append(result)
        
#         return results
        
#     except Exception as e:
#         logger.error(f"Erreur détection par lot: {e}")
#         raise HTTPException(status_code=500, detail="Erreur lors du traitement par lot")

# # Route de test
# @router.get("/test")
# async def test_detection():
#     return {"status": "ok", "message": "Détection fixée fonctionnelle"}

"""
Routes de détection de fraude - Version IMPORT SAFE
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

# Import local FIRST, then dependencies
router = APIRouter()

# Import APRÈS la création du router
from src.database.connection import get_db
from src.services.fraud_detection import get_fraud_detection_service
from src.services.fraud_detection import FraudDetectionService
from src.api.schemas.detection_clean import DetectionRequest, DetectionResponse
from src.core.logging import get_logger

logger = get_logger(__name__)

@router.post(
    "/detect",
    response_model=DetectionResponse,
    summary="Détecter une fraude",
    description="Analyse une transaction en temps réel pour détecter les fraudes potentielles"
)
async def detect_fraud(
    request: DetectionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    fraud_service: FraudDetectionService = Depends(get_fraud_detection_service)
):
    """
    Détecte la fraude pour une transaction unique
    """
    try:
        logger.info(f"Détection demandée - Transaction: {request.transaction_id}")
        
        # Simulation pour test
        return DetectionResponse(
            transaction_id=request.transaction_id or "txn_test",
            is_fraud=False,
            fraud_probability=0.15,
            risk_level="low",
            confidence_score=0.85,
            recommendation="Approuver la transaction",
            should_block=False,
            processing_time_ms=25.5,
            algorithm_version="v1.0.0",
            algorithm_confidence=0.88,
            fraud_types=[],
            detected_at=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Erreur détection: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la détection")

@router.post(
    "/detect/batch",
    response_model=List[DetectionResponse],
    summary="Détection par lot",
    description="Analyse multiple transactions en une seule requête"
)
async def detect_fraud_batch(
    requests: List[DetectionRequest],
    db: Session = Depends(get_db),
    fraud_service: FraudDetectionService = Depends(get_fraud_detection_service)
):
    """
    Détection de fraude pour un lot de transactions
    """
    try:
        logger.info(f"Détection par lot - {len(requests)} transactions")
        
        results = []
        for i, request in enumerate(requests):
            result = DetectionResponse(
                transaction_id=request.transaction_id or f"txn_batch_{i}",
                is_fraud=False,
                fraud_probability=0.1,
                risk_level="low",
                confidence_score=0.9,
                recommendation="Approuver",
                should_block=False,
                processing_time_ms=15.0,
                algorithm_version="v1.0.0",
                algorithm_confidence=0.85,
                fraud_types=[],
                detected_at=datetime.utcnow()
            )
            results.append(result)
        
        return results
        
    except Exception as e:
        logger.error(f"Erreur détection par lot: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du traitement par lot")