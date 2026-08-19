import os
import pandas as pd
from backend.etl_pipeline import get_db_connection

GOVT_PORTALS = {
    "KEA_PORTAL": "https://cetonline.karnataka.gov.in/kea/",
    "JOSAA_PORTAL": "https://josaa.nic.in/",
    "COMEDK_PORTAL": "https://www.comedk.org/member-institutions",
    "NIRF_PORTAL": "https://nirfindia.org/",
    "SSP_SCHOLARSHIP_PORTAL": "https://ssp.postmatric.karnataka.gov.in/"
}

BRANCH_MULTIPLIERS = {
    "CSE": 1.0,
    "AI_DS": 1.15,
    "IT": 1.25,
    "ECE": 1.45,
    "EEE": 1.85,
    "ME": 2.50,
    "CE": 3.20
}

BRANCH_NAMES = {
    "CSE": "Computer Science & Engineering (CSE)",
    "AI_DS": "Artificial Intelligence & Data Science (AI & DS)",
    "IT": "Information Technology (IT)",
    "ECE": "Electronics & Communication Engg (ECE)",
    "EEE": "Electrical & Electronics Engg (EEE)",
    "ME": "Mechanical Engineering (ME)",
    "CE": "Civil Engineering (CE)"
}

KARNATAKA_COLLEGES = [
    {"id": "kar_rvce", "name": "RV College of Engineering (RVCE)", "short_name": "RVCE Bengaluru", "location": "Mysore Road, Bengaluru", "website_url": "https://rvce.edu.in", "govt_portal_url": GOVT_PORTALS["KEA_PORTAL"], "contact_phone": "+91-080-68188100", "kcet_code": "E001", "comedk_code": "E095", "nirf_rank": 35, "tier": "Top Autonomous / Govt Aided", "kcet_fee_annual": 112000, "comedk_fee_annual": 264000, "mgmt_fee_annual": 650000, "hostel_fee_annual": 135000, "avg_placement_lpa": 16.5, "highest_placement_lpa": 62.0, "placement_rate_pct": 95.5, "kcet_cse_cutoff": 450, "comedk_cse_cutoff": 680, "cutoffs": {"General": 450, "2A": 1200, "2B": 1500, "3A": 850, "3B": 750, "SC": 5400, "ST": 8200, "Cat-1": 1800}},
    {"id": "kar_uvce", "name": "University Visvesvaraya College of Engineering (UVCE)", "short_name": "UVCE Bengaluru", "location": "KR Circle, Bengaluru", "website_url": "https://uvce.ac.in", "govt_portal_url": GOVT_PORTALS["KEA_PORTAL"], "contact_phone": "+91-080-22961800", "kcet_code": "E002", "comedk_code": "N/A (Govt Univ)", "nirf_rank": 72, "tier": "Government Autonomous University (Estd 1917)", "kcet_fee_annual": 45000, "comedk_fee_annual": 45000, "mgmt_fee_annual": 45000, "hostel_fee_annual": 45000, "avg_placement_lpa": 11.5, "highest_placement_lpa": 58.0, "placement_rate_pct": 94.0, "kcet_cse_cutoff": 850, "comedk_cse_cutoff": 850, "cutoffs": {"General": 850, "2A": 1950, "2B": 2200, "3A": 1400, "3B": 1150, "SC": 7800, "ST": 11000, "Cat-1": 2900}},
    {"id": "kar_bmsce", "name": "BMS College of Engineering (BMSCE)", "short_name": "BMSCE Basavanagudi", "location": "Basavanagudi, Bengaluru", "website_url": "https://bmsce.ac.in", "govt_portal_url": GOVT_PORTALS["KEA_PORTAL"], "contact_phone": "+91-080-26622130", "kcet_code": "E003", "comedk_code": "E027", "nirf_rank": 65, "tier": "Top Autonomous / Govt Aided", "kcet_fee_annual": 105000, "comedk_fee_annual": 240000, "mgmt_fee_annual": 550000, "hostel_fee_annual": 125000, "avg_placement_lpa": 13.8, "highest_placement_lpa": 50.0, "placement_rate_pct": 92.0, "kcet_cse_cutoff": 1200, "comedk_cse_cutoff": 1850, "cutoffs": {"General": 1200, "2A": 2800, "2B": 3200, "3A": 1900, "3B": 1600, "SC": 9500, "ST": 14000, "Cat-1": 3800}},
    {"id": "kar_drait", "name": "Dr. Ambedkar Institute of Technology (Dr. AIT)", "short_name": "Dr. AIT Mallathahalli", "location": "Mallathahalli, Bengaluru", "website_url": "https://drait.edu.in", "govt_portal_url": GOVT_PORTALS["KEA_PORTAL"], "contact_phone": "+91-080-23211505", "kcet_code": "E004", "comedk_code": "E041", "nirf_rank": 140, "tier": "Govt Aided Autonomous Institute", "kcet_fee_annual": 98000, "comedk_fee_annual": 220000, "mgmt_fee_annual": 350000, "hostel_fee_annual": 85000, "avg_placement_lpa": 7.8, "highest_placement_lpa": 32.0, "placement_rate_pct": 87.0, "kcet_cse_cutoff": 6500, "comedk_cse_cutoff": 9200, "cutoffs": {"General": 6500, "2A": 12500, "2B": 14000, "3A": 9200, "3B": 8100, "SC": 32000, "ST": 41000, "Cat-1": 16500}},
    {"id": "kar_msrit", "name": "MS Ramaiah Institute of Technology (MSRIT)", "short_name": "MSRIT Mathikere", "location": "MSR Nagar, Bengaluru", "website_url": "https://msrit.edu", "govt_portal_url": GOVT_PORTALS["KEA_PORTAL"], "contact_phone": "+91-080-23600822", "kcet_code": "E005", "comedk_code": "E077", "nirf_rank": 78, "tier": "Top Autonomous / Govt Aided", "kcet_fee_annual": 108000, "comedk_fee_annual": 245000, "mgmt_fee_annual": 580000, "hostel_fee_annual": 130000, "avg_placement_lpa": 12.5, "highest_placement_lpa": 48.0, "placement_rate_pct": 91.0, "kcet_cse_cutoff": 1650, "comedk_cse_cutoff": 2300, "cutoffs": {"General": 1650, "2A": 3500, "2B": 3900, "3A": 2400, "3B": 2100, "SC": 11500, "ST": 16500, "Cat-1": 4500}},
    {"id": "kar_mvjce", "name": "MVJ College of Engineering (MVJCE)", "short_name": "MVJCE Whitefield", "location": "Channasandra, Whitefield, Bengaluru", "website_url": "https://mvjce.edu.in", "govt_portal_url": GOVT_PORTALS["KEA_PORTAL"], "contact_phone": "+91-080-42571241", "kcet_code": "E006", "comedk_code": "E084", "nirf_rank": 165, "tier": "NAAC A Grade Autonomous Institute", "kcet_fee_annual": 105000, "comedk_fee_annual": 225000, "mgmt_fee_annual": 380000, "hostel_fee_annual": 95000, "avg_placement_lpa": 6.8, "highest_placement_lpa": 27.5, "placement_rate_pct": 85.0, "kcet_cse_cutoff": 11500, "comedk_cse_cutoff": 16000, "cutoffs": {"General": 11500, "2A": 21000, "2B": 23500, "3A": 16500, "3B": 14200, "SC": 55000, "ST": 68000, "Cat-1": 27000}},
    {"id": "kar_gec_hassan", "name": "Government Engineering College (GEC Hassan)", "short_name": "GEC Hassan", "location": "Dairy Circle, Katihalli, Hassan", "website_url": "http://gechassan.ac.in", "govt_portal_url": GOVT_PORTALS["KEA_PORTAL"], "contact_phone": "+91-08172-240444", "kcet_code": "E007", "comedk_code": "N/A (Govt)", "nirf_rank": 190, "tier": "Government Engineering College", "kcet_fee_annual": 35000, "comedk_fee_annual": 35000, "mgmt_fee_annual": 35000, "hostel_fee_annual": 40000, "avg_placement_lpa": 5.5, "highest_placement_lpa": 18.0, "placement_rate_pct": 82.0, "kcet_cse_cutoff": 15500, "comedk_cse_cutoff": 15500, "cutoffs": {"General": 15500, "2A": 28000, "2B": 31000, "3A": 21000, "3B": 19000, "SC": 65000, "ST": 78000, "Cat-1": 34000}},
    {"id": "kar_bit", "name": "Bangalore Institute of Technology (BIT)", "short_name": "BIT VV Puram", "location": "VV Puram, KR Road, Bengaluru", "website_url": "https://bit-bangalore.edu.in", "govt_portal_url": GOVT_PORTALS["KEA_PORTAL"], "contact_phone": "+91-080-26615865", "kcet_code": "E008", "comedk_code": "E019", "nirf_rank": 130, "tier": "Top Govt Aided", "kcet_fee_annual": 102000, "comedk_fee_annual": 230000, "mgmt_fee_annual": 400000, "hostel_fee_annual": 105000, "avg_placement_lpa": 9.2, "highest_placement_lpa": 38.0, "placement_rate_pct": 88.0, "kcet_cse_cutoff": 3900, "comedk_cse_cutoff": 5200, "cutoffs": {"General": 3900, "2A": 8100, "2B": 8900, "3A": 6200, "3B": 5400, "SC": 24500, "ST": 32500, "Cat-1": 10800}},
    {"id": "kar_pesce", "name": "PES College of Engineering (PESCE)", "short_name": "PESCE Mandya", "location": "KV Shankaragowda Road, Mandya", "website_url": "https://pesce.ac.in", "govt_portal_url": GOVT_PORTALS["KEA_PORTAL"], "contact_phone": "+91-08232-220043", "kcet_code": "E009", "comedk_code": "E096", "nirf_rank": 148, "tier": "Govt Aided Autonomous Institute", "kcet_fee_annual": 95000, "comedk_fee_annual": 215000, "mgmt_fee_annual": 340000, "hostel_fee_annual": 75000, "avg_placement_lpa": 6.8, "highest_placement_lpa": 24.0, "placement_rate_pct": 85.5, "kcet_cse_cutoff": 9800, "comedk_cse_cutoff": 13500, "cutoffs": {"General": 9800, "2A": 18000, "2B": 20000, "3A": 13500, "3B": 11800, "SC": 46000, "ST": 56000, "Cat-1": 23500}},
    {"id": "kar_ssit", "name": "Sri Siddhartha Institute of Technology (SSIT)", "short_name": "SSIT Tumakuru", "location": "Maralur, Tumakuru", "website_url": "https://ssit.edu.in", "govt_portal_url": GOVT_PORTALS["KEA_PORTAL"], "contact_phone": "+91-0816-2200314", "kcet_code": "E010", "comedk_code": "E117", "nirf_rank": 170, "tier": "Deemed / VTU Affiliated Autonomous", "kcet_fee_annual": 102000, "comedk_fee_annual": 210000, "mgmt_fee_annual": 320000, "hostel_fee_annual": 80000, "avg_placement_lpa": 6.0, "highest_placement_lpa": 22.0, "placement_rate_pct": 83.0, "kcet_cse_cutoff": 13500, "comedk_cse_cutoff": 18500, "cutoffs": {"General": 13500, "2A": 24000, "2B": 27000, "3A": 18500, "3B": 16200, "SC": 58000, "ST": 70000, "Cat-1": 29000}},
    {"id": "kar_sir_mvit", "name": "Sir M Visvesvaraya Institute of Technology (Sir MVIT)", "short_name": "Sir MVIT Yelahanka", "location": "Hunasamaranahalli, International Airport Road, Bengaluru", "website_url": "https://sirmvit.edu", "govt_portal_url": GOVT_PORTALS["KEA_PORTAL"], "contact_phone": "+91-080-28384201", "kcet_code": "E012", "comedk_code": "E114", "nirf_rank": 135, "tier": "Govt Aided / Autonomous Institute", "kcet_fee_annual": 102000, "comedk_fee_annual": 230000, "mgmt_fee_annual": 410000, "hostel_fee_annual": 105000, "avg_placement_lpa": 8.5, "highest_placement_lpa": 36.0, "placement_rate_pct": 88.0, "kcet_cse_cutoff": 5800, "comedk_cse_cutoff": 8200, "cutoffs": {"General": 5800, "2A": 11500, "2B": 13000, "3A": 8800, "3B": 7500, "SC": 34000, "ST": 43000, "Cat-1": 15000}},
    {"id": "kar_dsce", "name": "Dayananda Sagar College of Engineering (DSCE)", "short_name": "DSCE Kumaraswamy Layout", "location": "Kumaraswamy Layout, Bengaluru", "website_url": "https://dayanandasagar.edu", "govt_portal_url": GOVT_PORTALS["KEA_PORTAL"], "contact_phone": "+91-080-42161750", "kcet_code": "E014", "comedk_code": "E040", "nirf_rank": 125, "tier": "Top Autonomous / Govt Aided", "kcet_fee_annual": 108000, "comedk_fee_annual": 240000, "mgmt_fee_annual": 450000, "hostel_fee_annual": 120000, "avg_placement_lpa": 10.5, "highest_placement_lpa": 45.0, "placement_rate_pct": 90.0, "kcet_cse_cutoff": 3400, "comedk_cse_cutoff": 4800, "cutoffs": {"General": 3400, "2A": 7200, "2B": 8100, "3A": 5400, "3B": 4800, "SC": 22000, "ST": 29000, "Cat-1": 9500}},
    {"id": "kar_svce", "name": "Sri Venkateswara College of Engineering (SVCE)", "short_name": "SVCE Yelahanka", "location": "Vidyanagar, Yelahanka, Bengaluru", "website_url": "https://svce.edu.in", "govt_portal_url": GOVT_PORTALS["KEA_PORTAL"], "contact_phone": "+91-080-28372800", "kcet_code": "E015", "comedk_code": "E120", "nirf_rank": 180, "tier": "NAAC A Grade Autonomous Institute", "kcet_fee_annual": 105000, "comedk_fee_annual": 220000, "mgmt_fee_annual": 350000, "hostel_fee_annual": 90000, "avg_placement_lpa": 6.2, "highest_placement_lpa": 25.0, "placement_rate_pct": 84.0, "kcet_cse_cutoff": 12800, "comedk_cse_cutoff": 17500, "cutoffs": {"General": 12800, "2A": 23000, "2B": 25500, "3A": 17800, "3B": 15500, "SC": 60000, "ST": 72000, "Cat-1": 31000}},
    {"id": "kar_pesu", "name": "PES University (RR Campus)", "short_name": "PESU Banashankari", "location": "100 Feet Ring Road, Banashankari 3rd Stage, Bengaluru", "website_url": "https://pes.edu", "govt_portal_url": GOVT_PORTALS["KEA_PORTAL"], "contact_phone": "+91-080-26721983", "kcet_code": "E016", "comedk_code": "N/A (PESSAT)", "nirf_rank": 85, "tier": "Top Autonomous / State Private University", "kcet_fee_annual": 112000, "comedk_fee_annual": 380000, "mgmt_fee_annual": 450000, "hostel_fee_annual": 130000, "avg_placement_lpa": 13.5, "highest_placement_lpa": 52.0, "placement_rate_pct": 93.0, "kcet_cse_cutoff": 1100, "comedk_cse_cutoff": 1500, "cutoffs": {"General": 1100, "2A": 2500, "2B": 2900, "3A": 1700, "3B": 1450, "SC": 8800, "ST": 13000, "Cat-1": 3400}},
    {"id": "kar_reva", "name": "REVA University", "short_name": "REVA Yelahanka", "location": "Rukmini Knowledge Park, Yelahanka, Bengaluru", "website_url": "https://reva.edu.in", "govt_portal_url": GOVT_PORTALS["KEA_PORTAL"], "contact_phone": "+91-080-46966966", "kcet_code": "E017", "comedk_code": "N/A (REVA CET)", "nirf_rank": 115, "tier": "State Private University with KEA Seats", "kcet_fee_annual": 110000, "comedk_fee_annual": 280000, "mgmt_fee_annual": 390000, "hostel_fee_annual": 120000, "avg_placement_lpa": 8.2, "highest_placement_lpa": 36.0, "placement_rate_pct": 87.5, "kcet_cse_cutoff": 7800, "comedk_cse_cutoff": 10500, "cutoffs": {"General": 7800, "2A": 15000, "2B": 17000, "3A": 11500, "3B": 9800, "SC": 39000, "ST": 48000, "Cat-1": 20000}},
    {"id": "kar_cmrit", "name": "CMR Institute of Technology (CMRIT)", "short_name": "CMRIT ITPL", "location": "ITPL Main Road, Marathahalli, Bengaluru", "website_url": "https://cmrit.ac.in", "govt_portal_url": GOVT_PORTALS["KEA_PORTAL"], "contact_phone": "+91-080-28524466", "kcet_code": "E019", "comedk_code": "E033", "nirf_rank": 155, "tier": "NAAC A+ Autonomous Institute", "kcet_fee_annual": 105000, "comedk_fee_annual": 230000, "mgmt_fee_annual": 380000, "hostel_fee_annual": 110000, "avg_placement_lpa": 7.6, "highest_placement_lpa": 30.0, "placement_rate_pct": 86.5, "kcet_cse_cutoff": 8200, "comedk_cse_cutoff": 11500, "cutoffs": {"General": 8200, "2A": 15800, "2B": 17500, "3A": 12200, "3B": 10500, "SC": 41000, "ST": 50000, "Cat-1": 21500}},
    {"id": "kar_nhce", "name": "New Horizon College of Engineering (NHCE)", "short_name": "NHCE Marathahalli", "location": "Outer Ring Road, Kadubesanahalli, Bengaluru", "website_url": "https://newhorizonindia.edu", "govt_portal_url": GOVT_PORTALS["KEA_PORTAL"], "contact_phone": "+91-080-66297777", "kcet_code": "E020", "comedk_code": "E088", "nirf_rank": 120, "tier": "NAAC A Grade Autonomous Institute", "kcet_fee_annual": 108000, "comedk_fee_annual": 240000, "mgmt_fee_annual": 420000, "hostel_fee_annual": 115000, "avg_placement_lpa": 9.0, "highest_placement_lpa": 40.0, "placement_rate_pct": 89.0, "kcet_cse_cutoff": 6200, "comedk_cse_cutoff": 8800, "cutoffs": {"General": 6200, "2A": 12000, "2B": 13800, "3A": 9400, "3B": 8000, "SC": 35000, "ST": 44000, "Cat-1": 15800}},
    {"id": "kar_nmit", "name": "Nitte Meenakshi Institute of Technology (NMIT)", "short_name": "NMIT Yelahanka", "location": "Govindapura, Yelahanka, Bengaluru", "website_url": "https://nmit.ac.in", "govt_portal_url": GOVT_PORTALS["KEA_PORTAL"], "contact_phone": "+91-080-22167800", "kcet_code": "E027", "comedk_code": "E087", "nirf_rank": 135, "tier": "NAAC A+ Grade Autonomous Institute", "kcet_fee_annual": 105000, "comedk_fee_annual": 235000, "mgmt_fee_annual": 410000, "hostel_fee_annual": 110000, "avg_placement_lpa": 8.4, "highest_placement_lpa": 41.0, "placement_rate_pct": 88.0, "kcet_cse_cutoff": 5500, "comedk_cse_cutoff": 7900, "cutoffs": {"General": 5500, "2A": 11000, "2B": 12500, "3A": 8400, "3B": 7200, "SC": 33000, "ST": 42000, "Cat-1": 14500}},
    {"id": "kar_sit_tumkur", "name": "Siddaganga Institute of Technology (SIT)", "short_name": "SIT Tumakuru", "location": "BH Road, Tumakuru", "website_url": "http://www.sit.ac.in", "govt_portal_url": GOVT_PORTALS["KEA_PORTAL"], "contact_phone": "+91-0816-2214000", "kcet_code": "E030", "comedk_code": "E115", "nirf_rank": 100, "tier": "Top Govt Aided Autonomous", "kcet_fee_annual": 95000, "comedk_fee_annual": 225000, "mgmt_fee_annual": 380000, "hostel_fee_annual": 85000, "avg_placement_lpa": 8.8, "highest_placement_lpa": 36.5, "placement_rate_pct": 89.0, "kcet_cse_cutoff": 4800, "comedk_cse_cutoff": 6800, "cutoffs": {"General": 4800, "2A": 9800, "2B": 10800, "3A": 7400, "3B": 6200, "SC": 28000, "ST": 36000, "Cat-1": 12800}},
    {"id": "kar_kle_hubli", "name": "KLE Technological University (BVB College of Engg)", "short_name": "KLE Tech / BVB Hubballi", "location": "Vidyanagar, Hubballi", "website_url": "https://kletech.ac.in", "govt_portal_url": GOVT_PORTALS["KEA_PORTAL"], "contact_phone": "+91-0836-2378101", "kcet_code": "E031", "comedk_code": "E034", "nirf_rank": 101, "tier": "Top North Karnataka Autonomous University", "kcet_fee_annual": 102000, "comedk_fee_annual": 230000, "mgmt_fee_annual": 390000, "hostel_fee_annual": 88000, "avg_placement_lpa": 8.5, "highest_placement_lpa": 43.0, "placement_rate_pct": 88.5, "kcet_cse_cutoff": 5200, "comedk_cse_cutoff": 7500, "cutoffs": {"General": 5200, "2A": 10500, "2B": 11800, "3A": 8100, "3B": 6900, "SC": 31000, "ST": 39000, "Cat-1": 14200}},
    {"id": "kar_git_belgaum", "name": "KLS Gogte Institute of Technology (GIT)", "short_name": "GIT Belagavi", "location": "Udyambag, Belagavi", "website_url": "https://git.edu", "govt_portal_url": GOVT_PORTALS["KEA_PORTAL"], "contact_phone": "+91-0831-2405500", "kcet_code": "E039", "comedk_code": "E061", "nirf_rank": 160, "tier": "Top North Karnataka Autonomous", "kcet_fee_annual": 98000, "comedk_fee_annual": 220000, "mgmt_fee_annual": 350000, "hostel_fee_annual": 82000, "avg_placement_lpa": 7.2, "highest_placement_lpa": 26.0, "placement_rate_pct": 86.0, "kcet_cse_cutoff": 8800, "comedk_cse_cutoff": 12000, "cutoffs": {"General": 8800, "2A": 16500, "2B": 18500, "3A": 12800, "3B": 11200, "SC": 42000, "ST": 52000, "Cat-1": 22000}},
    {"id": "kar_sjce", "name": "Sri Jayachamarajendra College of Engineering (SJCE / JSS STU)", "short_name": "SJCE Mysuru", "location": "Manasagangothri, Mysuru", "website_url": "https://jssstuniv.in", "govt_portal_url": GOVT_PORTALS["KEA_PORTAL"], "contact_phone": "+91-0821-2548285", "kcet_code": "E057", "comedk_code": "E058", "nirf_rank": 140, "tier": "Top Govt Aided / Univ", "kcet_fee_annual": 98000, "comedk_fee_annual": 230000, "mgmt_fee_annual": 420000, "hostel_fee_annual": 95000, "avg_placement_lpa": 11.2, "highest_placement_lpa": 42.0, "placement_rate_pct": 90.5, "kcet_cse_cutoff": 2900, "comedk_cse_cutoff": 4200, "cutoffs": {"General": 2900, "2A": 6500, "2B": 7200, "3A": 4800, "3B": 4100, "SC": 21000, "ST": 29000, "Cat-1": 8200}},
    {"id": "kar_nie_north", "name": "The National Institute of Engineering (NIE Mysuru)", "short_name": "NIE South & North Mysuru", "location": "Manandavadi Road / Koorgalli, Mysuru", "website_url": "https://nie.ac.in", "govt_portal_url": GOVT_PORTALS["KEA_PORTAL"], "contact_phone": "+91-0821-2480478", "kcet_code": "E056", "comedk_code": "E085", "nirf_rank": 150, "tier": "Top Govt Aided Autonomous", "kcet_fee_annual": 95000, "comedk_fee_annual": 225000, "mgmt_fee_annual": 380000, "hostel_fee_annual": 90000, "avg_placement_lpa": 10.5, "highest_placement_lpa": 38.0, "placement_rate_pct": 88.5, "kcet_cse_cutoff": 3800, "comedk_cse_cutoff": 5500, "cutoffs": {"General": 3800, "2A": 8200, "2B": 9100, "3A": 6100, "3B": 5200, "SC": 24000, "ST": 32000, "Cat-1": 10500}},
    {"id": "kar_mit_mysore", "name": "Maharaja Institute of Technology Mysore (MIT Mysore, Belawadi)", "short_name": "MIT Mysore (Belawadi)", "location": "Belawadi, Srirangapatna Tq, Mandya-Mysore Highway, Mysuru", "website_url": "https://mitmysore.in/", "govt_portal_url": GOVT_PORTALS["KEA_PORTAL"], "contact_phone": "+91-08236-292601", "kcet_code": "E158", "comedk_code": "E078", "pgcet_mba_code": "B219", "pgcet_mca_code": "C446", "nirf_rank": 175, "tier": "NAAC A Grade Autonomous / VTU", "kcet_fee_annual": 105000, "comedk_fee_annual": 225000, "mgmt_fee_annual": 320000, "hostel_fee_annual": 90000, "avg_placement_lpa": 6.2, "highest_placement_lpa": 28.0, "placement_rate_pct": 86.5, "kcet_cse_cutoff": 14500, "comedk_cse_cutoff": 19500, "cutoffs": {"General": 14500, "2A": 26000, "2B": 29000, "3A": 19500, "3B": 17800, "SC": 62000, "ST": 72000, "Cat-1": 31000}},
    {"id": "kar_mit_thandavapura", "name": "Maharaja Institute of Technology Thandavapura (MITT)", "short_name": "MIT Thandavapura", "location": "Thandavapura, Nanjangud Taluk, Mysuru", "website_url": "https://mitt.edu.in/", "govt_portal_url": GOVT_PORTALS["KEA_PORTAL"], "contact_phone": "+91-0821-2970170", "kcet_code": "E258", "comedk_code": "E082", "nirf_rank": 210, "tier": "VTU Affiliated Engineering Institute", "kcet_fee_annual": 102000, "comedk_fee_annual": 210000, "mgmt_fee_annual": 280000, "hostel_fee_annual": 85000, "avg_placement_lpa": 5.2, "highest_placement_lpa": 20.0, "placement_rate_pct": 80.0, "kcet_cse_cutoff": 22000, "comedk_cse_cutoff": 28000, "cutoffs": {"General": 22000, "2A": 38000, "2B": 42000, "3A": 29000, "3B": 26000, "SC": 85000, "ST": 95000, "Cat-1": 45000}},
    {"id": "kar_rrce", "name": "Raja Rajeswari College of Engineering (RRCE)", "short_name": "RRCE Kumbalgodu", "location": "Kumbalgodu, Mysore Road, Bengaluru", "website_url": "https://www.rrce.org", "govt_portal_url": GOVT_PORTALS["KEA_PORTAL"], "contact_phone": "+91-080-28437124", "kcet_code": "E158_ALT", "comedk_code": "E099", "nirf_rank": 195, "tier": "NAAC A+ & NBA Accredited Autonomous", "kcet_fee_annual": 105000, "comedk_fee_annual": 220000, "mgmt_fee_annual": 320000, "hostel_fee_annual": 95000, "avg_placement_lpa": 5.5, "highest_placement_lpa": 24.0, "placement_rate_pct": 82.5, "kcet_cse_cutoff": 18500, "comedk_cse_cutoff": 24000, "cutoffs": {"General": 18500, "2A": 32000, "2B": 35000, "3A": 24000, "3B": 22000, "SC": 75000, "ST": 85000, "Cat-1": 38000}},
    {"id": "kar_acharya", "name": "Acharya Institute of Technology", "short_name": "Acharya Soladevanahalli", "location": "Soladevanahalli, Hesaraghatta Road, Bengaluru", "website_url": "https://www.acharya.ac.in", "govt_portal_url": GOVT_PORTALS["KEA_PORTAL"], "contact_phone": "+91-080-23722222", "kcet_code": "E086", "comedk_code": "E086_COMEDK", "nirf_rank": 150, "tier": "NAAC A Grade Autonomous / VTU", "kcet_fee_annual": 105000, "comedk_fee_annual": 235000, "mgmt_fee_annual": 400000, "hostel_fee_annual": 110000, "avg_placement_lpa": 7.5, "highest_placement_lpa": 34.0, "placement_rate_pct": 86.0, "kcet_cse_cutoff": 9500, "comedk_cse_cutoff": 12500, "cutoffs": {"General": 9500, "2A": 18500, "2B": 20500, "3A": 14200, "3B": 12500, "SC": 48000, "ST": 58000, "Cat-1": 24000}},
    {"id": "kar_bmsit", "name": "BMS Institute of Technology & Management (BMSIT)", "short_name": "BMSIT Yelahanka", "location": "Yelahanka, Bengaluru", "website_url": "https://bmsit.ac.in", "govt_portal_url": GOVT_PORTALS["KEA_PORTAL"], "contact_phone": "+91-080-68730424", "kcet_code": "E092", "comedk_code": "E028", "nirf_rank": 145, "tier": "Top Private Autonomous", "kcet_fee_annual": 105000, "comedk_fee_annual": 235000, "mgmt_fee_annual": 420000, "hostel_fee_annual": 110000, "avg_placement_lpa": 9.5, "highest_placement_lpa": 44.0, "placement_rate_pct": 89.5, "kcet_cse_cutoff": 4200, "comedk_cse_cutoff": 5800, "cutoffs": {"General": 4200, "2A": 8500, "2B": 9400, "3A": 6500, "3B": 5800, "SC": 26000, "ST": 34000, "Cat-1": 11200}}
]

def calculate_karnataka_scholarship(
    category: str,
    annual_income: float,
    is_kannada_medium: bool = False,
    is_rural: bool = False,
    kcet_rank: int = 5000,
    tuition_fee: float = 112000
):
    eligible_schemes = []
    total_benefit = 0.0

    if category in ["SC", "ST"]:
        if annual_income <= 2.5:
            waiver = tuition_fee
            total_benefit += waiver
            eligible_schemes.append({
                "name": "SSP Karnataka Post-Matric SC/ST 100% Fee Reimbursement",
                "authority": "Social Welfare Dept, Govt of Karnataka",
                "benefit": f"100% Tuition Fee Waiver (INR {waiver:,.0f}/year)",
                "amount": waiver,
                "portal": GOVT_PORTALS["SSP_SCHOLARSHIP_PORTAL"],
                "documents_required": ["Caste Certificate", "Income Certificate (< 2.5L)", "KEA Allotment Letter", "Aadhaar Seeded Bank Account"]
            })
    elif category in ["Cat-1", "2A", "2B", "3A", "3B"]:
        if annual_income <= 2.5:
            waiver = min(tuition_fee, 60000.0)
            total_benefit += waiver
            eligible_schemes.append({
                "name": "SSP Backward Classes Welfare Fee Concession (EPass)",
                "authority": "BCWD Karnataka",
                "benefit": f"Tuition Fee Reimbursement up to INR {waiver:,.0f}/year",
                "amount": waiver,
                "portal": GOVT_PORTALS["SSP_SCHOLARSHIP_PORTAL"],
                "documents_required": ["BCWD Income Certificate (< 2.5L)", "KEA Allotment Order", "SSLC Marksheet"]
            })

    if annual_income <= 8.0 and kcet_rank <= 15000:
        tfw_benefit = tuition_fee * 0.90
        eligible_schemes.append({
            "name": "AICTE Supernumerary Tuition Fee Waiver (TFW) Scheme",
            "authority": "Karnataka Examinations Authority (KEA)",
            "benefit": f"100% Waiver of Tuition Component (INR {tfw_benefit:,.0f}/year)",
            "amount": tfw_benefit,
            "portal": GOVT_PORTALS["KEA_PORTAL"],
            "documents_required": ["RD Income Certificate (< INR 8.0 Lakhs)", "Verification Slip"]
        })

    if annual_income <= 2.5 and category in ["Cat-1", "2A", "2B", "3A", "3B", "SC", "ST"]:
        eligible_schemes.append({
            "name": "Vidyasiri Hostel Maintenance Allowance Scheme",
            "authority": "Dept of Backward Classes Welfare",
            "benefit": "INR 15,000 per annum (INR 1,500/month for 10 months)",
            "amount": 15000.0,
            "portal": GOVT_PORTALS["SSP_SCHOLARSHIP_PORTAL"],
            "documents_required": ["Hostel Admission Certificate", "Hostel Warden Verification"]
        })

    return {
        "candidate_category": category,
        "annual_income_lakhs": annual_income,
        "eligible_scholarships_count": len(eligible_schemes),
        "total_estimated_annual_benefit": total_benefit,
        "net_effective_fee": max(0.0, tuition_fee - total_benefit),
        "schemes": eligible_schemes,
        "govt_portals": GOVT_PORTALS
    }

def get_karnataka_college_recommendations(
    search_query: str = None,
    entrance_exam: str = "KCET",
    rank: int = 2500,
    category: str = "General",
    preferred_branch: str = "CSE",
    max_budget: float = 999.0
):
    results = []
    sq_raw = search_query.strip() if search_query and search_query.strip() else None
    sq_upper = sq_raw.upper() if sq_raw else None
    sq_lower = sq_raw.lower() if sq_raw else None

    mult = BRANCH_MULTIPLIERS.get(preferred_branch, 1.0)
    branch_full_name = BRANCH_NAMES.get(preferred_branch, preferred_branch)

    # First Pass: Search strictly by KEA/KCET Code if E-code query is provided
    matched_colleges = []
    if sq_upper and sq_upper.startswith("E"):
        for c in KARNATAKA_COLLEGES:
            # Exact or prefix match on KCET code (e.g. E006, E001, E003, E004, E005, E016...)
            code_num = sq_upper[1:]
            kcet_num = c["kcet_code"].upper()[1:] if c["kcet_code"].upper().startswith("E") else ""
            if c["kcet_code"].upper() == sq_upper or (code_num and kcet_num and code_num == kcet_num.lstrip("0")):
                matched_colleges.append(c)

    # Second Pass: Name or fuzzy match if first pass returned nothing
    if not matched_colleges:
        for c in KARNATAKA_COLLEGES:
            if sq_lower:
                matches_name = sq_lower in c["name"].lower() or sq_lower in c["short_name"].lower() or sq_lower in c["id"].lower() or sq_lower in c["location"].lower()
                matches_kcet = sq_upper == c["kcet_code"].upper() or (sq_upper.startswith("E") and sq_upper in c["kcet_code"].upper())
                if not (matches_name or matches_kcet):
                    continue
            matched_colleges.append(c)

    for c in matched_colleges:
        base_cutoff = c["cutoffs"].get(category, c["kcet_cse_cutoff"])
        branch_cutoff = int(base_cutoff * mult)
        
        if entrance_exam == "KCET":
            annual_fee = c["kcet_fee_annual"]
            eff_cutoff = branch_cutoff
        elif entrance_exam == "COMEDK":
            annual_fee = c["comedk_fee_annual"]
            eff_cutoff = int(branch_cutoff * 1.4)
        else:
            annual_fee = c["mgmt_fee_annual"]
            eff_cutoff = 999999
            
        fee_in_lakhs = annual_fee / 100000.0
        
        if rank <= eff_cutoff:
            prob_score = 92.0
            status = "Strong Admission Chance (KEA Seat)"
        elif rank <= eff_cutoff * 1.35:
            prob_score = 68.0
            status = "Target Round 2 / Extended Round"
        else:
            prob_score = 45.0
            status = "High Competition - Consider COMEDK Quota"
            
        results.append({
            "college_id": c["id"],
            "college_name": c["name"],
            "short_name": c["short_name"],
            "location": c["location"],
            "website_url": c["website_url"],
            "govt_portal_url": c["govt_portal_url"],
            "contact_phone": c["contact_phone"],
            "kcet_code": c["kcet_code"],
            "comedk_code": c.get("comedk_code", "N/A"),
            "pgcet_mba_code": c.get("pgcet_mba_code", "N/A"),
            "pgcet_mca_code": c.get("pgcet_mca_code", "N/A"),
            "nirf_rank": c["nirf_rank"],
            "tier": c["tier"],
            "entrance_exam": entrance_exam,
            "selected_branch": preferred_branch,
            "selected_branch_name": branch_full_name,
            "avg_placement_lpa": c["avg_placement_lpa"],
            "highest_placement_lpa": c["highest_placement_lpa"],
            "placement_rate_pct": c["placement_rate_pct"],
            "category_cutoff_rank": eff_cutoff,
            "admission_status": status,
            "match_score": round(prob_score, 1)
        })
        
    # Rank colleges strictly by NIRF Rank & Admission Status
    results.sort(key=lambda x: (x["nirf_rank"], -x["match_score"]))
    return results

if __name__ == "__main__":
    res = get_karnataka_college_recommendations(search_query="E006")
    print([r["kcet_code"] + ": " + r["college_name"] for r in res])
