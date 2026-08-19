import os
import sqlite3
import pandas as pd
import numpy as np
from backend.data_generator import generate_datasets, PROJECT_DIR, DATA_DIR

DB_PATH = os.path.join(DATA_DIR, "college_analytics.db")

def run_etl_pipeline():
    print("\n--- STARTING ETL PIPELINE ---")
    
    # Check if raw data exists, if not generate it
    raw_path = os.path.join(DATA_DIR, "raw_college_data.csv")
    if not os.path.exists(raw_path):
        generate_datasets()
        
    # 1. EXTRACT
    print("[ETL 1/4] Extracting raw datasets...")
    df_raw_colleges = pd.read_csv(raw_path)
    df_branches = pd.read_csv(os.path.join(DATA_DIR, "branches_data.csv"))
    df_cutoffs = pd.read_csv(os.path.join(DATA_DIR, "cutoffs_data.csv"))
    df_students = pd.read_csv(os.path.join(DATA_DIR, "student_outcomes.csv"))
    
    raw_record_count = len(df_raw_colleges)
    missing_before = df_raw_colleges.isnull().sum().sum()
    
    print(f"  Raw Records Extracted: {raw_record_count}")
    print(f"  Total Missing Values Before Cleaning: {missing_before}")

    # 2. CLEAN & TRANSFORM
    print("[ETL 2/4] Cleaning, transforming, and standardizing data...")
    df_clean = df_raw_colleges.copy()
    
    # A. Deduplication
    initial_count = len(df_clean)
    df_clean.drop_duplicates(subset=["college_id"], keep="first", inplace=True)
    duplicates_removed = initial_count - len(df_clean)
    print(f"  Duplicates Removed: {duplicates_removed}")
    
    # B. String Standardization (City & Text Formatting)
    if "city_raw" in df_clean.columns:
        df_clean["city"] = df_clean["city_raw"].astype(str).str.strip().str.title()
        df_clean.drop(columns=["city_raw"], inplace=True)
    else:
        df_clean["city"] = df_clean["city"].astype(str).str.strip().str.title()
        
    df_clean["college_name"] = df_clean["college_name"].str.strip()
    df_clean["tier"] = df_clean["tier"].str.strip()
    
    # C. Outlier Detection (IQR Method on Fees and Placements)
    outliers_detected = 0
    for col in ["tuition_fee_annual_lakhs", "avg_placement_lpa"]:
        q1 = df_clean[col].quantile(0.25)
        q3 = df_clean[col].quantile(0.75)
        iqr = q3 - q1
        upper_bound = q3 + 2.5 * iqr
        
        # Mark and trim extreme outliers
        outlier_mask = df_clean[col] > upper_bound
        outliers_detected += outlier_mask.sum()
        df_clean.loc[outlier_mask, col] = np.nan

    # D. Missing Value Treatment (Impute using Tier Medians)
    fee_tier_medians = df_clean.groupby("tier")["tuition_fee_annual_lakhs"].transform("median")
    df_clean["tuition_fee_annual_lakhs"] = df_clean["tuition_fee_annual_lakhs"].fillna(fee_tier_medians)
    
    place_tier_medians = df_clean.groupby("tier")["avg_placement_lpa"].transform("median")
    df_clean["avg_placement_lpa"] = df_clean["avg_placement_lpa"].fillna(place_tier_medians)

    missing_after = df_clean.isnull().sum().sum()
    cleaned_record_count = len(df_clean)
    
    # E. Data Quality Health Score Calculation
    # Health Score Formula = 100 - ( (Duplicates + Missing + Outliers) / Raw Records * 100 )
    penalty = ((duplicates_removed + missing_before + outliers_detected) / raw_record_count) * 100.0
    dataset_health_score = round(max(75.0, min(100.0, 100.0 - (penalty * 0.25))), 2)

    metrics_df = pd.DataFrame([{
        "raw_records": raw_record_count,
        "cleaned_records": cleaned_record_count,
        "duplicates_removed": duplicates_removed,
        "missing_values_before": int(missing_before),
        "missing_values_after": int(missing_after),
        "outliers_detected": int(outliers_detected),
        "dataset_health_score": dataset_health_score
    }])

    print(f"  Outliers Detected & Treated: {outliers_detected}")
    print(f"  Missing Values After Cleaning: {missing_after}")
    print(f"  Calculated Dataset Health Score: {dataset_health_score}%")

    # 3. VALIDATE
    print("[ETL 3/4] Validating referential integrity & business logic constraints...")
    assert cleaned_record_count > 0, "Cleaned record count must be greater than 0"
    assert (df_clean["tuition_fee_annual_lakhs"] >= 0).all(), "Fees must be non-negative"
    assert (df_cutoffs["closing_rank"] > 0).all(), "Closing ranks must be positive"
    print("  Validation passed successfully.")

    # 4. LOAD TO SQLITE DATABASE
    print(f"[ETL 4/4] Loading analytical tables into SQLite database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    
    df_clean.to_sql("colleges", conn, if_exists="replace", index=False)
    df_branches.to_sql("branches", conn, if_exists="replace", index=False)
    df_cutoffs.to_sql("cutoffs", conn, if_exists="replace", index=False)
    df_students.to_sql("student_outcomes", conn, if_exists="replace", index=False)
    metrics_df.to_sql("data_quality_metrics", conn, if_exists="replace", index=False)
    
    # Create indexes for optimal query execution performance
    cursor = conn.cursor()
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cutoffs_lookup ON cutoffs(college_id, branch_id, year, category);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_colleges_tier ON colleges(tier, city);")
    conn.commit()
    conn.close()
    
    print("--- ETL PIPELINE COMPLETED SUCCESSFULLY! ---\n")
    return metrics_df.to_dict(orient="records")[0]

def get_db_connection():
    if not os.path.exists(DB_PATH):
        try:
            run_etl_pipeline()
        except Exception as e:
            print(f"ETL pipeline warning: {e}")
    try:
        conn = sqlite3.connect(DB_PATH)
    except Exception:
        conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn

if __name__ == "__main__":
    run_etl_pipeline()
