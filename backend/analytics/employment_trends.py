import pandas as pd
import numpy as np

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
    trend_df = df.dropna(subset=["year", "employment_rate_overall"])
    if len(trend_df) < 2: return None
    x, y = trend_df["year"].values, trend_df["employment_rate_overall"].values
    slope, _ = np.polyfit(x, y, 1)
    return round(float(slope), 3)

def employment_trend(engine):
    query = "SELECT * FROM graduate_employment_survey"
    df = pd.read_sql(query, engine)

    df["employment_rate_overall"] = clean_employment_column(df["employment_rate_overall"])
    df["employment_rate_ft_perm"] = clean_employment_column(df["employment_rate_ft_perm"])


    trend = df.groupby("year")[["employment_rate_overall", "employment_rate_ft_perm"]].mean().reset_index()

    avg_overall = trend["employment_rate_overall"].mean()
    avg_ft_perm = trend["employment_rate_ft_perm"].mean()
    
    # Stability Ratio (Latest Year)
    latest_year_data = trend.iloc[-1]
    stability = latest_year_data["employment_rate_ft_perm"] / latest_year_data["employment_rate_overall"]

    return {
        "trend": trend.replace({np.nan: None}).to_dict(orient="records"),
        "kpis": {
            "avg_employment_rate_overall": avg_overall,
            "avg_employment_rate_ft_perm": avg_ft_perm, # Required for 'Avg FT Permanent' card
            "stability_ratio": stability,               # Required for 'Stability Ratio' card
            "trend_strength": compute_trend_strength(trend)
        }
    }
def employment_by_school(engine, year):
    survey_query = f"SELECT * FROM graduate_employment_survey WHERE year = {year}"
    df = pd.read_sql(survey_query, engine)
    
    mapping_query = "SELECT * FROM school_mapping"
    schools_lookup = pd.read_sql(mapping_query, engine)
    
    df = df.merge(schools_lookup, on="school_id", how="left")
    df["employment_rate_overall"] = clean_employment_column(df["employment_rate_overall"])
    
    school_breakdown = df.groupby("full_name")["employment_rate_overall"].mean().reset_index()
    school_breakdown = school_breakdown.rename(columns={"full_name": "school"}) 
    
    result = []
    for _, row in school_breakdown.iterrows():
        result.append({
            "school": row["school"],
            "employment_rate_overall": row["employment_rate_overall"],
            "total_schools": len(school_breakdown)
        })
    
    return {
        "year": int(year),
        "schools": result,
        "total_schools": len(result)
    }


def employment_by_degree(engine, year, school_name, metric_type='overall'):
    """
    Get employment rates broken down by degree for a specific school and year.
    
    Args:
        engine: SQLAlchemy engine
        year: Specific year to analyze
        school_name: Name of the school to filter by
        metric_type: Either 'overall' or 'ft_perm' to determine which employment rate to show
    
    Returns:
        List of degrees with their employment rates for that school and year
    """
    survey_query = f"SELECT * FROM graduate_employment_survey WHERE year = {year}"
    df = pd.read_sql(survey_query, engine)
    
    mapping_query = "SELECT * FROM school_mapping"
    schools_lookup = pd.read_sql(mapping_query, engine)
    
    df = df.merge(schools_lookup, on="school_id", how="left")
    df["employment_rate_overall"] = clean_employment_column(df["employment_rate_overall"])
    df["employment_rate_ft_perm"] = clean_employment_column(df["employment_rate_ft_perm"])
    
    filtered_df = df[df["full_name"] == school_name]
    
    if len(filtered_df) == 0:
        return {
            "year": int(year),
            "school": school_name,
            "metric_type": metric_type,
            "degrees": [],
            "total_degrees": 0
        }
    
    rate_column = "employment_rate_overall" if metric_type == "overall" else "employment_rate_ft_perm"
    filtered_df = filtered_df.dropna(subset=[rate_column])
    
    if len(filtered_df) == 0:
        return {
            "year": int(year),
            "school": school_name,
            "metric_type": metric_type,
            "degrees": [],
            "total_degrees": 0
        }
    
    degree_breakdown = filtered_df.groupby("degree").agg({
        rate_column: "mean"
    }).reset_index()
    
    degree_breakdown = degree_breakdown.dropna(subset=[rate_column])
    degree_breakdown[rate_column] = degree_breakdown[rate_column].round(1)
    degree_breakdown = degree_breakdown.sort_values(rate_column, ascending=False)
    
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
