"""
Script to load CSV data into MySQL database
Make sure to install required package: pip install mysql-connector-python
"""

import pandas as pd
import mysql.connector
from mysql.connector import Error
import os

# =====================================================
# CONFIGURATION - Update these with your MySQL credentials
# =====================================================
DB_CONFIG = {
    'host': 'localhost',      # Your MySQL host
    'user': 'root',           # Your MySQL username
    'password': 'your_password',  # Your MySQL password
    'database': 'education_data'   # Your database name
}

# File paths
base_path = os.path.dirname(os.path.abspath(__file__))

def create_connection():
    """Create a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("✓ Successfully connected to MySQL database")
            return connection
    except Error as e:
        print(f"✗ Error connecting to MySQL: {e}")
        return None

def load_schools_lookup(connection):
    """Load schools lookup table"""
    try:
        cursor = connection.cursor()
        df = pd.read_csv(os.path.join(base_path, 'schools_lookup.csv'))
        
        # Clear existing data
        cursor.execute("DELETE FROM schools")
        
        # Insert data
        insert_query = "INSERT INTO schools (school_id, school_name) VALUES (%s, %s)"
        for _, row in df.iterrows():
            cursor.execute(insert_query, (int(row['school_id']), row['school_name']))
        
        connection.commit()
        print(f"✓ Loaded {len(df)} schools into schools table")
        cursor.close()
        return True
    except Error as e:
        print(f"✗ Error loading schools: {e}")
        return False

def load_ges_data(connection):
    """Load Graduate Employment Survey data"""
    try:
        cursor = connection.cursor()
        df = pd.read_csv(os.path.join(base_path, 'GES_cleaned.csv'))
        
        # Clear existing data
        cursor.execute("DELETE FROM graduate_employment_survey")
        
        # Insert data
        insert_query = """
            INSERT INTO graduate_employment_survey 
            (year, university, school_id, school, degree, employment_rate_overall,
             employment_rate_ft_perm, basic_monthly_mean, basic_monthly_median,
             gross_monthly_mean, gross_monthly_median, gross_mthly_25_percentile,
             gross_mthly_75_percentile)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        records = 0
        for _, row in df.iterrows():
            values = (
                int(row['year']),
                row['university'],
                int(row['school_id']),
                row['school'],
                row['degree'],
                float(row['employment_rate_overall']) if pd.notna(row['employment_rate_overall']) else None,
                float(row['employment_rate_ft_perm']) if pd.notna(row['employment_rate_ft_perm']) else None,
                float(row['basic_monthly_mean']) if pd.notna(row['basic_monthly_mean']) else None,
                float(row['basic_monthly_median']) if pd.notna(row['basic_monthly_median']) else None,
                float(row['gross_monthly_mean']) if pd.notna(row['gross_monthly_mean']) else None,
                float(row['gross_monthly_median']) if pd.notna(row['gross_monthly_median']) else None,
                float(row['gross_mthly_25_percentile']) if pd.notna(row['gross_mthly_25_percentile']) else None,
                float(row['gross_mthly_75_percentile']) if pd.notna(row['gross_mthly_75_percentile']) else None
            )
            cursor.execute(insert_query, values)
            records += 1
            
            if records % 100 == 0:
                connection.commit()
                print(f"  Progress: {records} records inserted...")
        
        connection.commit()
        print(f"✓ Loaded {records} records into graduate_employment_survey table")
        cursor.close()
        return True
    except Error as e:
        print(f"✗ Error loading GES data: {e}")
        return False

def load_enrolment_data(connection):
    """Load Enrolment by Institutions data"""
    try:
        cursor = connection.cursor()
        df = pd.read_csv(os.path.join(base_path, 'Enrolment_cleaned.csv'))
        
        # Clear existing data
        cursor.execute("DELETE FROM enrolment_by_institutions")
        
        # Insert data
        insert_query = """
            INSERT INTO enrolment_by_institutions 
            (year, sex, school_id, school_name, enrolment)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        records = 0
        for _, row in df.iterrows():
            if pd.notna(row['school_id']):  # Only insert rows with valid school_id
                values = (
                    int(row['year']),
                    row['sex'],
                    int(row['school_id']),
                    row['school_name'],
                    int(row['enrolment']) if pd.notna(row['enrolment']) else None
                )
                cursor.execute(insert_query, values)
                records += 1
        
        connection.commit()
        print(f"✓ Loaded {records} records into enrolment_by_institutions table")
        cursor.close()
        return True
    except Error as e:
        print(f"✗ Error loading enrolment data: {e}")
        return False

def load_graduates_data(connection):
    """Load Graduates by Institutions data"""
    try:
        cursor = connection.cursor()
        df = pd.read_csv(os.path.join(base_path, 'Graduates_cleaned.csv'))
        
        # Clear existing data
        cursor.execute("DELETE FROM graduates_by_institutions")
        
        # Insert data
        insert_query = """
            INSERT INTO graduates_by_institutions 
            (year, sex, school_id, school_name, graduates)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        records = 0
        for _, row in df.iterrows():
            if pd.notna(row['school_id']):  # Only insert rows with valid school_id
                values = (
                    int(row['year']),
                    row['sex'],
                    int(row['school_id']),
                    row['school_name'],
                    int(row['graduates']) if pd.notna(row['graduates']) else None
                )
                cursor.execute(insert_query, values)
                records += 1
        
        connection.commit()
        print(f"✓ Loaded {records} records into graduates_by_institutions table")
        cursor.close()
        return True
    except Error as e:
        print(f"✗ Error loading graduates data: {e}")
        return False

def main():
    """Main execution function"""
    print("="*70)
    print("MySQL Data Import Script")
    print("="*70)
    print("\nIMPORTANT: Update DB_CONFIG in this script with your MySQL credentials!")
    print()
    
    # Check if files exist
    required_files = [
        'schools_lookup.csv',
        'GES_cleaned.csv',
        'Enrolment_cleaned.csv',
        'Graduates_cleaned.csv'
    ]
    
    for filename in required_files:
        filepath = os.path.join(base_path, filename)
        if not os.path.exists(filepath):
            print(f"✗ Error: {filename} not found!")
            print("  Please run process_and_clean_data.py first to generate the CSV files.")
            return
    
    print("All required CSV files found.\n")
    
    # Create connection
    connection = create_connection()
    if not connection:
        return
    
    try:
        # Load data in order (schools first due to foreign key constraints)
        print("\n1. Loading schools lookup table...")
        load_schools_lookup(connection)
        
        print("\n2. Loading GES data...")
        load_ges_data(connection)
        
        print("\n3. Loading enrolment data...")
        load_enrolment_data(connection)
        
        print("\n4. Loading graduates data...")
        load_graduates_data(connection)
        
        print("\n" + "="*70)
        print("DATA IMPORT COMPLETED SUCCESSFULLY!")
        print("="*70)
        
        # Display summary statistics
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM schools")
        schools_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM graduate_employment_survey")
        ges_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM enrolment_by_institutions")
        enrolment_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM graduates_by_institutions")
        graduates_count = cursor.fetchone()[0]
        
        print(f"\nDatabase Summary:")
        print(f"  - Schools: {schools_count}")
        print(f"  - GES Records: {ges_count}")
        print(f"  - Enrolment Records: {enrolment_count}")
        print(f"  - Graduates Records: {graduates_count}")
        print("="*70)
        
        cursor.close()
        
    except Exception as e:
        print(f"\n✗ An error occurred: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()
            print("\nMySQL connection closed.")

if __name__ == "__main__":
    main()
