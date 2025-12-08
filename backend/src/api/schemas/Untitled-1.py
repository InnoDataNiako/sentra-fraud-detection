"""
Routes de détection de fraude
POST /detect - Détection en temps réel
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from src.database.connection import get_db
from src.services.fraud_detection import get_fraud_detection_service
from src.services.fraud_detection import FraudDetectionService
from src.api.schemas.detection_clean import DetectionRequest, DetectionResponse, FraudExplanation
from src.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()

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
        logger.info(f"🔍 Détection demandée - Transaction: {request.transaction_id}")
        
        # Conversion du schéma Pydantic en dict pour le service
        transaction_data = request.dict()
        
        # Appel du service de détection
        detection_result = fraud_service.detect_fraud(transaction_data)
        
        # Vérification s'il y a une erreur
        if "error" in detection_result:
            logger.error(f"❌ Erreur détection: {detection_result['error']}")
            raise HTTPException(
                status_code=422,
                detail=f"Erreur lors de la détection: {detection_result['error']}"
            )
        
        # Log du résultat
        fraud_probability = detection_result.get("fraud_probability", detection_result.get("combined_risk_score", 0))
        if detection_result["is_fraud"]:
            logger.warning(
                f"🚨 Fraude détectée - Transaction: {request.transaction_id}, "
                f"Probabilité: {fraud_probability:.3f}"
            )
        else:
            logger.info(
                f"✅ Transaction légitime - Transaction: {request.transaction_id}, "
                f"Probabilité: {fraud_probability:.3f}"
            )
        
        # Construction de l'explication si disponible
        explanation = None
        if any(key in detection_result for key in ["top_features", "fraud_indicators", "risk_factors"]):
            explanation = FraudExplanation(
                top_features=detection_result.get("top_features", {}),
                fraud_indicators=detection_result.get("fraud_indicators", []),
                risk_factors=detection_result.get("risk_factors", {}),
                algorithm_confidence=detection_result.get("confidence", 0.0)
            )
        
        # Conversion en réponse AVEC LES NOUVEAUX CHAMPS
        response = DetectionResponse(
            transaction_id=detection_result.get("transaction_id", request.transaction_id or f"txn_{datetime.utcnow().timestamp()}"),
            is_fraud=detection_result["is_fraud"],
            fraud_probability=detection_result.get("fraud_probability", detection_result.get("combined_risk_score", 0.0)),
            risk_level=detection_result.get("risk_level", "high" if detection_result["is_fraud"] else "low"),
            confidence_score=detection_result.get("confidence_score", detection_result.get("confidence", 0.0)),
            recommendation=detection_result.get("recommendation", "Bloquer" if detection_result["is_fraud"] else "Approuver"),
            should_block=detection_result.get("should_block", detection_result["is_fraud"]),
            processing_time_ms=detection_result.get("processing_time_ms", detection_result.get("total_processing_time_ms", 0)),
            algorithm_version=detection_result.get("algorithm_version", "v1.0.0"),
            algorithm_confidence=detection_result.get("algorithm_confidence", detection_result.get("confidence", 0.0)),
            fraud_types=detection_result.get("fraud_types", detection_result.get("rules_violated", [])),
            explanation=explanation,
            detected_at=datetime.utcnow()
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur inattendue lors de la détection: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur interne du serveur lors de la détection de fraude"
        )

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
        logger.info(f"🔍 Détection par lot - {len(requests)} transactions")
        
        results = []
        for request in requests:
            transaction_data = request.dict()
            detection_result = fraud_service.detect_fraud(transaction_data)
            
            # Construction de l'explication si disponible
            explanation = None
            if any(key in detection_result for key in ["top_features", "fraud_indicators", "risk_factors"]):
                explanation = FraudExplanation(
                    top_features=detection_result.get("top_features", {}),
                    fraud_indicators=detection_result.get("fraud_indicators", []),
                    risk_factors=detection_result.get("risk_factors", {}),
                    algorithm_confidence=detection_result.get("confidence", 0.0)
                )
            
            # Création de la réponse avec les NOUVEAUX CHAMPS
            response = DetectionResponse(
                transaction_id=detection_result.get("transaction_id", request.transaction_id or f"txn_{datetime.utcnow().timestamp()}"),
                is_fraud=detection_result["is_fraud"],
                fraud_probability=detection_result.get("fraud_probability", detection_result.get("combined_risk_score", 0.0)),
                risk_level=detection_result.get("risk_level", "high" if detection_result["is_fraud"] else "low"),
                confidence_score=detection_result.get("confidence_score", detection_result.get("confidence", 0.0)),
                recommendation=detection_result.get("recommendation", "Bloquer" if detection_result["is_fraud"] else "Approuver"),
                should_block=detection_result.get("should_block", detection_result["is_fraud"]),
                processing_time_ms=detection_result.get("processing_time_ms", detection_result.get("total_processing_time_ms", 0)),
                algorithm_version=detection_result.get("algorithm_version", "v1.0.0"),
                algorithm_confidence=detection_result.get("algorithm_confidence", detection_result.get("confidence", 0.0)),
                fraud_types=detection_result.get("fraud_types", detection_result.get("rules_violated", [])),
                explanation=explanation,
                detected_at=datetime.utcnow()
            )
            results.append(response)
        
        fraud_count = sum(1 for r in results if r.is_fraud)
        logger.info(f" Lot traité - Fraudes: {fraud_count}/{len(results)}")
        
        return results
        
    except Exception as e:
        logger.error(f"Erreur détection par lot: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors du traitement par lot"
        )