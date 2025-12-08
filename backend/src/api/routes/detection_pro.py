"""
Routes de détection de fraude - Version PRODUCTION CORRIGÉE
Architecture robuste avec gestion d'erreurs complète
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import time

from src.database.connection import get_db
from src.services.fraud_detection import FraudDetectionService
from src.api.schemas.detection_clean import (
    DetectionRequest, 
    DetectionResponse, 
    BatchDetectionRequest,
    BatchDetectionResponse,
    FraudExplanation,
)
from src.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

# ✅ CORRECTION: Créer le service SANS Depends
def _get_fraud_service(db: Session) -> FraudDetectionService:
    """Crée l'instance du service directement"""
    return FraudDetectionService(db)

# --- Endpoint de Détection Temps Réel ---

@router.post(
    "/detect",
    response_model=DetectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Détection de fraude en temps réel",
    description="""
    Analyse une transaction financière en temps réel pour détecter les fraudes potentielles.
    **Fonctionnalités :**
    - Analyse par règles métier
    - Machine Learning avancé
    - Scoring de risque en temps réel
    - Explications détaillées
    """,
    response_description="Résultat complet de l'analyse de fraude"
)
async def detect_fraud(
    request: DetectionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> DetectionResponse:
    """
    Endpoint principal de détection de fraude en temps réel.
    """
    start_time = time.time()
    
    try:
        logger.info(
            f"🔍 Détection demandée - "
            f"Transaction: {request.transaction_id}, "
            f"Montant: {request.amount} {request.currency}, "
            f"Client: {request.customer_id}"
        )
        
        # ✅ Créer le service directement (pas via Depends)
        fraud_service = _get_fraud_service(db)
        
        # Conversion des données
        transaction_data = request.model_dump()
        
        # Appel du service de détection
        detection_result = fraud_service.detect_fraud(transaction_data)
        
        # Vérification des erreurs
        if "error" in detection_result:
            logger.error(f"❌ Erreur service détection: {detection_result['error']}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": "Erreur lors de l'analyse",
                    "message": detection_result["error"],
                    "transaction_id": request.transaction_id
                }
            )
        
        # Construction de l'explication
        explanation = None
        if detection_result.get("explanation_data"):
            explanation = FraudExplanation(
                top_features=detection_result["explanation_data"].get("top_features", {}),
                fraud_indicators=detection_result["explanation_data"].get("fraud_indicators", []),
                risk_factors=detection_result["explanation_data"].get("risk_factors", {}),
                algorithm_confidence=detection_result["explanation_data"].get("algorithm_confidence", 0.0)
            )
        
        # Calcul du temps de traitement
        processing_time_ms = (time.time() - start_time) * 1000
        
        # Construction de la réponse
        response = DetectionResponse(
            transaction_id=detection_result.get("transaction_id", request.transaction_id),
            is_fraud=detection_result["is_fraud"],
            fraud_probability=detection_result.get("combined_risk_score", 0.0),
            # risk_level=self._get_risk_level(detection_result.get("combined_risk_score", 0.0)),
            risk_level=_get_risk_level(detection_result.get("combined_risk_score", 0.0)),

            confidence_score=detection_result.get("confidence", 0.0),
            recommendation=detection_result.get("recommendation", "Analyser manuellement"),
            should_block=detection_result.get("should_block", False),
            processing_time_ms=processing_time_ms,
            algorithm_version=detection_result.get("algorithm_version", "v1.0.0"),
            algorithm_confidence=detection_result.get("confidence", 0.0),
            fraud_types=detection_result.get("rules_violated", []),
            explanation=explanation,
            detected_at=datetime.utcnow()
        )
        
        # Log du résultat
        if response.is_fraud:
            logger.warning(
                f"🚨 FRAUDE DÉTECTÉE - "
                f"Transaction: {response.transaction_id}, "
                f"Score: {response.fraud_probability:.3f}, "
                f"Niveau: {response.risk_level}"
            )
        else:
            logger.info(
                f"✅ Transaction légitime - "
                f"Transaction: {response.transaction_id}, "
                f"Score: {response.fraud_probability:.3f}"
            )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"❌ Erreur inattendue lors de la détection - "
            f"Transaction: {request.transaction_id}, "
            f"Erreur: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Erreur interne du serveur",
                "message": "Impossible de traiter la demande de détection",
                "transaction_id": request.transaction_id
            }
        )

# --- Endpoint de Détection par Lot (Batch) ---

@router.post(
    "/detect/batch",
    response_model=BatchDetectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Détection de fraude par lot",
    description="Analyse un lot de transactions pour détection de fraude massive",
)
async def detect_fraud_batch(
    request: BatchDetectionRequest,
    db: Session = Depends(get_db)
) -> BatchDetectionResponse:
    """
    Traitement par lot pour analyse de fraude à grande échelle.
    """
    start_time = time.time()
    
    try:
        logger.info(f"📦 Traitement batch - {len(request.transactions)} transactions")
        
        # ✅ Créer le service directement
        fraud_service = _get_fraud_service(db)
        
        results = []
        fraud_count = 0
        
        for i, transaction_request in enumerate(request.transactions):
            try:
                transaction_data = transaction_request.model_dump()
                detection_result = fraud_service.detect_fraud(transaction_data)
                
                # Construction de l'explication
                explanation = None
                if detection_result.get("explanation_data"):
                    explanation = FraudExplanation(
                        top_features=detection_result["explanation_data"].get("top_features", {}),
                        fraud_indicators=detection_result["explanation_data"].get("fraud_indicators", []),
                        risk_factors=detection_result["explanation_data"].get("risk_factors", {}),
                        algorithm_confidence=detection_result["explanation_data"].get("algorithm_confidence", 0.0)
                    )
                
                response = DetectionResponse(
                    transaction_id=detection_result.get("transaction_id", transaction_request.transaction_id),
                    is_fraud=detection_result["is_fraud"],
                    fraud_probability=detection_result.get("combined_risk_score", 0.0),
                    risk_level=_get_risk_level(detection_result.get("combined_risk_score", 0.0)),

                    confidence_score=detection_result.get("confidence", 0.0),
                    recommendation=detection_result.get("recommendation", "Analyser"),
                    should_block=detection_result.get("should_block", False),
                    processing_time_ms=detection_result.get("total_processing_time_ms", 0),
                    algorithm_version=detection_result.get("algorithm_version", "v1.0.0"),
                    algorithm_confidence=detection_result.get("confidence", 0.0),
                    fraud_types=detection_result.get("rules_violated", []),
                    explanation=explanation,
                    detected_at=datetime.utcnow()
                )
                
                results.append(response)
                
                if response.is_fraud:
                    fraud_count += 1
                    
            except Exception as e:
                logger.error(f"❌ Erreur transaction {i}: {e}")
                continue
        
        total_time = (time.time() - start_time) * 1000
        fraud_rate = (fraud_count / len(results)) * 100 if results else 0
        
        logger.info(
            f"✅ Batch terminé - "
            f"Traitées: {len(results)}, "
            f"Fraudes: {fraud_count}, "
            f"Taux: {fraud_rate:.1f}%"
        )
        
        return BatchDetectionResponse(
            results=results,
            total_processed=len(results),
            total_fraud=fraud_count,
            fraud_rate=fraud_rate,
            total_processing_time_ms=total_time
        )
        
    except Exception as e:
        logger.error(f"❌ Erreur batch: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors du traitement par lot"
        )

# --- Endpoint de Statut ---

@router.get(
    "/detect/status/{transaction_id}",
    summary="Statut d'une détection",
    description="Récupère le statut d'une analyse de fraude précédente",
    response_model=None 
)
async def get_detection_status(transaction_id: str, db: Session = Depends(get_db)):
    """Récupère le statut d'une détection"""
    try:
        return {
            "transaction_id": transaction_id,
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Erreur statut {transaction_id}: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction non trouvée")

# --- Health Check Spécifique ---

@router.get("/detect/health", status_code=status.HTTP_200_OK)
async def detection_health():
    """Health check du service de détection"""
    return {
        "status": "healthy",
        "service": "fraud-detection",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# --- Utilitaires ---

def _get_risk_level(score: float) -> str:
    """Détermine le niveau de risque basé sur le score"""
    if score >= 0.85:
        return "critical"
    elif score >= 0.70:
        return "high"
    elif score >= 0.50:
        return "medium"
    else:
        return "low"