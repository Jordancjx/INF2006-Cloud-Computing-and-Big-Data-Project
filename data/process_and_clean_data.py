"""
Combined Data Processing and Cleaning Script (Improved)
=====================================================
Optimized to handle string-based placeholders like '-' or 'na'.
"""

import pandas as pd
import os

# =====================================================
# CONFIGURATION
# =====================================================
base_path = os.path.dirname(os.path.abspath(__file__))

ORIGINAL_FILES = {
    'ges': 'GES.csv',
    'enrolment': 'EnrolmentbyInstitutions.csv',
    'graduates': 'Graduatesbyinstitutions.csv'
}

OUTPUT_FILES = {
    'schools': 'schools_lookup.csv',
    'ges': 'GES_cleaned.csv',
    'enrolment': 'Enrolment_cleaned.csv',
    'graduates': 'Graduates_cleaned.csv',
    'mapping': 'column_name_mapping.csv'
}

COLUMN_NAME_MAPPING = {
    'nus': 'National University of Singapore',
    'ntu': 'Nanyang Technological University',
    'smu': 'Singapore Management University',
    'sit': 'Singapore Institute of Technology',
    'sutd': 'Singapore University of Technology and Design',
    'suss': 'Singapore University of Social Sciences',
    'nie': 'National Institute of Education',
    'singapore_polytechnic': 'Singapore Polytechnic',
    'ngee_ann_polytechnic': 'Ngee Ann Polytechnic',
    'temasek_polytechnic': 'Temasek Polytechnic',
    'nanyang_polytechnic': 'Nanyang Polytechnic',
    'republic_polytechnic': 'Republic Polytechnic',
    'lasalle_diploma': 'LASALLE College of the Arts (Diploma)',
    'lasalle_degree': 'LASALLE College of the Arts (Degree)',
    'nafa_diploma': 'Nanyang Academy of Fine Arts (Diploma)',
    'nafa_degree': 'Nanyang Academy of Fine Arts (Degree)',
    'ite': 'Institute of Technical Education'
}

# =====================================================
# HELPER: CLEAN NUMERIC COLUMNS
# =====================================================
def clean_numeric_column(df, column_name):
    """Converts strings like 'na' or '-' to actual NaN and then to numeric"""
    if column_name in df.columns:
        # Strip whitespace, replace placeholders with NaN, remove commas
        df[column_name] = df[column_name].astype(str).str.replace(',', '').str.strip()
        df[column_name] = pd.to_numeric(df[column_name], errors='coerce')
    return df

# =====================================================
# STEP 1: CREATE SCHOOL ID MAPPINGS
# =====================================================
def create_school_mappings():
    print("\nSTEP 1: Creating School ID Mappings")
    
    ges_df = pd.read_csv(os.path.join(base_path, ORIGINAL_FILES['ges']))
    
    # Standardize school names by stripping whitespace
    ges_df['university'] = ges_df['university'].astype(str).str.strip()
    ges_schools = set(ges_df['university'].unique())
    
    all_schools = set()
    for school in ges_schools:
        all_schools.add(school)
    for full_name in COLUMN_NAME_MAPPING.values():
        all_schools.add(full_name.strip())
    
    sorted_schools = sorted(list(all_schools))
    school_id_mapping = {school: idx + 1 for idx, school in enumerate(sorted_schools)}
    
    column_to_id = {col: school_id_mapping[full_name.strip()] 
                    for col, full_name in COLUMN_NAME_MAPPING.items()}
    
    return school_id_mapping, column_to_id

# =====================================================
# STEP 2: PROCESS AND CLEAN GES DATA
# =====================================================
def process_ges_data(school_id_mapping):
    print("\nSTEP 2: Processing GES Data")
    df = pd.read_csv(os.path.join(base_path, ORIGINAL_FILES['ges']))
    
    # 1. Standardize names
    df['university'] = df['university'].astype(str).str.strip()
    df['school_id'] = df['university'].map(school_id_mapping)
    
    # 2. Clean numeric columns (Salaries and Rates)
    numeric_cols = ['employment_rate_overall', 'employment_rate_ft_perm', 
                    'basic_monthly_mean', 'basic_monthly_median', 
                    'gross_monthly_mean', 'gross_monthly_median', 'gross_mthly_25_percentile', 'gross_mthly_75_percentile']
    
    for col in numeric_cols:
        df = clean_numeric_column(df, col)
    
    # 3. Drop NAs and Duplicates
    df = df.dropna()
    df = df.drop_duplicates(subset=['year', 'school_id', 'degree'], keep='first')
    
    return df

# =====================================================
# STEP 3: PROCESS AND CLEAN ENROLMENT/GRADUATES DATA
# =====================================================
def process_institutional_data(file_key, column_to_id, value_name):
    print(f"\nSTEP 3/4: Processing {file_key.capitalize()} Data")
    df = pd.read_csv(os.path.join(base_path, ORIGINAL_FILES[file_key]))
    
    # Melt to long format
    df_melted = df.melt(id_vars=['year', 'sex'], var_name='column_name', value_name=value_name)
    
    # Add IDs
    df_melted['school_id'] = df_melted['column_name'].map(column_to_id)
    df_melted['school_name'] = df_melted['column_name'].map(COLUMN_NAME_MAPPING)
    
    # Clean the numeric value (enrolment or graduates)
    df_melted = clean_numeric_column(df_melted, value_name)
    
    # Final cleanup
    df_cleaned = df_melted.dropna(subset=['school_id', value_name])
    df_cleaned = df_cleaned.drop_duplicates(subset=['year', 'sex', 'school_id'])
    
    return df_cleaned[['year', 'sex', 'school_id', 'school_name', value_name]]

# =====================================================
# STEP 5: SAVE OUTPUT
# =====================================================
def save_output_files(school_id_mapping, column_to_id, ges_df, enrolment_df, graduates_df):
    print("\nSTEP 5: Saving Output Files")
    
    # Save Schools Lookup
    schools_lookup_df = pd.DataFrame({
        'school_id': list(school_id_mapping.values()),
        'school_name': list(school_id_mapping.keys())
    }).sort_values('school_id')
    schools_lookup_df.to_csv(os.path.join(base_path, OUTPUT_FILES['schools']), index=False)
    
    # Save Data
    ges_df.to_csv(os.path.join(base_path, OUTPUT_FILES['ges']), index=False)
    enrolment_df.to_csv(os.path.join(base_path, OUTPUT_FILES['enrolment']), index=False)
    graduates_df.to_csv(os.path.join(base_path, OUTPUT_FILES['graduates']), index=False)
    
    # Save Column Map
    mapping_df = pd.DataFrame({
        'column_name': list(COLUMN_NAME_MAPPING.keys()),
        'full_name': list(COLUMN_NAME_MAPPING.values()),
        'school_id': [column_to_id.get(col) for col in COLUMN_NAME_MAPPING.keys()]
    })
    mapping_df.to_csv(os.path.join(base_path, OUTPUT_FILES['mapping']), index=False)
    print("✓ All files saved and cleaned.")

def main():
    try:
        school_id_mapping, column_to_id = create_school_mappings()
        ges_df = process_ges_data(school_id_mapping)
        enrolment_df = process_institutional_data('enrolment', column_to_id, 'enrolment')
        graduates_df = process_institutional_data('graduates', column_to_id, 'graduates')
        save_output_files(school_id_mapping, column_to_id, ges_df, enrolment_df, graduates_df)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()