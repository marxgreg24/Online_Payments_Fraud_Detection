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
    
    
    