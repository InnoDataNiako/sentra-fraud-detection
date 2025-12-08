# scripts/clean_and_populate.py
import sys
import os
import pandas as pd
import asyncio
from datetime import datetime
import random
from sqlalchemy import text  # 🔧 IMPORT AJOUTÉ

# 🔧 CORRECTION : Ajouter le répertoire src au PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.database.connection import get_db, SessionLocal, engine
from src.database.models import Transaction, FraudAlert, AlertSeverity, TransactionStatus, Base
from src.core.config import settings

class DatabaseManager:
    def __init__(self):
        self.db = SessionLocal()
    
    def clean_database(self):
        """Vide toutes les tables"""
        print("🧹 Nettoyage de la base de données...")
        try:
            # Désactiver les contraintes de clé étrangère temporairement
            self.db.execute(text("SET session_replication_role = 'replica';"))  # 🔧 CORRECTION
            
            # Supprimer toutes les données dans l'ordre inverse des dépendances
            self.db.query(FraudAlert).delete()
            self.db.query(Transaction).delete()
            
            # Réactiver les contraintes
            self.db.execute(text("SET session_replication_role = 'origin';"))  # 🔧 CORRECTION
            
            self.db.commit()
            print("✅ Base de données nettoyée avec succès!")
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ Erreur lors du nettoyage: {e}")
            return False
    
    def load_transaction_data(self):
        """Charge les données depuis vos fichiers CSV"""
        try:
            # Chemin absolu vers les données
            data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'transactions_train.csv')
            print(f"📁 Chargement depuis: {data_path}")
            
            # Charger seulement les 50 premières lignes pour tester
            # df = pd.read_csv(data_path, nrows=2000)  # 🔧 LIMITE À 50 POUR TESTER
            df = pd.read_csv(data_path)  # 🔧 CHARGE TOUTES LES DONNÉES SANS LIMITE
            print(f"✅ Données chargées: {len(df)} transactions")
            
            # Afficher les statistiques
            fraud_rate = df['is_fraud'].mean() * 100
            print(f"📊 Taux de fraude: {fraud_rate:.2f}%")
            print(f"💰 Montant moyen: {df['amount'].mean():.2f} XOF")
            print(f"🏙️  Villes: {list(df['location'].unique()[:3])}")
            print(f"💳 Types: {list(df['transaction_type'].unique())}")
            
            return df
            
        except Exception as e:
            print(f"❌ Erreur chargement CSV: {e}")
            return None
    
    def calculate_risk_score(self, row):
        """Calcule un score de risque réaliste"""
        base_score = random.uniform(0.1, 0.3)
        
        # Facteurs de risque
        if row['is_fraud'] == 1:
            base_score += random.uniform(0.5, 0.7)
        
        # Montant élevé = risque plus élevé
        amount = float(row['amount'])
        if amount > 100000:
            base_score += 0.2
        elif amount > 50000:
            base_score += 0.1
            
        return min(base_score, 1.0)
    
    def generate_fraud_reason(self, transaction_data, fraud_score):
        """Génère une explication réaliste pour la fraude"""
        reasons = []
        
        if fraud_score > 0.7:
            reasons.append("Montant anormalement élevé")
        if "Dakar" not in transaction_data['location']:
            reasons.append("Localisation suspecte")
        if transaction_data['transaction_type'] in ['transfer', 'withdrawal']:
            reasons.append("Type de transaction à risque")
        if fraud_score > 0.8:
            reasons.append("Comportement client inhabituel")
            
        return ", ".join(reasons) if reasons else "Multiple indicateurs de risque"
    
    async def populate_transactions(self):
        """Peuple la table transactions avec vos données réelles"""
        print("\n🗃️  Peuplement de la table transactions...")
        
        df = self.load_transaction_data()
        if df is None:
            print("❌ Impossible de charger les données")
            return 0
        
        transactions_created = 0
        
        for index, row in df.iterrows():
            try:
                # Vérifier si la transaction existe déjà
                existing = self.db.query(Transaction).filter(
                    Transaction.transaction_id == row['transaction_id']
                ).first()
                
                if existing:
                    print(f"⚠️  Transaction {row['transaction_id']} existe déjà, ignorée")
                    continue
                
                # Calculer le score de risque
                risk_score = self.calculate_risk_score(row)
                
                # Déterminer le statut selon votre enum
                if row['is_fraud'] == 1:
                    status = TransactionStatus.FRAUD
                else:
                    status = TransactionStatus.APPROVED
                
                # Convertir le timestamp
                try:
                    timestamp = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
                except:
                    timestamp = datetime.now()
                
                # Générer une raison de fraude si applicable
                fraud_reason = None
                if row['is_fraud'] == 1:
                    fraud_reason = self.generate_fraud_reason(row, risk_score)
                
                # Créer la transaction
                transaction = Transaction(
                    # Identifiants
                    transaction_id=row['transaction_id'],
                    customer_id=row['customer_id'],
                    merchant_id=row['merchant_id'],
                    
                    # Détails transaction
                    amount=float(row['amount']),
                    currency=row['currency'],
                    transaction_type=row['transaction_type'],
                    
                    # Informations géographiques
                    location=row['location'],
                    country_code="SN",  # Sénégal
                    ip_address=row.get('ip_address', '196.0.0.1'),
                    
                    # Informations temporelles
                    timestamp=timestamp,
                    
                    # Détection de fraude
                    is_fraud=bool(row['is_fraud']),
                    fraud_score=risk_score,
                    fraud_reason=fraud_reason,
                    
                    # Statut
                    status=status
                )
                
                self.db.add(transaction)
                transactions_created += 1
                
                # Commit immédiat pour éviter les problèmes
                if transactions_created % 100 == 0:  # 🔧 COMMIT TOUS LES 100 POUR PERFORMANCE
                    self.db.commit()
                    print(f"   ✅ {transactions_created} transactions insérées...")
                    
            except Exception as e:
                print(f"❌ Erreur sur transaction {index}: {e}")
                self.db.rollback()
                continue
        
        # Commit final
        self.db.commit()
        print(f"🎉 {transactions_created} transactions insérées avec succès!")
        return transactions_created
    
    async def populate_alerts(self):
        """Crée des alertes basées sur les transactions frauduleuses"""
        print("\n🚨 Création des alertes de fraude...")
        
        fraud_transactions = self.db.query(Transaction).filter(Transaction.is_fraud == True).all()
        alerts_created = 0
        
        for transaction in fraud_transactions:
            try:
                # Déterminer le niveau de risque selon votre enum
                if transaction.fraud_score >= 0.85:
                    severity = AlertSeverity.CRITICAL
                elif transaction.fraud_score >= 0.7:
                    severity = AlertSeverity.HIGH
                elif transaction.fraud_score >= 0.5:
                    severity = AlertSeverity.MEDIUM
                else:
                    severity = AlertSeverity.LOW
                
                # Générer un ID d'alerte unique
                alert_id = f"ALERT-{transaction.transaction_id}-{alerts_created:04d}"
                
                # Description détaillée
                description = (
                    f"Transaction frauduleuse détectée: {transaction.amount} {transaction.currency} "
                    f"à {transaction.location} via {transaction.transaction_type}. "
                    f"Score de fraude: {transaction.fraud_score:.2f}"
                )
                
                # Indicateurs de fraude
                fraud_indicators = {
                    "high_amount": transaction.amount > 50000,
                    "suspicious_location": "Dakar" not in transaction.location,
                    "transaction_type": transaction.transaction_type,
                    "risk_score": transaction.fraud_score,
                    "reason": transaction.fraud_reason
                }
                
                alert = FraudAlert(
                    alert_id=alert_id,
                    transaction_id=transaction.id,
                    severity=severity,
                    title=f"Alerte Fraude - {severity.value.upper()}",
                    description=description,
                    fraud_indicators=str(fraud_indicators),
                    is_reviewed=False
                )
                
                self.db.add(alert)
                alerts_created += 1
                
            except Exception as e:
                print(f"❌ Erreur création alerte: {e}")
                continue
        
        self.db.commit()
        print(f"✅ {alerts_created} alertes créées!")
        return alerts_created

async def main():
    print("🚀 DÉMARRAGE DU NETTOYAGE ET PEUPLEMENT")
    print("=" * 60)
    
    manager = DatabaseManager()
    
    # Étape 1: Nettoyer la base
    if not manager.clean_database():
        print("❌ Impossible de nettoyer la base de données")
        return
    
    # Étape 2: Peupler les transactions
    transactions_count = await manager.populate_transactions()
    if transactions_count == 0:
        print("❌ Échec du peuplement des transactions")
        return
    
    # Étape 3: Créer les alertes
    alerts_count = await manager.populate_alerts()
    
    # Statistiques finales
    total_transactions = manager.db.query(Transaction).count()
    total_frauds = manager.db.query(Transaction).filter(Transaction.is_fraud == True).count()
    total_alerts = manager.db.query(FraudAlert).count()
    
    print("\n📊 STATISTIQUES FINALES:")
    print(f"   • Transactions totales: {total_transactions}")
    print(f"   • Fraudes détectées: {total_frauds}")
    print(f"   • Taux de fraude: {(total_frauds/total_transactions)*100:.2f}%")
    print(f"   • Alertes générées: {total_alerts}")
    print("\n🎉 Base de données nettoyée et peuplée avec succès!")

if __name__ == "__main__":
    asyncio.run(main())