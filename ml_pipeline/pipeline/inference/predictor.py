"""Load trained pipeline and score new data."""
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd

from pipeline.feature_engineering.features import build_feature_matrix, get_feature_columns
from pipeline.training.model import load_pipeline, predict_anomaly_scores


class Predictor:
    """Load once, score many. Uses same feature columns as training."""

    def __init__(self, model_dir: str | Path):
        self.model_dir = Path(model_dir)
        self.scaler, self.pca, self.kmeans, self.config = load_pipeline(self.model_dir)
        self.feature_columns = self.config.get("feature_columns") or get_feature_columns()
        self.anomaly_threshold = self.config.get("anomaly_score_threshold")

    def score_feature_matrix(self, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """X: (n, n_features) in training order. Returns (anomaly_scores, cluster_ids)."""
        scores, labels = predict_anomaly_scores(X, self.scaler, self.pca, self.kmeans)
        return scores, labels

    def score_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        df must have feature columns. Returns same df with added columns:
        anomaly_score, cluster_id, is_anomaly.
        """
        for c in self.feature_columns:
            if c not in df.columns:
                raise ValueError(f"Missing feature column: {c}")
        X = df[self.feature_columns].to_numpy().astype(np.float64)
        # Replace inf/nan with 0 for inference
        X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
        scores, labels = self.score_feature_matrix(X)
        out = df.copy()
        out["anomaly_score"] = scores
        out["cluster_id"] = labels
        threshold = self.anomaly_threshold
        out["is_anomaly"] = scores > threshold if threshold is not None else np.zeros_like(scores, dtype=bool)
        return out

    def score_transactions(self, transactions_df: pd.DataFrame) -> pd.DataFrame:
        """
        Raw transaction DataFrame (from API/CSV with standard columns).
        Builds features then scores. Returns featured DataFrame + anomaly_score, cluster_id, is_anomaly.
        """
        feat = build_feature_matrix(transactions_df, drop_na_rows=False)
        if feat.empty:
            feat["anomaly_score"] = []
            feat["cluster_id"] = []
            feat["is_anomaly"] = []
            return feat
        return self.score_dataframe(feat)


def load_predictor(model_dir: str | Path) -> Predictor:
    return Predictor(model_dir)


def predict(
    model_dir: str | Path,
    features_path: Optional[str | Path] = None,
    transactions_df: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """
    One-shot: load model and score.
    Either pass features_path (parquet with feature columns) or transactions_df (raw transactions).
    """
    pred = load_predictor(model_dir)
    if transactions_df is not None:
        return pred.score_transactions(transactions_df)
    if features_path is not None:
        df = pd.read_parquet(features_path)
        return pred.score_dataframe(df)
    raise ValueError("Provide either features_path or transactions_df")
