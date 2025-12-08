# Script pour inspecter les CSV
import pandas as pd

def inspect_csv():
    train_path = "data/processed/transactions_train.csv"
    test_path = "data/processed/transactions_test.csv"
    
    print("=== transactions_train.csv ===")
    df_train = pd.read_csv(train_path)
    print(f"Colonnes: {list(df_train.columns)}")
    print(f"Premières lignes:\n{df_train.head(2)}")
    
    print("\n=== transactions_test.csv ===") 
    df_test = pd.read_csv(test_path)
    print(f"Colonnes: {list(df_test.columns)}")
    print(f"Premières lignes:\n{df_test.head(2)}")

inspect_csv()