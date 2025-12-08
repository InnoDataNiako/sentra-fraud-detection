
# # """
# # Routes pour la gestion des transactions
# # CRUD complet des transactions
# # """

# # from fastapi import APIRouter, Depends, HTTPException, Query, Path
# # from sqlalchemy.orm import Session
# # from typing import List, Optional
# # from datetime import datetime, timedelta

# # from src.database.connection import get_db
# # from src.database.repositories.transaction_repository import TransactionRepository
# # from src.api.schemas.transaction import (
# #     TransactionResponse, 
# #     TransactionListResponse,
# #     TransactionUpdate
# # )
# # from src.core.logging import get_logger

# # logger = get_logger(__name__)

# # router = APIRouter()

# # @router.get(
# #     "/",
# #     response_model=TransactionListResponse,
# #     summary="Lister les transactions",
# #     description="Récupère la liste des transactions avec pagination et filtres"
# # )
# # async def list_transactions(
# #     skip: int = Query(0, ge=0, description="Nombre d'éléments à sauter"),
# #     limit: int = Query(100, ge=1, le=1000, description="Nombre maximum d'éléments"),
# #     customer_id: Optional[str] = Query(None, description="Filtrer par client"),
# #     is_fraud: Optional[bool] = Query(None, description="Filtrer par statut fraude"),
# #     start_date: Optional[datetime] = Query(None, description="Date de début"),
# #     end_date: Optional[datetime] = Query(None, description="Date de fin"),
# #     db: Session = Depends(get_db)
# # ):
# #     """
# #     Liste les transactions avec pagination et filtres
# #     """
# #     try:
# #         transaction_repo = TransactionRepository(db)
        
# #         # Construction des filtres
# #         filters = {}
# #         if customer_id:
# #             filters["customer_id"] = customer_id
# #         if is_fraud is not None:
# #             filters["is_fraud"] = is_fraud
        
# #         # Récupération des transactions
# #         transactions = transaction_repo.get_all(
# #             skip=skip,
# #             limit=limit,
# #             filters=filters,
# #             start_date=start_date,
# #             end_date=end_date
# #         )
        
# #         # 🔧 CORRECTION : Conversion des objets SQLAlchemy en dictionnaires
# #         transactions_data = [transaction.to_dict() for transaction in transactions]
        
# #         # Calcul du total pour la pagination
# #         total = transaction_repo.count(filters, start_date, end_date)
        
# #         # Calcul des pages
# #         total_pages = (total + limit - 1) // limit if limit > 0 else 1
# #         current_page = (skip // limit) + 1 if limit > 0 else 1
        
# #         logger.info(f"📋 Liste transactions - {len(transactions_data)}/{total} résultats")
        
# #         # 🔧 CORRECTION : Utiliser les données converties
# #         return TransactionListResponse(
# #             transactions=transactions_data,  # 🔧 Utiliser transactions_data au lieu de transactions
# #             total=total,
# #             page=current_page,
# #             page_size=limit,
# #             total_pages=total_pages
# #         )
        
# #     except Exception as e:
# #         logger.error(f"❌ Erreur liste transactions: {e}")
# #         raise HTTPException(
# #             status_code=500,
# #             detail="Erreur lors de la récupération des transactions"
# #         )

# # @router.get(
# #     "/{transaction_id}",
# #     response_model=TransactionResponse,
# #     summary="Obtenir une transaction",
# #     description="Récupère les détails d'une transaction spécifique"
# # )
# # async def get_transaction(
# #     transaction_id: str = Path(..., description="ID de la transaction"),
# #     db: Session = Depends(get_db)
# # ):
# #     """
# #     Récupère une transaction par son ID
# #     """
# #     try:
# #         transaction_repo = TransactionRepository(db)
# #         transaction = transaction_repo.get_by_transaction_id(transaction_id)
        
# #         if not transaction:
# #             raise HTTPException(
# #                 status_code=404,
# #                 detail=f"Transaction non trouvée: {transaction_id}"
# #             )
        
# #         # 🔧 CORRECTION : Convertir en dict pour Pydantic
# #         return transaction.to_dict()
        
# #     except HTTPException:
# #         raise
# #     except Exception as e:
# #         logger.error(f"❌ Erreur récupération transaction {transaction_id}: {e}")
# #         raise HTTPException(
# #             status_code=500,
# #             detail="Erreur lors de la récupération de la transaction"
# #         )

# # @router.get(
# #     "/customer/{customer_id}",
# #     response_model=List[TransactionResponse],
# #     summary="Transactions d'un client",
# #     description="Récupère l'historique des transactions d'un client"
# # )
# # async def get_customer_transactions(
# #     customer_id: str = Path(..., description="ID du client"),
# #     days: int = Query(30, ge=1, le=365, description="Nombre de jours d'historique"),
# #     db: Session = Depends(get_db)
# # ):
# #     """
# #     Récupère les transactions d'un client sur une période
# #     """
# #     try:
# #         transaction_repo = TransactionRepository(db)
        
# #         end_date = datetime.now()
# #         start_date = end_date - timedelta(days=days)
        
# #         transactions = transaction_repo.get_by_customer(
# #             customer_id, 
# #             start_date=start_date, 
# #             end_date=end_date
# #         )
        
# #         # 🔧 CORRECTION : Convertir toutes les transactions
# #         transactions_data = [transaction.to_dict() for transaction in transactions]
        
# #         logger.info(f"👤 Transactions client {customer_id}: {len(transactions_data)} sur {days} jours")
        
# #         return transactions_data
        
# #     except Exception as e:
# #         logger.error(f"❌ Erreur transactions client {customer_id}: {e}")
# #         raise HTTPException(
# #             status_code=500,
# #             detail="Erreur lors de la récupération des transactions client"
# #         )

# # @router.put(
# #     "/{transaction_id}",
# #     response_model=TransactionResponse,
# #     summary="Mettre à jour une transaction",
# #     description="Met à jour les informations d'une transaction (statut, etc.)"
# # )
# # async def update_transaction(
# #     transaction_update: TransactionUpdate,
# #     transaction_id: str = Path(..., description="ID de la transaction"),
# #     db: Session = Depends(get_db)
# # ):
# #     """
# #     Met à jour une transaction existante
# #     """
# #     try:
# #         transaction_repo = TransactionRepository(db)
        
# #         # Vérification existence
# #         existing = transaction_repo.get_by_transaction_id(transaction_id)
# #         if not existing:
# #             raise HTTPException(
# #                 status_code=404,
# #                 detail=f"Transaction non trouvée: {transaction_id}"
# #             )
        
# #         # Mise à jour
# #         updated_transaction = transaction_repo.update(
# #             existing.id, 
# #             transaction_update.dict(exclude_unset=True)
# #         )
        
# #         logger.info(f"✏️ Transaction mise à jour: {transaction_id}")
        
# #         # 🔧 CORRECTION : Convertir en dict pour Pydantic
# #         return updated_transaction.to_dict()
        
# #     except HTTPException:
# #         raise
# #     except Exception as e:
# #         logger.error(f"❌ Erreur mise à jour transaction {transaction_id}: {e}")
# #         raise HTTPException(
# #             status_code=500,
# #             detail="Erreur lors de la mise à jour de la transaction"
# #         )

# # @router.delete(
# #     "/{transaction_id}",
# #     summary="Supprimer une transaction",
# #     description="Supprime une transaction de la base de données"
# # )
# # async def delete_transaction(
# #     transaction_id: str = Path(..., description="ID de la transaction"),
# #     db: Session = Depends(get_db)
# # ):
# #     """
# #     Supprime une transaction
# #     """
# #     try:
# #         transaction_repo = TransactionRepository(db)
        
# #         # Vérification existence
# #         existing = transaction_repo.get_by_transaction_id(transaction_id)
# #         if not existing:
# #             raise HTTPException(
# #                 status_code=404,
# #                 detail=f"Transaction non trouvée: {transaction_id}"
# #             )
        
# #         # Suppression
# #         transaction_repo.delete(existing.id)
        
# #         logger.warning(f"🗑️ Transaction supprimée: {transaction_id}")
        
# #         return {
# #             "message": f"Transaction {transaction_id} supprimée avec succès",
# #             "deleted_at": datetime.now().isoformat()
# #         }
        
# #     except HTTPException:
# #         raise
# #     except Exception as e:
# #         logger.error(f"❌ Erreur suppression transaction {transaction_id}: {e}")
# #         raise HTTPException(
# #             status_code=500,
# #             detail="Erreur lors de la suppression de la transaction"
# #         )

# # @router.get(
# #     "/stats/summary",
# #     summary="Statistiques des transactions",
# #     description="Récupère les statistiques globales des transactions"
# # )
# # async def get_transaction_stats(
# #     days: int = Query(7, ge=1, le=365, description="Période en jours"),
# #     db: Session = Depends(get_db)
# # ):
# #     """
# #     Récupère les statistiques des transactions
# #     """
# #     try:
# #         transaction_repo = TransactionRepository(db)
        
# #         end_date = datetime.now()
# #         start_date = end_date - timedelta(days=days)
        
# #         stats = transaction_repo.get_stats_by_period(start_date, end_date)
        
# #         return {
# #             "period": {
# #                 "start_date": start_date.isoformat(),
# #                 "end_date": end_date.isoformat(),
# #                 "days": days
# #             },
# #             "statistics": stats
# #         }
        
# #     except Exception as e:
# #         logger.error(f"❌ Erreur statistiques transactions: {e}")
# #         raise HTTPException(
# #             status_code=500,
# #             detail="Erreur lors du calcul des statistiques"
# #         )
# """
# Routes pour la gestion des transactions
# CRUD complet des transactions
# """

# from fastapi import APIRouter, Depends, HTTPException, Query, Path
# from sqlalchemy.orm import Session
# from typing import List, Optional
# from datetime import datetime, timedelta

# from src.database.connection import get_db
# from src.database.repositories.transaction_repository import TransactionRepository
# from src.api.schemas.transaction import (
#     TransactionResponse, 
#     TransactionListResponse,
#     TransactionUpdate
# )
# from src.core.logging import get_logger

# logger = get_logger(__name__)

# # 🔧 CORRECTION : Ajouter le prefix pour éviter les conflits de routes
# router = APIRouter(prefix="/transactions", tags=["Transactions"])

# # 🔧 CORRECTION : ORDRE CORRECT DES ROUTES - Les routes statiques en premier

# @router.get(
#     "/stats/summary",  # 🔧 PREMIÈRE - Route statique
#     summary="Statistiques des transactions",
#     description="Récupère les statistiques globales des transactions"
# )
# async def get_transaction_stats(
#     days: int = Query(7, ge=1, le=365, description="Période en jours"),
#     db: Session = Depends(get_db)
# ):
#     """
#     Récupère les statistiques des transactions
#     """
#     try:
#         transaction_repo = TransactionRepository(db)
        
#         end_date = datetime.now()
#         start_date = end_date - timedelta(days=days)
        
#         stats = transaction_repo.get_stats_by_period(start_date, end_date)
        
#         return {
#             "period": {
#                 "start_date": start_date.isoformat(),
#                 "end_date": end_date.isoformat(),
#                 "days": days
#             },
#             "statistics": stats
#         }
        
#     except Exception as e:
#         logger.error(f"❌ Erreur statistiques transactions: {e}")
#         raise HTTPException(
#             status_code=500,
#             detail="Erreur lors du calcul des statistiques"
#         )

# @router.get(
#     "/customer/{customer_id}",  # 🔧 DEUXIÈME - Route avec paramètre spécifique
#     response_model=List[TransactionResponse],
#     summary="Transactions d'un client",
#     description="Récupère l'historique des transactions d'un client"
# )
# async def get_customer_transactions(
#     customer_id: str = Path(..., description="ID du client"),
#     days: int = Query(30, ge=1, le=365, description="Nombre de jours d'historique"),
#     db: Session = Depends(get_db)
# ):
#     """
#     Récupère les transactions d'un client sur une période
#     """
#     try:
#         transaction_repo = TransactionRepository(db)
        
#         end_date = datetime.now()
#         start_date = end_date - timedelta(days=days)
        
#         transactions = transaction_repo.get_by_customer(
#             customer_id, 
#             start_date=start_date, 
#             end_date=end_date
#         )
        
#         # 🔧 CORRECTION : Convertir toutes les transactions
#         transactions_data = [transaction.to_dict() for transaction in transactions]
        
#         logger.info(f"👤 Transactions client {customer_id}: {len(transactions_data)} sur {days} jours")
        
#         return transactions_data
        
#     except Exception as e:
#         logger.error(f"❌ Erreur transactions client {customer_id}: {e}")
#         raise HTTPException(
#             status_code=500,
#             detail="Erreur lors de la récupération des transactions client"
#         )

# @router.get(
#     "/",  # 🔧 TROISIÈME - Route racine (doit être AVANT la route dynamique)
#     response_model=TransactionListResponse,
#     summary="Lister les transactions",
#     description="Récupère la liste des transactions avec pagination et filtres"
# )
# async def list_transactions(
#     skip: int = Query(0, ge=0, description="Nombre d'éléments à sauter"),
#     limit: int = Query(100, ge=1, le=1000, description="Nombre maximum d'éléments"),
#     customer_id: Optional[str] = Query(None, description="Filtrer par client"),
#     is_fraud: Optional[bool] = Query(None, description="Filtrer par statut fraude"),
#     start_date: Optional[datetime] = Query(None, description="Date de début"),
#     end_date: Optional[datetime] = Query(None, description="Date de fin"),
#     db: Session = Depends(get_db)
# ):
#     """
#     Liste les transactions avec pagination et filtres
#     """
#     try:
#         transaction_repo = TransactionRepository(db)
        
#         # Construction des filtres
#         filters = {}
#         if customer_id:
#             filters["customer_id"] = customer_id
#         if is_fraud is not None:
#             filters["is_fraud"] = is_fraud
        
#         # Récupération des transactions
#         transactions = transaction_repo.get_all(
#             skip=skip,
#             limit=limit,
#             filters=filters,
#             start_date=start_date,
#             end_date=end_date
#         )
        
#         # 🔧 CORRECTION : Conversion des objets SQLAlchemy en dictionnaires
#         transactions_data = [transaction.to_dict() for transaction in transactions]
        
#         # Calcul du total pour la pagination
#         total = transaction_repo.count(filters, start_date, end_date)
        
#         # Calcul des pages
#         total_pages = (total + limit - 1) // limit if limit > 0 else 1
#         current_page = (skip // limit) + 1 if limit > 0 else 1
        
#         logger.info(f"📋 Liste transactions - {len(transactions_data)}/{total} résultats")
        
#         # 🔧 CORRECTION : Utiliser les données converties
#         return TransactionListResponse(
#             transactions=transactions_data,
#             total=total,
#             page=current_page,
#             page_size=limit,
#             total_pages=total_pages
#         )
        
#     except Exception as e:
#         logger.error(f"❌ Erreur liste transactions: {e}")
#         raise HTTPException(
#             status_code=500,
#             detail="Erreur lors de la récupération des transactions"
#         )

# @router.get(
#     "/{transaction_id}",  # 🔧 DERNIÈRE - Route dynamique (doit être APRÈS toutes les autres)
#     response_model=TransactionResponse,
#     summary="Obtenir une transaction",
#     description="Récupère les détails d'une transaction spécifique"
# )
# async def get_transaction(
#     transaction_id: str = Path(..., description="ID de la transaction"),
#     db: Session = Depends(get_db)
# ):
#     """
#     Récupère une transaction par son ID
#     """
#     try:
#         transaction_repo = TransactionRepository(db)
#         transaction = transaction_repo.get_by_transaction_id(transaction_id)
        
#         if not transaction:
#             raise HTTPException(
#                 status_code=404,
#                 detail=f"Transaction non trouvée: {transaction_id}"
#             )
        
#         # 🔧 CORRECTION : Convertir en dict pour Pydantic
#         return transaction.to_dict()
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"❌ Erreur récupération transaction {transaction_id}: {e}")
#         raise HTTPException(
#             status_code=500,
#             detail="Erreur lors de la récupération de la transaction"
#         )

# @router.put(
#     "/{transaction_id}",
#     response_model=TransactionResponse,
#     summary="Mettre à jour une transaction",
#     description="Met à jour les informations d'une transaction (statut, etc.)"
# )
# async def update_transaction(
#     transaction_update: TransactionUpdate,
#     transaction_id: str = Path(..., description="ID de la transaction"),
#     db: Session = Depends(get_db)
# ):
#     """
#     Met à jour une transaction existante
#     """
#     try:
#         transaction_repo = TransactionRepository(db)
        
#         # Vérification existence
#         existing = transaction_repo.get_by_transaction_id(transaction_id)
#         if not existing:
#             raise HTTPException(
#                 status_code=404,
#                 detail=f"Transaction non trouvée: {transaction_id}"
#             )
        
#         # Mise à jour
#         updated_transaction = transaction_repo.update(
#             existing.id, 
#             transaction_update.dict(exclude_unset=True)
#         )
        
#         logger.info(f"✏️ Transaction mise à jour: {transaction_id}")
        
#         # 🔧 CORRECTION : Convertir en dict pour Pydantic
#         return updated_transaction.to_dict()
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"❌ Erreur mise à jour transaction {transaction_id}: {e}")
#         raise HTTPException(
#             status_code=500,
#             detail="Erreur lors de la mise à jour de la transaction"
#         )

# @router.delete(
#     "/{transaction_id}",
#     summary="Supprimer une transaction",
#     description="Supprime une transaction de la base de données"
# )
# async def delete_transaction(
#     transaction_id: str = Path(..., description="ID de la transaction"),
#     db: Session = Depends(get_db)
# ):
#     """
#     Supprime une transaction
#     """
#     try:
#         transaction_repo = TransactionRepository(db)
        
#         # Vérification existence
#         existing = transaction_repo.get_by_transaction_id(transaction_id)
#         if not existing:
#             raise HTTPException(
#                 status_code=404,
#                 detail=f"Transaction non trouvée: {transaction_id}"
#             )
        
#         # Suppression
#         transaction_repo.delete(existing.id)
        
#         logger.warning(f"🗑️ Transaction supprimée: {transaction_id}")
        
#         return {
#             "message": f"Transaction {transaction_id} supprimée avec succès",
#             "deleted_at": datetime.now().isoformat()
#         }
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"❌ Erreur suppression transaction {transaction_id}: {e}")
#         raise HTTPException(
#             status_code=500,
#             detail="Erreur lors de la suppression de la transaction"
#         )






"""
Routes pour la gestion des transactions
CRUD complet des transactions
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from src.database.connection import get_db
from src.database.repositories.transaction_repository import TransactionRepository
from src.api.schemas.transaction import (
    TransactionResponse, 
    TransactionListResponse,
    TransactionUpdate
)
from src.core.logging import get_logger

logger = get_logger(__name__)

# 🔧 CORRECTION : ENLEVER LE PREFIX (déjà ajouté dans main.py)
router = APIRouter()

# 🔧 ORDRE CORRECT DES ROUTES - Les routes statiques en premier

@router.get(
    "/stats",  # 🔧 SIMPLIFIÉ : /api/v1/transactions/stats
    summary="Statistiques des transactions",
    description="Récupère les statistiques globales des transactions"
)
async def get_transaction_stats(
    days: int = Query(7, ge=1, le=365, description="Période en jours"),
    db: Session = Depends(get_db)
):
    """
    Récupère les statistiques des transactions
    """
    try:
        transaction_repo = TransactionRepository(db)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        stats = transaction_repo.get_stats_by_period(start_date, end_date)
        
        logger.info(f"📊 Stats transactions récupérées: {stats}")
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            },
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur statistiques transactions: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du calcul des statistiques: {str(e)}"
        )

@router.get(
    "/customer/{customer_id}",
    response_model=List[TransactionResponse],
    summary="Transactions d'un client",
    description="Récupère l'historique des transactions d'un client"
)
async def get_customer_transactions(
    customer_id: str = Path(..., description="ID du client"),
    days: int = Query(30, ge=1, le=365, description="Nombre de jours d'historique"),
    db: Session = Depends(get_db)
):
    """
    Récupère les transactions d'un client sur une période
    """
    try:
        transaction_repo = TransactionRepository(db)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        transactions = transaction_repo.get_by_customer(
            customer_id, 
            start_date=start_date, 
            end_date=end_date
        )
        
        transactions_data = [transaction.to_dict() for transaction in transactions]
        
        logger.info(f"👤 Transactions client {customer_id}: {len(transactions_data)} sur {days} jours")
        
        return transactions_data
        
    except Exception as e:
        logger.error(f"❌ Erreur transactions client {customer_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la récupération des transactions client"
        )

@router.get(
    "/",
    response_model=TransactionListResponse,
    summary="Lister les transactions",
    description="Récupère la liste des transactions avec pagination et filtres"
)
async def list_transactions(
    skip: int = Query(0, ge=0, description="Nombre d'éléments à sauter"),
    limit: int = Query(100, ge=1, le=1000, description="Nombre maximum d'éléments"),

    customer_id: Optional[str] = Query(None, description="Filtrer par client"),
    is_fraud: Optional[bool] = Query(None, description="Filtrer par statut fraude"),
    start_date: Optional[datetime] = Query(None, description="Date de début"),
    end_date: Optional[datetime] = Query(None, description="Date de fin"),
    db: Session = Depends(get_db)
):
    """
    Liste les transactions avec pagination et filtres
    """
    try:
        transaction_repo = TransactionRepository(db)
        
        # Construction des filtres
        filters = {}
        if customer_id:
            filters["customer_id"] = customer_id
        if is_fraud is not None:
            filters["is_fraud"] = is_fraud
        
        # Récupération des transactions
        transactions = transaction_repo.get_all(
            skip=skip,
            limit=limit,
            filters=filters,
            start_date=start_date,
            end_date=end_date
        )
        
        transactions_data = [transaction.to_dict() for transaction in transactions]
        
        # Calcul du total pour la pagination
        total = transaction_repo.count(filters, start_date, end_date)
        
        # Calcul des pages
        total_pages = (total + limit - 1) // limit if limit > 0 else 1
        current_page = (skip // limit) + 1 if limit > 0 else 1
        
        logger.info(f"📋 Liste transactions - {len(transactions_data)}/{total} résultats")
        
        return TransactionListResponse(
            transactions=transactions_data,
            total=total,
            page=current_page,
            page_size=limit,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"❌ Erreur liste transactions: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la récupération des transactions"
        )

@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
    summary="Obtenir une transaction",
    description="Récupère les détails d'une transaction spécifique"
)
async def get_transaction(
    transaction_id: str = Path(..., description="ID de la transaction"),
    db: Session = Depends(get_db)
):
    """
    Récupère une transaction par son ID
    """
    try:
        transaction_repo = TransactionRepository(db)
        transaction = transaction_repo.get_by_transaction_id(transaction_id)
        
        if not transaction:
            raise HTTPException(
                status_code=404,
                detail=f"Transaction non trouvée: {transaction_id}"
            )
        
        return transaction.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur récupération transaction {transaction_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la récupération de la transaction"
        )

@router.put(
    "/{transaction_id}",
    response_model=TransactionResponse,
    summary="Mettre à jour une transaction",
    description="Met à jour les informations d'une transaction (statut, etc.)"
)
async def update_transaction(
    transaction_update: TransactionUpdate,
    transaction_id: str = Path(..., description="ID de la transaction"),
    db: Session = Depends(get_db)
):
    """
    Met à jour une transaction existante
    """
    try:
        transaction_repo = TransactionRepository(db)
        
        # Vérification existence
        existing = transaction_repo.get_by_transaction_id(transaction_id)
        if not existing:
            raise HTTPException(
                status_code=404,
                detail=f"Transaction non trouvée: {transaction_id}"
            )
        
        # Mise à jour
        updated_transaction = transaction_repo.update(
            existing.id, 
            transaction_update.dict(exclude_unset=True)
        )
        
        logger.info(f"✏️ Transaction mise à jour: {transaction_id}")
        
        return updated_transaction.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur mise à jour transaction {transaction_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la mise à jour de la transaction"
        )



@router.delete(
    "/{transaction_id}",
    summary="Supprimer une transaction",
    description="Supprime une transaction de la base de données"
)
async def delete_transaction(
    transaction_id: str = Path(..., description="ID de la transaction"),
    db: Session = Depends(get_db)
):
    """
    Supprime une transaction
    """
    try:
        transaction_repo = TransactionRepository(db)
        
        # Vérification existence
        existing = transaction_repo.get_by_transaction_id(transaction_id)
        if not existing:
            raise HTTPException(
                status_code=404,
                detail=f"Transaction non trouvée: {transaction_id}"
            )
        
        # Suppression
        transaction_repo.delete(existing.id)
        
        logger.warning(f"🗑️ Transaction supprimée: {transaction_id}")
        
        return {
            "message": f"Transaction {transaction_id} supprimée avec succès",
            "deleted_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur suppression transaction {transaction_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la suppression de la transaction"
        )