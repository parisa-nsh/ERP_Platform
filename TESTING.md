# Quick test – see results in the app

## Prerequisites

- **PostgreSQL** running locally with a database `erp_inventory`
- **Python 3.10+** and **Node.js** (for frontend)

---

## 1. Backend (API)

```bash
cd backend/erp_api
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
```

Create the database (in PostgreSQL):

```sql
CREATE DATABASE erp_inventory;
```

Then:

```bash
cp .env.example .env
# Edit .env if needed: DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/erp_inventory
python scripts/seed_data.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see: **Uvicorn running on http://0.0.0.0:8000**

---

## 2. Frontend

In a **new terminal**:

```bash
cd frontend
cp .env.example .env
npm install
npm start
```

Browser should open at **http://localhost:3000** (or 3002 if PORT=3002 in .env).

---

## 3. What to do in the app

1. **Login**  
   - Email: `admin@erp.example.com`  
   - Password: `admin123`

2. **Dashboard**  
   - You’ll see the welcome message and cards.

3. **Items**  
   - List of seeded items (e.g. Widget A, Widget B, Gadget X).  
   - Use **Category** filter and **pagination**.  
   - Try **Add Item** and **Edit**.

4. **Warehouses**  
   - Seeded warehouses (e.g. WH-NYC, WH-LA).  
   - **Add Warehouse** and **pagination**.

5. **Transactions**  
   - Seeded inventory transactions.  
   - Use **Item / Warehouse / Type** filters and **pagination**.  
   - **Add Transaction** (choose item, warehouse, type, quantity).

6. **Export ML data**  
   - On **Dashboard** or **Anomaly Detection**: click **Export ML data (CSV)**.  
   - A CSV file should download (ML-ready transaction rows).

7. **Anomaly Detection**  
   - Without a trained model: click **Score recent** → you’ll get “ML model not loaded” (expected).  
   - With a trained model: you’ll see a table with **anomaly_score**, **cluster_id**, **is_anomaly**.

---

## 4. (Optional) See real anomaly scores

To have **Anomaly Detection** return real scores:

```bash
cd ml_pipeline
pip install -r requirements.txt
```

Get a JWT (from frontend: login, then DevTools → Application → Local Storage → copy `token`), then:

```bash
set ERP_API_TOKEN=YOUR_JWT_COPIED_FROM_BROWSER    # Windows
# export ERP_API_TOKEN=YOUR_JWT_COPIED_FROM_BROWSER  # macOS/Linux
python -m pipeline.feature_engineering.run --source api --token %ERP_API_TOKEN%
python -m pipeline.training.train
```

Then set the backend’s model path and restart the API:

- In `backend/erp_api/.env` add (use the **absolute** path to the `model` folder):
  ```env
  ML_MODEL_DIR=D:\07_My_Projects\ERP Platform\ml_pipeline\model
  ```
- Restart uvicorn. After that, **Score recent** on the Anomaly page will show a table with scores and anomaly flags.

---

## 5. API docs (no UI)

- **Swagger:** http://localhost:8000/docs  
- **Health:** http://localhost:8000/health  

You can test login with:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login -H "Content-Type: application/json" -d "{\"email\":\"admin@erp.example.com\",\"password\":\"admin123\"}"
```
