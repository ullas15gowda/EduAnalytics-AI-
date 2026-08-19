import os
import sys
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, Query, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List

# Add parent directory to sys.path for backend imports
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)

from backend.etl_pipeline import run_etl_pipeline, get_db_connection
from backend.eda_engine import get_overview_kpis, get_eda_visualizations
from backend.sql_analytics import SQL_QUESTIONS, execute_predefined_sql, execute_custom_sql
from backend.ml_engine import load_ml_artifacts, predict_admission_probability, train_and_evaluate_models
from backend.recommendation_engine import recommend_colleges
from backend.rag_engine import query_rag_system
from backend.llm_engine import ask_llm_assistant

app = FastAPI(
    title="AI-Powered Engineering College Admission Analytics Platform",
    description="Analytics-first decision support platform enhanced with ML & GenAI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Schemas for Requests
class PredictRequest(BaseModel):
    entrance_rank: int = Field(..., json_schema_extra={'example': 4500})
    closing_rank: int = Field(..., json_schema_extra={'example': 6000})
    annual_budget: float = Field(..., json_schema_extra={'example': 3.5})
    tuition_fee: float = Field(..., json_schema_extra={'example': 2.2})
    avg_placement_lpa: float = Field(..., json_schema_extra={'example': 16.5})
    tier: str = Field("Tier 1", json_schema_extra={'example': "Tier 1"})
    hostel_needed: int = Field(1, json_schema_extra={'example': 1})
    model_choice: str = Field("Gradient Boosting", json_schema_extra={'example': "Gradient Boosting"})

class RecommendRequest(BaseModel):
    entrance_rank: int = Field(..., json_schema_extra={'example': 4500})
    category: str = Field("General", json_schema_extra={'example': "General"})
    preferred_branch: str = Field("CSE", json_schema_extra={'example': "CSE"})
    preferred_state: Optional[str] = Field(None, json_schema_extra={'example': "Karnataka"})
    max_annual_budget: float = Field(5.0, json_schema_extra={'example': 4.0})
    hostel_needed: bool = Field(True, json_schema_extra={'example': True})
    min_placement_lpa: float = Field(0.0, json_schema_extra={'example': 8.0})
    top_n: int = Field(8, json_schema_extra={'example': 8})

class SQLExecuteRequest(BaseModel):
    sql_query: str

class RAGQueryRequest(BaseModel):
    query: str

class LLMQueryRequest(BaseModel):
    prompt: str

# 1. Health Check & Core Overview
@app.get("/api/health")
def health_check():
    return {"status": "online", "system": "FastAPI Analytical Engine", "version": "1.0.0"}

@app.get("/api/overview")
def get_overview():
    return get_overview_kpis()

@app.get("/api/data-quality")
def get_data_quality_report():
    conn = get_db_connection()
    df = conn.execute("SELECT * FROM data_quality_metrics").fetchone()
    conn.close()
    if df:
        return dict(df)
    return run_etl_pipeline()

@app.post("/api/data-quality/trigger-etl")
def trigger_etl():
    return run_etl_pipeline()

# 2. Colleges & Dataset Queries
@app.get("/api/colleges")
def get_colleges(
    tier: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    min_placement: Optional[float] = None,
    max_fee: Optional[float] = None
):
    conn = get_db_connection()
    sql = "SELECT * FROM colleges WHERE 1=1"
    params = []
    
    if tier:
        sql += " AND tier = ?"
        params.append(tier)
    if city:
        sql += " AND city LIKE ?"
        params.append(f"%{city}%")
    if state:
        sql += " AND state LIKE ?"
        params.append(f"%{state}%")
    if min_placement:
        sql += " AND avg_placement_lpa >= ?"
        params.append(min_placement)
    if max_fee:
        sql += " AND tuition_fee_annual_lakhs <= ?"
        params.append(max_fee)
        
    sql += " ORDER BY nirf_rank ASC"
    
    cursor = conn.cursor()
    rows = cursor.execute(sql, params).fetchall()
    conn.close()
    
    return [dict(r) for r in rows]

# 3. EDA & Visual Analytics
@app.get("/api/eda/visualizations")
def eda_visualizations():
    return get_eda_visualizations()

# 4. SQL Analytics Endpoints
@app.get("/api/sql/questions")
def get_sql_questions():
    return [{"id": q["id"], "question": q["question"], "sql": q["sql"]} for q in SQL_QUESTIONS]

@app.get("/api/sql/execute-predefined/{question_id}")
def run_predefined_sql(question_id: str):
    res = execute_predefined_sql(question_id)
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return res

@app.post("/api/sql/execute-custom")
def run_custom_sql(req: SQLExecuteRequest):
    res = execute_custom_sql(req.sql_query)
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return res

# 5. Machine Learning & Feature Engineering
@app.get("/api/ml/metrics")
def get_ml_metrics():
    artifacts = load_ml_artifacts()
    return artifacts["metadata"]

@app.post("/api/ml/retrain")
def retrain_models():
    return train_and_evaluate_models()

@app.post("/api/predict")
def predict(req: PredictRequest):
    return predict_admission_probability(
        entrance_rank=req.entrance_rank,
        closing_rank=req.closing_rank,
        annual_budget=req.annual_budget,
        tuition_fee=req.tuition_fee,
        avg_placement_lpa=req.avg_placement_lpa,
        tier=req.tier,
        hostel_needed=req.hostel_needed,
        model_choice=req.model_choice
    )

# 6. Hybrid Recommendation Engine
@app.post("/api/recommend")
def recommend(req: RecommendRequest):
    return recommend_colleges(
        entrance_rank=req.entrance_rank,
        category=req.category,
        preferred_branch=req.preferred_branch,
        preferred_state=req.preferred_state,
        max_annual_budget=req.max_annual_budget,
        hostel_needed=req.hostel_needed,
        min_placement_lpa=req.min_placement_lpa,
        top_n=req.top_n
    )

# 7. RAG & LLM Assistant
@app.post("/api/rag/query")
def rag_query(req: RAGQueryRequest):
    return query_rag_system(req.query)

@app.post("/api/llm/assistant")
def llm_assistant(req: LLMQueryRequest):
    return ask_llm_assistant(req.prompt)

# 8. Dedicated Karnataka Admission & Scholarship Assistant Endpoints
from backend.karnataka_engine import calculate_karnataka_scholarship, get_karnataka_college_recommendations, KARNATAKA_COLLEGES

class KarnatakaScholarshipRequest(BaseModel):
    category: str = Field("SC", json_schema_extra={'example': "SC"})
    annual_income: float = Field(1.8, json_schema_extra={'example': 1.8})
    is_kannada_medium: bool = Field(False, json_schema_extra={'example': False})
    is_rural: bool = Field(False, json_schema_extra={'example': False})
    kcet_rank: int = Field(5000, json_schema_extra={'example': 5000})
    tuition_fee: float = Field(112000.0, json_schema_extra={'example': 112000.0})

class KarnatakaGuideRequest(BaseModel):
    search_query: Optional[str] = Field(None, json_schema_extra={'example': "E001"})
    entrance_exam: str = Field("KCET", json_schema_extra={'example': "KCET"})
    rank: int = Field(2500, json_schema_extra={'example': 2500})
    category: str = Field("General", json_schema_extra={'example': "General"})
    preferred_branch: str = Field("CSE", json_schema_extra={'example': "CSE"})
    max_budget: float = Field(5.0, json_schema_extra={'example': 5.0})

@app.get("/api/karnataka/colleges")
def get_karnataka_colleges_list():
    return KARNATAKA_COLLEGES

@app.post("/api/karnataka/scholarship-check")
def karnataka_scholarship_check(req: KarnatakaScholarshipRequest):
    return calculate_karnataka_scholarship(
        category=req.category,
        annual_income=req.annual_income,
        is_kannada_medium=req.is_kannada_medium,
        is_rural=req.is_rural,
        kcet_rank=req.kcet_rank,
        tuition_fee=req.tuition_fee
    )

@app.post("/api/karnataka/college-guide")
def karnataka_college_guide(req: KarnatakaGuideRequest):
    return get_karnataka_college_recommendations(
        search_query=req.search_query,
        entrance_exam=req.entrance_exam,
        rank=req.rank,
        category=req.category,
        preferred_branch=req.preferred_branch,
        max_budget=req.max_budget
    )

# 9. Static Frontend Web UI Mount
FRONTEND_DIR = os.path.join(PROJECT_DIR, "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
def read_root():
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file, headers={"Cache-Control": "no-store"})
    return {"message": "Engineering College Analytics API Backend is active. Access /docs for OpenAPI specifications."}

if __name__ == "__main__":
    import uvicorn
    # Trigger initial ETL and ML training
    run_etl_pipeline()
    load_ml_artifacts()
    print("Starting FastAPI REST API server on http://localhost:8000 ...")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
