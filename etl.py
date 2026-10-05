import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

#1. Load the connection string from the .env file
load_dotenv()
connection_string = os.getenv("NEON_DB_URL")
CSV_FILE_PATH = "/home/mark-gregory/projects/online_fraud_detection/paysim dataset.csv"
TABLE_NAME = "Transactions"
SAMPLE_FRACTION = 0.20

def run_etl():
    if not connection_string:
        print("Error: Database connection string is not set. Please check your .env file.")
        return
    
    print("Starting ETL process....")
    engine = create_engine(connection_string)
    
    #2.Extracting data from the CSV file
    print("Extracting data: Loading CSV into memory (this may take a minute)...")
    df = pd.read_csv(CSV_FILE_PATH)
    
    #Transformation phase1: Stratified sampling to reduce the dataset size while maintaining class distribution
    print("Transforming data: Performing stratified sampling to preserve fraud ratios ...")
    
    # Group by the target variable and sample 20% from both legitimate and fraudulent transactions
    sampled_df = df.groupby('isFraud', group_keys=False).apply(
        lambda x: x.sample(frac=SAMPLE_FRACTION, random_state=42)
     )
    
    #Transformation phase2: # TRANSFORM Phase 2: Clean column names for SQL standards
    print("Transforming data: Renaming columns to snake_case...")
    sampled_df = sampled_df.rename(columns={
        'oldbalanceOrg': 'old_balance_org',
        'newbalanceOrg': 'new_balance_org',
        'oldbalanceDest': 'old_balance_dest',
        'newbalanceDest': 'new_balance_dest',
        'isFraud': 'is_fraud',
        'isFlaggedFraud': 'is_flagged_fraud'
    })
    
    # LOAD
    # We still use chunksize to send data over the internet so Neon doesn't time out the connection
    print(f"Loading data: Pushing {len(sampled_df):,} rows to Neon database in chunks...")
    sampled_df.to_sql(TABLE_NAME, con=engine, if_exists='replace', index=False, chunksize=10_000)
    
    print("ETL pipeline completed successfully! Data is live in the cloud.")

if __name__ == "__main__":
    run_etl()
    