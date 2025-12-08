"""
API FastAPI ultra-minimaliste pour test
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from datetime import datetime

app = FastAPI(title="SÉNTRA Clean Test", version="1.0.0")

# Schémas DIRECTEMENT dans le fichier
class DetectionRequest(BaseModel):
    amount: float
    customer_id: str

class DetectionResponse(BaseModel):
    transaction_id: str
    is_fraud: bool
    fraud_probability: float

@app.post("/detect", response_model=DetectionResponse)
async def detect_fraud(request: DetectionRequest):
    """Endpoint de test ultra-simple"""
    return DetectionResponse(
        transaction_id="test_123",
        is_fraud=False,
        fraud_probability=0.15
    )

@app.post("/detect/batch", response_model=List[DetectionResponse])
async def detect_batch(requests: List[DetectionRequest]):
    """Batch ultra-simple"""
    return [
        DetectionResponse(
            transaction_id=f"txn_{i}",
            is_fraud=i % 5 == 0,  # 20% de fraude simulée
            fraud_probability=i * 0.1
        )
        for i in range(len(requests))
    ]

@app.get("/")
async def root():
    return {"message": "API Clean Test OK", "timestamp": datetime.utcnow().isoformat()}

@app.get("/health")
async def health():
    return {"status": "healthy"}