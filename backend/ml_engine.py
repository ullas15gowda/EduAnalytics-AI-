import os
import time
import pickle
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

from backend.etl_pipeline import get_db_connection, DATA_DIR

MODEL_PATH = os.path.join(DATA_DIR, "trained_models.pkl")

def prepare_feature_dataset(df_students):
    df = df_students.copy()
    
    # 1. Feature Engineering
    # Feature A: cutoff_gap (Closing rank minus Entrance rank)
    df["cutoff_gap"] = df["closing_rank"] - df["entrance_rank"]
    
    # Feature B: rank_fit (Ratio of closing rank to entrance rank)
    df["rank_fit"] = df["closing_rank"] / (df["entrance_rank"] + 1.0)
    
    # Feature C: fee_affordability (Ratio of budget to tuition fee)
    df["fee_affordability"] = df["annual_budget_lakhs"] / (df["tuition_fee"] + 0.1)
    
    # Feature D: placement_score (Placement package normalized)
    df["placement_score"] = df["avg_placement_lpa"] / 35.0
    
    # Feature E: tier_weight
    tier_map = {"Tier 1": 1.0, "Tier 2": 0.75, "Tier 3": 0.50}
    df["tier_weight"] = df["tier"].map(tier_map).fillna(0.5)
    
    # Feature F: hostel_needed
    df["hostel_needed"] = df["hostel_needed"].astype(int)

    feature_cols = [
        "entrance_rank", "closing_rank", "cutoff_gap", "rank_fit",
        "annual_budget_lakhs", "tuition_fee", "fee_affordability",
        "avg_placement_lpa", "placement_score", "tier_weight", "hostel_needed"
    ]
    
    X = df[feature_cols]
    y = df["admitted"]
    
    return X, y, feature_cols

def train_and_evaluate_models():
    print("\n--- TRAINING MACHINE LEARNING MODELS ---")
    conn = get_db_connection()
    df_students = pd.read_sql_query("SELECT * FROM student_outcomes", conn)
    conn.close()
    
    X, y, feature_cols = prepare_feature_dataset(df_students)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42),
        "Gradient Boosting": HistGradientBoostingClassifier(max_iter=100, random_state=42),
        "Artificial Neural Network (ANN)": MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=500, random_state=42)
    }
    
    results = {}
    best_model_name = None
    best_f1 = -1.0
    
    for name, model in models.items():
        print(f"Training model: {name}...")
        
        if name in ["Logistic Regression", "Artificial Neural Network (ANN)"]:
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
            y_prob = model.predict_proba(X_test_scaled)[:, 1]
        else:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_prob = model.predict_proba(X_test)[:, 1]
            
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_prob)
        cm = confusion_matrix(y_test, y_pred).tolist()
        
        results[name] = {
            "accuracy": round(float(acc), 4),
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
            "f1_score": round(float(f1), 4),
            "roc_auc": round(float(auc), 4),
            "confusion_matrix": cm,
            "model_obj": model
        }
        
        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name

    # Feature Importance (Extract from Random Forest)
    rf_model = models["Random Forest"]
    importances = rf_model.feature_importances_
    feat_imp = sorted(
        [{"feature": col, "importance": round(float(imp), 4)} for col, imp in zip(feature_cols, importances)],
        key=lambda x: x["importance"], reverse=True
    )

    training_metadata = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "model_version": "v1.4.2-prod",
        "dataset_size": len(df_students),
        "train_size": len(X_train),
        "test_size": len(X_test),
        "feature_list": feature_cols,
        "feature_importance": feat_imp,
        "best_model_name": best_model_name,
        "metrics_comparison": {
            m_name: {
                "accuracy": data["accuracy"],
                "precision": data["precision"],
                "recall": data["recall"],
                "f1_score": data["f1_score"],
                "roc_auc": data["roc_auc"],
                "confusion_matrix": data["confusion_matrix"]
            } for m_name, data in results.items()
        }
    }

    # Save artifacts to pickle (fallback to /tmp on read-only filesystems)
    save_path = MODEL_PATH
    try:
        with open(save_path, "wb") as f:
            pickle.dump({
                "scaler": scaler,
                "models": {k: v["model_obj"] for k, v in results.items()},
                "metadata": training_metadata
            }, f)
    except Exception:
        save_path = os.path.join("/tmp", "trained_models.pkl")
        with open(save_path, "wb") as f:
            pickle.dump({
                "scaler": scaler,
                "models": {k: v["model_obj"] for k, v in results.items()},
                "metadata": training_metadata
            }, f)

    print(f"Machine learning training completed. Best performing model: {best_model_name} (F1: {best_f1:.4f})")
    return training_metadata

def load_ml_artifacts():
    paths_to_try = [MODEL_PATH, os.path.join("/tmp", "trained_models.pkl")]
    for path in paths_to_try:
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    return pickle.load(f)
            except (AttributeError, ImportError, ModuleNotFoundError, OSError, pickle.UnpicklingError, ValueError) as exc:
                print(f"Stored ML artifact at {path} is incompatible ({exc}).")

    # If no valid model pickle found, retrain models
    train_and_evaluate_models()
    for path in paths_to_try:
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    return pickle.load(f)
            except Exception:
                pass
    raise RuntimeError("Failed to load or retrain ML models.")

def predict_admission_probability(
    entrance_rank: int,
    closing_rank: int,
    annual_budget: float,
    tuition_fee: float,
    avg_placement_lpa: float,
    tier: str,
    hostel_needed: int = 1,
    model_choice: str = "Gradient Boosting"
):
    artifacts = load_ml_artifacts()
    scaler = artifacts["scaler"]
    models = artifacts["models"]
    
    if model_choice not in models:
        model_choice = artifacts["metadata"]["best_model_name"]
        
    model = models[model_choice]
    
    cutoff_gap = closing_rank - entrance_rank
    rank_fit = closing_rank / (entrance_rank + 1.0)
    fee_affordability = annual_budget / (tuition_fee + 0.1)
    placement_score = avg_placement_lpa / 35.0
    tier_map = {"Tier 1": 1.0, "Tier 2": 0.75, "Tier 3": 0.50}
    tier_weight = tier_map.get(tier, 0.5)

    input_df = pd.DataFrame([{
        "entrance_rank": entrance_rank,
        "closing_rank": closing_rank,
        "cutoff_gap": cutoff_gap,
        "rank_fit": rank_fit,
        "annual_budget_lakhs": annual_budget,
        "tuition_fee": tuition_fee,
        "fee_affordability": fee_affordability,
        "avg_placement_lpa": avg_placement_lpa,
        "placement_score": placement_score,
        "tier_weight": tier_weight,
        "hostel_needed": int(hostel_needed)
    }])

    if model_choice in ["Logistic Regression", "Artificial Neural Network (ANN)"]:
        input_scaled = scaler.transform(input_df)
        prob = model.predict_proba(input_scaled)[0, 1]
    else:
        prob = model.predict_proba(input_df)[0, 1]
        
    return {
        "admission_probability": round(float(prob), 4),
        "model_used": model_choice,
        "entrance_rank": entrance_rank,
        "closing_rank": closing_rank,
        "rank_gap": cutoff_gap,
        "rank_fit": round(float(rank_fit), 2),
        "fee_affordability_ratio": round(float(fee_affordability), 2)
    }

if __name__ == "__main__":
    meta = train_and_evaluate_models()
    sample_pred = predict_admission_probability(
        entrance_rank=4500, closing_rank=6200, annual_budget=3.5, tuition_fee=2.2, avg_placement_lpa=16.5, tier="Tier 1"
    )
    print("Sample Admission Prediction Output:", sample_pred)
