"""
Export des modules d'inference
"""

from .predictor import FraudPredictor
from .ensemble import EnsemblePredictor

__all__ = [
    'FraudPredictor',
    'EnsemblePredictor'
]