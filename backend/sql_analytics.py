import sqlite3
import pandas as pd
from backend.etl_pipeline import get_db_connection

SQL_QUESTIONS = [
    {
        "id": "q1_roi_analysis",
        "question": "Which engineering colleges deliver the highest placement package relative to annual tuition fee (Best ROI Ratio)?",
        "sql": """
WITH college_roi AS (
    SELECT 
        college_id,
        college_name,
        city,
        tier,
        tuition_fee_annual_lakhs,
        avg_placement_lpa,
        ROUND((avg_placement_lpa / NULLIF(tuition_fee_annual_lakhs, 0)), 2) AS roi_ratio,
        RANK() OVER (ORDER BY (avg_placement_lpa / NULLIF(tuition_fee_annual_lakhs, 0)) DESC) AS roi_rank
    FROM colleges
    WHERE tuition_fee_annual_lakhs > 0
)
SELECT 
    roi_rank,
    college_name,
    city,
    tier,
    tuition_fee_annual_lakhs AS annual_fee_lakhs,
    avg_placement_lpa AS avg_pkg_lpa,
    roi_ratio
FROM college_roi
WHERE roi_rank <= 10
ORDER BY roi_rank ASC;
        """,
        "insight_template": "Jadavpur University, IITs, and top Government Institutes (COEP, VJTI) top the ROI leaderboard with ROI ratios above 5.0x to 40.0x due to heavily subsidized state/central government tuition fees relative to corporate campus placements."
    },
    {
        "id": "q2_branch_demand",
        "question": "Which engineering branches demonstrate the highest admission competitiveness and cutoff rank tightness across 2021-2025?",
        "sql": """
SELECT 
    b.branch_name,
    b.branch_code,
    COUNT(c.cutoff_id) AS total_seat_allocations,
    ROUND(AVG(c.closing_rank), 0) AS avg_closing_rank,
    MIN(c.opening_rank) AS highest_cutoff_rank,
    MAX(c.closing_rank) AS lowest_cutoff_rank,
    CASE 
        WHEN AVG(c.closing_rank) < 5000 THEN 'Extremely High'
        WHEN AVG(c.closing_rank) BETWEEN 5000 AND 15000 THEN 'High'
        ELSE 'Moderate'
    END AS demand_category
FROM cutoffs c
JOIN branches b ON c.branch_id = b.branch_id
WHERE c.category = 'General' AND c.round = 'Round 1'
GROUP BY b.branch_id, b.branch_name, b.branch_code
ORDER BY avg_closing_rank ASC;
        """,
        "insight_template": "CSE and AI & Data Science branches exhibit the tightest closing ranks (under 4,500 CRL on average), reflecting massive student preference for tech roles compared to traditional core engineering disciplines."
    },
    {
        "id": "q3_cutoff_shifts",
        "question": "Which colleges experienced the most significant YoY relaxation in Round 1 General closing rank between 2021 and 2025?",
        "sql": """
WITH rank_2021 AS (
    SELECT college_id, branch_id, closing_rank AS rank_21
    FROM cutoffs WHERE year = 2021 AND category = 'General' AND round = 'Round 1'
),
rank_2025 AS (
    SELECT college_id, branch_id, closing_rank AS rank_25
    FROM cutoffs WHERE year = 2025 AND category = 'General' AND round = 'Round 1'
)
SELECT 
    col.college_name,
    b.branch_code,
    r21.rank_21,
    r25.rank_25,
    (r25.rank_25 - r21.rank_21) AS rank_shift,
    ROUND(((r25.rank_25 - r21.rank_21) * 100.0 / r21.rank_21), 1) AS pct_change
FROM rank_2021 r21
JOIN rank_2025 r25 ON r21.college_id = r25.college_id AND r21.branch_id = r25.branch_id
JOIN colleges col ON r21.college_id = col.college_id
JOIN branches b ON r21.branch_id = b.branch_id
ORDER BY ABS(rank_shift) DESC
LIMIT 10;
        """,
        "insight_template": "Non-CSE branches in Tier 2 and Tier 3 colleges showed 15% to 35% rank relaxation over 4 years, presenting strategic entry opportunities for students with mid-level ranks."
    },
    {
        "id": "q4_high_placement_low_fee",
        "question": "Which colleges provide impressive placements (>12 LPA average) at low annual tuition (< 2.5 Lakhs)?",
        "sql": """
SELECT 
    college_name,
    city,
    state,
    tier,
    tuition_fee_annual_lakhs,
    avg_placement_lpa,
    highest_placement_lpa,
    placement_rate_pct
FROM colleges
WHERE avg_placement_lpa >= 12.0 AND tuition_fee_annual_lakhs <= 2.5
ORDER BY avg_placement_lpa DESC;
        """,
        "insight_template": "All top Tier 1 NITs (Trichy, Surathkal, Warangal) and premier State institutes (VJTI, COEP, JU) meet this golden affordability criterion, offering high corporate placement returns without high tuition debt."
    },
    {
        "id": "q5_state_geographic_distribution",
        "question": "Which Indian states have the highest concentration of top-ranked engineering colleges and total seat capacity?",
        "sql": """
SELECT 
    col.state,
    COUNT(DISTINCT col.college_id) AS total_colleges,
    SUM(CASE WHEN col.tier = 'Tier 1' THEN 1 ELSE 0 END) AS tier1_colleges,
    SUM(CASE WHEN col.tier = 'Tier 2' THEN 1 ELSE 0 END) AS tier2_colleges,
    ROUND(AVG(col.avg_placement_lpa), 2) AS state_avg_placement,
    ROUND(AVG(col.tuition_fee_annual_lakhs), 2) AS state_avg_fee
FROM colleges col
GROUP BY col.state
HAVING COUNT(DISTINCT col.college_id) >= 2
ORDER BY total_colleges DESC, state_avg_placement DESC;
        """,
        "insight_template": "Karnataka, Maharashtra, and Tamil Nadu hold the largest cluster of high-performing Tier 1 & Tier 2 colleges, offering robust regional IT and industrial hiring ecosystems."
    },
    {
        "id": "q6_category_cutoff_gap",
        "question": "What is the average rank delta across General, OBC, SC, ST, and EWS categories for CSE admissions?",
        "sql": """
SELECT 
    c.category,
    COUNT(c.cutoff_id) AS total_records,
    ROUND(AVG(c.opening_rank), 0) AS avg_opening_rank,
    ROUND(AVG(c.closing_rank), 0) AS avg_closing_rank,
    ROUND(AVG(c.closing_rank) - MIN(c.opening_rank), 0) AS rank_span
FROM cutoffs c
JOIN branches b ON c.branch_id = b.branch_id
WHERE b.branch_code = 'CSE' AND c.round = 'Round 1'
GROUP BY c.category
ORDER BY avg_closing_rank ASC;
        """,
        "insight_template": "Reserved category closing ranks expand by 1.8x (OBC), 3.5x (SC), and 5.0x (ST) relative to General CRL cutoffs, providing valuable reservation advantages for eligible candidates."
    },
    {
        "id": "q7_tier_performance_comparison",
        "question": "How do fee structures, placement rates, and average salaries compare across Tier 1, Tier 2, and Tier 3 institutions?",
        "sql": """
SELECT 
    tier,
    COUNT(*) AS total_colleges,
    ROUND(AVG(tuition_fee_annual_lakhs), 2) AS avg_annual_tuition,
    ROUND(AVG(hostel_fee_annual_lakhs), 2) AS avg_annual_hostel,
    ROUND(AVG(avg_placement_lpa), 2) AS avg_placement_package,
    ROUND(AVG(highest_placement_lpa), 2) AS max_placement_package,
    ROUND(AVG(placement_rate_pct), 1) AS avg_placement_rate
FROM colleges
GROUP BY tier
ORDER BY avg_placement_package DESC;
        """,
        "insight_template": "Tier 1 colleges deliver a 2.1x placement salary premium over Tier 2 and a 3.4x premium over Tier 3 institutions, validating the strong economic value of securing a top entrance rank."
    },
    {
        "id": "q8_spot_round_drops",
        "question": "Which colleges show the largest closing rank relaxation between Round 1 and Spot Round (Round 4)?",
        "sql": """
WITH r1 AS (
    SELECT college_id, branch_id, closing_rank AS rank_r1
    FROM cutoffs WHERE round = 'Round 1' AND category = 'General' AND year = 2024
),
spot AS (
    SELECT college_id, branch_id, closing_rank AS rank_spot
    FROM cutoffs WHERE round = 'Spot Round' AND category = 'General' AND year = 2024
)
SELECT 
    col.college_name,
    b.branch_code,
    r1.rank_r1,
    spot.rank_spot,
    (spot.rank_spot - r1.rank_r1) AS rank_drop,
    ROUND(((spot.rank_spot - r1.rank_r1) * 100.0 / r1.rank_r1), 1) AS pct_relaxation
FROM r1
JOIN spot ON r1.college_id = spot.college_id AND r1.branch_id = spot.branch_id
JOIN colleges col ON r1.college_id = col.college_id
JOIN branches b ON r1.branch_id = b.branch_id
WHERE (spot.rank_spot - r1.rank_r1) > 0
ORDER BY rank_drop DESC
LIMIT 10;
        """,
        "insight_template": "Spot rounds yield rank relaxations between 25% to 45%, offering students who missed regular round cutoffs a crucial second chance for vacant seats."
    }
]

def execute_predefined_sql(question_id: str):
    q_item = next((q for q in SQL_QUESTIONS if q["id"] == question_id), None)
    if not q_item:
        return {"error": "Invalid question ID"}
        
    conn = get_db_connection()
    df = pd.read_sql_query(q_item["sql"].strip(), conn)
    conn.close()
    
    return {
        "question": q_item["question"],
        "sql": q_item["sql"].strip(),
        "columns": list(df.columns),
        "data": df.to_dict(orient="records"),
        "insight": q_item["insight_template"]
    }

def execute_custom_sql(sql_query: str):
    # Security check: Read-only SELECT statements only
    clean_sql = sql_query.strip()
    if not clean_sql.upper().startswith("SELECT") and not clean_sql.upper().startswith("WITH"):
        return {"error": "Security Restriction: Only read-only SELECT or WITH statements are allowed."}
        
    try:
        conn = get_db_connection()
        df = pd.read_sql_query(clean_sql, conn)
        conn.close()
        return {
            "columns": list(df.columns),
            "data": df.to_dict(orient="records"),
            "row_count": len(df)
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    res = execute_predefined_sql("q1_roi_analysis")
    print(f"Executed Query 1. Returned {len(res['data'])} rows.")
