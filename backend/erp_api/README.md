# ML-Enabled ERP Inventory Intelligence – Backend API

Python backend service that **generates ML-ready inventory data** for the ERP platform. Built with FastAPI, PostgreSQL, SQLAlchemy, and JWT (role-based auth). This service is the **data source** and future **inference consumer** for the SageMaker ML pipeline (anomaly detection & clustering).

## Tech Stack

- **Language:** Python 3.10+
- **Framework:** FastAPI
- **DB:** PostgreSQL
- **ORM:** SQLAlchemy 2.x
- **Auth:** JWT (role-based: admin, manager, viewer)

## Data Models (Implemented)

| Model | Purpose |
|-------|---------|
| **User** | JWT auth, roles (admin, manager, viewer) |
| **Item** | Product/SKU master (sku, name, category, unit_cost) |
| **Warehouse** | Location dimension |
| **InventoryTransaction** | Core event stream for ML: item, warehouse, type (in/out/adjust/transfer), quantity, unit_price, total_amount, timestamps |

## Quick Start

### 1. Environment

```bash
cd backend/erp_api
cp .env.example .env
# Edit .env: set DATABASE_URL and SECRET_KEY
```

### 2. PostgreSQL

Create a database:

```sql
CREATE DATABASE erp_inventory;
```

Use the same credentials in `DATABASE_URL` (e.g. `postgresql+psycopg2://postgres:postgres@localhost:5432/erp_inventory`).

### 3. Install & Run

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
python scripts/seed_data.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API: http://localhost:8000  
- Docs: http://localhost:8000/docs  
- Health: http://localhost:8000/health  

### 4. Auth & API

- **Login:** `POST /api/v1/auth/login` with `{"email": "admin@erp.example.com", "password": "admin123"}`.  
- Use the returned `access_token` in the `Authorization: Bearer <token>` header for protected routes.

Seed users:

- `admin@erp.example.com` / `admin123` (admin)
- `manager@erp.example.com` / `manager123` (manager)
- `viewer@erp.example.com` / `viewer123` (viewer)

## API Overview

| Area | Endpoints |
|------|-----------|
| **Auth** | `POST /api/v1/auth/login`, `GET /api/v1/auth/me`, `POST /api/v1/auth/register` (admin only) |
| **Items** | CRUD: `GET/POST /api/v1/items`, `GET/PATCH/DELETE /api/v1/items/{id}` |
| **Warehouses** | CRUD: `GET/POST /api/v1/warehouses`, `GET/PATCH/DELETE /api/v1/warehouses/{id}` |
| **Inventory transactions** | CRUD: `GET/POST /api/v1/inventory-transactions`, `GET/PATCH/DELETE /api/v1/inventory-transactions/{id}` |
| **ML export** | `GET /api/v1/ml/export?offset=0&limit=10000` – paginated, denormalized rows for feature pipeline / SageMaker |

## ML Export

`GET /api/v1/ml/export` returns **ML-ready flat rows** (denormalized):

- `transaction_id`, `item_id`, `item_sku`, `item_category`, `warehouse_id`, `warehouse_code`
- `transaction_type`, `quantity` (signed: +in, -out), `unit_price`, `total_amount`
- `created_at`, `created_at_ts` (Unix timestamp for time-series features)

Downstream use: feature engineering pipeline and SageMaker training/inference (e.g. CNN embeddings + clustering for anomaly detection).

## Project Layout

```
backend/erp_api/
├── app/
│   ├── main.py           # FastAPI app, CORS, routers
│   ├── config.py         # Settings (env)
│   ├── database.py       # SQLAlchemy engine, session, Base
│   ├── core/             # security (JWT, password), deps (get_current_user, require_roles)
│   ├── models/           # User, Item, Warehouse, InventoryTransaction
│   ├── schemas/          # Pydantic request/response + ML export
│   └── api/routes/       # auth, items, warehouses, inventory_transactions, ml_export
├── scripts/
│   └── seed_data.py      # Seed admin + sample data
├── requirements.txt
├── .env.example
└── README.md
```

## Next Steps (ML Pipeline)

- **Feature engineering:** Consume `/api/v1/ml/export` (or DB directly) to build aggregates and time windows.  
- **SageMaker:** Train unsupervised model (e.g. embeddings + clustering), deploy endpoint.  
- **Inference consumer:** Backend to call SageMaker endpoint for anomaly scores and expose them via API.
