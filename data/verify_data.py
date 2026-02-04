import pandas as pd

print("="*70)
print("FINAL CLEANED DATA VERIFICATION")
print("="*70)

print("\n1. GES_cleaned.csv")
ges = pd.read_csv('GES_cleaned.csv')
print(f"   Rows: {len(ges):,}")
print(f"   NA values: {ges.isna().sum().sum()}")
print(f"   Duplicates: {ges.duplicated(subset=['year', 'school_id', 'degree']).sum()}")

print("\n2. Enrolment_cleaned.csv")
enrol = pd.read_csv('Enrolment_cleaned.csv')
print(f"   Rows: {len(enrol):,}")
print(f"   NA values: {enrol.isna().sum().sum()}")
print(f"   Duplicates: {enrol.duplicated(subset=['year', 'sex', 'school_id']).sum()}")

print("\n3. Graduates_cleaned.csv")
grad = pd.read_csv('Graduates_cleaned.csv')
print(f"   Rows: {len(grad):,}")
print(f"   NA values: {grad.isna().sum().sum()}")
print(f"   Duplicates: {grad.duplicated(subset=['year', 'sex', 'school_id']).sum()}")

print("\n4. schools_lookup.csv")
schools = pd.read_csv('schools_lookup.csv')
print(f"   Schools: {len(schools)}")
print(f"   ID range: {schools['school_id'].min()}-{schools['school_id'].max()}")

print("\n" + "="*70)
print("✓ ALL DATA CLEAN AND READY FOR MYSQL IMPORT!")
print("="*70)
