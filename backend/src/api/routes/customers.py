# backend/src/api/routes/customers.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import datetime, timedelta
from typing import List, Dict, Any

from src.database.connection import get_db
from src.database.models import Transaction

router = APIRouter()

@router.get("/", summary="Liste des clients")
async def list_customers(
    limit: int = Query(50, ge=1, le=500, description="Nombre maximum de clients"),
    min_transactions: int = Query(1, ge=1, description="Nombre minimum de transactions"),
    db: Session = Depends(get_db)
):
    """Retourne la liste des clients avec leurs statistiques"""
    
    try:
        # Récupérer les clients distincts avec leurs stats
        customer_stats = db.query(
            Transaction.customer_id,
            func.count(Transaction.id).label('transaction_count'),
            func.max(Transaction.timestamp).label('last_transaction'),
            func.avg(Transaction.amount).label('avg_amount'),
            func.sum(case((Transaction.is_fraud == True, 1), else_=0)).label('fraud_count')
        ).group_by(Transaction.customer_id)\
         .having(func.count(Transaction.id) >= min_transactions)\
         .order_by(func.max(Transaction.timestamp).desc())\
         .limit(limit).all()
        
        if not customer_stats:
            return []
        
        return [
            {
                "customer_id": stat.customer_id,
                "transaction_count": stat.transaction_count,
                "last_transaction": stat.last_transaction.isoformat() if stat.last_transaction else None,
                "avg_amount": float(stat.avg_amount) if stat.avg_amount else 0.0,
                "fraud_count": stat.fraud_count or 0,
                "fraud_rate": (stat.fraud_count / stat.transaction_count * 100) if stat.fraud_count else 0.0
            }
            for stat in customer_stats
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des clients: {str(e)}"
        )


@router.get("/{customer_id}/stats", summary="Statistiques d'un client")
async def get_customer_stats(
    customer_id: str,
    days: int = Query(90, ge=1, le=365, description="Période en jours"),
    db: Session = Depends(get_db)
):
    """Retourne les statistiques détaillées d'un client"""
    
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Récupérer les transactions du client
        transactions = db.query(Transaction).filter(
            Transaction.customer_id == customer_id,
            Transaction.timestamp >= start_date,
            Transaction.timestamp <= end_date
        ).order_by(Transaction.timestamp.desc()).all()
        
        if not transactions:
            raise HTTPException(
                status_code=404, 
                detail=f"Client non trouvé ou aucune transaction sur les {days} derniers jours"
            )
        
        # Calculer les statistiques
        amounts = [t.amount for t in transactions]
        fraud_transactions = [t for t in transactions if t.is_fraud]
        
        # Trouver la localisation la plus fréquente
        locations = [t.location for t in transactions if t.location]
        common_location = max(set(locations), key=locations.count) if locations else "Inconnu"
        
        # Trouver le type de transaction le plus fréquent
        types = [t.transaction_type for t in transactions if t.transaction_type]
        common_type = max(set(types), key=types.count) if types else "payment"
        
        return {
            "customer_id": customer_id,
            "period_days": days,
            "transaction_count": len(transactions),
            "total_amount": sum(amounts),
            "avg_amount": sum(amounts) / len(amounts) if amounts else 0,
            "min_amount": min(amounts) if amounts else 0,
            "max_amount": max(amounts) if amounts else 0,
            "fraud_count": len(fraud_transactions),
            "fraud_rate": (len(fraud_transactions) / len(transactions)) * 100 if transactions else 0,
            "last_transaction": max(t.timestamp for t in transactions).isoformat(),
            "first_transaction": min(t.timestamp for t in transactions).isoformat(),
            "common_location": common_location,
            "common_type": common_type,
            "locations": list(set(locations)),
            "has_fraud_history": len(fraud_transactions) > 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des statistiques: {str(e)}"
        )


@router.get("/{customer_id}/transactions", summary="Transactions d'un client")
async def get_customer_transactions(
    customer_id: str,
    limit: int = Query(10, ge=1, le=100, description="Nombre de transactions"),
    db: Session = Depends(get_db)
):
    """Retourne les dernières transactions d'un client"""
    
    try:
        transactions = db.query(Transaction).filter(
            Transaction.customer_id == customer_id
        ).order_by(Transaction.timestamp.desc()).limit(limit).all()
        
        return [
            {
                "transaction_id": t.transaction_id,
                "amount": t.amount,
                "currency": t.currency,
                "location": t.location,
                "timestamp": t.timestamp.isoformat(),
                "is_fraud": t.is_fraud,
                "fraud_score": t.fraud_score
            }
            for t in transactions
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des transactions: {str(e)}"
        )