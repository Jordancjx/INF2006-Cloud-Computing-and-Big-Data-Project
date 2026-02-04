# Streamlined Data Processing Workflow

## Overview

All data processing and cleaning is now handled by **ONE script**: `process_and_clean_data.py`

This script reads your original CSV files and outputs clean, MySQL-ready data files with school IDs.

---

## Quick Start (2 Steps)

### Step 1: Process & Clean Data
```bash
python process_and_clean_data.py
```

**This single script:**
- ✅ Creates school ID mappings (17 schools, IDs 1-17)
- ✅ Transforms data to include school IDs
- ✅ Normalizes enrolment/graduates from wide to long format
- ✅ Removes all NA/nil values
- ✅ Removes all duplicates
- ✅ Outputs 5 clean, MySQL-ready files

### Step 2: Load into MySQL
```bash
# 1. Update credentials in load_data_to_mysql.py
# 2. Run:
python load_data_to_mysql.py
```

---

## Files Structure

### Input Files (Original Data)
```
GES.csv                         # Employment survey data
EnrolmentbyInstitutions.csv     # Enrolment by institution
Graduatesbyinstitutions.csv     # Graduates by institution
```

### Output Files (Clean & Ready for MySQL)
```
schools_lookup.csv              # Master lookup table (17 schools)
GES_cleaned.csv                 # Employment data with school IDs (1,396 rows)
Enrolment_cleaned.csv          # Normalized enrolment data (958 rows)
Graduates_cleaned.csv          # Normalized graduates data (904 rows)
column_name_mapping.csv        # Reference for column name mappings
```

### Scripts
```
process_and_clean_data.py      # Main: Process & clean all data
load_data_to_mysql.py          # Load cleaned data into MySQL
cleanup_intermediate_files.py  # Optional: Remove old intermediate files
```

---

## What the Script Does

### 1. Creates School ID Mappings
- Extracts all unique school names from all datasets
- Assigns unique IDs (1-17) to each school
- Creates lookup table and mappings

### 2. Transforms GES Data
- Adds `school_id` column to employment survey data
- Maps university names to school IDs
- Removes 5 duplicate records

### 3. Transforms Enrolment Data
- Converts from wide format (schools as columns) to long format
- Adds `school_id` and `school_name` columns
- Removes 504 records with missing enrolment values

### 4. Transforms Graduates Data
- Converts from wide format (schools as columns) to long format
- Adds `school_id` and `school_name` columns
- Removes 524 records with missing graduate values

### 5. Quality Assurance
- ✅ 0 NA values in all output files
- ✅ 0 duplicates in all output files
- ✅ All foreign key relationships valid

---

## Data Quality Summary

| Dataset | Input Rows | Output Rows | Removed | NA Values | Duplicates |
|---------|------------|-------------|---------|-----------|------------|
| GES | 1,401 | 1,396 | 5 | 0 | 0 |
| Enrolment | 1,462* | 958 | 504 | 0 | 0 |
| Graduates | 1,428* | 904 | 524 | 0 | 0 |

*After normalization from wide to long format

---

## School ID Reference

| ID | School Name | Type |
|----|-------------|------|
| 1 | Institute of Technical Education | ITE |
| 2 | LASALLE College of the Arts (Degree) | Arts |
| 3 | LASALLE College of the Arts (Diploma) | Arts |
| 4 | Nanyang Academy of Fine Arts (Degree) | Arts |
| 5 | Nanyang Academy of Fine Arts (Diploma) | Arts |
| 6 | Nanyang Polytechnic | Polytechnic |
| 7 | Nanyang Technological University | University |
| 8 | National Institute of Education | Institute |
| 9 | National University of Singapore | University |
| 10 | Ngee Ann Polytechnic | Polytechnic |
| 11 | Republic Polytechnic | Polytechnic |
| 12 | Singapore Institute of Technology | University |
| 13 | Singapore Management University | University |
| 14 | Singapore Polytechnic | Polytechnic |
| 15 | Singapore University of Social Sciences | University |
| 16 | Singapore University of Technology and Design | University |
| 17 | Temasek Polytechnic | Polytechnic |

---

## MySQL Database Setup

### 1. Create Database Tables
```bash
mysql -u root -p < mysql_schema.sql
```

### 2. Configure MySQL Credentials
Edit `load_data_to_mysql.py`:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'YOUR_USERNAME',
    'password': 'YOUR_PASSWORD',
    'database': 'education_data'
}
```

### 3. Install Required Package
```bash
pip install mysql-connector-python
```

### 4. Load Data
```bash
python load_data_to_mysql.py
```

---

## Cleanup (Optional)

If you have old intermediate files from previous runs, clean them up:

```bash
python cleanup_intermediate_files.py
```

This removes:
- Old `*_with_ids.csv` files
- Old `*_with_ids_cleaned.csv` files
- Deprecated scripts

---

## Reprocessing Data

If you update the original CSV files and need to reprocess:

```bash
# Just run the main script again
python process_and_clean_data.py

# Then reload into MySQL
python load_data_to_mysql.py
```

---

## Backend Integration Example

```python
# Flask API endpoint
from flask import Flask, jsonify
import mysql.connector

@app.route('/api/schools')
def get_schools():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT school_id, school_name FROM schools ORDER BY school_name")
    schools = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(schools)

@app.route('/api/employment/<int:school_id>/<int:year>')
def get_employment(school_id, year):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT degree, employment_rate_overall, gross_monthly_median
        FROM graduate_employment_survey
        WHERE school_id = %s AND year = %s
        ORDER BY degree
    """
    cursor.execute(query, (school_id, year))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data)
```

---

## Benefits of This Approach

✅ **Single Command** - One script does everything  
✅ **Clean Workspace** - Minimal intermediate files  
✅ **Reproducible** - Run anytime to regenerate clean data  
✅ **Maintainable** - All logic in one place  
✅ **Quality Assured** - Built-in validation and cleaning  
✅ **MySQL Ready** - Foreign keys and indexes included  

---

## File Naming Convention

**Old (messy):**
- GES.csv → GES_with_ids.csv → GES_with_ids_cleaned.csv

**New (clean):**
- GES.csv → GES_cleaned.csv

Simple, clear, and fewer files!

---

## Troubleshooting

**Problem:** Script can't find input files  
**Solution:** Make sure GES.csv, EnrolmentbyInstitutions.csv, and Graduatesbyinstitutions.csv are in the data/ folder

**Problem:** MySQL import fails  
**Solution:** Run mysql_schema.sql first to create the database tables

**Problem:** Want to change school IDs  
**Solution:** Don't! IDs are stable. Changing them will break foreign key relationships.

---

## Support Files

- `mysql_schema.sql` - Database schema with foreign keys
- `QUICK_START.md` - Quick reference guide
- `README_SCHOOL_IDS.md` - Detailed documentation
- `CLEANING_REPORT.md` - Data quality report

---

**That's it!** Your data processing is now streamlined and organized. Just run `process_and_clean_data.py` whenever you need to reprocess your data.
