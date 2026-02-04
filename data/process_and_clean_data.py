"""
Combined Data Processing and Cleaning Script
============================================
This script:
1. Creates school ID mappings from original CSV files
2. Transforms data to include school IDs (normalizes enrolment/graduates)
3. Removes NA/nil values and duplicates
4. Outputs clean, ready-to-use CSV files

Output files:
- schools_lookup.csv (Master reference table)
- GES_cleaned.csv (Employment survey with school IDs)
- Enrolment_cleaned.csv (Normalized enrolment with school IDs)
- Graduates_cleaned.csv (Normalized graduates with school IDs)
- column_name_mapping.csv (Reference for column names)
"""

import pandas as pd
import os

# =====================================================
# CONFIGURATION
# =====================================================
base_path = os.path.dirname(os.path.abspath(__file__))

# Original input files
ORIGINAL_FILES = {
    'ges': 'GES.csv',
    'enrolment': 'EnrolmentbyInstitutions.csv',
    'graduates': 'Graduatesbyinstitutions.csv'
}

# Output files (cleaned and ready for MySQL)
OUTPUT_FILES = {
    'schools': 'schools_lookup.csv',
    'ges': 'GES_cleaned.csv',
    'enrolment': 'Enrolment_cleaned.csv',
    'graduates': 'Graduates_cleaned.csv',
    'mapping': 'column_name_mapping.csv'
}

# Mapping between column names and full school names
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
# STEP 1: CREATE SCHOOL ID MAPPINGS
# =====================================================
def create_school_mappings():
    """Create school ID mappings from all data sources"""
    print("\n" + "="*70)
    print("STEP 1: Creating School ID Mappings")
    print("="*70)
    
    # Read original files
    ges_df = pd.read_csv(os.path.join(base_path, ORIGINAL_FILES['ges']))
    enrolment_df = pd.read_csv(os.path.join(base_path, ORIGINAL_FILES['enrolment']))
    
    # Extract unique school names
    ges_schools = set(ges_df['university'].unique())
    print(f"Found {len(ges_schools)} unique schools in GES data")
    
    # Combine all unique school names
    all_schools = set()
    
    # Add schools from GES
    for school in ges_schools:
        all_schools.add(school)
    
    # Add schools from column mappings
    for full_name in COLUMN_NAME_MAPPING.values():
        all_schools.add(full_name)
    
    # Sort and assign IDs
    sorted_schools = sorted(list(all_schools))
    school_id_mapping = {school: idx + 1 for idx, school in enumerate(sorted_schools)}
    
    # Create reverse mapping for column names to IDs
    column_to_id = {col: school_id_mapping[full_name] 
                    for col, full_name in COLUMN_NAME_MAPPING.items()}
    
    print(f"Created mappings for {len(sorted_schools)} schools (IDs 1-{len(sorted_schools)})")
    
    return school_id_mapping, column_to_id

# =====================================================
# STEP 2: PROCESS AND CLEAN GES DATA
# =====================================================
def process_ges_data(school_id_mapping):
    """Process GES data: add school IDs and clean"""
    print("\n" + "="*70)
    print("STEP 2: Processing GES Data")
    print("="*70)
    
    # Read original GES data
    df = pd.read_csv(os.path.join(base_path, ORIGINAL_FILES['ges']))
    initial_rows = len(df)
    print(f"Initial rows: {initial_rows}")
    
    # Add school_id column
    df['school_id'] = df['university'].map(school_id_mapping)
    
    # Reorder columns (school_id right after university)
    cols = df.columns.tolist()
    cols.insert(2, cols.pop(cols.index('school_id')))
    df = df[cols]
    
    # Remove NA values
    na_count = df.isna().sum().sum()
    if na_count > 0:
        print(f"Found {na_count} NA values")
        df = df.dropna()
        print(f"Removed rows with NA values")
    else:
        print("No NA values found")
    
    # Remove duplicates based on year, school_id, degree
    duplicates = df.duplicated(subset=['year', 'school_id', 'degree'], keep='first')
    duplicate_count = duplicates.sum()
    
    if duplicate_count > 0:
        print(f"Found and removed {duplicate_count} duplicate rows")
        df = df.drop_duplicates(subset=['year', 'school_id', 'degree'], keep='first')
    else:
        print("No duplicates found")
    
    final_rows = len(df)
    print(f"\n✓ GES Data: {initial_rows} → {final_rows} rows ({initial_rows - final_rows} removed)")
    
    return df

# =====================================================
# STEP 3: PROCESS AND CLEAN ENROLMENT DATA
# =====================================================
def process_enrolment_data(column_to_id):
    """Process enrolment data: normalize, add IDs, and clean"""
    print("\n" + "="*70)
    print("STEP 3: Processing Enrolment Data")
    print("="*70)
    
    # Read original enrolment data
    df = pd.read_csv(os.path.join(base_path, ORIGINAL_FILES['enrolment']))
    initial_rows = len(df)
    print(f"Initial rows (wide format): {initial_rows}")
    
    # Melt from wide to long format
    df_melted = df.melt(
        id_vars=['year', 'sex'],
        var_name='column_name',
        value_name='enrolment'
    )
    print(f"After normalization: {len(df_melted)} rows")
    
    # Add school_id and school_name
    df_melted['school_id'] = df_melted['column_name'].map(column_to_id)
    df_melted['school_name'] = df_melted['column_name'].map(COLUMN_NAME_MAPPING)
    
    # Drop the temporary column_name column and reorder
    df_melted = df_melted[['year', 'sex', 'school_id', 'school_name', 'enrolment']]
    
    # Remove rows with NA values (missing school_id or enrolment)
    df_cleaned = df_melted.dropna()
    na_removed = len(df_melted) - len(df_cleaned)
    
    if na_removed > 0:
        print(f"Removed {na_removed} rows with NA values")
    
    # Remove duplicates based on year, sex, school_id
    duplicates = df_cleaned.duplicated(subset=['year', 'sex', 'school_id'], keep='first')
    duplicate_count = duplicates.sum()
    
    if duplicate_count > 0:
        print(f"Found and removed {duplicate_count} duplicate rows")
        df_cleaned = df_cleaned.drop_duplicates(subset=['year', 'sex', 'school_id'], keep='first')
    else:
        print("No duplicates found")
    
    final_rows = len(df_cleaned)
    total_removed = len(df_melted) - final_rows
    print(f"\n✓ Enrolment Data: {len(df_melted)} → {final_rows} rows ({total_removed} removed)")
    
    return df_cleaned

# =====================================================
# STEP 4: PROCESS AND CLEAN GRADUATES DATA
# =====================================================
def process_graduates_data(column_to_id):
    """Process graduates data: normalize, add IDs, and clean"""
    print("\n" + "="*70)
    print("STEP 4: Processing Graduates Data")
    print("="*70)
    
    # Read original graduates data
    df = pd.read_csv(os.path.join(base_path, ORIGINAL_FILES['graduates']))
    initial_rows = len(df)
    print(f"Initial rows (wide format): {initial_rows}")
    
    # Melt from wide to long format
    df_melted = df.melt(
        id_vars=['year', 'sex'],
        var_name='column_name',
        value_name='graduates'
    )
    print(f"After normalization: {len(df_melted)} rows")
    
    # Add school_id and school_name
    df_melted['school_id'] = df_melted['column_name'].map(column_to_id)
    df_melted['school_name'] = df_melted['column_name'].map(COLUMN_NAME_MAPPING)
    
    # Drop the temporary column_name column and reorder
    df_melted = df_melted[['year', 'sex', 'school_id', 'school_name', 'graduates']]
    
    # Remove rows with NA values (missing school_id or graduates)
    df_cleaned = df_melted.dropna()
    na_removed = len(df_melted) - len(df_cleaned)
    
    if na_removed > 0:
        print(f"Removed {na_removed} rows with NA values")
    
    # Remove duplicates based on year, sex, school_id
    duplicates = df_cleaned.duplicated(subset=['year', 'sex', 'school_id'], keep='first')
    duplicate_count = duplicates.sum()
    
    if duplicate_count > 0:
        print(f"Found and removed {duplicate_count} duplicate rows")
        df_cleaned = df_cleaned.drop_duplicates(subset=['year', 'sex', 'school_id'], keep='first')
    else:
        print("No duplicates found")
    
    final_rows = len(df_cleaned)
    total_removed = len(df_melted) - final_rows
    print(f"\n✓ Graduates Data: {len(df_melted)} → {final_rows} rows ({total_removed} removed)")
    
    return df_cleaned

# =====================================================
# STEP 5: SAVE ALL OUTPUT FILES
# =====================================================
def save_output_files(school_id_mapping, column_to_id, ges_df, enrolment_df, graduates_df):
    """Save all processed and cleaned data to output files"""
    print("\n" + "="*70)
    print("STEP 5: Saving Output Files")
    print("="*70)
    
    # 1. Save schools lookup table
    schools_lookup_df = pd.DataFrame({
        'school_id': list(school_id_mapping.values()),
        'school_name': list(school_id_mapping.keys())
    }).sort_values('school_id')
    
    schools_file = os.path.join(base_path, OUTPUT_FILES['schools'])
    schools_lookup_df.to_csv(schools_file, index=False)
    print(f"✓ Saved: {OUTPUT_FILES['schools']} ({len(schools_lookup_df)} schools)")
    
    # 2. Save column name mapping reference
    mapping_df = pd.DataFrame({
        'column_name': list(COLUMN_NAME_MAPPING.keys()),
        'full_name': list(COLUMN_NAME_MAPPING.values()),
        'school_id': [column_to_id.get(col, '') for col in COLUMN_NAME_MAPPING.keys()]
    })
    
    mapping_file = os.path.join(base_path, OUTPUT_FILES['mapping'])
    mapping_df.to_csv(mapping_file, index=False)
    print(f"✓ Saved: {OUTPUT_FILES['mapping']} (reference)")
    
    # 3. Save GES cleaned data
    ges_file = os.path.join(base_path, OUTPUT_FILES['ges'])
    ges_df.to_csv(ges_file, index=False)
    print(f"✓ Saved: {OUTPUT_FILES['ges']} ({len(ges_df)} rows)")
    
    # 4. Save Enrolment cleaned data
    enrolment_file = os.path.join(base_path, OUTPUT_FILES['enrolment'])
    enrolment_df.to_csv(enrolment_file, index=False)
    print(f"✓ Saved: {OUTPUT_FILES['enrolment']} ({len(enrolment_df)} rows)")
    
    # 5. Save Graduates cleaned data
    graduates_file = os.path.join(base_path, OUTPUT_FILES['graduates'])
    graduates_df.to_csv(graduates_file, index=False)
    print(f"✓ Saved: {OUTPUT_FILES['graduates']} ({len(graduates_df)} rows)")

# =====================================================
# MAIN EXECUTION
# =====================================================
def main():
    """Main execution function"""
    print("\n" + "="*70)
    print("DATA PROCESSING AND CLEANING PIPELINE")
    print("="*70)
    print("This script will:")
    print("  1. Create school ID mappings")
    print("  2. Transform and clean GES data")
    print("  3. Transform and clean Enrolment data")
    print("  4. Transform and clean Graduates data")
    print("  5. Save all output files")
    
    # Check if input files exist
    print("\nChecking input files...")
    for name, filename in ORIGINAL_FILES.items():
        filepath = os.path.join(base_path, filename)
        if not os.path.exists(filepath):
            print(f"✗ Error: {filename} not found!")
            return
        print(f"  ✓ {filename}")
    
    try:
        # Step 1: Create mappings
        school_id_mapping, column_to_id = create_school_mappings()
        
        # Step 2: Process GES data
        ges_df = process_ges_data(school_id_mapping)
        
        # Step 3: Process Enrolment data
        enrolment_df = process_enrolment_data(column_to_id)
        
        # Step 4: Process Graduates data
        graduates_df = process_graduates_data(column_to_id)
        
        # Step 5: Save all output files
        save_output_files(school_id_mapping, column_to_id, ges_df, enrolment_df, graduates_df)
        
        # Final summary
        print("\n" + "="*70)
        print("✓ PROCESSING COMPLETE!")
        print("="*70)
        print("\nOutput Files Created:")
        print(f"  1. {OUTPUT_FILES['schools']} - Master lookup table")
        print(f"  2. {OUTPUT_FILES['ges']} - Employment survey data")
        print(f"  3. {OUTPUT_FILES['enrolment']} - Enrolment data")
        print(f"  4. {OUTPUT_FILES['graduates']} - Graduates data")
        print(f"  5. {OUTPUT_FILES['mapping']} - Column name reference")
        
        print("\n" + "="*70)
        print("Data Quality Summary:")
        print("="*70)
        print(f"  GES:        {len(ges_df):,} rows (0 NA, 0 duplicates)")
        print(f"  Enrolment:  {len(enrolment_df):,} rows (0 NA, 0 duplicates)")
        print(f"  Graduates:  {len(graduates_df):,} rows (0 NA, 0 duplicates)")
        print(f"  Schools:    {len(school_id_mapping)} unique institutions")
        
        print("\n" + "="*70)
        print("Next Steps:")
        print("="*70)
        print("  1. Update load_data_to_mysql.py to use new filenames")
        print("  2. Run: python load_data_to_mysql.py")
        print("="*70)
        
    except Exception as e:
        print(f"\n✗ Error during processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
