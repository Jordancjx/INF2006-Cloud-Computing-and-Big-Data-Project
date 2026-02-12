import pandas as pd
import boto3
import io
from sqlalchemy import create_engine

S3_BUCKET_NAME = "cloud-programming-project-grp4"
RDS_ENDPOINT = "database-1.cxuyppgplsie.us-east-1.rds.amazonaws.com"
USER = "admin"
PASSWORD = "adminadmin"
DB_NAME = "ges_data"

# Mapping files in S3 to target RDS tables
data_files = {
    "GES_cleaned.csv": "graduate_employment_survey",
    "Graduates_cleaned.csv": "graduates_stats",
    "Enrolment_cleaned.csv": "enrolment_stats",
    "column_name_mapping.csv": "school_mapping"
}

# Database connection
connection_string = f"mysql+pymysql://{USER}:{PASSWORD}@{RDS_ENDPOINT}:3306/{DB_NAME}"
engine = create_engine(connection_string)
s3_client = boto3.client('s3')

def ingest_from_s3():
    for file_name, table_name in data_files.items():
        try:
            print(f"Fetching {file_name} from S3...")
            # Get the object from S3
            response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=file_name)
            
            # Read directly into Pandas
            df = pd.read_csv(io.BytesIO(response['Body'].read()))
            
            print(f"Uploading {len(df)} rows to RDS table: {table_name}...")
            df.to_sql(table_name, con=engine, if_exists='replace', index=False)
            print(f"Success!\n")
            
        except Exception as e:
            print(f"Error processing {file_name}: {e}")

if __name__ == "__main__":
    ingest_from_s3()