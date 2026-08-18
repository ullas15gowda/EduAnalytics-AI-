import os
import random
import pandas as pd
import numpy as np

# Seed for reproducibility
random.seed(42)
np.random.seed(42)

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_DIR, "data")
RAG_DIR = os.path.join(DATA_DIR, "rag_documents")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(RAG_DIR, exist_ok=True)

# 1. Base Master College Seed Data (120 Institutions with Official Website URLs)
COLLEGES_SEED = [
    # Tier 1 (IITs, NITs, BITS, Top IIITs)
    ("IIT Bombay", "IITB", "Mumbai", "Maharashtra", "Tier 1", 3, 4.9, 2.50, 0.90, 24.5, 21.0, 1.20, 98.5, "https://iitb.ac.in"),
    ("IIT Delhi", "IITD", "New Delhi", "Delhi", "Tier 1", 2, 4.9, 2.45, 0.85, 25.0, 21.5, 1.35, 99.0, "https://iitd.ac.in"),
    ("IIT Madras", "IITM", "Chennai", "Tamil Nadu", "Tier 1", 1, 4.95, 2.30, 0.80, 24.0, 20.5, 1.10, 98.0, "https://iitm.ac.in"),
    ("IIT Kharagpur", "IITKGP", "Kharagpur", "West Bengal", "Tier 1", 6, 4.8, 2.35, 0.75, 21.5, 18.0, 0.95, 96.5, "https://iitkgp.ac.in"),
    ("IIT Kanpur", "IITK", "Kanpur", "Uttar Pradesh", "Tier 1", 4, 4.85, 2.40, 0.80, 23.0, 19.5, 1.05, 97.5, "https://iitk.ac.in"),
    ("IIT Roorkee", "IITR", "Roorkee", "Uttarakhand", "Tier 1", 8, 4.75, 2.25, 0.75, 20.0, 17.5, 0.90, 95.5, "https://iitr.ac.in"),
    ("IIT Guwahati", "IITG", "Guwahati", "Assam", "Tier 1", 7, 4.7, 2.20, 0.70, 19.5, 17.0, 0.88, 95.0, "https://iitg.ac.in"),
    ("BITS Pilani", "BITS", "Pilani", "Rajasthan", "Tier 1", 11, 4.8, 5.50, 1.20, 22.0, 19.0, 0.95, 97.0, "https://bits-pilani.ac.in"),
    ("IIIT Hyderabad", "IIITH", "Hyderabad", "Telangana", "Tier 1", 15, 4.85, 3.80, 1.10, 31.0, 28.0, 1.02, 99.2, "https://iiit.ac.in"),
    ("NIT Trichy", "NITT", "Tiruchirappalli", "Tamil Nadu", "Tier 1", 9, 4.7, 1.80, 0.65, 17.5, 15.0, 0.75, 94.5, "https://nitt.edu"),
    ("NIT Surathkal", "NITK", "Surathkal", "Karnataka", "Tier 1", 12, 4.65, 1.85, 0.68, 16.8, 14.5, 0.72, 93.8, "https://nitk.ac.in"),
    ("VNIT Nagpur", "VNIT", "Nagpur", "Maharashtra", "Tier 1", 41, 4.4, 1.75, 0.60, 13.5, 11.5, 0.55, 91.0, "https://vnit.ac.in"),
    ("MNIT Jaipur", "MNIT", "Jaipur", "Rajasthan", "Tier 1", 37, 4.45, 1.70, 0.60, 14.0, 12.0, 0.58, 91.5, "https://mnit.ac.in"),
    ("MNNIT Allahabad", "MNNIT", "Prayagraj", "Uttar Pradesh", "Tier 1", 49, 4.5, 1.78, 0.62, 15.2, 13.0, 0.65, 92.5, "https://mnnit.ac.in"),
    ("IIIT Allahabad", "IIITA", "Prayagraj", "Uttar Pradesh", "Tier 1", 89, 4.6, 2.10, 0.70, 20.5, 18.0, 0.85, 96.0, "https://iiita.ac.in"),

    # Tier 2 (Top State Govt & Top Private Universities)
    ("RV College of Engineering", "RVCE", "Bengaluru", "Karnataka", "Tier 2", 35, 4.6, 3.20, 1.10, 15.5, 13.2, 0.62, 93.0, "https://rvce.edu.in"),
    ("BMS College of Engineering", "BMSCE", "Bengaluru", "Karnataka", "Tier 2", 65, 4.45, 2.90, 1.05, 12.8, 11.0, 0.50, 90.5, "https://bmsce.ac.in"),
    ("College of Engineering Pune", "COEP", "Pune", "Maharashtra", "Tier 2", 52, 4.55, 1.45, 0.55, 13.2, 11.5, 0.48, 92.0, "https://coep.org.in"),
    ("Veermata Jijabai Technological Institute", "VJTI", "Mumbai", "Maharashtra", "Tier 2", 58, 4.5, 1.40, 0.52, 14.0, 12.0, 0.52, 92.5, "https://vjti.ac.in"),
    ("PSG College of Technology", "PSG", "Coimbatore", "Tamil Nadu", "Tier 2", 63, 4.5, 1.65, 0.60, 12.5, 10.8, 0.45, 91.2, "https://psgtech.edu"),
    ("VIT Vellore", "VIT", "Vellore", "Tamil Nadu", "Tier 2", 11, 4.4, 2.45, 1.15, 9.8, 8.5, 0.42, 88.5, "https://vit.ac.in"),
    ("SRM Institute of Science and Technology", "SRM", "Chennai", "Tamil Nadu", "Tier 2", 28, 4.2, 2.60, 1.25, 8.5, 7.2, 0.38, 85.0, "https://srmist.edu.in"),
    ("Manipal Institute of Technology", "MIT", "Manipal", "Karnataka", "Tier 2", 45, 4.35, 3.85, 1.40, 11.5, 9.8, 0.45, 89.0, "https://manipal.edu/mit.html"),
    ("Thapar Institute of Engg & Tech", "TIET", "Patiala", "Punjab", "Tier 2", 20, 4.3, 4.20, 1.30, 12.0, 10.2, 0.48, 89.5, "https://thapar.edu"),
    ("Jadavpur University", "JU", "Kolkata", "West Bengal", "Tier 2", 10, 4.7, 0.25, 0.15, 15.8, 13.5, 0.65, 94.0, "https://jadavpuruniversity.in"),
    ("College of Engg Guindy", "CEG", "Chennai", "Tamil Nadu", "Tier 2", 22, 4.6, 0.35, 0.20, 12.0, 10.0, 0.45, 91.0, "https://ceg.annauniv.edu"),
    ("MS Ramaiah Institute of Technology", "MSRIT", "Bengaluru", "Karnataka", "Tier 2", 78, 4.3, 3.10, 1.00, 11.2, 9.5, 0.42, 88.0, "https://msrit.edu"),
    ("PES University", "PESU", "Bengaluru", "Karnataka", "Tier 2", 100, 4.25, 4.50, 1.20, 11.8, 10.0, 0.45, 88.5, "https://pes.edu"),
    ("SSN College of Engineering", "SSN", "Chennai", "Tamil Nadu", "Tier 2", 45, 4.4, 1.80, 0.70, 10.5, 9.0, 0.40, 89.5, "https://ssn.edu.in"),
    ("Kalinga Institute of Industrial Tech", "KIIT", "Bhubaneswar", "Odisha", "Tier 2", 39, 4.15, 3.50, 1.10, 8.2, 7.0, 0.35, 84.0, "https://kiit.ac.in"),
]

# Generate additional 90 colleges programmatically to complete 120 total colleges
CITIES_STATES = [
    ("Bengaluru", "Karnataka"), ("Pune", "Maharashtra"), ("Hyderabad", "Telangana"),
    ("Chennai", "Tamil Nadu"), ("Noida", "Uttar Pradesh"), ("Ahmedabad", "Gujarat"),
    ("Kochi", "Kerala"), ("Indore", "Madhya Pradesh"), ("Jaipur", "Rajasthan"),
    ("Chandigarh", "Punjab"), ("Bhubaneswar", "Odisha"), ("Lucknow", "Uttar Pradesh")
]

PREFIXES = ["National", "Metropolitan", "Apex", "Horizon", "Pioneer", "Global", "Imperial", "Summit", "Vanguard", "Zenith"]
TYPES = ["Institute of Technology", "College of Engineering", "University of Engineering", "Polytechnic & Tech Campus"]

for i in range(16, 121):
    city, state = random.choice(CITIES_STATES)
    prefix = random.choice(PREFIXES)
    ctype = random.choice(TYPES)
    cname = f"{prefix} {city} {ctype}"
    sname = f"{prefix[:3].upper()}{city[:3].upper()}"
    tier = random.choice(["Tier 2", "Tier 3", "Tier 3", "Tier 3"])
    nirf = 100 + i
    rating = round(random.uniform(3.5, 4.3), 2)
    fee = round(random.uniform(1.2, 3.5), 2) if tier == "Tier 3" else round(random.uniform(2.5, 4.5), 2)
    hostel = round(random.uniform(0.4, 0.9), 2)
    avg_pkg = round(random.uniform(4.5, 8.5), 2) if tier == "Tier 3" else round(random.uniform(7.5, 11.5), 2)
    med_pkg = round(avg_pkg * random.uniform(0.82, 0.92), 2)
    max_pkg = round(avg_pkg * random.uniform(2.2, 3.5), 2)
    p_rate = round(random.uniform(72.0, 88.0), 1)
    COLLEGES_SEED.append((cname, sname, city, state, tier, nirf, rating, fee, hostel, avg_pkg, med_pkg, max_pkg, p_rate))

BRANCHES = [
    ("CSE", "Computer Science & Engineering", 1.0, 1.25),
    ("AI_DS", "Artificial Intelligence & Data Science", 0.95, 1.20),
    ("ECE", "Electronics & Communication Engineering", 0.85, 1.05),
    ("IT", "Information Technology", 0.90, 1.10),
    ("EEE", "Electrical & Electronics Engineering", 0.75, 0.95),
    ("ME", "Mechanical Engineering", 0.65, 0.85),
    ("CE", "Civil Engineering", 0.60, 0.80),
    ("CHE", "Chemical Engineering", 0.70, 0.88),
    ("AERO", "Aerospace Engineering", 0.80, 1.00),
    ("BIOTECH", "Biotechnology", 0.65, 0.82)
]

CATEGORIES = ["General", "OBC", "SC", "ST", "EWS"]
ROUNDS = ["Round 1", "Round 2", "Round 3", "Spot Round"]
YEARS = [2021, 2022, 2023, 2024, 2025]

def generate_datasets():
    print("Generating Engineering College Analytics Master Dataset...")

    # 1. Colleges Table DataFrame
    colleges_list = []
    for cid, c in enumerate(COLLEGES_SEED, 1):
        colleges_list.append({
            "college_id": cid,
            "college_name": c[0],
            "short_name": c[1],
            "city": c[2],
            "state": c[3],
            "tier": c[4],
            "nirf_rank": c[5],
            "campus_rating": c[6],
            "tuition_fee_annual_lakhs": c[7],
            "hostel_fee_annual_lakhs": c[8],
            "avg_placement_lpa": c[9],
            "median_placement_lpa": c[10],
            "highest_placement_lpa": c[11],
            "placement_rate_pct": c[12],
            "accreditation": "NAAC A++" if c[4] == "Tier 1" else ("NAAC A+" if c[4] == "Tier 2" else "NAAC A"),
            "scholarship_available": "Yes" if c[4] in ["Tier 1", "Tier 2"] else random.choice(["Yes", "No"])
        })
    df_colleges = pd.DataFrame(colleges_list)

    # 2. Branches Table DataFrame
    branches_list = []
    for bid, b in enumerate(BRANCHES, 1):
        branches_list.append({
            "branch_id": bid,
            "branch_code": b[0],
            "branch_name": b[1],
            "demand_weight": b[2],
            "placement_multiplier": b[3]
        })
    df_branches = pd.DataFrame(branches_list)

    # 3. Cutoffs & Admission Trends Data (2021-2025)
    cutoffs_list = []
    cutoff_id = 1
    for cid, col in df_colleges.iterrows():
        base_tier_rank = 300 if col["tier"] == "Tier 1" else (3000 if col["tier"] == "Tier 2" else 15000)
        for bid, br in df_branches.iterrows():
            # Seat capacity
            seats = random.randint(60, 240) if br["branch_code"] in ["CSE", "ECE", "AI_DS", "IT"] else random.randint(30, 120)
            
            for year in YEARS:
                year_trend = 1.0 - (year - 2021) * 0.04 if br["branch_code"] in ["CSE", "AI_DS"] else 1.0 + (year - 2021) * 0.02
                for cat in CATEGORIES:
                    cat_mult = 1.0 if cat == "General" else (1.4 if cat == "EWS" else (1.8 if cat == "OBC" else (3.5 if cat == "SC" else 5.0)))
                    
                    for r_idx, rnd in enumerate(ROUNDS):
                        round_drop = 1.0 + (r_idx * 0.12)
                        
                        base_rank = int(base_tier_rank * br["demand_weight"] * cat_mult * year_trend * round_drop)
                        opening_rank = max(1, int(base_rank * random.uniform(0.70, 0.85)))
                        closing_rank = max(opening_rank + 10, int(base_rank * random.uniform(1.05, 1.25)))
                        
                        cutoffs_list.append({
                            "cutoff_id": cutoff_id,
                            "college_id": col["college_id"],
                            "branch_id": br["branch_id"],
                            "year": year,
                            "category": cat,
                            "round": rnd,
                            "opening_rank": opening_rank,
                            "closing_rank": closing_rank,
                            "seat_capacity": seats
                        })
                        cutoff_id += 1

    df_cutoffs = pd.DataFrame(cutoffs_list)

    # 4. Student Historical Outcomes Dataset for ML Training (15,000 records)
    print("Generating Historical Student Outcomes for ML Engine...")
    students_list = []
    states_all = list(set([c[3] for c in COLLEGES_SEED]))
    
    for sid in range(1, 15001):
        entrance_rank = int(np.random.exponential(scale=12000) + random.randint(100, 1000))
        cat = random.choices(CATEGORIES, weights=[0.45, 0.27, 0.15, 0.05, 0.08])[0]
        pref_br_obj = random.choice(BRANCHES)
        pref_state = random.choice(states_all)
        budget = round(random.uniform(1.0, 6.0), 2)
        hostel = random.choice([True, False])
        
        # Pick a target college
        target_col = df_colleges.sample(1).iloc[0]
        target_br = df_branches[df_branches["branch_code"] == pref_br_obj[0]].iloc[0]
        
        # Fetch relevant closing rank
        matching_cutoff = df_cutoffs[
            (df_cutoffs["college_id"] == target_col["college_id"]) & 
            (df_cutoffs["branch_id"] == target_br["branch_id"]) & 
            (df_cutoffs["category"] == cat) & 
            (df_cutoffs["year"] == 2024) & 
            (df_cutoffs["round"] == "Round 1")
        ]
        
        if not matching_cutoff.empty:
            c_rank = matching_cutoff.iloc[0]["closing_rank"]
        else:
            c_rank = 50000
            
        rank_diff = c_rank - entrance_rank
        annual_fee = target_col["tuition_fee_annual_lakhs"] + (target_col["hostel_fee_annual_lakhs"] if hostel else 0)
        budget_diff = budget - annual_fee
        
        # Admission probability formula for label creation
        prob = 1.0 / (1.0 + np.exp(-(rank_diff / 2500.0 + budget_diff * 0.5)))
        admitted = 1 if (random.random() < prob and entrance_rank <= c_rank * 1.15) else 0
        
        students_list.append({
            "student_id": sid,
            "entrance_rank": entrance_rank,
            "category": cat,
            "preferred_branch": pref_br_obj[0],
            "preferred_state": pref_state,
            "annual_budget_lakhs": budget,
            "hostel_needed": 1 if hostel else 0,
            "college_id": target_col["college_id"],
            "college_name": target_col["college_name"],
            "tier": target_col["tier"],
            "branch_id": target_br["branch_id"],
            "branch_code": target_br["branch_code"],
            "closing_rank": c_rank,
            "tuition_fee": target_col["tuition_fee_annual_lakhs"],
            "avg_placement_lpa": target_col["avg_placement_lpa"],
            "admitted": admitted
        })
        
    df_students = pd.DataFrame(students_list)

    # 5. Create Raw Messy Dataset for Data Quality & ETL Demonstrations
    print("Injecting realistic synthetic data quality issues into raw_college_data.csv...")
    raw_colleges = df_colleges.copy()
    
    # Add dirty columns & inconsistent formats
    raw_colleges["city_raw"] = raw_colleges["city"].apply(
        lambda c: f"  {c.upper()} " if random.random() < 0.2 else (c.lower() if random.random() < 0.15 else c)
    )
    
    # Inject missing values (NaN)
    missing_indices_fee = random.sample(range(len(raw_colleges)), 12)
    missing_indices_place = random.sample(range(len(raw_colleges)), 8)
    for idx in missing_indices_fee:
        raw_colleges.loc[idx, "tuition_fee_annual_lakhs"] = np.nan
    for idx in missing_indices_place:
        raw_colleges.loc[idx, "avg_placement_lpa"] = np.nan
        
    # Inject Outliers
    outlier_idx1 = random.randint(0, len(raw_colleges)-1)
    outlier_idx2 = random.randint(0, len(raw_colleges)-1)
    raw_colleges.loc[outlier_idx1, "tuition_fee_annual_lakhs"] = 99.9  # Fee outlier
    raw_colleges.loc[outlier_idx2, "avg_placement_lpa"] = 180.0       # Placement outlier
    
    # Duplicate rows (Append 15 duplicate rows)
    dup_rows = raw_colleges.sample(15)
    raw_colleges_dirty = pd.concat([raw_colleges, dup_rows], ignore_index=True)
    
    # Save CSV files
    raw_colleges_dirty.to_csv(os.path.join(DATA_DIR, "raw_college_data.csv"), index=False)
    df_colleges.to_csv(os.path.join(DATA_DIR, "cleaned_college_data.csv"), index=False)
    df_branches.to_csv(os.path.join(DATA_DIR, "branches_data.csv"), index=False)
    df_cutoffs.to_csv(os.path.join(DATA_DIR, "cutoffs_data.csv"), index=False)
    df_students.to_csv(os.path.join(DATA_DIR, "student_outcomes.csv"), index=False)
    
    # 6. Generate Verification Documents for RAG Knowledge Base
    generate_rag_documents()

    print("Master datasets generated successfully!")

def generate_rag_documents():
    docs = {
        "JoSAA_Counseling_Guidelines_2025.txt": """
OFFICIAL JOINT SEAT ALLOCATION AUTHORITY (JoSAA) ADMISSION GUIDELINES 2025

1. ELIGIBILITY & RANKING:
Candidates who qualify JEE Main / JEE Advanced are eligible for seat allocation across 23 IITs, 31 NITs, 26 IIITs, and 38 Other-GFTIs. Seat matrix is strictly allocated based on Category Rank (CRL for General, OBC-NCL Rank, SC/ST Rank, EWS Rank).

2. RESERVATION POLICY:
- General-EWS: 10% seats reserved for candidates with family annual income under INR 8 Lakhs.
- OBC-NCL: 27% seats reserved for Non-Creamy Layer candidates.
- SC: 15% seats reserved.
- ST: 7.5% seats reserved.
- PwD: 5% horizontal reservation across all categories.

3. SEAT ACCEPTANCE & DUAL REPORTING:
Upon receiving seat offer in any round, candidate must upload documents, pay Seat Acceptance Fee (INR 40,000 for Gen/OBC, INR 20,000 for SC/ST), and select Float, Freeze, or Slide options.

4. WITHDRAWAL & SPOT ROUND RULES:
Candidates wishing to exit counseling must withdraw prior to the final regular round. CSAB Special/Spot Rounds are conducted post JoSAA to fill vacant NIT+ system seats.
""",
        "Karnataka_CET_COMEDK_Fee_Structure_2025.txt": """
KARNATAKA ENGINEERING COLLEGE ADMISSION & SCHOLARSHIP NORMS 2025

1. FEE REGULATION (KEA & COMEDK):
- Government Seats (KEA CET): Tuition fee regulated at INR 75,000 to INR 1,15,000 per annum depending on college type.
- Management/COMEDK Seats: Quota tuition fee ranges between INR 2,20,000 and INR 3,50,000 per annum for top institutions like RVCE, BMSCE, and MSRIT.
- Hostel & Mess Charges: Range between INR 85,000 and INR 1,40,000 per annum across Bengaluru colleges.

2. TUITION FEE WAIVER (TFW) SCHEME:
Under AICTE guidelines, 5% supernumerary seats are reserved in every branch for meritorious students whose parental income is below INR 8.0 Lakhs per annum. TFW waives 100% tuition fees.

3. SCHOLARSHIPS:
- SSP (State Scholarship Portal): Full tuition fee reimbursement for SC/ST/OBC category students.
- Fee Concession for Rural & Kannada Medium candidates meeting eligibility cutoffs.
""",
        "Tier1_Institute_Placement_Report_2024.txt": """
ANNUAL PLACEMENT AUDIT REPORT 2024 - TOP ENGINEERING INSTITUTES

1. OVERALL HIGHLIGHTS:
- Average Compensation: IIT Bombay (24.5 LPA), IIT Delhi (25.0 LPA), IIIT Hyderabad (31.0 LPA), BITS Pilani (22.0 LPA), NIT Trichy (17.5 LPA).
- Highest Domestic Offer: INR 1.35 Crore (Software & Tech Sector).
- Placement Rate: Top Tier 1 CSE & AI/DS branches achieved 98% to 100% placement rate.

2. SECTOR-WISE BREAKDOWN:
- Software & Artificial Intelligence: 48% of total offers (Key Recruiters: Google, Microsoft, Apple, Nvidia, Texas Instruments).
- Analytics & Core Engineering: 28% of total offers (Key Recruiters: Goldman Sachs, Morgan Stanley, Schlumberger, L&T, Airbus).
- Product & Consulting: 24% of total offers (Key Recruiters: McKinsey, BCG, Bain, Amazon).

3. ROI ANALYSIS:
IIIT Hyderabad and Jadavpur University demonstrated the highest ROI ratio (Average Salary package relative to 4-year tuition outlay).
"""
    }
    
    for filename, content in docs.items():
        filepath = os.path.join(RAG_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content.strip())
            
    print(f"RAG document repository initialized with {len(docs)} verified texts.")

if __name__ == "__main__":
    generate_datasets()
