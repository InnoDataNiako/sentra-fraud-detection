"""
Export des modèles ML
"""

from .random_forest import FraudRandomForest
from .isolation_forest import FraudIsolationForest

__all__ = [
    'FraudRandomForest',
    'FraudIsolationForest'
]