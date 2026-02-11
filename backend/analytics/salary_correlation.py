import pandas as pd
import numpy as np

def salary_employment_correlation(engine, year=None, school=None):
    # Fetch data from RDS
    query = "SELECT * FROM graduate_employment_survey"
    df = pd.read_sql(query, engine)
    
    # Load mapping from RDS
    schools_lookup = pd.read_sql("SELECT * FROM school_mapping", engine)
    df = df.merge(schools_lookup, on="school_id", how="left")
    
    # Cleanup and analysis logic
    df["gross_monthly_median"] = pd.to_numeric(df["gross_monthly_median"], errors="coerce")
    df["employment_rate_overall"] = pd.to_numeric(df["employment_rate_overall"], errors="coerce")
    
    # Get available years and schools
    available_years = sorted(df["year"].dropna().unique().tolist())
    available_schools = sorted(df["full_name"].dropna().unique().tolist())
    
    # Filter by year (use latest if not specified)
    if year is None:
        year = int(max(available_years))
    
    year_df = df[df["year"] == year].copy()
    
    # Filter by school if specified
    if school:
        year_df = year_df[year_df["full_name"] == school].copy()
    
    # Remove rows with missing key values and filter out 'na' entries
    year_df = year_df.dropna(subset=["employment_rate_overall", "gross_monthly_median", "degree", "full_name"])
    year_df = year_df[year_df["degree"].str.lower() != "na"]
    
    # Aggregate differently based on whether a specific school is selected
    if school:
        # If specific school selected, group by degree only
        analysis_df = year_df.groupby("degree").agg({
            "employment_rate_overall": "mean",
            "gross_monthly_median": "mean",
            "full_name": "first"
        }).reset_index()
    else:
        # If viewing all schools, group by both degree and school
        analysis_df = year_df.groupby(["degree", "full_name"]).agg({
            "employment_rate_overall": "mean",
            "gross_monthly_median": "mean"
        }).reset_index()
    
    # Round values
    analysis_df["employment_rate_overall"] = analysis_df["employment_rate_overall"].round(1)
    analysis_df["gross_monthly_median"] = analysis_df["gross_monthly_median"].round(0)
    
    # Calculate correlation coefficient
    correlation_coefficient = analysis_df["gross_monthly_median"].corr(analysis_df["employment_rate_overall"]) if len(analysis_df) > 1 else 0
    
    # Prepare scatter plot data (include school information)
    scatter_data = []
    for _, row in analysis_df.iterrows():
        scatter_data.append({
            "degree": row["degree"],
            "school": row["full_name"],
            "employment_rate": row["employment_rate_overall"],
            "median_salary": row["gross_monthly_median"]
        })
    
    # Sort by median salary descending
    scatter_data = sorted(scatter_data, key=lambda x: x["median_salary"], reverse=True)
    
    return {
        "year": int(year),
        "available_years": [int(y) for y in available_years],
        "available_schools": available_schools,
        "selected_school": school,
        "data": scatter_data,
        "correlation_coefficient": round(correlation_coefficient, 3) if not pd.isna(correlation_coefficient) else None
    }


def degree_historical_trends(engine, degree_name, school_name=None):
    """
    Get historical salary and employment trends for a specific degree over all years.
    
    Args:
        engine: SQLAlchemy engine
        degree_name: Name of the degree to analyze
        school_name: Optional school filter (if None, aggregates across all schools)
    
    Returns:
        Dictionary with year-by-year salary and employment data
    """
    # Fetch data from RDS
    query = "SELECT * FROM graduate_employment_survey"
    df = pd.read_sql(query, engine)
    
    # Load mapping from RDS
    schools_lookup = pd.read_sql("SELECT * FROM school_mapping", engine)
    df = df.merge(schools_lookup, on="school_id", how="left")
    
    # Clean numeric columns
    df["employment_rate_overall"] = pd.to_numeric(df["employment_rate_overall"], errors="coerce")
    df["gross_monthly_median"] = pd.to_numeric(df["gross_monthly_median"], errors="coerce")
    
    # Filter by degree name
    filtered_df = df[df["degree"] == degree_name].copy()
    
    # Filter by school if specified
    if school_name:
        filtered_df = filtered_df[filtered_df["full_name"] == school_name].copy()
    
    if len(filtered_df) == 0:
        return {
            "degree": degree_name,
            "school": school_name,
            "schools_offering": [],
            "trends": [],
            "total_years": 0
        }
    
    # Remove rows with missing values
    filtered_df = filtered_df.dropna(subset=["year", "employment_rate_overall", "gross_monthly_median"])
    
    # Get list of schools offering this degree
    schools_offering = sorted(filtered_df["full_name"].unique().tolist())
    
    # Aggregate by year
    yearly_trends = filtered_df.groupby("year").agg({
        "employment_rate_overall": "mean",
        "gross_monthly_median": "mean"
    }).reset_index()
    
    # Round values
    yearly_trends["employment_rate_overall"] = yearly_trends["employment_rate_overall"].round(1)
    yearly_trends["gross_monthly_median"] = yearly_trends["gross_monthly_median"].round(0)
    
    # Convert to list of dicts
    trends = []
    for _, row in yearly_trends.iterrows():
        trends.append({
            "year": int(row["year"]),
            "employment_rate": row["employment_rate_overall"],
            "median_salary": row["gross_monthly_median"]
        })
    
    return {
        "degree": degree_name,
        "school": school_name,
        "schools_offering": schools_offering,
        "trends": trends,
        "total_years": len(trends)
    }
