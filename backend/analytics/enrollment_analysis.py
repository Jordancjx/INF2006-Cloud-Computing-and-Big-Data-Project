import pandas as pd
import numpy as np

def clean_numeric_column(series):
    """Clean numeric columns by handling NaN and converting to int where possible"""
    return pd.to_numeric(series, errors="coerce")

def enrollment_graduate_analysis(enrolment_path, graduates_path, start_year=None, end_year=None, school_id=None):
    """
    Analyze enrollment vs graduates trends over time.
    
    Args:
        enrolment_path: Path to Enrolment_cleaned.csv
        graduates_path: Path to Graduates_cleaned.csv
        start_year: Optional start year filter
        end_year: Optional end year filter
        school_id: Optional school_id filter (if None, aggregates all schools)
    
    Returns:
        Dictionary with enrollment/graduate trends and statistics
    """
    # Load data
    enrol_df = pd.read_csv(enrolment_path)
    grad_df = pd.read_csv(graduates_path)
    
    # Clean numeric columns
    enrol_df["enrolment"] = clean_numeric_column(enrol_df["enrolment"])
    grad_df["graduates"] = clean_numeric_column(grad_df["graduates"])
    
    # Filter for total (MF = Male + Female combined) to avoid double counting
    enrol_df = enrol_df[enrol_df["sex"] == "MF"].copy()
    grad_df = grad_df[grad_df["sex"] == "MF"].copy()
    
    # Get available years
    all_years = sorted(set(enrol_df["year"].unique()) & set(grad_df["year"].unique()))
    
    # Set default year range
    if start_year is None:
        start_year = min(all_years) if all_years else 2010
    if end_year is None:
        end_year = max(all_years) if all_years else 2023
    
    # Filter by year range
    enrol_df = enrol_df[(enrol_df["year"] >= start_year) & (enrol_df["year"] <= end_year)]
    grad_df = grad_df[(grad_df["year"] >= start_year) & (grad_df["year"] <= end_year)]
    
    # Get unique schools
    schools = enrol_df[["school_id", "school_name"]].drop_duplicates().to_dict("records")
    
    # Filter by school if specified
    if school_id is not None:
        enrol_df = enrol_df[enrol_df["school_id"] == school_id]
        grad_df = grad_df[grad_df["school_id"] == school_id]
        school_name = enrol_df["school_name"].iloc[0] if len(enrol_df) > 0 else "Unknown"
    else:
        school_name = "All Schools"
    
    # Aggregate by year
    enrol_by_year = enrol_df.groupby("year")["enrolment"].sum().reset_index()
    grad_by_year = grad_df.groupby("year")["graduates"].sum().reset_index()
    
    # Merge enrollment and graduates data
    merged = pd.merge(enrol_by_year, grad_by_year, on="year", how="outer")
    merged = merged.sort_values("year")
    
    # Calculate completion rate (graduates / enrolment from ~4 years ago for degree programs)
    # Using simple ratio for current year as approximation
    merged["completion_rate"] = (merged["graduates"] / merged["enrolment"] * 100).round(1)
    
    # Calculate year-over-year growth
    merged["enrolment_growth"] = merged["enrolment"].pct_change() * 100
    merged["graduates_growth"] = merged["graduates"].pct_change() * 100
    
    # Prepare trend data for frontend
    trend_data = []
    for _, row in merged.iterrows():
        trend_data.append({
            "year": int(row["year"]),
            "school_name": school_name,
            "enrolment": int(row["enrolment"]) if pd.notna(row["enrolment"]) else None,
            "graduates": int(row["graduates"]) if pd.notna(row["graduates"]) else None,
            "completion_rate": row["completion_rate"] if pd.notna(row["completion_rate"]) else None,
            "enrolment_growth": round(row["enrolment_growth"], 1) if pd.notna(row["enrolment_growth"]) else None,
            "graduates_growth": round(row["graduates_growth"], 1) if pd.notna(row["graduates_growth"]) else None
        })
    
    # Calculate summary statistics
    total_enrolment = merged["enrolment"].sum()
    total_graduates = merged["graduates"].sum()
    avg_completion_rate = merged["completion_rate"].mean()
    
    # Calculate trend (linear regression slope)
    enrol_trend = calculate_trend(merged["year"].values, merged["enrolment"].values)
    grad_trend = calculate_trend(merged["year"].values, merged["graduates"].values)
    
    # School breakdown (if showing all schools)
    school_breakdown = None
    if school_id is None:
        school_breakdown = get_school_breakdown(enrol_df, grad_df, start_year, end_year)
    
    return {
        "start_year": int(start_year),
        "end_year": int(end_year),
        "school_name": school_name,
        "available_years": [int(y) for y in all_years],
        "available_schools": schools,
        "data": trend_data,
        "average_completion_rate": round(avg_completion_rate, 1) if pd.notna(avg_completion_rate) else None,
        "statistics": {
            "total_enrolment": int(total_enrolment) if pd.notna(total_enrolment) else None,
            "total_graduates": int(total_graduates) if pd.notna(total_graduates) else None,
            "enrolment_trend": enrol_trend,
            "graduates_trend": grad_trend,
            "enrolment_trend_interpretation": get_trend_interpretation(enrol_trend, "Enrolment"),
            "graduates_trend_interpretation": get_trend_interpretation(grad_trend, "Graduates")
        },
        "school_breakdown": school_breakdown
    }

def calculate_trend(years, values):
    """Calculate linear trend (slope) for a time series"""
    mask = ~np.isnan(values)
    if mask.sum() < 2:
        return None
    
    x = years[mask].astype(float)
    y = values[mask].astype(float)
    
    slope, _ = np.polyfit(x, y, 1)
    return round(float(slope), 1)

def get_trend_interpretation(slope, metric):
    """Provide interpretation of the trend"""
    if slope is None:
        return "Insufficient data to calculate trend"
    
    if abs(slope) < 100:
        return f"{metric} has remained relatively stable over the period"
    elif slope > 0:
        return f"{metric} shows an increasing trend (+{slope:.0f} per year)"
    else:
        return f"{metric} shows a decreasing trend ({slope:.0f} per year)"

def get_school_breakdown(enrol_df, grad_df, start_year, end_year):
    """Get breakdown by school for the specified period"""
    # Aggregate by school
    enrol_by_school = enrol_df.groupby(["school_id", "school_name"])["enrolment"].sum().reset_index()
    grad_by_school = grad_df.groupby(["school_id", "school_name"])["graduates"].sum().reset_index()
    
    # Merge
    merged = pd.merge(enrol_by_school, grad_by_school, on=["school_id", "school_name"], how="outer")
    merged["completion_rate"] = (merged["graduates"] / merged["enrolment"] * 100).round(1)
    
    # Sort by enrolment
    merged = merged.sort_values("enrolment", ascending=False)
    
    breakdown = []
    for _, row in merged.iterrows():
        breakdown.append({
            "school_id": int(row["school_id"]),
            "school_name": row["school_name"],
            "total_enrolment": int(row["enrolment"]) if pd.notna(row["enrolment"]) else 0,
            "total_graduates": int(row["graduates"]) if pd.notna(row["graduates"]) else 0,
            "completion_rate": row["completion_rate"] if pd.notna(row["completion_rate"]) else None
        })
    
    return breakdown

def enrollment_by_school_for_year(enrolment_path, graduates_path, year):
    """
    Get school breakdown for a specific year.
    
    Args:
        enrolment_path: Path to Enrolment_cleaned.csv
        graduates_path: Path to Graduates_cleaned.csv
        year: The year to filter by
    
    Returns:
        Dictionary with school breakdown data for the specified year
    """
    # Load data
    enrol_df = pd.read_csv(enrolment_path)
    grad_df = pd.read_csv(graduates_path)
    
    # Clean numeric columns
    enrol_df["enrolment"] = clean_numeric_column(enrol_df["enrolment"])
    grad_df["graduates"] = clean_numeric_column(grad_df["graduates"])
    
    # Filter for total (MF = Male + Female combined) to avoid double counting
    enrol_df = enrol_df[enrol_df["sex"] == "MF"].copy()
    grad_df = grad_df[grad_df["sex"] == "MF"].copy()
    
    # Filter by year
    enrol_df = enrol_df[enrol_df["year"] == year]
    grad_df = grad_df[grad_df["year"] == year]
    
    # Drop NaN values
    enrol_df = enrol_df.dropna(subset=["enrolment"])
    grad_df = grad_df.dropna(subset=["graduates"])
    
    # Aggregate by school
    enrol_by_school = enrol_df.groupby(["school_id", "school_name"])["enrolment"].sum().reset_index()
    grad_by_school = grad_df.groupby(["school_id", "school_name"])["graduates"].sum().reset_index()
    
    # Merge
    merged = pd.merge(enrol_by_school, grad_by_school, on=["school_id", "school_name"], how="outer")
    merged["completion_rate"] = (merged["graduates"] / merged["enrolment"] * 100).round(1)
    
    # Sort by enrolment
    merged = merged.sort_values("enrolment", ascending=False)
    
    schools = []
    for _, row in merged.iterrows():
        schools.append({
            "school_id": int(row["school_id"]),
            "school_name": row["school_name"],
            "enrolment": int(row["enrolment"]) if pd.notna(row["enrolment"]) else 0,
            "graduates": int(row["graduates"]) if pd.notna(row["graduates"]) else 0,
            "completion_rate": row["completion_rate"] if pd.notna(row["completion_rate"]) else None
        })
    
    return {
        "year": int(year),
        "schools": schools,
        "total_schools": len(schools)
    }
