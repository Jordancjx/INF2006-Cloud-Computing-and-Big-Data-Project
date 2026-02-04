# Dataset Cleaning Report

## Cleaning Summary

Successfully cleaned all three datasets by removing NA/nil values and duplicate records.

---

## Results

### 1. GES_with_ids.csv → GES_with_ids_cleaned.csv
- **Initial rows:** 1,401
- **NA values removed:** 0 rows (no NA values found)
- **Duplicates removed:** 5 rows
  - Duplicates checked based on: year + school_id + degree
- **Final rows:** 1,396
- **Reduction:** 0.36%

### 2. EnrolmentbyInstitutions_with_ids.csv → EnrolmentbyInstitutions_with_ids_cleaned.csv
- **Initial rows:** 1,462
- **NA values removed:** 504 rows
  - NA values were in the 'enrolment' column
  - These were records where schools didn't exist yet or had no enrolment data
- **Duplicates removed:** 0 rows
- **Final rows:** 958
- **Reduction:** 34.47%

### 3. Graduatesbyinstitutions_with_ids.csv → Graduatesbyinstitutions_with_ids_cleaned.csv
- **Initial rows:** 1,428
- **NA values removed:** 524 rows
  - NA values were in the 'graduates' column
  - These were records where schools didn't exist yet or had no graduate data
- **Duplicates removed:** 0 rows
- **Final rows:** 904
- **Reduction:** 36.69%

---

## Overall Impact

| Metric | Value |
|--------|-------|
| Total rows before cleaning | 4,291 |
| Total rows after cleaning | 3,258 |
| Total rows removed | 1,033 |
| Overall reduction | 24.07% |

---

## Data Quality Verification

✅ **All cleaned datasets have 0 NA values**
✅ **All duplicates removed**
✅ **Data integrity maintained**

### NA Count Verification:
- GES_with_ids_cleaned.csv: **0 NA values**
- EnrolmentbyInstitutions_with_ids_cleaned.csv: **0 NA values**
- Graduatesbyinstitutions_with_ids_cleaned.csv: **0 NA values**

---

## Files Created

### Cleaned Data Files (Ready for MySQL)
1. **GES_with_ids_cleaned.csv** - Employment survey data (1,396 rows)
2. **EnrolmentbyInstitutions_with_ids_cleaned.csv** - Enrolment data (958 rows)
3. **Graduatesbyinstitutions_with_ids_cleaned.csv** - Graduates data (904 rows)

### Script
- **clean_datasets.py** - Cleaning script (can be rerun anytime)

---

## What Was Cleaned

### NA Values
- **Enrolment data:** 504 records with missing enrolment numbers
  - Example: Early years (1982-1990s) before some schools existed
  - New schools like SUTD, SIT, SUSS didn't have data in early years
  
- **Graduates data:** 524 records with missing graduate numbers
  - Similar to enrolment - schools that didn't exist yet

### Duplicates
- **GES data:** 5 duplicate entries
  - Same year, school, and degree program appearing twice
  - Kept the first occurrence, removed duplicates

---

## Usage

### For MySQL Import
The MySQL loader script (`load_data_to_mysql.py`) has been updated to use the cleaned files:
- `GES_with_ids_cleaned.csv`
- `EnrolmentbyInstitutions_with_ids_cleaned.csv`
- `Graduatesbyinstitutions_with_ids_cleaned.csv`

### To Re-clean Data
If you modify the original CSV files and need to re-clean:
```bash
python clean_datasets.py
```

---

## Data Integrity

### Duplicate Detection Logic
- **GES:** Checked for duplicates based on `[year, school_id, degree]`
  - Ensures each degree program per school per year appears only once
  
- **Enrolment:** Checked for duplicates based on `[year, sex, school_id]`
  - Ensures each school's enrolment per gender per year appears only once
  
- **Graduates:** Checked for duplicates based on `[year, sex, school_id]`
  - Ensures each school's graduates per gender per year appears only once

### Foreign Key Integrity Maintained
- All `school_id` values remain valid and link to `schools_lookup.csv`
- No orphaned records created during cleaning

---

## Next Steps

1. ✅ Data is cleaned and ready
2. ✅ MySQL loader script updated to use cleaned files
3. 🔄 **Next:** Import data into MySQL
   - Update credentials in `load_data_to_mysql.py`
   - Run `python load_data_to_mysql.py`

---

## Notes

- **Original files preserved:** The original `*_with_ids.csv` files remain untouched
- **Cleaned files separate:** All cleaned data saved with `_cleaned` suffix
- **Reproducible:** Run `clean_datasets.py` anytime to regenerate cleaned files
- **Safe for production:** All NA values and duplicates removed
