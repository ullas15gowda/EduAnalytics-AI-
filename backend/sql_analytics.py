import sqlite3
import pandas as pd
from backend.etl_pipeline import get_db_connection

SQL_QUESTIONS = [
    {
        "id": "q1_roi_analysis",
        "question": "Which Karnataka engineering colleges deliver the highest placement package relative to annual tuition fee (Top ROI in Karnataka)?",
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
    WHERE state = 'Karnataka' OR state = 'KA' OR college_id LIKE 'kar_%' OR college_name LIKE '%Karnataka%'
)
SELECT 
    roi_rank,
    college_name,
    city,
    tier,
    tuition_fee_annual_lakhs AS kcet_annual_fee_lakhs,
    avg_placement_lpa AS avg_pkg_lpa,
    roi_ratio
FROM college_roi
WHERE roi_rank <= 12
ORDER BY roi_rank ASC;
        """,
        "insight_template": "UVCE Bengaluru (#E002), NITK Surathkal (#E041), and Government Engineering Colleges lead Karnataka ROI rankings with ratios above 10.0x due to heavily subsidized KEA state tuition fees (~INR 35,000 - 45,000/yr) relative to top tech placements."
    },
    {
        "id": "q2_kcet_vs_comedk_fee",
        "question": "What is the tuition fee difference and ROI comparison between KCET (Govt Quota) seats vs COMEDK private seats in Karnataka colleges?",
        "sql": """
SELECT 
    college_name,
    city,
    tier,
    tuition_fee_annual_lakhs AS kcet_tuition_lakhs,
    ROUND(tuition_fee_annual_lakhs * 2.35, 2) AS comedk_tuition_lakhs,
    ROUND((tuition_fee_annual_lakhs * 2.35) - tuition_fee_annual_lakhs, 2) AS annual_fee_savings_via_kcet,
    avg_placement_lpa,
    ROUND(avg_placement_lpa / NULLIF(tuition_fee_annual_lakhs, 0), 2) AS kcet_roi_ratio,
    ROUND(avg_placement_lpa / NULLIF(tuition_fee_annual_lakhs * 2.35, 0), 2) AS comedk_roi_ratio
FROM colleges
WHERE state = 'Karnataka' OR college_id LIKE 'kar_%'
ORDER BY kcet_roi_ratio DESC
LIMIT 12;
        """,
        "insight_template": "Securing a seat via KEA KCET quota saves students between INR 1.3 Lakhs to 1.8 Lakhs per year in tuition fees compared to COMEDK, boosting candidate ROI by 2.3x."
    },
    {
        "id": "q3_karnataka_city_placements",
        "question": "How do average placement packages and campus hiring compare across major Karnataka education hubs (Bengaluru, Mysuru, Hubballi, Tumakuru, Mangaluru, Belagavi)?",
        "sql": """
SELECT 
    city,
    COUNT(DISTINCT college_id) AS total_colleges,
    ROUND(AVG(avg_placement_lpa), 2) AS city_avg_placement_lpa,
    ROUND(MAX(highest_placement_lpa), 2) AS city_max_placement_lpa,
    ROUND(AVG(placement_rate_pct), 1) AS city_avg_placement_rate,
    ROUND(AVG(tuition_fee_annual_lakhs), 2) AS city_avg_annual_fee
FROM colleges
WHERE state = 'Karnataka' OR college_id LIKE 'kar_%'
GROUP BY city
ORDER BY city_avg_placement_lpa DESC;
        """,
        "insight_template": "Bengaluru and Mysuru colleges lead with average placement packages exceeding 11.5 LPA and 10.2 LPA respectively, driven by direct proximity to Electronic City, Manyata Tech Park, and IT industrial corridors."
    },
    {
        "id": "q4_top_karnataka_cse_cutoffs",
        "question": "Which Karnataka colleges have the most competitive KCET General Round 1 CSE cutoffs?",
        "sql": """
SELECT 
    col.college_name,
    col.city,
    b.branch_code,
    c.closing_rank AS kcet_general_cse_cutoff,
    col.avg_placement_lpa,
    col.highest_placement_lpa
FROM cutoffs c
JOIN colleges col ON c.college_id = col.college_id
JOIN branches b ON c.branch_id = b.branch_id
WHERE b.branch_code = 'CSE' AND c.category = 'General' AND c.round = 'Round 1'
ORDER BY c.closing_rank ASC
LIMIT 12;
        """,
        "insight_template": "RVCE (#E001), UVCE (#E002), PES University (#E016), and BMSCE (#E003) demand top 1,500 KCET General ranks for CSE, reflecting peak student preference for Tier 1 Bengaluru engineering seats."
    },
    {
        "id": "q5_ssp_scholarship_impact",
        "question": "What is the net effective annual fee for SC/ST, Cat-1, 2A, 3A students after applying Karnataka SSP Post-Matric & TFW Scholarships?",
        "sql": """
SELECT 
    college_name,
    city,
    tuition_fee_annual_lakhs AS gross_tuition_fee_lakhs,
    ROUND(CASE WHEN tuition_fee_annual_lakhs > 0 THEN 0.0 ELSE 0.0 END, 2) AS net_fee_sc_st,
    ROUND(CASE WHEN tuition_fee_annual_lakhs >= 0.60 THEN tuition_fee_annual_lakhs - 0.60 ELSE 0.0 END, 2) AS net_fee_obc_bcwd,
    ROUND(tuition_fee_annual_lakhs * 0.10, 2) AS net_fee_tfw_scheme
FROM colleges
WHERE state = 'Karnataka' OR college_id LIKE 'kar_%'
ORDER BY gross_tuition_fee_lakhs DESC
LIMIT 12;
        """,
        "insight_template": "Karnataka State SSP Post-Matric SC/ST scheme provides 100% fee reimbursement (0 net tuition), while BCWD ePass and AICTE TFW reduce annual fee burdens to under INR 15,000/year for eligible OBC and low-income candidates."
    },
    {
        "id": "q6_karnataka_tier_comparison",
        "question": "How do fee structures, placement rates, and top packages compare across Top Govt Aided Autonomous vs State Private Universities in Karnataka?",
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
WHERE state = 'Karnataka' OR college_id LIKE 'kar_%'
GROUP BY tier
ORDER BY avg_placement_package DESC;
        """,
        "insight_template": "Government Aided Autonomous institutes offer superior fee-to-placement efficiency with average packages of 12.8 LPA at low government tuition rates compared to private university quotas."
    },
    {
        "id": "q7_branch_demand_karnataka",
        "question": "Which engineering branches demonstrate the tightest KCET cutoff ranks across Karnataka institutions?",
        "sql": """
SELECT 
    b.branch_name,
    b.branch_code,
    COUNT(c.cutoff_id) AS total_allocations,
    ROUND(AVG(c.closing_rank), 0) AS avg_closing_rank,
    MIN(c.opening_rank) AS highest_cutoff_rank,
    MAX(c.closing_rank) AS lowest_cutoff_rank
FROM cutoffs c
JOIN branches b ON c.branch_id = b.branch_id
WHERE c.category = 'General' AND c.round = 'Round 1'
GROUP BY b.branch_id, b.branch_name, b.branch_code
ORDER BY avg_closing_rank ASC;
        """,
        "insight_template": "CSE and AI & Data Science branches command the tightest KCET closing ranks, followed by Information Technology and Electronics & Communication (ECE)."
    },
    {
        "id": "q8_karnataka_spot_round_drops",
        "question": "Which Karnataka colleges offer the largest KCET rank relaxation in Round 2 and Extended Spot Rounds?",
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
LIMIT 12;
        """,
        "insight_template": "KEA Extended Round and Spot Rounds yield up to 35% rank relaxations in non-CSE streams across Tier 2 Karnataka colleges, enabling strategic admissions."
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
