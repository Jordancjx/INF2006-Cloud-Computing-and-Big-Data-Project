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