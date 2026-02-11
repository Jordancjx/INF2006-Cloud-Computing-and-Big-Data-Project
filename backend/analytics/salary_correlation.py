import pandas as pd
import numpy as np

def salary_employment_correlation(engine, year=None, school=None):
    # Fetch data from RDS [cite: 554]
    query = "SELECT * FROM graduate_employment_survey"
    df = pd.read_sql(query, engine)
    
    # Load mapping from RDS
    schools_lookup = pd.read_sql("SELECT * FROM school_mapping", engine)
    df = df.merge(schools_lookup, on="school_id", how="left")
    
    # Cleanup and analysis logic
    df["gross_monthly_median"] = pd.to_numeric(df["gross_monthly_median"], errors="coerce")
    df["employment_rate_overall"] = pd.to_numeric(df["employment_rate_overall"], errors="coerce")
    
    if year:
        df = df[df["year"] == year]
    
    analysis = df.groupby("degree").agg({
        "employment_rate_overall": "mean",
        "gross_monthly_median": "mean"
    }).reset_index()
    
    analysis = analysis.rename(columns={
        "gross_monthly_median": "median_salary",
        "employment_rate_overall": "employment_rate"
    })
    
    return {
        "data": analysis.to_dict(orient="records"),
        "correlation_coefficient": analysis["median_salary"].corr(analysis["employment_rate"]),
        "available_schools": schools_lookup["full_name"].unique().tolist()
    }