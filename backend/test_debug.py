#!/usr/bin/env python3
"""
Script de débogage pour isoler l'erreur FastAPI
"""

import sys
import os

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Test d'import simple
    from src.api.schemas.detection_clean import DetectionResponse
    print(" Import DetectionResponse réussi")
    
    # Test de création d'instance
    test_instance = DetectionResponse(
        transaction_id="test_123",
        is_fraud=False,
        fraud_probability=0.1,
        risk_level="low",
        confidence_score=0.9,
        recommendation="Approuver",
        should_block=False,
        processing_time_ms=10.0,
        algorithm_version="v1.0.0",
        algorithm_confidence=0.9,
        detected_at="2024-01-01T00:00:00Z",
        fraud_types=[]
    )
    print(" Création instance DetectionResponse réussi")
    
except Exception as e:
    print(f" Erreur: {e}")
    print(f" Type d'erreur: {type(e)}")
    import traceback
    traceback.print_exc()