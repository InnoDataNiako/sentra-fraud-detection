"""
Repository pour la gestion des transactions
Pattern Repository pour abstraire l'accès aux données
"""

from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from src.database.models import Transaction, TransactionStatus
from src.core.logging import get_logger

logger = get_logger(__name__)


class TransactionRepository:
    """Repository pour les opérations CRUD sur les transactions"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, transaction_data: dict) -> Transaction:
        """
        Crée une nouvelle transaction
        
        Args:
            transaction_data: Dictionnaire avec les données de la transaction
            
        Returns:
            Transaction créée
        """
        transaction = Transaction(**transaction_data)
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        
        logger.info(f"Transaction créée: {transaction.transaction_id}")
        return transaction
    
    def get_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """Récupère une transaction par son ID"""
        return self.db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    def get_by_transaction_id(self, transaction_id: str) -> Optional[Transaction]:
        """Récupère une transaction par son transaction_id unique"""
        return self.db.query(Transaction).filter(
            Transaction.transaction_id == transaction_id
        ).first()
    
    def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: dict = None,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> List[Transaction]:
        """Récupère toutes les transactions avec pagination et filtres"""
        query = self.db.query(Transaction)
        
        # Appliquer les filtres
        if filters:
            if "customer_id" in filters:
                query = query.filter(Transaction.customer_id == filters["customer_id"])
            if "is_fraud" in filters:
                query = query.filter(Transaction.is_fraud == filters["is_fraud"])
        
        # Appliquer les filtres de date
        if start_date:
            query = query.filter(Transaction.timestamp >= start_date)
        if end_date:
            query = query.filter(Transaction.timestamp <= end_date)
        
        return query.offset(skip).limit(limit).all()
    
    def count(
        self, 
        filters: dict = None,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> int:
        """Compte le nombre total de transactions avec filtres"""
        query = self.db.query(func.count(Transaction.id))
        
        # Appliquer les filtres
        if filters:
            if "customer_id" in filters:
                query = query.filter(Transaction.customer_id == filters["customer_id"])
            if "is_fraud" in filters:
                query = query.filter(Transaction.is_fraud == filters["is_fraud"])
        
        # Appliquer les filtres de date
        if start_date:
            query = query.filter(Transaction.timestamp >= start_date)
        if end_date:
            query = query.filter(Transaction.timestamp <= end_date)
        
        return query.scalar()
    def get_fraudulent(self, skip: int = 0, limit: int = 100) -> List[Transaction]:
        """Récupère uniquement les transactions frauduleuses"""
        return self.db.query(Transaction).filter(
            Transaction.is_fraud == True
        ).offset(skip).limit(limit).all()
    
    def get_by_customer(
        self, 
        customer_id: str, 
        skip: int = 0, 
        limit: int = 50
    ) -> List[Transaction]:
        """Récupère les transactions d'un client"""
        return self.db.query(Transaction).filter(
            Transaction.customer_id == customer_id
        ).order_by(Transaction.timestamp.desc()).offset(skip).limit(limit).all()
    
    def get_recent(self, hours: int = 24, limit: int = 100) -> List[Transaction]:
        """Récupère les transactions récentes des X dernières heures"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return self.db.query(Transaction).filter(
            Transaction.timestamp >= cutoff_time
        ).order_by(Transaction.timestamp.desc()).limit(limit).all()
    
    def update(self, transaction_id: int, update_data: dict) -> Optional[Transaction]:
        """
        Met à jour une transaction
        
        Args:
            transaction_id: ID de la transaction
            update_data: Dictionnaire avec les champs à mettre à jour
            
        Returns:
            Transaction mise à jour ou None
        """
        transaction = self.get_by_id(transaction_id)
        if not transaction:
            return None
        
        for key, value in update_data.items():
            setattr(transaction, key, value)
        
        transaction.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(transaction)
        
        logger.info(f"Transaction mise à jour: {transaction.transaction_id}")
        return transaction
    
    def mark_as_fraud(
        self, 
        transaction_id: int, 
        fraud_score: float, 
        reason: str
    ) -> Optional[Transaction]:
        """Marque une transaction comme frauduleuse"""
        return self.update(transaction_id, {
            "is_fraud": True,
            "fraud_score": fraud_score,
            "fraud_reason": reason,
            "status": TransactionStatus.FRAUD
        })
    
    def delete(self, transaction_id: int) -> bool:
        """
        Supprime une transaction (soft delete recommandé en prod)
        
        Returns:
            True si supprimée, False sinon
        """
        transaction = self.get_by_id(transaction_id)
        if not transaction:
            return False
        
        self.db.delete(transaction)
        self.db.commit()
        
        logger.warning(f"Transaction supprimée: {transaction.transaction_id}")
        return True
    
    # === STATISTIQUES ===
    
    def count_total(self) -> int:
        """Compte le nombre total de transactions"""
        return self.db.query(func.count(Transaction.id)).scalar()
    
    def count_fraudulent(self) -> int:
        """Compte le nombre de transactions frauduleuses"""
        return self.db.query(func.count(Transaction.id)).filter(
            Transaction.is_fraud == True
        ).scalar()
    
    def get_fraud_rate(self) -> float:
        """Calcule le taux de fraude (pourcentage)"""
        total = self.count_total()
        if total == 0:
            return 0.0
        fraudulent = self.count_fraudulent()
        return (fraudulent / total) * 100
    
    def get_total_amount(self) -> float:
        """Calcule le montant total des transactions"""
        result = self.db.query(func.sum(Transaction.amount)).scalar()
        return result or 0.0
    
    def get_average_amount(self) -> float:
        """Calcule le montant moyen des transactions"""
        result = self.db.query(func.avg(Transaction.amount)).scalar()
        return result or 0.0
    
    def get_stats_by_period(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> dict:
        """
        Récupère les statistiques pour une période donnée
        
        Returns:
            Dictionnaire avec : total, fraudulent, amount, avg_score
        """
        transactions = self.db.query(Transaction).filter(
            and_(
                Transaction.timestamp >= start_date,
                Transaction.timestamp <= end_date
            )
        ).all()
        
        total = len(transactions)
        fraudulent = sum(1 for t in transactions if t.is_fraud)
        total_amount = sum(t.amount for t in transactions)
        avg_fraud_score = sum(t.fraud_score for t in transactions) / total if total > 0 else 0
        
        return {
            "total_transactions": total,
            "fraudulent_transactions": fraudulent,
            "fraud_rate": (fraudulent / total * 100) if total > 0 else 0,
            "total_amount": total_amount,
            "average_fraud_score": avg_fraud_score
        }

    # Ajoute à la fin de ta classe TransactionRepository :

    def count_recent_transactions(self, customer_id: str, hours: int = 24) -> int:
        """Compte les transactions récentes d'un client"""
        from datetime import datetime, timedelta
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return self.db.query(func.count(Transaction.id)).filter(
            Transaction.customer_id == customer_id,
            Transaction.timestamp >= cutoff_time
        ).scalar()
    
    def get_total_amount_period(self, start_date: datetime, end_date: datetime) -> float:
        """Calcule le montant total sur une période"""
        result = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.timestamp >= start_date,
            Transaction.timestamp <= end_date
        ).scalar()
        return result or 0.0
    
    def get_avg_amount_period(self, start_date: datetime, end_date: datetime) -> float:
        """Calcule le montant moyen sur une période"""
        result = self.db.query(func.avg(Transaction.amount)).filter(
            Transaction.timestamp >= start_date,
            Transaction.timestamp <= end_date
        ).scalar()
        return result or 0.0    