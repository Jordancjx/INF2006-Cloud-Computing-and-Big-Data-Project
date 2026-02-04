import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus

# === CHANGE THESE TO MATCH YOUR LOCAL SETUP ===
CSV_PATH = "GES.csv"

ENDPOINT = "localhost"
USER = "root"  # replace with your MySQL username
PASSWORD = "your_password"  # replace with your MySQL password
DB_NAME = "ges_db"

connection_string = f"mysql+pymysql://{USER}:{PASSWORD}@{ENDPOINT}:3306/{DB_NAME}"

try:
    # 1. Read CSV from your computer
    print("Reading CSV file...")
    df = pd.read_csv(CSV_PATH)

    print("Preview:")
    print(df.head())

    # 2. Clean data (optional)
    df = df.replace('na', pd.NA).dropna()

    # 3. Upload to MySQL Workbench
    engine = create_engine(connection_string)
    print("Uploading to MySQL Workbench...")

    df.to_sql(
        'graduate_employment_survey',
        con=engine,
        if_exists='replace',
        index=False
    )

    print("Ingestion Complete! Check MySQL Workbench.")

except Exception as e:
    print(f"Error: {e}")
