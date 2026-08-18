# EduAnalytics AI

An engineering-college admission decision-support platform for Indian students, with a dedicated Karnataka KCET/COMEDK guide. It combines local college data, SQLite analytics, machine-learning admission predictions, recommendations, document retrieval, and a browser-based dashboard.

## What it includes

- **Karnataka admission guide** for KCET, COMEDK, and management-quota college matching.
- **Scholarship estimator** for Karnataka-oriented fee concessions and support schemes.
- **ETL and data-quality workflow** that cleans CSV inputs and loads analytical tables into SQLite.
- **Exploratory and SQL analytics** for colleges, branches, cutoffs, and student outcomes.
- **Admission predictor** trained with Logistic Regression, Random Forest, Gradient Boosting, and an ANN.
- **Hybrid college recommendations** using rank, branch, location, budget, hostel, and placement preferences.
- **RAG-style document search** over the bundled admission-guidance text files.
- **Multimodal demo tools** for campus search, captions, document classification, insight cards, and storyboards.

## Project layout

```text
college_analytics_platform/
|- backend/                  # FastAPI app, Flask admin service, ETL, ML, and engines
|- data/                     # CSV data, SQLite database, ML artefacts, RAG documents
|- frontend/                 # Static HTML, CSS, and JavaScript dashboard
`- requirements.txt
```

## Requirements

- Python 3.10+ (the app is developed with modern FastAPI and scikit-learn versions)
- pip

## Run locally

From the project root:

```bash
python -m venv .venv
```

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

```bash
pip install -r requirements.txt
python -m uvicorn backend.main:app --reload
```

Open the application at [http://localhost:8000](http://localhost:8000). Interactive API documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).

The SQLite database is created automatically from the CSV files when an endpoint first needs it. To explicitly run the ETL pipeline and initialise ML artefacts, start the module directly instead:

```bash
python backend/main.py
```

### Optional Flask admin service

In a second terminal, with the same virtual environment active:

```bash
python backend/flask_app.py
```

It exposes health, data-quality, ETL-trigger, and system-stat endpoints at `http://localhost:5001`.

## Key API endpoints

| Area | Endpoint |
| --- | --- |
| Health and overview | `GET /api/health`, `GET /api/overview` |
| Data quality | `GET /api/data-quality`, `POST /api/data-quality/trigger-etl` |
| College data | `GET /api/colleges` |
| Analytics | `GET /api/eda/visualizations`, `GET /api/sql/questions` |
| ML | `GET /api/ml/metrics`, `GET /api/ml/feature-importance`, `POST /api/ml/retrain`, `POST /api/predict` |
| Recommendations | `POST /api/recommend` |
| Knowledge assistant | `POST /api/rag/query`, `POST /api/llm/assistant` |
| Karnataka tools | `GET /api/karnataka/colleges`, `POST /api/karnataka/scholarship-check`, `POST /api/karnataka/college-guide` |
| Multimodal tools | `POST /api/multimodal/clip-search`, `POST /api/multimodal/blip-caption`, `POST /api/multimodal/classify-doc` |

## Data and model notes

The application uses the CSV files in `data/` as its local source data and stores analytical tables in `data/college_analytics.db`. Model artefacts are stored in `data/trained_models.pkl`.

The admission model uses only pre-decision profile information: entrance rank, budget, tuition fee, hostel requirement, category, branch, state, and optional college name. It intentionally excludes current closing rank, rank-fit derivatives, placement data, and subjective college tier; current cutoff information is instead used only by the recommendation layer for historical cutoff analysis. The `/api/predict` response is therefore labelled an **estimated historical admission likelihood**, not a guarantee.

`student_outcomes.csv` is a synthetic demonstration dataset. Its metrics demonstrate the implementation only and must not be presented as accuracy on real admissions data. The metrics endpoint reports this, its validation strategy, class distribution, excluded leakage fields, baseline, and confusion matrices.

The RAG endpoint retrieves relevant sections from the text documents in `data/rag_documents/` using TF-IDF similarity. The campus search, image-captioning, and document-classification endpoints currently return curated or simulated demonstration results; they do not run production CLIP, BLIP, or CNN models.

`/api/llm/assistant` uses the local database and RAG fallback by default. To enable GPT-enhanced answers, set `OPENAI_API_KEY` in the server environment (copy `.env.example` as a guide) and restart the backend. The key is used only server-side and must never be committed or sent to the browser. `OPENAI_MODEL` is optional and defaults to `gpt-4.1-mini`.

## Important disclaimer

This platform is a decision-support and educational tool. Admission cutoffs, fees, scholarship eligibility, placements, and counselling rules can change. Verify all final decisions with the relevant official institute, counselling authority, and scholarship portal.
