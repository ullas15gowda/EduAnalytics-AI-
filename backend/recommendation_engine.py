import pandas as pd
from backend.etl_pipeline import get_db_connection
from backend.ml_engine import predict_admission_probability

def recommend_colleges(
    entrance_rank: int,
    category: str = "General",
    preferred_branch: str = "CSE",
    preferred_state: str = None,
    max_annual_budget: float = 5.0,
    hostel_needed: bool = True,
    min_placement_lpa: float = 0.0,
    top_n: int = 8
):
    conn = get_db_connection()
    
    # Query colleges and branch cutoffs for year 2024 / Round 1
    sql = """
    SELECT 
        c.college_id, c.college_name, c.short_name, c.city, c.state, c.tier,
        c.nirf_rank, c.campus_rating, c.tuition_fee_annual_lakhs, c.hostel_fee_annual_lakhs,
        c.avg_placement_lpa, c.highest_placement_lpa, c.placement_rate_pct,
        b.branch_id, b.branch_code, b.branch_name,
        cut.closing_rank, cut.opening_rank
    FROM colleges c
    JOIN cutoffs cut ON c.college_id = cut.college_id
    JOIN branches b ON cut.branch_id = b.branch_id
    WHERE cut.category = ? AND cut.round = 'Round 1' AND cut.year = 2024
    """
    
    df = pd.read_sql_query(sql, conn, params=[category])
    conn.close()
    
    recommendations = []
    
    for _, row in df.iterrows():
        total_fee = row["tuition_fee_annual_lakhs"] + (row["hostel_fee_annual_lakhs"] if hostel_needed else 0.0)
        
        # 1. Eligibility Filtering
        if total_fee > (max_annual_budget * 1.35): # Allow 35% margin for soft recommendation
            continue
        if row["avg_placement_lpa"] < min_placement_lpa:
            continue

        # 2. ML Probability Estimation
        ml_res = predict_admission_probability(
            entrance_rank=entrance_rank,
            closing_rank=row["closing_rank"],
            annual_budget=max_annual_budget,
            tuition_fee=total_fee,
            avg_placement_lpa=row["avg_placement_lpa"],
            tier=row["tier"],
            hostel_needed=1 if hostel_needed else 0
        )
        adm_prob = ml_res["admission_probability"]

        # 3. Sub-component Feature Score Calculation (Scale 0 - 100)
        # Rank Fit
        if entrance_rank <= row["closing_rank"]:
            rank_fit_score = min(100.0, 70.0 + (row["closing_rank"] - entrance_rank) / 300.0)
        else:
            rank_fit_score = max(0.0, 70.0 - (entrance_rank - row["closing_rank"]) / 200.0)
            
        # Branch Match
        branch_fit_score = 100.0 if row["branch_code"] == preferred_branch else (75.0 if preferred_branch in ["CSE", "AI_DS", "IT"] and row["branch_code"] in ["CSE", "AI_DS", "IT"] else 50.0)
        
        # Budget Fit
        if total_fee <= max_annual_budget:
            budget_fit_score = 100.0
        else:
            budget_fit_score = max(20.0, 100.0 - ((total_fee - max_annual_budget) / max_annual_budget * 100.0))
            
        # Placement Score
        placement_fit_score = min(100.0, (row["avg_placement_lpa"] / 25.0) * 100.0)
        
        # Location Fit
        location_fit_score = 100.0 if (preferred_state and row["state"].lower() == preferred_state.lower()) else 70.0

        # 4. Composite Hybrid Match Score Formula
        overall_match = (
            (adm_prob * 100.0 * 0.35) +
            (placement_fit_score * 0.25) +
            (budget_fit_score * 0.20) +
            (branch_fit_score * 0.10) +
            (location_fit_score * 0.10)
        )
        
        # 5. Natural Language Decision Factors Generation
        decision_factors = []
        if entrance_rank <= row["closing_rank"]:
            decision_factors.append(f"Strong rank fit (Entrance Rank #{entrance_rank:,} meets closing rank #{row['closing_rank']:,})")
        else:
            decision_factors.append(f"Borderline rank fit (May require Round 2/3 or Spot Round)")
            
        if total_fee <= max_annual_budget:
            decision_factors.append(f"Comfortably within your annual budget (INR {total_fee:.2f} Lakhs vs max INR {max_annual_budget:.2f} Lakhs)")
        else:
            decision_factors.append(f"Slightly exceeds budget (Scholarships/Loans available)")
            
        if row["avg_placement_lpa"] >= 14.0:
            decision_factors.append(f"High-tier placements (Avg Package: {row['avg_placement_lpa']} LPA)")
            
        if preferred_state and row["state"].lower() == preferred_state.lower():
            decision_factors.append(f"Matches preferred state location ({row['state']})")
            
        recommendations.append({
            "college_id": row["college_id"],
            "college_name": row["college_name"],
            "short_name": row["short_name"],
            "city": row["city"],
            "state": row["state"],
            "tier": row["tier"],
            "nirf_rank": row["nirf_rank"],
            "branch_code": row["branch_code"],
            "branch_name": row["branch_name"],
            "closing_rank": row["closing_rank"],
            "annual_fee_lakhs": round(total_fee, 2),
            "avg_placement_lpa": row["avg_placement_lpa"],
            "placement_rate_pct": row["placement_rate_pct"],
            "overall_match_score": round(overall_match, 1),
            "admission_probability_pct": round(adm_prob * 100.0, 1),
            "score_breakdown": {
                "admission_probability": round(adm_prob * 100.0, 1),
                "rank_fit": round(rank_fit_score, 1),
                "branch_fit": round(branch_fit_score, 1),
                "budget_fit": round(budget_fit_score, 1),
                "placement_score": round(placement_fit_score, 1),
                "location_fit": round(location_fit_score, 1)
            },
            "decision_factors": decision_factors
        })
        
    # Sort recommendations by overall match score
    recommendations.sort(key=lambda x: x["overall_match_score"], reverse=True)
    return recommendations[:top_n]

if __name__ == "__main__":
    recs = recommend_colleges(entrance_rank=4200, category="General", preferred_branch="CSE", max_annual_budget=3.5)
    print(f"Generated {len(recs)} Top Recommendations.")
    print("Top Rec:", recs[0])
