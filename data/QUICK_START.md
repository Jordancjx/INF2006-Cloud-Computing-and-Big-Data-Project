# Quick Start Guide - School ID System

## What Was Done

✅ Created unique IDs (1-17) for all schools/institutions
✅ Generated transformed CSV files with school_id columns
✅ Created MySQL database schema with foreign key relationships
✅ Generated Python scripts for data loading

## Files You'll Use

### For MySQL Database Setup:
1. **schools_lookup.csv** - Import this first (contains school_id and names)
2. **GES_with_ids.csv** - GES data with school_id added
3. **EnrolmentbyInstitutions_with_ids.csv** - Normalized enrolment data
4. **Graduatesbyinstitutions_with_ids.csv** - Normalized graduates data

### Scripts:
- **mysql_schema.sql** - Run this to create your database tables
- **load_data_to_mysql.py** - Run this to import all CSV data into MySQL

## Quick MySQL Setup (3 Steps)

### Step 1: Create Tables
```bash
mysql -u root -p < mysql_schema.sql
```

### Step 2: Configure Loader Script
Edit `load_data_to_mysql.py` and update these lines:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'YOUR_USERNAME',      # ← Change this
    'password': 'YOUR_PASSWORD',  # ← Change this
    'database': 'education_data'
}
```

### Step 3: Load Data
```bash
pip install mysql-connector-python
python load_data_to_mysql.py
```

## Database Structure

```
schools (Master Table)
├── school_id (PRIMARY KEY)
└── school_name

graduate_employment_survey
├── id (PRIMARY KEY)
├── school_id (FOREIGN KEY → schools)
├── year, university, degree
└── employment rates, salaries

enrolment_by_institutions
├── id (PRIMARY KEY)
├── school_id (FOREIGN KEY → schools)
└── year, sex, enrolment

graduates_by_institutions
├── id (PRIMARY KEY)
├── school_id (FOREIGN KEY → schools)
└── year, sex, graduates
```

## Key Changes Made

### Before:
- **GES.csv**: `university` column had text names
- **Enrolment/Graduates**: School names were column headers

### After:
- **GES_with_ids.csv**: Added `school_id` column (keeps `university` for reference)
- **Enrolment/Graduates**: Transformed from wide to long format with `school_id`

### Example Transformation:

**Before (Wide Format):**
| year | sex | nus | ntu | smu |
|------|-----|-----|-----|-----|
| 2020 | F   | 5000| 4000| 2000|

**After (Long Format):**
| year | sex | school_id | school_name | enrolment |
|------|-----|-----------|-------------|-----------|
| 2020 | F   | 9         | National University of Singapore | 5000 |
| 2020 | F   | 7         | Nanyang Technological University | 4000 |
| 2020 | F   | 13        | Singapore Management University | 2000 |

## Sample Queries

### Get employment data by school
```sql
SELECT s.school_name, g.year, g.degree, 
       g.employment_rate_overall, g.gross_monthly_median
FROM graduate_employment_survey g
JOIN schools s ON g.school_id = s.school_id
WHERE s.school_id = 9  -- NUS
ORDER BY g.year DESC;
```

### Compare all universities
```sql
SELECT s.school_name,
       AVG(g.employment_rate_overall) as avg_employment,
       AVG(g.gross_monthly_median) as avg_salary
FROM graduate_employment_survey g
JOIN schools s ON g.school_id = s.school_id
WHERE g.year >= 2018
GROUP BY s.school_id, s.school_name
ORDER BY avg_employment DESC;
```

### Trend analysis
```sql
SELECT e.year,
       SUM(e.enrolment) as total_enrolment,
       SUM(g.graduates) as total_graduates
FROM enrolment_by_institutions e
JOIN graduates_by_institutions g 
    ON e.year = g.year AND e.school_id = g.school_id AND e.sex = g.sex
WHERE e.sex = 'MF'
GROUP BY e.year
ORDER BY e.year;
```

## School ID Reference

| ID | School | Type |
|----|--------|------|
| 1  | Institute of Technical Education | ITE |
| 2  | LASALLE College of the Arts (Degree) | Arts |
| 3  | LASALLE College of the Arts (Diploma) | Arts |
| 4  | Nanyang Academy of Fine Arts (Degree) | Arts |
| 5  | Nanyang Academy of Fine Arts (Diploma) | Arts |
| 6  | Nanyang Polytechnic | Polytechnic |
| 7  | Nanyang Technological University | University |
| 8  | National Institute of Education | Institute |
| 9  | National University of Singapore | University |
| 10 | Ngee Ann Polytechnic | Polytechnic |
| 11 | Republic Polytechnic | Polytechnic |
| 12 | Singapore Institute of Technology | University |
| 13 | Singapore Management University | University |
| 14 | Singapore Polytechnic | Polytechnic |
| 15 | Singapore University of Social Sciences | University |
| 16 | Singapore University of Technology and Design | University |
| 17 | Temasek Polytechnic | Polytechnic |

## Common Use Cases in Your Application

### Backend API Endpoint Example (Flask/Python):
```python
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

@app.route('/api/employment/<int:school_id>')
def get_employment(school_id):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT year, degree, employment_rate_overall, gross_monthly_median
        FROM graduate_employment_survey
        WHERE school_id = %s
        ORDER BY year DESC
    """
    cursor.execute(query, (school_id,))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data)
```

### Frontend JavaScript Example:
```javascript
// Fetch all schools for dropdown
fetch('/api/schools')
    .then(response => response.json())
    .then(schools => {
        const select = document.getElementById('school-select');
        schools.forEach(school => {
            const option = document.createElement('option');
            option.value = school.school_id;
            option.text = school.school_name;
            select.appendChild(option);
        });
    });

// Fetch employment data for selected school
function loadEmploymentData(schoolId) {
    fetch(`/api/employment/${schoolId}`)
        .then(response => response.json())
        .then(data => {
            // Display data in chart or table
            console.log(data);
        });
}
```

## Need Help?

- See `README_SCHOOL_IDS.md` for complete documentation
- Check `mysql_schema.sql` for full database schema
- Review `create_school_ids.py` to understand the transformation logic

## Important Notes

⚠️ **DO NOT** modify school_id values once in production
⚠️ Always use school_id for joins, not school names
✅ School names are kept for reference/display purposes
✅ All foreign key relationships are enforced by MySQL
