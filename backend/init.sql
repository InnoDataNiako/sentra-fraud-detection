-- Création des tables si elles n'existent pas

-- Table des transactions
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(50) UNIQUE NOT NULL,
    customer_id VARCHAR(50) NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'XOF',
    transaction_type VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    fraud_score DECIMAL(5, 4) NOT NULL,
    is_fraud BOOLEAN NOT NULL DEFAULT false,
    location VARCHAR(255),
    device_id VARCHAR(100),
    merchant VARCHAR(100),
    time_of_day VARCHAR(20),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour les performances
CREATE INDEX IF NOT EXISTS idx_transactions_customer_id ON transactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp);
CREATE INDEX IF NOT EXISTS idx_transactions_is_fraud ON transactions(is_fraud);
CREATE INDEX IF NOT EXISTS idx_transactions_fraud_score ON transactions(fraud_score);
CREATE INDEX IF NOT EXISTS idx_transactions_transaction_type ON transactions(transaction_type);

-- Table pour les logs système
CREATE TABLE IF NOT EXISTS system_logs (
    id SERIAL PRIMARY KEY,
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    source VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertion de données de démo (optionnel)
INSERT INTO transactions (transaction_id, customer_id, amount, transaction_type, timestamp, fraud_score, is_fraud, location)
VALUES 
    ('txn_00009425', 'cust_02367', 28139.00, 'payment', '2024-08-21 14:23:00', 0.155, false, 'Diourbel, Sénégal'),
    ('txn_00008752', 'cust_01906', 44715.00, 'withdrawal', '2024-08-21 14:34:00', 0.264, false, 'Kaolack, Sénégal'),
    ('txn_00009927', 'cust_00619', 1100000.00, 'transfer', '2024-08-21 10:15:00', 0.807, true, 'Dakar, Sénégal'),
    ('txn_00009788', 'cust_01024', 1100000.00, 'transfer', '2024-08-21 11:30:00', 0.814, true, 'Thiès, Sénégal')
ON CONFLICT (transaction_id) DO NOTHING;

-- Vérification
SELECT 'Base de données SÉNTRA initialisée avec succès!' as message;