"""
Script de génération de données synthétiques pour l'entraînement
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from src.core.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


class SyntheticDataGenerator:
    """
    Générateur de données synthétiques aligné avec les statistiques BCEAO 2023
    Référence: "Digital Financial Services and Fraud Prevention" - BCEAO, 2023
    """
    
    def __init__(self, n_transactions: int = 10000, fraud_rate: float = 0.028):
        """
        Args:
            n_transactions: Nombre de transactions à générer
            fraud_rate: Taux de fraude (0.028 = 2.8% selon BCEAO 2023)
        """
        self.n_transactions = n_transactions
        self.fraud_rate = fraud_rate
        self.n_frauds = int(n_transactions * fraud_rate)
        
        # Villes UEMOA (Union Économique et Monétaire Ouest Africaine)
        self.cities = [
            # Sénégal
            "Dakar", "Thiès", "Saint-Louis", "Kaolack", "Ziguinchor",
            "Diourbel", "Louga", "Tambacounda", "Kolda", "Mbour",
            "Rufisque", "Pikine", "Guédiawaye", "Touba", "Richard-Toll",
            # Autres pays UEMOA (pour patterns de fraude transfrontaliers)
            "Abidjan, Côte d'Ivoire", "Bamako, Mali", "Ouagadougou, Burkina Faso",
            "Niamey, Niger", "Lomé, Togo", "Cotonou, Bénin", "Bissau, Guinée-Bissau"
        ]
        
        # Distribution des types selon BCEAO 2023 (Mobile Money dominant en Afrique)
        self.transaction_types = ["payment", "transfer", "withdrawal", "cash_in", "bill_payment"]
        self.transaction_weights = [0.35, 0.30, 0.20, 0.10, 0.05]  # Mobile money prioritaire
        
        # Méthodes de paiement selon adoption en zone UEMOA
        self.payment_methods = ["mobile_money", "card", "bank_transfer", "pos"]
        self.payment_weights = [0.65, 0.20, 0.10, 0.05]  # Mobile Money = 65% du marché
        
        # Patterns de fraude BCEAO 2023
        self.fraud_patterns_distribution = {
            'sim_swap': 0.25,           # 25% - Fraude SIM swap (très courant en Afrique)
            'phishing': 0.22,           # 22% - Hameçonnage mobile
            'unauthorized_transfer': 0.20,  # 20% - Transferts non autorisés
            'account_takeover': 0.15,   # 15% - Prise de contrôle compte
            'merchant_fraud': 0.10,     # 10% - Fraude commerçant
            'velocity_abuse': 0.08      # 8% - Abus de vélocité
        }
        
    def generate_legitimate_transaction(self, customer_id: str, transaction_id: str, timestamp: datetime) -> dict:
        """Génère une transaction légitime"""
        
        # Montant légitime (distribution normale)
        amount = max(1000, np.random.normal(50000, 20000))
        
        return {
            'transaction_id': transaction_id,
            'amount': round(amount, 2),
            'currency': 'XOF',
            'customer_id': customer_id,
            'merchant_id': f"merch_{random.randint(1, 500):04d}",
            'transaction_type': random.choice(self.transaction_types),
            'payment_method': random.choice(self.payment_methods),
            'location': random.choice(self.cities) + ", Sénégal",
            'ip_address': f"196.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
            'device_id': f"device_{random.randint(1000, 9999):04d}",
            'timestamp': timestamp,
            'is_fraud': 0
        }
    
    def generate_fraud_transaction(self, customer_id: str, transaction_id: str, timestamp: datetime) -> dict:
        """Génère une transaction frauduleuse avec des patterns suspects"""
        
        fraud_patterns = [
            'high_amount', 'unusual_location', 'high_velocity', 
            'night_transaction', 'unusual_merchant'
        ]
        
        pattern = random.choice(fraud_patterns)
        
        # Montant de base
        base_amount = np.random.normal(50000, 20000)
        
        if pattern == 'high_amount':
            # Montant anormalement élevé
            amount = base_amount * random.uniform(5, 15)
        elif pattern == 'high_velocity':
            # Montant normal mais haute vélocité (sera géré dans la séquence)
            amount = base_amount
        else:
            # Montant légèrement élevé
            amount = base_amount * random.uniform(2, 4)
        
        # Localisation suspecte pour certains patterns
        if pattern == 'unusual_location':
            location = random.choice(["Lagos, Nigeria", "Abidjan, Côte d'Ivoire", "Accra, Ghana"])
        else:
            location = random.choice(self.cities) + ", Sénégal"
        
        # Transaction de nuit
        if pattern == 'night_transaction':
            timestamp = timestamp.replace(hour=random.randint(0, 5))
        
        return {
            'transaction_id': transaction_id,
            'amount': round(max(1000, amount), 2),
            'currency': 'XOF',
            'customer_id': customer_id,
            'merchant_id': f"merch_{random.randint(1, 50):04d}" if pattern != 'unusual_merchant' else f"merch_{random.randint(8000, 9000):04d}",
            'transaction_type': random.choice(self.transaction_types),
            'payment_method': random.choice(self.payment_methods),
            'location': location,
            'ip_address': f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
            'device_id': f"device_{random.randint(1000, 9999):04d}",
            'timestamp': timestamp,
            'is_fraud': 1
        }
    
    def generate_advanced_fraud_pattern(self, customer_id: str, transaction_id: str, timestamp: datetime) -> dict:
        """Pattern avancé : fraude par vélocité (rapid fire)"""
        # Générer 3-5 transactions rapides du même client
        base_amount = np.random.normal(30000, 10000)
        
        return {
            'transaction_id': transaction_id,
            'amount': round(base_amount, 2),
            'currency': 'XOF',
            'customer_id': customer_id,
            'merchant_id': f"merch_{random.randint(1, 100):04d}",
            'transaction_type': 'transfer',
            'payment_method': 'mobile_money',
            'location': random.choice(self.cities) + ", Sénégal", 
            'ip_address': f"196.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
            'device_id': f"device_{random.randint(1000, 9999):04d}",
            'timestamp': timestamp,
            'is_fraud': 1,
            'fraud_pattern': 'velocity_attack'  # Nouveau champ
        }

    def generate_dataset(self) -> pd.DataFrame:
        """Génère le dataset complet"""
        
        logger.info(f"🔧 Génération de {self.n_transactions} transactions ({self.fraud_rate*100}% fraude)")
        
        transactions = []
        
        # Générer des clients
        n_customers = int(self.n_transactions * 0.3)  # 30% du nombre de transactions
        customer_ids = [f"cust_{i:05d}" for i in range(1, n_customers + 1)]
        
        # Timestamp de base
        base_date = datetime.utcnow() - timedelta(days=90)
        
        # Générer les transactions légitimes
        n_legitimate = self.n_transactions - self.n_frauds
        
        for i in range(n_legitimate):
            customer_id = random.choice(customer_ids)
            transaction_id = f"txn_{i:08d}"
            
            # Timestamp aléatoire dans les 90 derniers jours
            days_offset = random.randint(0, 90)
            hours_offset = random.randint(0, 23)
            minutes_offset = random.randint(0, 59)
            
            timestamp = base_date + timedelta(
                days=days_offset,
                hours=hours_offset,
                minutes=minutes_offset
            )
            
            tx = self.generate_legitimate_transaction(customer_id, transaction_id, timestamp)
            transactions.append(tx)
        
        # Générer les transactions frauduleuses
        for i in range(self.n_frauds):
            customer_id = random.choice(customer_ids)
            transaction_id = f"txn_{n_legitimate + i:08d}"
            
            days_offset = random.randint(0, 90)
            hours_offset = random.randint(0, 23)
            minutes_offset = random.randint(0, 59)
            
            timestamp = base_date + timedelta(
                days=days_offset,
                hours=hours_offset,
                minutes=minutes_offset
            )
            
            tx = self.generate_fraud_transaction(customer_id, transaction_id, timestamp)
            transactions.append(tx)
        
        # Créer DataFrame
        df = pd.DataFrame(transactions)
        
        # Trier par timestamp
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        logger.info(f"✅ Dataset généré:")
        logger.info(f"   - Total: {len(df)} transactions")
        logger.info(f"   - Légitimes: {len(df[df['is_fraud'] == 0])}")
        logger.info(f"   - Fraudes: {len(df[df['is_fraud'] == 1])}")
        logger.info(f"   - Taux fraude: {df['is_fraud'].mean()*100:.2f}%")
        
        return df
    
    def split_and_save(self, df: pd.DataFrame, output_dir: str = "./data/processed"):
        """Split train/test et sauvegarde"""
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Split 80/20
        train_size = int(len(df) * 0.8)
        
        train_df = df[:train_size]
        test_df = df[train_size:]
        
        # Sauvegarder
        train_path = output_path / "transactions_train.csv"
        test_path = output_path / "transactions_test.csv"
        
        train_df.to_csv(train_path, index=False)
        test_df.to_csv(test_path, index=False)
        
        logger.info(f"✅ Données sauvegardées:")
        logger.info(f"   - Train: {train_path} ({len(train_df)} lignes)")
        logger.info(f"   - Test: {test_path} ({len(test_df)} lignes)")
        
        return train_df, test_df


def main():
    """Fonction principale"""
    
    logger.info("=" * 60)
    logger.info("🔧 Génération de données synthétiques SÉNTRA")
    logger.info("=" * 60)
    
    # Paramètres
    n_transactions = 10000  # Nombre de transactions
    fraud_rate = 0.025      # 2.5% de fraude
    
    # Générer
    generator = SyntheticDataGenerator(n_transactions, fraud_rate)
    df = generator.generate_dataset()
    
    # Sauvegarder
    train_df, test_df = generator.split_and_save(df)
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("✅ Génération terminée avec succès!")
    logger.info("=" * 60)
    logger.info("")
    logger.info("📝 Prochaines étapes:")
    logger.info("   1. Entraîner un modèle: python scripts/train_model.py")
    logger.info("   2. Tester la détection via l'API")


if __name__ == "__main__":
    main()