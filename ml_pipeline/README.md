# ML Pipeline: Feature Engineering → Training → Inference

End-to-end ML pipeline for **inventory anomaly detection**: ERP transaction data is featurized, used to train an unsupervised model (PCA + KMeans), and scored at inference. Deployable on **AWS SageMaker** or run locally.

## Flow

```
ERP API (export) → Feature Engineering → Training → Model artifacts
                        ↓
              Inference ← Load model ← Model dir
                        ↓
              Backend API (POST /api/v1/ml/score) or CLI/batch
```

## Components

| Step | Description | Output |
|------|-------------|--------|
| **Feature engineering** | Pull transactions from API (or CSV), build numeric/categorical features | `features/transactions_featured.parquet` |
| **Training** | Fit StandardScaler + PCA + KMeans; compute anomaly threshold | `model/scaler.joblib`, `pca.joblib`, `kmeans.joblib`, `config.json` |
| **Inference** | Load model, score new transactions → `anomaly_score`, `cluster_id`, `is_anomaly` | Parquet/API response |

## Quick start (local)

### 1. ERP API running with data

```bash
# From project root: run backend, seed, get a JWT
cd backend/erp_api && uvicorn app.main:app --reload --port 8000
# In another terminal:
python scripts/seed_data.py
# Login: POST /api/v1/auth/login → copy access_token
```

### 2. Feature engineering

```bash
cd ml_pipeline
pip install -r requirements.txt
# From API (set token in .env or pass --token)
python -m pipeline.feature_engineering.run --source api --token YOUR_JWT
# Or from CSV
python -m pipeline.feature_engineering.run --source csv --csv-path data/export.csv --output features/transactions_featured.parquet
```

### 3. Training

```bash
python -m pipeline.training.train
# Or: python train_sagemaker.py  (uses features/transactions_featured.parquet and model/ by default when not on SageMaker)
```

### 4. Inference

**CLI**

```bash
# Score featured parquet
python -m pipeline.inference.run --model-dir model --output output/scored.parquet
# Score from API
python -m pipeline.inference.run --source api --token YOUR_JWT --model-dir model --output output/scored.parquet
```

**Backend API**

Set `ML_MODEL_DIR` to the trained `model/` directory (absolute path), restart the API, then:

```http
POST /api/v1/ml/score
Authorization: Bearer YOUR_JWT
Content-Type: application/json

{"transaction_ids": [1, 2, 3]}
```

or inline transactions in ML export format:

```json
{"transactions": [{"transaction_id": 1, "item_id": 1, "warehouse_id": 1, "transaction_type": "in", "quantity": 10, "unit_price": 19.99, "total_amount": 199.9, "created_at_ts": 1234567890.0, ...}]}
```

Response includes `anomaly_score`, `cluster_id`, `is_anomaly` per transaction.

## SageMaker

### Training job

1. Upload `transactions_featured.parquet` to S3, e.g. `s3://bucket/train/transactions_featured.parquet`.
2. Use the SageMaker Python SDK or console to run a training job with:
   - **Entrypoint**: `train_sagemaker.py` (packaged with pipeline code and dependencies).
   - **Input channel** `train` pointing to the S3 path above.
   - **Output** `model` → SageMaker will place artifacts in S3.
3. Hyperparameters: `--n-components`, `--n-clusters`, `--random-state`.

### Inference

- **Option A**: Copy model artifacts from S3 to the backend server and set `ML_MODEL_DIR`.
- **Option B**: Deploy a SageMaker endpoint with a custom inference script that loads `scaler.joblib`, `pca.joblib`, `kmeans.joblib`, and `config.json`, and implements `model_fn`, `input_fn`, `predict_fn`, `output_fn`. The backend would then call the endpoint instead of in-process inference.

## Feature columns (fixed)

Must match between pipeline and backend inference:

- `quantity`, `abs_quantity`, `unit_price`, `total_amount`
- `hour`, `day_of_week`, `day_of_month` (from `created_at_ts`)
- `item_id`, `warehouse_id`, `transaction_type_enc`, `item_category_enc`

## Layout

```
ml_pipeline/
├── pipeline/
│   ├── config.py
│   ├── feature_engineering/   # fetcher, features, run
│   ├── training/              # model (scaler/PCA/KMeans), train
│   └── inference/             # predictor, run
├── train_sagemaker.py         # SageMaker entrypoint
├── requirements.txt
├── .env.example
└── README.md
```
