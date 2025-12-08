# """
# Routes pour les statistiques et analytics
# Optimisé pour 10k+ transactions - Requêtes SQL directes pour performance
# """

# from fastapi import APIRouter, Depends, HTTPException, Query
# from sqlalchemy.orm import Session
# from sqlalchemy import func, and_, case, text, extract
# from typing import Dict, List, Any
# from datetime import datetime, timedelta, date
# import asyncio  # ⬅️ AJOUTEZ CETTE LIGNE
# import logging

# from src.database.connection import get_db
# from src.database.models import Transaction
# from src.core.logging import get_logger

# logger = get_logger(__name__)

# router = APIRouter(tags=["Statistiques"])  # ⬅️ Pas de prefix ici


# # ============================================================================
# # 1. STATISTIQUES GLOBALES (Optimisées pour 10k+ transactions)
# # ============================================================================

# @router.get(
#     "/summary",
#     summary="Statistiques globales optimisées",
#     description="KPIs calculés en une seule requête SQL pour 10k+ transactions"
# )
# async def get_global_stats(
#     db: Session = Depends(get_db)
# ):
#     """
#     Toutes les statistiques en UNE requête SQL optimisée
#     """
#     try:
#         #  REQUÊTE UNIQUE OPTIMISÉE POUR 10K+ TRANSACTIONS
#         query = text("""
#             SELECT 
#                 -- Totaux
#                 COUNT(*) as total_transactions,
#                 SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) as fraud_count,
                
#                 -- Montants
#                 COALESCE(SUM(amount), 0) as total_amount,
#                 COALESCE(AVG(amount), 0) as avg_amount,
#                 COALESCE(MIN(amount), 0) as min_amount,
#                 COALESCE(MAX(amount), 0) as max_amount,
                
#                 -- Scores
#                 COALESCE(AVG(fraud_score) * 100, 0) as avg_fraud_score,
                
#                 -- Dernières 24h
#                 SUM(CASE WHEN created_at >= NOW() - INTERVAL '24 hours' THEN 1 ELSE 0 END) as last_24h_count,
#                 SUM(CASE WHEN created_at >= NOW() - INTERVAL '24 hours' AND is_fraud THEN 1 ELSE 0 END) as last_24h_fraud,
                
#                 -- Distribution des montants
#                 SUM(CASE WHEN amount < 50000 THEN 1 ELSE 0 END) as amount_0_50k,
#                 SUM(CASE WHEN amount BETWEEN 50000 AND 100000 THEN 1 ELSE 0 END) as amount_50_100k,
#                 SUM(CASE WHEN amount BETWEEN 100000 AND 250000 THEN 1 ELSE 0 END) as amount_100_250k,
#                 SUM(CASE WHEN amount BETWEEN 250000 AND 500000 THEN 1 ELSE 0 END) as amount_250_500k,
#                 SUM(CASE WHEN amount >= 500000 THEN 1 ELSE 0 END) as amount_500k_plus,
                
#                 -- Distribution fraudes par montant
#                 SUM(CASE WHEN amount < 50000 AND is_fraud THEN 1 ELSE 0 END) as fraud_0_50k,
#                 SUM(CASE WHEN amount BETWEEN 50000 AND 100000 AND is_fraud THEN 1 ELSE 0 END) as fraud_50_100k,
#                 SUM(CASE WHEN amount BETWEEN 100000 AND 250000 AND is_fraud THEN 1 ELSE 0 END) as fraud_100_250k,
#                 SUM(CASE WHEN amount BETWEEN 250000 AND 500000 AND is_fraud THEN 1 ELSE 0 END) as fraud_250_500k,
#                 SUM(CASE WHEN amount >= 500000 AND is_fraud THEN 1 ELSE 0 END) as fraud_500k_plus
#             FROM transactions
#         """)
        
#         result = db.execute(query).first()
        
#         # 🔥 CALCUL DES POURCENTAGES (évite de refaire des requêtes)
#         total = result.total_transactions or 0
#         fraud_count = result.fraud_count or 0
#         fraud_rate = (fraud_count / total * 100) if total > 0 else 0
        
#         # Distribution des montants pour graphiques
#         amount_distribution = [
#             {"range": "0-50k", "count": result.amount_0_50k or 0, "fraud_count": result.fraud_0_50k or 0},
#             {"range": "50-100k", "count": result.amount_50_100k or 0, "fraud_count": result.fraud_50_100k or 0},
#             {"range": "100-250k", "count": result.amount_100_250k or 0, "fraud_count": result.fraud_100_250k or 0},
#             {"range": "250-500k", "count": result.amount_250_500k or 0, "fraud_count": result.fraud_250_500k or 0},
#             {"range": "500k+", "count": result.amount_500k_plus or 0, "fraud_count": result.fraud_500k_plus or 0},
#         ]
        
#         return {
#             "summary": {
#                 "total_transactions": total,
#                 "fraud_transactions": fraud_count,
#                 "fraud_rate": round(fraud_rate, 2),
#                 "total_amount": float(result.total_amount or 0),
#                 "avg_amount": float(result.avg_amount or 0),
#                 "min_amount": float(result.min_amount or 0),
#                 "max_amount": float(result.max_amount or 0),
#                 "avg_fraud_score": float(result.avg_fraud_score or 0),
#                 "last_24h": {
#                     "transactions": result.last_24h_count or 0,
#                     "frauds": result.last_24h_fraud or 0,
#                     "fraud_rate": (result.last_24h_fraud / result.last_24h_count * 100) if result.last_24h_count > 0 else 0
#                 }
#             },
#             "amount_distribution": amount_distribution,
#             "timestamp": datetime.now().isoformat()
#         }
        
#     except Exception as e:
#         logger.error(f"❌ Erreur statistiques globales: {e}", exc_info=True)
#         raise HTTPException(
#             status_code=500,
#             detail=f"Erreur lors du calcul des statistiques: {str(e)}"
#         )


# # ============================================================================
# # 2. TENDANCES QUOTIDIENNES (Optimisé)
# # ============================================================================

# @router.get(
#     "/trend/daily",
#     summary="Tendances quotidiennes",
#     description="Données groupées par jour - Optimisé avec index sur created_at"
# )
# async def get_daily_trend(
#     days: int = Query(30, ge=1, le=90, description="Nombre de jours (max 90 pour performance)"),
#     db: Session = Depends(get_db)
# ):
#     """
#     Tendances par jour - Utilise des dates pour éviter les calculs coûteux
#     """
#     try:
#         # 🔥 REQUÊTE OPTIMISÉE AVEC INDEX
#         query = text("""
#             SELECT 
#                 DATE(created_at) as date,
#                 COUNT(*) as total,
#                 SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) as fraud,
#                 AVG(fraud_score) * 100 as avg_score,
#                 SUM(amount) as total_amount
#             FROM transactions
#             WHERE created_at >= CURRENT_DATE - INTERVAL ':days days'
#             GROUP BY DATE(created_at)
#             ORDER BY date
#         """)
        
#         result = db.execute(query, {"days": days})
        
#         daily_data = []
#         for row in result:
#             total = row.total or 0
#             fraud = row.fraud or 0
            
#             daily_data.append({
#                 "date": row.date.isoformat(),
#                 "total": total,
#                 "fraud": fraud,
#                 "fraud_rate": round((fraud / total * 100) if total > 0 else 0, 2),
#                 "avg_fraud_score": float(row.avg_score or 0),
#                 "total_amount": float(row.total_amount or 0)
#             })
        
#         return {
#             "period_days": days,
#             "daily_data": daily_data,
#             "total_days": len(daily_data)
#         }
        
#     except Exception as e:
#         logger.error(f"❌ Erreur tendances quotidiennes: {e}", exc_info=True)
#         raise HTTPException(
#             status_code=500,
#             detail=f"Erreur tendances: {str(e)}"
#         )


# # ============================================================================
# # 3. STATISTIQUES PAR TYPE DE TRANSACTION
# # ============================================================================

# @router.get(
#     "/by-type",
#     summary="Statistiques par type",
#     description="Données groupées par type de transaction"
# )
# async def get_stats_by_type(
#     db: Session = Depends(get_db)
# ):
#     """
#     Statistiques agrégées par type de transaction
#     """
#     try:
#         query = text("""
#             SELECT 
#                 transaction_type,
#                 COUNT(*) as total,
#                 SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) as fraud,
#                 AVG(amount) as avg_amount,
#                 AVG(fraud_score) * 100 as avg_score
#             FROM transactions
#             GROUP BY transaction_type
#             ORDER BY total DESC
#         """)
        
#         result = db.execute(query)
        
#         by_type = []
#         for row in result:
#             total = row.total or 0
#             fraud = row.fraud or 0
            
#             by_type.append({
#                 "type": row.transaction_type,
#                 "total": total,
#                 "fraud": fraud,
#                 "fraud_rate": round((fraud / total * 100) if total > 0 else 0, 2),
#                 "avg_amount": float(row.avg_amount or 0),
#                 "avg_fraud_score": float(row.avg_score or 0)
#             })
        
#         return {"by_type": by_type}
        
#     except Exception as e:
#         logger.error(f"❌ Erreur stats par type: {e}")
#         raise HTTPException(
#             status_code=500,
#             detail=f"Erreur stats par type: {str(e)}"
#         )


# # ============================================================================
# # 4. DISTRIBUTION DES SCORES DE FRAUDE
# # ============================================================================

# @router.get(
#     "/score-distribution",
#     summary="Distribution des scores",
#     description="Répartition des transactions par score de fraude"
# )
# async def get_score_distribution(
#     db: Session = Depends(get_db)
# ):
#     """
#     Distribution des scores pour le graphique circulaire
#     """
#     try:
#         query = text("""
#             SELECT 
#                 CASE 
#                     WHEN fraud_score < 0.2 THEN 'Très faible'
#                     WHEN fraud_score < 0.4 THEN 'Faible'
#                     WHEN fraud_score < 0.6 THEN 'Moyen'
#                     WHEN fraud_score < 0.8 THEN 'Élevé'
#                     ELSE 'Très élevé'
#                 END as risk_level,
#                 COUNT(*) as count,
#                 AVG(fraud_score) * 100 as avg_score
#             FROM transactions
#             GROUP BY risk_level
#             ORDER BY 
#                 CASE risk_level
#                     WHEN 'Très faible' THEN 1
#                     WHEN 'Faible' THEN 2
#                     WHEN 'Moyen' THEN 3
#                     WHEN 'Élevé' THEN 4
#                     WHEN 'Très élevé' THEN 5
#                 END
#         """)
        
#         result = db.execute(query)
        
#         distribution = []
#         colors = {
#             'Très faible': '#10b981',  # vert
#             'Faible': '#22c55e',        # vert clair
#             'Moyen': '#f59e0b',         # orange
#             'Élevé': '#f97316',         # orange foncé
#             'Très élevé': '#ef4444'     # rouge
#         }
        
#         for row in result:
#             distribution.append({
#                 "level": row.risk_level,
#                 "count": row.count,
#                 "avg_score": float(row.avg_score or 0),
#                 "color": colors.get(row.risk_level, '#6b7280')
#             })
        
#         return {"distribution": distribution}
        
#     except Exception as e:
#         logger.error(f"❌ Erreur distribution scores: {e}")
#         raise HTTPException(
#             status_code=500,
#             detail=f"Erreur distribution: {str(e)}"
#         )


# # ============================================================================
# # 5. TOP CLIENTS & TRANSACTIONS
# # ============================================================================

# @router.get(
#     "/top",
#     summary="Top statistiques",
#     description="Top clients, transactions, etc."
# )
# async def get_top_stats(
#     limit: int = Query(10, ge=1, le=50, description="Nombre d'éléments"),
#     db: Session = Depends(get_db)
# ):
#     """
#     Top clients frauduleux, plus grosses transactions, etc.
#     """
#     try:
#         # Top clients avec le plus de fraudes
#         top_fraudulent_clients = db.execute(text("""
#             SELECT 
#                 customer_id,
#                 COUNT(*) as total_transactions,
#                 SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) as fraud_count,
#                 ROUND(100.0 * SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) / COUNT(*), 2) as fraud_rate
#             FROM transactions
#             GROUP BY customer_id
#             HAVING SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) > 0
#             ORDER BY fraud_count DESC
#             LIMIT :limit
#         """), {"limit": limit}).fetchall()
        
#         # Top transactions frauduleuses par montant
#         top_fraud_transactions = db.execute(text("""
#             SELECT 
#                 transaction_id,
#                 customer_id,
#                 amount,
#                 fraud_score * 100 as fraud_score_percent,
#                 created_at
#             FROM transactions
#             WHERE is_fraud = true
#             ORDER BY amount DESC
#             LIMIT :limit
#         """), {"limit": limit}).fetchall()
        
#         return {
#             "top_fraudulent_clients": [
#                 {
#                     "customer_id": row.customer_id,
#                     "total_transactions": row.total_transactions,
#                     "fraud_count": row.fraud_count,
#                     "fraud_rate": float(row.fraud_rate)
#                 }
#                 for row in top_fraudulent_clients
#             ],
#             "top_fraud_transactions": [
#                 {
#                     "transaction_id": row.transaction_id,
#                     "customer_id": row.customer_id,
#                     "amount": float(row.amount),
#                     "fraud_score": float(row.fraud_score_percent),
#                     "created_at": row.created_at.isoformat() if row.created_at else None
#                 }
#                 for row in top_fraud_transactions
#             ]
#         }
        
#     except Exception as e:
#         logger.error(f"❌ Erreur top stats: {e}")
#         raise HTTPException(
#             status_code=500,
#             detail=f"Erreur top stats: {str(e)}"
#         )


# # ============================================================================
# # 6. ENDPOINT COMPLET POUR LE FRONTEND
# # ============================================================================

# @router.get(
#     "/dashboard",
#     summary="Toutes les données dashboard",
#     description="Retourne TOUTES les données nécessaires au dashboard en un seul appel"
# )
# async def get_dashboard_data(
#     db: Session = Depends(get_db)
# ):
#     """
#     Version ULTRA-SIMPLE qui fonctionne à coup sûr
#     """
#     try:
#         # 1. Statistiques globales
#         summary_query = text("""
#             SELECT 
#                 COUNT(*) as total_transactions,
#                 SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) as fraud_count,
#                 COALESCE(SUM(amount), 0) as total_amount,
#                 COALESCE(AVG(amount), 0) as avg_amount
#             FROM transactions
#         """)
#         summary_result = db.execute(summary_query).first()
        
#         total = summary_result.total_transactions or 0
#         fraud_count = summary_result.fraud_count or 0
        
#         # Construire la réponse minimale
#         response = {
#             "summary": {
#                 "summary": {
#                     "total_transactions": total,
#                     "fraud_transactions": fraud_count,
#                     "fraud_rate": round((fraud_count / total * 100) if total > 0 else 0, 2),
#                     "total_amount": float(summary_result.total_amount or 0),
#                     "avg_amount": float(summary_result.avg_amount or 0),
#                     "min_amount": 0,
#                     "max_amount": 0,
#                     "avg_fraud_score": 0,
#                     "last_24h": {
#                         "transactions": 0,
#                         "frauds": 0,
#                         "fraud_rate": 0
#                     }
#                 },
#                 "amount_distribution": []
#             },
#             "trends": {
#                 "period_days": 30,
#                 "daily_data": [],
#                 "total_days": 0
#             },
#             "by_type": {
#                 "by_type": []
#             },
#             "score_distribution": {
#                 "distribution": []
#             },
#             "top_stats": {
#                 "top_fraudulent_clients": [],
#                 "top_fraud_transactions": []
#             },
#             "generated_at": datetime.now().isoformat(),
#             "total_transactions_in_db": total
#         }
        
#         return response
        
#     except Exception as e:
#         logger.error(f"❌ Erreur dashboard: {e}", exc_info=True)
#         raise HTTPException(
#             status_code=500,
#             detail=f"Erreur génération dashboard: {str(e)}"
#         )





"""
Routes pour les statistiques et analytics
Optimisé pour 10k+ transactions - Requêtes SQL directes pour performance
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case, text, extract
from typing import Dict, List, Any
from datetime import datetime, timedelta, date
import logging

from src.database.connection import get_db
from src.database.models import Transaction
from src.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["Statistiques"])


# ============================================================================
# 1. STATISTIQUES GLOBALES (Optimisées pour 10k+ transactions)
# ============================================================================

@router.get(
    "/summary",
    summary="Statistiques globales optimisées",
    description="KPIs calculés en une seule requête SQL pour 10k+ transactions"
)
async def get_global_stats(
    db: Session = Depends(get_db)
):
    """
    Toutes les statistiques en UNE requête SQL optimisée
    """
    try:
        # REQUÊTE UNIQUE OPTIMISÉE POUR 10K+ TRANSACTIONS
        query = text("""
            SELECT 
                -- Totaux
                COUNT(*) as total_transactions,
                SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) as fraud_count,
                
                -- Montants
                COALESCE(SUM(amount), 0) as total_amount,
                COALESCE(AVG(amount), 0) as avg_amount,
                COALESCE(MIN(amount), 0) as min_amount,
                COALESCE(MAX(amount), 0) as max_amount,
                
                -- Scores
                COALESCE(AVG(fraud_score) * 100, 0) as avg_fraud_score,
                
                -- Dernières 24h
                SUM(CASE WHEN created_at >= NOW() - INTERVAL '24 hours' THEN 1 ELSE 0 END) as last_24h_count,
                SUM(CASE WHEN created_at >= NOW() - INTERVAL '24 hours' AND is_fraud THEN 1 ELSE 0 END) as last_24h_fraud,
                
                -- Distribution des montants
                SUM(CASE WHEN amount < 50000 THEN 1 ELSE 0 END) as amount_0_50k,
                SUM(CASE WHEN amount BETWEEN 50000 AND 100000 THEN 1 ELSE 0 END) as amount_50_100k,
                SUM(CASE WHEN amount BETWEEN 100000 AND 250000 THEN 1 ELSE 0 END) as amount_100_250k,
                SUM(CASE WHEN amount BETWEEN 250000 AND 500000 THEN 1 ELSE 0 END) as amount_250_500k,
                SUM(CASE WHEN amount >= 500000 THEN 1 ELSE 0 END) as amount_500k_plus,
                
                -- Distribution fraudes par montant
                SUM(CASE WHEN amount < 50000 AND is_fraud THEN 1 ELSE 0 END) as fraud_0_50k,
                SUM(CASE WHEN amount BETWEEN 50000 AND 100000 AND is_fraud THEN 1 ELSE 0 END) as fraud_50_100k,
                SUM(CASE WHEN amount BETWEEN 100000 AND 250000 AND is_fraud THEN 1 ELSE 0 END) as fraud_100_250k,
                SUM(CASE WHEN amount BETWEEN 250000 AND 500000 AND is_fraud THEN 1 ELSE 0 END) as fraud_250_500k,
                SUM(CASE WHEN amount >= 500000 AND is_fraud THEN 1 ELSE 0 END) as fraud_500k_plus
            FROM transactions
        """)
        
        result = db.execute(query).first()
        
        # CALCUL DES POURCENTAGES
        total = result.total_transactions or 0
        fraud_count = result.fraud_count or 0
        fraud_rate = (fraud_count / total * 100) if total > 0 else 0
        
        # Distribution des montants pour graphiques
        amount_distribution = [
            {"range": "0-50k", "count": result.amount_0_50k or 0, "fraud_count": result.fraud_0_50k or 0},
            {"range": "50-100k", "count": result.amount_50_100k or 0, "fraud_count": result.fraud_50_100k or 0},
            {"range": "100-250k", "count": result.amount_100_250k or 0, "fraud_count": result.fraud_100_250k or 0},
            {"range": "250-500k", "count": result.amount_250_500k or 0, "fraud_count": result.fraud_250_500k or 0},
            {"range": "500k+", "count": result.amount_500k_plus or 0, "fraud_count": result.fraud_500k_plus or 0},
        ]
        
        return {
            "summary": {
                "total_transactions": total,
                "fraud_transactions": fraud_count,
                "fraud_rate": round(fraud_rate, 2),
                "total_amount": float(result.total_amount or 0),
                "avg_amount": float(result.avg_amount or 0),
                "min_amount": float(result.min_amount or 0),
                "max_amount": float(result.max_amount or 0),
                "avg_fraud_score": float(result.avg_fraud_score or 0),
                "last_24h": {
                    "transactions": result.last_24h_count or 0,
                    "frauds": result.last_24h_fraud or 0,
                    "fraud_rate": (result.last_24h_fraud / result.last_24h_count * 100) if result.last_24h_count > 0 else 0
                }
            },
            "amount_distribution": amount_distribution,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur statistiques globales: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du calcul des statistiques: {str(e)}"
        )


# ============================================================================
# 2. TENDANCES QUOTIDIENNES (Optimisé)
# ============================================================================

@router.get(
    "/trend/daily",
    summary="Tendances quotidiennes",
    description="Données groupées par jour - Optimisé avec index sur created_at"
)
async def get_daily_trend(
    days: int = Query(30, ge=1, le=90, description="Nombre de jours (max 90 pour performance)"),
    db: Session = Depends(get_db)
):
    """
    Tendances par jour - Utilise des dates pour éviter les calculs coûteux
    """
    try:
        # REQUÊTE OPTIMISÉE AVEC INDEX
        query = text("""
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as total,
                SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) as fraud,
                AVG(fraud_score) * 100 as avg_score,
                SUM(amount) as total_amount
            FROM transactions
            WHERE created_at >= CURRENT_DATE - INTERVAL ':days days'
            GROUP BY DATE(created_at)
            ORDER BY date
        """)
        
        result = db.execute(query, {"days": days})
        
        daily_data = []
        for row in result:
            total = row.total or 0
            fraud = row.fraud or 0
            
            daily_data.append({
                "date": row.date.isoformat(),
                "total": total,
                "fraud": fraud,
                "fraud_rate": round((fraud / total * 100) if total > 0 else 0, 2),
                "avg_fraud_score": float(row.avg_score or 0),
                "total_amount": float(row.total_amount or 0)
            })
        
        return {
            "period_days": days,
            "daily_data": daily_data,
            "total_days": len(daily_data)
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur tendances quotidiennes: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erreur tendances: {str(e)}"
        )


# ============================================================================
# 3. STATISTIQUES PAR TYPE DE TRANSACTION
# ============================================================================

@router.get(
    "/by-type",
    summary="Statistiques par type",
    description="Données groupées par type de transaction"
)
async def get_stats_by_type(
    db: Session = Depends(get_db)
):
    """
    Statistiques agrégées par type de transaction
    """
    try:
        query = text("""
            SELECT 
                transaction_type,
                COUNT(*) as total,
                SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) as fraud,
                AVG(amount) as avg_amount,
                AVG(fraud_score) * 100 as avg_score
            FROM transactions
            GROUP BY transaction_type
            ORDER BY total DESC
        """)
        
        result = db.execute(query)
        
        by_type = []
        for row in result:
            total = row.total or 0
            fraud = row.fraud or 0
            
            by_type.append({
                "type": row.transaction_type,
                "total": total,
                "fraud": fraud,
                "fraud_rate": round((fraud / total * 100) if total > 0 else 0, 2),
                "avg_amount": float(row.avg_amount or 0),
                "avg_fraud_score": float(row.avg_score or 0)
            })
        
        return {"by_type": by_type}
        
    except Exception as e:
        logger.error(f"❌ Erreur stats par type: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur stats par type: {str(e)}"
        )


# ============================================================================
# 4. DISTRIBUTION DES SCORES DE FRAUDE
# ============================================================================

# ============================================================================
# 4. DISTRIBUTION DES SCORES DE FRAUDE - VERSION CORRIGÉE
# ============================================================================

@router.get(
    "/score-distribution",
    summary="Distribution des scores",
    description="Répartition des transactions par score de fraude"
)
async def get_score_distribution(
    db: Session = Depends(get_db)
):
    """
    Distribution des scores pour le graphique circulaire
    CORRECTION: Utilise un sous-requête pour le GROUP BY
    """
    try:
        # VERSION CORRIGÉE: Sous-requête pour créer risk_level d'abord
        query = text("""
            SELECT 
                risk_level,
                COUNT(*) as count,
                AVG(fraud_score) * 100 as avg_score
            FROM (
                SELECT 
                    fraud_score,
                    CASE 
                        WHEN fraud_score < 0.2 THEN 'Très faible'
                        WHEN fraud_score < 0.4 THEN 'Faible'
                        WHEN fraud_score < 0.6 THEN 'Moyen'
                        WHEN fraud_score < 0.8 THEN 'Élevé'
                        ELSE 'Très élevé'
                    END as risk_level
                FROM transactions
            ) as subquery
            GROUP BY risk_level
            ORDER BY 
                CASE risk_level
                    WHEN 'Très faible' THEN 1
                    WHEN 'Faible' THEN 2
                    WHEN 'Moyen' THEN 3
                    WHEN 'Élevé' THEN 4
                    WHEN 'Très élevé' THEN 5
                END
        """)
        
        result = db.execute(query)
        
        distribution = []
        colors = {
            'Très faible': '#10b981',
            'Faible': '#22c55e',
            'Moyen': '#f59e0b',
            'Élevé': '#f97316',
            'Très élevé': '#ef4444'
        }
        
        for row in result:
            distribution.append({
                "level": row.risk_level,
                "count": row.count,
                "avg_score": float(row.avg_score or 0),
                "color": colors.get(row.risk_level, '#6b7280')
            })
        
        return {"distribution": distribution}
        
    except Exception as e:
        logger.error(f"❌ Erreur distribution scores: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erreur distribution: {str(e)}"
        )

# ============================================================================
# 5. TOP CLIENTS & TRANSACTIONS
# ============================================================================

@router.get(
    "/top",
    summary="Top statistiques",
    description="Top clients, transactions, etc."
)
async def get_top_stats(
    limit: int = Query(10, ge=1, le=50, description="Nombre d'éléments"),
    db: Session = Depends(get_db)
):
    """
    Top clients frauduleux, plus grosses transactions, etc.
    """
    try:
        # Top clients avec le plus de fraudes
        top_fraudulent_clients = db.execute(text("""
            SELECT 
                customer_id,
                COUNT(*) as total_transactions,
                SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) as fraud_count,
                ROUND(100.0 * SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) / COUNT(*), 2) as fraud_rate
            FROM transactions
            GROUP BY customer_id
            HAVING SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) > 0
            ORDER BY fraud_count DESC
            LIMIT :limit
        """), {"limit": limit}).fetchall()
        
        # Top transactions frauduleuses par montant
        top_fraud_transactions = db.execute(text("""
            SELECT 
                transaction_id,
                customer_id,
                amount,
                fraud_score * 100 as fraud_score_percent,
                created_at
            FROM transactions
            WHERE is_fraud = true
            ORDER BY amount DESC
            LIMIT :limit
        """), {"limit": limit}).fetchall()
        
        return {
            "top_fraudulent_clients": [
                {
                    "customer_id": row.customer_id,
                    "total_transactions": row.total_transactions,
                    "fraud_count": row.fraud_count,
                    "fraud_rate": float(row.fraud_rate)
                }
                for row in top_fraudulent_clients
            ],
            "top_fraud_transactions": [
                {
                    "transaction_id": row.transaction_id,
                    "customer_id": row.customer_id,
                    "amount": float(row.amount),
                    "fraud_score": float(row.fraud_score_percent),
                    "created_at": row.created_at.isoformat() if row.created_at else None
                }
                for row in top_fraud_transactions
            ]
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur top stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur top stats: {str(e)}"
        )


# ============================================================================
# 6. ENDPOINT COMPLET POUR LE FRONTEND - VERSION CORRIGÉE
# ============================================================================
@router.get(
    "/dashboard",
    summary="Toutes les données dashboard",
    description="Retourne TOUTES les données nécessaires au dashboard en un seul appel"
)
async def get_dashboard_data(
    db: Session = Depends(get_db)
):
    """
    🔥 ENDPOINT OPTIMISÉ POUR LE FRONTEND
    Toutes les données en un seul appel pour éviter 5-6 requêtes séparées
    """
    try:
        # Appeler toutes les fonctions de manière séquentielle
        # Ces fonctions sont déjà async, pas besoin d'asyncio.gather
        
        summary = await get_global_stats(db)
        trends = await get_daily_trend(db=db, days=30)
        by_type = await get_stats_by_type(db)
        score_dist = await get_score_distribution(db)
        top = await get_top_stats(db=db, limit=10)
        
        return {
            "summary": summary,
            "trends": trends,
            "by_type": by_type,
            "score_distribution": score_dist,
            "top_stats": top,
            "generated_at": datetime.now().isoformat(),
            "total_transactions_in_db": summary.get("summary", {}).get("total_transactions", 0)
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur dashboard complet: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erreur génération dashboard: {str(e)}"
        )