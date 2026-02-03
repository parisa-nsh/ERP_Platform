"""
In-process ML inference: load trained scaler/PCA/KMeans and score transactions.
Feature building matches ml_pipeline/feature_engineering/features.py.
"""
from pathlib import Path
from typing import Any, Optional

import joblib
import numpy as np
import pandas as pd

# Must match pipeline.feature_engineering.features.get_feature_columns()
FEATURE_COLUMNS = [
    "quantity", "abs_quantity", "unit_price", "total_amount",
    "hour", "day_of_week", "day_of_month",
    "item_id", "warehouse_id", "transaction_type_enc", "item_category_enc",
]


def _build_features_from_rows(rows: list[dict]) -> np.ndarray:
    """Build feature matrix from list of ML export-style rows (created_at_ts, quantity, etc.)."""
    if not rows:
        return np.zeros((0, len(FEATURE_COLUMNS)))
    df = pd.DataFrame(rows)
    ts = df["created_at_ts"].astype(float)
    dt = pd.to_datetime(ts, unit="s", utc=True)
    quantity = df["quantity"].astype(float)
    unit_price = df["unit_price"].fillna(0).astype(float) if "unit_price" in df.columns else pd.Series(0.0, index=df.index)
    total_amount = df["total_amount"].fillna(0).astype(float) if "total_amount" in df.columns else pd.Series(0.0, index=df.index)
    tx_type = df["transaction_type"].fillna("unknown").astype(str) if "transaction_type" in df.columns else pd.Series(["unknown"] * len(df))
    uniq = sorted(tx_type.unique())
    tx_map = {v: i for i, v in enumerate(uniq)}
    cat = df["item_category"].fillna("unknown").astype(str) if "item_category" in df.columns else pd.Series(["unknown"] * len(df))
    cat_uniq = sorted(cat.unique())
    cat_map = {v: i for i, v in enumerate(cat_uniq)}
    X = np.column_stack([
        quantity,
        np.abs(quantity),
        unit_price,
        total_amount,
        dt.dt.hour.astype(float),
        dt.dt.dayofweek.astype(float),
        dt.dt.day.astype(float),
        df["item_id"].astype(np.int64),
        df["warehouse_id"].astype(np.int64),
        tx_type.map(tx_map).astype(float),
        cat.map(cat_map).astype(float),
    ])
    return np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)


def _score(X: np.ndarray, scaler: Any, pca: Any, kmeans: Any) -> tuple[np.ndarray, np.ndarray]:
    X_scaled = scaler.transform(X)
    X_embed = pca.transform(X_scaled)
    labels = kmeans.predict(X_embed)
    centroids = kmeans.cluster_centers_
    X_recon = pca.inverse_transform(X_embed)
    recon_error = np.mean((X_scaled - X_recon) ** 2, axis=1)
    dist = np.linalg.norm(X_embed - centroids[labels], axis=1)
    scale = np.std(dist) + 1e-8
    anomaly_score = recon_error + 0.5 * (dist / scale)
    return anomaly_score, labels


class InferenceService:
    def __init__(self, model_dir: str | Path):
        self.model_dir = Path(model_dir)
        self.scaler = joblib.load(self.model_dir / "scaler.joblib")
        self.pca = joblib.load(self.model_dir / "pca.joblib")
        self.kmeans = joblib.load(self.model_dir / "kmeans.joblib")
        with open(self.model_dir / "config.json") as f:
            import json
            self.config = json.load(f)
        self.threshold = self.config.get("anomaly_score_threshold")

    def score_transactions(self, rows: list[dict]) -> list[dict]:
        """Rows = ML export format. Returns list of {transaction_id, anomaly_score, cluster_id, is_anomaly}."""
        if not rows:
            return []
        X = _build_features_from_rows(rows)
        scores, labels = _score(X, self.scaler, self.pca, self.kmeans)
        ids = [r.get("transaction_id", i) for i, r in enumerate(rows)]
        return [
            {
                "transaction_id": tid,
                "anomaly_score": float(s),
                "cluster_id": int(l),
                "is_anomaly": bool(self.threshold and s > self.threshold),
            }
            for tid, s, l in zip(ids, scores, labels)
        ]


def load_inference_service(model_dir: Optional[str | Path]) -> Optional[InferenceService]:
    if not model_dir:
        return None
    path = Path(model_dir)
    if not (path / "config.json").exists():
        return None
    return InferenceService(path)
