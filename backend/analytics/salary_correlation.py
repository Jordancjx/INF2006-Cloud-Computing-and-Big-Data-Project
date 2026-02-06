import pandas as pd
import numpy as np
import os

def clean_numeric_column(series):
    """Clean numeric columns by removing % and handling N.A. values"""
    return pd.to_numeric(
        series.astype(str)
              .str.replace("%", "", regex=False)
              .str.replace(",", "", regex=False)
              .replace(["N.A.", "na", "NA", "-"], pd.NA),
        errors="coerce"
    )

def calculate_correlation(x, y):
    """Calculate Pearson correlation coefficient between two arrays"""
    # Remove pairs where either value is NaN
    mask = ~(np.isnan(x) | np.isnan(y))
    x_clean = x[mask]
    y_clean = y[mask]
    
    if len(x_clean) < 2:
        return None
    
    # Calculate correlation
    correlation = np.corrcoef(x_clean, y_clean)[0, 1]
    return round(float(correlation), 3) if not np.isnan(correlation) else None

def salary_employment_correlation(csv_path, year=None, school=None):
    """
    Analyze correlation between salary and employment rates by degree/school.
    
    Args:
        csv_path: Path to GES_cleaned.csv
        year: Optional year filter (if None, uses latest year)
        school: Optional school filter by university name (if None, shows all schools)
    
    Returns:
        Dictionary with correlation data, scatter plot data, and statistics
    """
    df = pd.read_csv(csv_path)
    
    # Load school lookup table to get proper school names
    base_dir = os.path.dirname(csv_path)
    schools_lookup = pd.read_csv(os.path.join(base_dir, "schools_lookup.csv"))
    
    # Merge to get proper school names using school_id
    df = df.merge(schools_lookup, on="school_id", how="left")
    
    # Clean numeric columns
    df["employment_rate_overall"] = clean_numeric_column(df["employment_rate_overall"])
    df["employment_rate_ft_perm"] = clean_numeric_column(df["employment_rate_ft_perm"])
    df["gross_monthly_median"] = clean_numeric_column(df["gross_monthly_median"])
    df["basic_monthly_median"] = clean_numeric_column(df["basic_monthly_median"])
    
    # Get available years and schools (using school_name from lookup)
    available_years = sorted(df["year"].dropna().unique().tolist())
    available_schools = sorted(df["school_name"].dropna().unique().tolist())
    
    # Filter by year (use latest if not specified)
    if year is None:
        year = int(max(available_years))
    
    year_df = df[df["year"] == year].copy()
    
    # Filter by school if specified (using school_name from lookup)
    if school:
        year_df = year_df[year_df["school_name"] == school].copy()
    
    # Remove rows with missing key values
    year_df = year_df.dropna(subset=["employment_rate_overall", "gross_monthly_median"])
    
    # Aggregate by faculty/school (the "school" column which contains faculty names)
    # This shows faculties like "College of Engineering", "College of Business", etc.
    analysis_df = year_df.groupby("school").agg({
        "employment_rate_overall": "mean",
        "employment_rate_ft_perm": "mean",
        "gross_monthly_median": "mean",
        "basic_monthly_median": "mean"
    }).reset_index()
    analysis_df = analysis_df.rename(columns={"school": "label"})
    
    # Round values
    analysis_df["employment_rate_overall"] = analysis_df["employment_rate_overall"].round(1)
    analysis_df["employment_rate_ft_perm"] = analysis_df["employment_rate_ft_perm"].round(1)
    analysis_df["gross_monthly_median"] = analysis_df["gross_monthly_median"].round(0)
    analysis_df["basic_monthly_median"] = analysis_df["basic_monthly_median"].round(0)
    
    # Calculate correlation coefficient
    correlation_coefficient = calculate_correlation(
        analysis_df["gross_monthly_median"].values,
        analysis_df["employment_rate_overall"].values
    )
    
    # Prepare scatter plot data (rename for frontend compatibility)
    scatter_data = []
    for _, row in analysis_df.iterrows():
        scatter_data.append({
            "degree": row["label"],  # Using label (school or degree name)
            "employment_rate": row["employment_rate_overall"],
            "median_salary": row["gross_monthly_median"]
        })
    
    # Sort by median salary descending
    scatter_data = sorted(scatter_data, key=lambda x: x["median_salary"], reverse=True)
    
    # Calculate summary statistics
    avg_salary = analysis_df["gross_monthly_median"].mean()
    avg_employment = analysis_df["employment_rate_overall"].mean()
    max_salary_item = analysis_df.loc[analysis_df["gross_monthly_median"].idxmax()]
    min_salary_item = analysis_df.loc[analysis_df["gross_monthly_median"].idxmin()]
    
    return {
        "year": int(year),
        "available_years": [int(y) for y in available_years],
        "available_schools": available_schools,
        "selected_school": school,
        "data": scatter_data,
        "correlation_coefficient": correlation_coefficient,
        "statistics": {
            "avg_median_salary": round(avg_salary, 0) if not pd.isna(avg_salary) else None,
            "avg_employment_rate": round(avg_employment, 1) if not pd.isna(avg_employment) else None,
            "highest_salary_school": {
                "name": max_salary_item["label"],
                "salary": max_salary_item["gross_monthly_median"],
                "employment_rate": max_salary_item["employment_rate_overall"]
            },
            "lowest_salary_school": {
                "name": min_salary_item["label"],
                "salary": min_salary_item["gross_monthly_median"],
                "employment_rate": min_salary_item["employment_rate_overall"]
            },
            "total_schools_analyzed": len(scatter_data)
        },
        "interpretation": get_correlation_interpretation(correlation_coefficient)
    }

def get_correlation_interpretation(correlation):
    """Provide interpretation of the correlation coefficient"""
    if correlation is None:
        return "Insufficient data to calculate correlation"
    
    abs_corr = abs(correlation)
    direction = "positive" if correlation > 0 else "negative"
    
    if abs_corr >= 0.7:
        strength = "strong"
    elif abs_corr >= 0.4:
        strength = "moderate"
    elif abs_corr >= 0.2:
        strength = "weak"
    else:
        strength = "very weak or no"
    
    return f"There is a {strength} {direction} correlation (r={correlation}) between median salary and employment rate."
