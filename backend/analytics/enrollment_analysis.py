import pandas as pd
import numpy as np

def enrollment_graduate_analysis(engine, start_year=None, end_year=None, school_id=None):
    enrol_df = pd.read_sql("SELECT * FROM enrolment_stats WHERE sex = 'MF'", engine)
    grad_df = pd.read_sql("SELECT * FROM graduates_stats WHERE sex = 'MF'", engine)
    
    # Filter years FIRST
    if start_year:
        enrol_df = enrol_df[enrol_df["year"] >= start_year]
        grad_df = grad_df[grad_df["year"] >= start_year]
    if end_year:
        enrol_df = enrol_df[enrol_df["year"] <= end_year]
        grad_df = grad_df[grad_df["year"] <= end_year]
        
    enrol_by_year = enrol_df.groupby("year")["enrolment"].sum().reset_index()
    grad_by_year = grad_df.groupby("year")["graduates"].sum().reset_index()
    
    # Define merged HERE
    merged = pd.merge(enrol_by_year, grad_by_year, on="year", how="outer").sort_values("year")
    
    # Now you can calculate completion_rate
    merged["completion_rate"] = (merged["graduates"] / merged["enrolment"] * 100).round(1)
    
    return {
        "data": merged.replace({np.nan: None}).to_dict(orient="records"),
        "average_completion_rate": merged["completion_rate"].mean(),
        "start_year": start_year,
        "end_year": end_year
    }


def enrollment_by_school_for_year(engine, year):
    """
    Get school breakdown for a specific year from database.
    
    Args:
        engine: SQLAlchemy engine
        year: The year to filter by
    
    Returns:
        Dictionary with school breakdown data for the specified year
    """
    enrol_df = pd.read_sql(f"SELECT * FROM enrolment_stats WHERE sex = 'MF' AND year = {year}", engine)
    grad_df = pd.read_sql(f"SELECT * FROM graduates_stats WHERE sex = 'MF' AND year = {year}", engine)
    
    enrol_df["enrolment"] = pd.to_numeric(enrol_df["enrolment"], errors="coerce")
    grad_df["graduates"] = pd.to_numeric(grad_df["graduates"], errors="coerce")
    
    enrol_df = enrol_df.dropna(subset=["enrolment"])
    grad_df = grad_df.dropna(subset=["graduates"])
    
    enrol_by_school = enrol_df.groupby(["school_id", "school_name"])["enrolment"].sum().reset_index()
    grad_by_school = grad_df.groupby(["school_id", "school_name"])["graduates"].sum().reset_index()
    
    merged = pd.merge(enrol_by_school, grad_by_school, on=["school_id", "school_name"], how="outer")
    merged["completion_rate"] = (merged["graduates"] / merged["enrolment"] * 100).round(1)
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
