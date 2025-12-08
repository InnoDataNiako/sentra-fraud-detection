"""
Import des schémas Pydantic
"""

from .common import (
    HealthCheck,
    ErrorResponse, 
    SuccessResponse,
    PaginationParams,
    PaginatedResponse,
    Statistics
)

# APRÈS :
from .detection_clean import (
    DetectionRequest,
    DetectionResponse, 
    DetectionResult,
    FraudExplanation,
    BatchDetectionRequest,
    BatchDetectionResponse,
    AlertResponse
)
from .transaction import (
    TransactionBase,
    TransactionCreate,
    TransactionResponse,
    TransactionUpdate, 
    TransactionListResponse,
    TransactionStats,
    TransactionAnalysis,
    TransactionStatus
)

__all__ = [
    # Common
    "HealthCheck",
    "ErrorResponse",
    "SuccessResponse", 
    "PaginationParams",
    "PaginatedResponse",
    "Statistics",
    
    # Detection
    "DetectionRequest",
    "DetectionResponse",
    "DetectionResult", 
    "FraudExplanation",
    "BatchDetectionRequest",
    "BatchDetectionResponse",
    "AlertResponse",
    
    # Transaction
    "TransactionBase",
    "TransactionCreate",
    "TransactionResponse",
    "TransactionUpdate",
    "TransactionListResponse", 
    "TransactionStats",
    "TransactionAnalysis",
    "TransactionStatus"
]