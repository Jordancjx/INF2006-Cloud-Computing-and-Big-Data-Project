# School ID Mapping for Education Data

This directory contains scripts and data files to create unique school IDs for linking data across multiple CSV files for MySQL database integration.

## Problem Statement

The original data had school names in different formats:
- **GES.csv**: School names as data values in the "university" column
- **EnrolmentbyInstitutions.csv**: School names as column headers (columns 3-19)
- **Graduatesbyinstitutions.csv**: School names as column headers (columns 3-19)

We needed a consistent way to link these datasets using a common foreign key (school_id).

## Solution Overview

A school ID mapping system was created with 17 unique schools, each assigned a unique integer ID (1-17). The data was normalized to use these IDs as foreign keys.

## Files Created

### 1. Reference Files
- **schools_lookup.csv** - Master lookup table with school_id and school_name
- **column_name_to_id_mapping.csv** - Maps column names to full school names and IDs

### 2. Transformed Data Files
- **GES_with_ids.csv** - Original GES data with school_id column added
- **EnrolmentbyInstitutions_with_ids.csv** - Normalized enrolment data with school_id
- **Graduatesbyinstitutions_with_ids.csv** - Normalized graduates data with school_id

### 3. Scripts
- **create_school_ids.py** - Python script to generate all transformed files
- **load_data_to_mysql.py** - Python script to load data into MySQL database
- **mysql_schema.sql** - SQL schema definition for MySQL database

## School ID Mapping

| ID | School Name |
|----|-------------|
| 1 | Institute of Technical Education |
| 2 | LASALLE College of the Arts (Degree) |
| 3 | LASALLE College of the Arts (Diploma) |
| 4 | Nanyang Academy of Fine Arts (Degree) |
| 5 | Nanyang Academy of Fine Arts (Diploma) |
| 6 | Nanyang Polytechnic |
| 7 | Nanyang Technological University |
| 8 | National Institute of Education |
| 9 | National University of Singapore |
| 10 | Ngee Ann Polytechnic |
| 11 | Republic Polytechnic |
| 12 | Singapore Institute of Technology |
| 13 | Singapore Management University |
| 14 | Singapore Polytechnic |
| 15 | Singapore University of Social Sciences |
| 16 | Singapore University of Technology and Design |
| 17 | Temasek Polytechnic |

## Usage Instructions

### Step 1: Generate Transformed CSV Files

If you need to regenerate the CSV files:

```bash
python create_school_ids.py
```

This will create all the transformed CSV files with school IDs.

### Step 2: Set Up MySQL Database

1. Create your database:
```sql
CREATE DATABASE education_data;
USE education_data;
```

2. Run the schema file:
```bash
mysql -u your_username -p education_data < mysql_schema.sql
```

Or manually execute the SQL in `mysql_schema.sql` using MySQL Workbench or your preferred tool.

### Step 3: Load Data into MySQL

1. Update the database credentials in `load_data_to_mysql.py`:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'education_data'
}
```

2. Install required Python package:
```bash
pip install mysql-connector-python
```

3. Run the loader script:
```bash
python load_data_to_mysql.py
```

## Database Schema

### Table: schools (Master Reference Table)
- **school_id** (INT, PRIMARY KEY)
- **school_name** (VARCHAR(255), UNIQUE)
- created_at (TIMESTAMP)

### Table: graduate_employment_survey
- id (INT, AUTO_INCREMENT, PRIMARY KEY)
- year (INT)
- **school_id** (INT, FOREIGN KEY → schools.school_id)
- university (VARCHAR)
- school (VARCHAR)
- degree (VARCHAR)
- employment_rate_overall (DECIMAL)
- employment_rate_ft_perm (DECIMAL)
- basic_monthly_mean/median (DECIMAL)
- gross_monthly_mean/median/percentiles (DECIMAL)

### Table: enrolment_by_institutions
- id (INT, AUTO_INCREMENT, PRIMARY KEY)
- year (INT)
- sex (VARCHAR)
- **school_id** (INT, FOREIGN KEY → schools.school_id)
- school_name (VARCHAR)
- enrolment (INT)

### Table: graduates_by_institutions
- id (INT, AUTO_INCREMENT, PRIMARY KEY)
- year (INT)
- sex (VARCHAR)
- **school_id** (INT, FOREIGN KEY → schools.school_id)
- school_name (VARCHAR)
- graduates (INT)

## Key Features

1. **Foreign Key Relationships**: All tables reference the schools table using school_id
2. **Data Normalization**: Enrolment and graduates data transformed from wide to long format
3. **Indexes**: Added for optimal query performance on year, school_id combinations
4. **Unique Constraints**: Prevent duplicate entries for year/sex/school combinations
5. **Cascade Operations**: ON DELETE CASCADE and ON UPDATE CASCADE for referential integrity

## Example Queries

### Get all schools
```sql
SELECT * FROM schools ORDER BY school_name;
```

### Join enrolment data with school names
```sql
SELECT e.year, s.school_name, e.sex, e.enrolment
FROM enrolment_by_institutions e
JOIN schools s ON e.school_id = s.school_id
WHERE e.year = 2020
ORDER BY e.enrolment DESC;
```

### Employment stats by school
```sql
SELECT s.school_name, 
       AVG(g.employment_rate_overall) as avg_employment_rate,
       AVG(g.gross_monthly_median) as avg_salary
FROM graduate_employment_survey g
JOIN schools s ON g.school_id = s.school_id
WHERE g.year BETWEEN 2018 AND 2022
GROUP BY s.school_id, s.school_name
ORDER BY avg_employment_rate DESC;
```

### Compare enrolment vs graduates
```sql
SELECT s.school_name,
       e.enrolment,
       g.graduates,
       ROUND((g.graduates * 100.0 / e.enrolment), 2) as completion_rate
FROM schools s
LEFT JOIN enrolment_by_institutions e 
    ON s.school_id = e.school_id AND e.year = 2020 AND e.sex = 'MF'
LEFT JOIN graduates_by_institutions g 
    ON s.school_id = g.school_id AND g.year = 2020 AND g.sex = 'MF'
WHERE e.enrolment IS NOT NULL AND g.graduates IS NOT NULL
ORDER BY completion_rate DESC;
```

## Data Transformations

### Original Enrolment Structure (Wide Format)
```
year,sex,nus,ntu,smu,...
2020,F,5000,4000,2000,...
```

### Transformed Enrolment Structure (Long Format)
```
year,sex,school_id,school_name,enrolment
2020,F,9,National University of Singapore,5000
2020,F,7,Nanyang Technological University,4000
2020,F,13,Singapore Management University,2000
```

This normalized structure makes it much easier to:
- Query specific schools
- Join across tables
- Maintain referential integrity
- Add new schools without schema changes

## Requirements

- Python 3.7+
- pandas
- mysql-connector-python (for database loading)
- MySQL 5.7+ or MariaDB 10.2+

## Notes

- The school_id values are stable and should not be changed once in production
- All monetary values in GES data are in Singapore Dollars (SGD)
- Employment rates are stored as percentages (e.g., 95.5 = 95.5%)
- Sex codes: 'F' = Female, 'M' = Male, 'MF' = Male & Female combined
