import os
import sys
from flask import Flask, jsonify, request

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)

from backend.etl_pipeline import run_etl_pipeline, get_db_connection

flask_app = Flask(__name__)

@flask_app.route("/health", methods=["GET"])
def health():
    return jsonify({"service": "Flask Admin & Data Quality Monitor", "status": "online", "port": 5001})

@flask_app.route("/admin/data-quality", methods=["GET"])
def data_quality_admin():
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM data_quality_metrics").fetchone()
    conn.close()
    if row:
        return jsonify(dict(row))
    metrics = run_etl_pipeline()
    return jsonify(metrics)

@flask_app.route("/admin/trigger-etl", methods=["POST"])
def trigger_etl():
    metrics = run_etl_pipeline()
    return jsonify({"message": "ETL pipeline re-executed successfully", "metrics": metrics})

@flask_app.route("/admin/system-stats", methods=["GET"])
def system_stats():
    conn = get_db_connection()
    c_count = conn.execute("SELECT COUNT(*) FROM colleges").fetchone()[0]
    b_count = conn.execute("SELECT COUNT(*) FROM branches").fetchone()[0]
    cut_count = conn.execute("SELECT COUNT(*) FROM cutoffs").fetchone()[0]
    std_count = conn.execute("SELECT COUNT(*) FROM student_outcomes").fetchone()[0]
    conn.close()
    
    return jsonify({
        "database": "SQLite Relational Storage (college_analytics.db)",
        "total_colleges": c_count,
        "total_branches": b_count,
        "total_cutoff_records": cut_count,
        "total_historical_students": std_count,
        "fastapi_backend_url": "http://localhost:8000"
    })

if __name__ == "__main__":
    print("Starting Flask Admin & Data Quality Monitor service on http://localhost:5001 ...")
    flask_app.run(host="0.0.0.0", port=5001, debug=False)
