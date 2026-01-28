import pandas as pd
import numpy as np

def clean_employment_column(series):
    return pd.to_numeric(
        series.astype(str)
              .str.replace("%", "", regex=False)
              .replace("N.A.", pd.NA),
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

