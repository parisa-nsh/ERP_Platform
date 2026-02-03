# ML-Enabled ERP Inventory Intelligence Platform

A full-stack ERP system with **inventory transaction data**, **unsupervised ML** (PCA + clustering) for anomaly detection, and a **React frontend**. Data, ML, and application layers are clearly separated; the ML pipeline can run locally or on **AWS SageMaker**.

## Overview

| Layer | Description |
|-------|-------------|
| **Backend** | FastAPI + SQLAlchemy. CRUD for items, warehouses, transactions; JWT auth; ML-ready export and in-process inference. |
| **ML Pipeline** | Feature engineering → training (StandardScaler + PCA + KMeans) → inference. Consumes backend export; outputs anomaly scores and cluster IDs. |
| **Frontend** | React + TypeScript + Redux + MUI. Dashboard, Items, Warehouses, Transactions, and Anomaly Detection UI. |

## Architecture

```
┌─────────────────┐     GET /api/v1/ml/export      ┌──────────────────┐
│  React Frontend │ ◄─────────────────────────────► │  FastAPI Backend  │
│  (port 3000)    │     POST /api/v1/ml/score      │  (port 8001)      │
└─────────────────┘                                └────────┬─────────┘
                                                           │
                                    ┌──────────────────────┼──────────────────────┐
                                    │                      │                      │
                                    ▼                      ▼                      ▼
                            SQLite / PostgreSQL    ML model artifacts      JWT auth
```

- **Backend** exposes `/api/v1/ml/export` (paginated, denormalized rows) and `/api/v1/ml/score` (anomaly scores when `ML_MODEL_DIR` is set).
- **ML pipeline** fetches from the API (or CSV), builds features, trains, and saves artifacts; inference can run in-process in the backend or via SageMaker.

## Tech Stack

- **Backend:** Python 3.10+, FastAPI, SQLAlchemy 2.x, PostgreSQL or SQLite (local), JWT (admin / manager / viewer).
- **ML:** pandas, scikit-learn (PCA, KMeans), joblib; SageMaker-compatible training entrypoint.
- **Frontend:** React 18, TypeScript, Redux Toolkit, Material-UI, Axios.

## Quick Start

### 1. Backend

```bash
cd backend/erp_api
cp .env.example .env
# Optional: set DATABASE_URL (defaults to SQLite for local dev)
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
python scripts/seed_data.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

- API: http://localhost:8001  
- Docs: http://localhost:8001/docs  

**Seed users:** `admin@erp.example.com` / `admin123` (admin), `manager@erp.example.com` / `manager123`, `viewer@erp.example.com` / `viewer123`.

### 2. Frontend

```bash
cd frontend
cp .env.example .env
# Set REACT_APP_API_URL=http://localhost:8001/api/v1 in .env (see frontend/.env.example)
npm install
npm start
```

Open http://localhost:3000 and log in with a seed user.

### 3. ML Pipeline (optional)

See [ml_pipeline/README.md](ml_pipeline/README.md). In short:

```bash
cd ml_pipeline
pip install -r requirements.txt
# With backend running and JWT from login:
python -m pipeline.feature_engineering.run --source api --token YOUR_JWT
python -m pipeline.training.train
python -m pipeline.inference.run --model-dir model --output output/scored.parquet
```

Set backend `ML_MODEL_DIR` to the trained `model/` directory to enable `POST /api/v1/ml/score` from the UI.

## Project Structure

```
├── backend/erp_api/     # FastAPI app, models, routes, ML export & score
│   └── README.md
├── ml_pipeline/         # Feature engineering, training, inference
│   └── README.md
├── frontend/            # React app (Dashboard, Items, Warehouses, Transactions, Anomaly)
│   └── README.md
├── CONTRIBUTING.md      # Branching, workflow, PR guidelines
├── TESTING.md           # Manual testing notes
├── LICENSE              # MIT
└── README.md            # This file
```

- **Backend:** [backend/erp_api/README.md](backend/erp_api/README.md) – API overview, data models, auth.
- **ML:** [ml_pipeline/README.md](ml_pipeline/README.md) – Pipeline flow, local and SageMaker usage.
- **Frontend:** [frontend/README.md](frontend/README.md) – Create React App scripts and deployment.

## Branching

- **`main`** – stable, deployable code. Keep it in a good state.
- **`develop`** – integration branch for ongoing work; merge feature branches here, then into `main` when releasing (optional: you can merge features directly into `main`).
- **Feature branches** – one branch per feature or fix. Create from `main` (or `develop`), then merge back when done (use a pull request if you want review).
  - Features: `feature/add-reporting`, `feature/export-pdf`
  - Fixes: `fix/login-validation`, `fix/csv-encoding`
- **Workflow:** `git checkout main` → `git pull` → `git checkout -b feature/your-feature` → work → commit → push → open PR (or merge) into `main`.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full workflow and commit/PR guidelines.

## License

MIT – see [LICENSE](LICENSE).
