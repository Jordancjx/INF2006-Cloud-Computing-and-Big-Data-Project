import pandas as pd
import numpy as np
import os

def clean_employment_column(series):
    return pd.to_numeric(
        series.astype(str)
              .str.replace("%", "", regex=False)
              .str.replace("N.A.", "", regex=False)
              .str.replace("na", "", regex=False)
              .replace("", pd.NA),
        errors="coerce"
    )

def compute_trend_strength(df):
    # Keep only valid rows
    trend_df = df.dropna(
        subset=["year", "employment_rate_overall"]
    )

    if len(trend_df) < 2:
        return None

    x = trend_df["year"].values
    y = trend_df["employment_rate_overall"].values
    slope, intercept = np.polyfit(x, y, 1)

    return round(float(slope), 3)

def employment_trend(csv_path):
    df = pd.read_csv(csv_path)

    df["employment_rate_overall"] = clean_employment_column(
        df["employment_rate_overall"]
    )

    df["employment_rate_ft_perm"] = clean_employment_column(
        df["employment_rate_ft_perm"]
    )

    trend = (
        df.groupby("year")[["employment_rate_overall", "employment_rate_ft_perm"]]
        .mean()
        .reset_index()
    )

    trend_strength = compute_trend_strength(trend)

    # for average employment rate KPIs
    avg_employment_rate_overall = trend["employment_rate_overall"].mean()
    avg_employment_rate_ft_perm = trend["employment_rate_ft_perm"].mean()

    # for other KPIs if needed, latest in this case is year 2023
    latest = trend.iloc[-1]    

    # for stability ratio KPI
    stability_ratio = None
    overall = latest["employment_rate_overall"]
    ft = latest["employment_rate_ft_perm"]

    if pd.notna(overall) and pd.notna(ft) and overall != 0:
        stability_ratio = ft / overall

    # trend = trend.replace({np.nan: None})

    # return trend.to_dict(orient="records")

    return {
        "trend": trend.replace({np.nan: None}).to_dict(orient="records"),
        "kpis": {
            "stability_ratio": stability_ratio,
            "avg_employment_rate_overall": avg_employment_rate_overall,
            "avg_employment_rate_ft_perm": avg_employment_rate_ft_perm,
            "trend_strength": trend_strength
        }
    }


def employment_by_school(csv_path, year):
    """
    Get employment rates broken down by school for a specific year.
    
    Args:
        csv_path: Path to GES_cleaned.csv
        year: Specific year to analyze
    
    Returns:
        List of schools with their employment rates for that year
    """
    df = pd.read_csv(csv_path)
    
    # Load school lookup table
    base_dir = os.path.dirname(csv_path)
    schools_lookup = pd.read_csv(os.path.join(base_dir, "schools_lookup.csv"))
    
    # Merge to get proper school names
    df = df.merge(schools_lookup, on="school_id", how="left")
    
    # Clean employment columns
    df["employment_rate_overall"] = clean_employment_column(df["employment_rate_overall"])
    df["employment_rate_ft_perm"] = clean_employment_column(df["employment_rate_ft_perm"])
    
    # Filter by year
    year_df = df[df["year"] == year].copy()
    
    # Aggregate by school
    school_breakdown = year_df.groupby("school_name").agg({
        "employment_rate_overall": "mean",
        "employment_rate_ft_perm": "mean"
    }).reset_index()
    
    # Round values
    school_breakdown["employment_rate_overall"] = school_breakdown["employment_rate_overall"].round(1)
    school_breakdown["employment_rate_ft_perm"] = school_breakdown["employment_rate_ft_perm"].round(1)
    
    # Sort by employment rate
    school_breakdown = school_breakdown.sort_values("employment_rate_overall", ascending=False)
    
    # Convert to list of dicts
    result = []
    for _, row in school_breakdown.iterrows():
        result.append({
            "school": row["school_name"],
            "employment_rate_overall": row["employment_rate_overall"],
            "employment_rate_ft_perm": row["employment_rate_ft_perm"]
        })
    
    return {
        "year": int(year),
        "schools": result,
        "total_schools": len(result)
    }


def employment_by_degree(csv_path, year, school_name, metric_type='overall'):
    """
    Get employment rates broken down by degree for a specific school and year.
    
    Args:
        csv_path: Path to GES_cleaned.csv
        year: Specific year to analyze
        school_name: Name of the school to filter by (from schools_lookup)
        metric_type: Either 'overall' or 'ft_perm' to determine which employment rate to show
    
    Returns:
        List of degrees with their employment rates for that school and year
    """
    df = pd.read_csv(csv_path)
    
    # Load school lookup table
    base_dir = os.path.dirname(csv_path)
    schools_lookup = pd.read_csv(os.path.join(base_dir, "schools_lookup.csv"))
    
    # Merge to get proper school names
    df = df.merge(schools_lookup, on="school_id", how="left")
    
    # Clean employment columns
    df["employment_rate_overall"] = clean_employment_column(df["employment_rate_overall"])
    df["employment_rate_ft_perm"] = clean_employment_column(df["employment_rate_ft_perm"])
    
    # Filter by year and school_name (using the merged school_name column)
    filtered_df = merged_df[
        (merged_df["year"] == year) & (merged_df["school_name"] == school_name)
    ]
    
    if len(filtered_df) == 0:
        return {
            "year": int(year),
            "school": school_name,
            "metric_type": metric_type,
            "degrees": [],
            "total_degrees": 0
        }
    
    # Determine which column to use
    rate_column = "employment_rate_overall" if metric_type == "overall" else "employment_rate_ft_perm"
    
    # Remove rows with NaN values for the selected metric before aggregating
    filtered_df = filtered_df.dropna(subset=[rate_column])
    
    if len(filtered_df) == 0:
        return {
            "year": int(year),
            "school": school_name,
            "metric_type": metric_type,
            "degrees": [],
            "total_degrees": 0
        }
    
    # Aggregate by degree
    degree_breakdown = filtered_df.groupby("degree").agg({
        rate_column: "mean"
    }).reset_index()
    
    # Drop any remaining NaN values (safety measure)
    degree_breakdown = degree_breakdown.dropna(subset=[rate_column])
    
    # Round values
    degree_breakdown[rate_column] = degree_breakdown[rate_column].round(1)
    
    # Sort by employment rate
    degree_breakdown = degree_breakdown.sort_values(rate_column, ascending=False)
    
    # Convert to list of dicts
    result = []
    for _, row in degree_breakdown.iterrows():
        result.append({
            "degree": row["degree"],
            "employment_rate": row[rate_column]
        })
    
    return {
        "year": int(year),
        "school": school_name,
        "metric_type": metric_type,
        "degrees": result,
        "total_degrees": len(result)
    }
