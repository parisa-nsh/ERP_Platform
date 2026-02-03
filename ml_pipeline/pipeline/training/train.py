"""Training entrypoint: read featured data, fit pipeline, save artifacts."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Allow running as script or SageMaker entrypoint
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pipeline.config import Settings, get_model_dir, get_features_dir
from pipeline.feature_engineering.features import get_feature_columns
from pipeline.training.model import fit_pipeline, save_pipeline


def load_training_config(model_dir: str | Path) -> dict:
    """Load config.json from a trained model dir."""
    with open(Path(model_dir) / "config.json") as f:
        return json.load(f)


def train(
    features_path: str | Path | None = None,
    model_dir: str | Path | None = None,
    n_components: int | None = None,
    n_clusters: int | None = None,
    random_state: int | None = None,
) -> dict:
    """
    Read parquet feature matrix, fit scaler/PCA/KMeans, save to model_dir.
    Returns config dict (includes anomaly_score_threshold).
    """
    settings = Settings()
    features_path = Path(features_path or get_features_dir() / "transactions_featured.parquet")
    model_dir = Path(model_dir or get_model_dir())

    if not features_path.exists():
        raise FileNotFoundError(f"Features not found: {features_path}. Run feature_engineering first.")

    df = pd.read_parquet(features_path)
    feature_cols = get_feature_columns()
    missing = [c for c in feature_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing feature columns: {missing}")

    X = df[feature_cols].to_numpy().astype(np.float64)
    # Drop any row with inf/nan
    mask = np.isfinite(X).all(axis=1)
    X = X[mask]
    if X.shape[0] == 0:
        raise ValueError("No valid rows after dropping inf/nan")

    n_components = n_components or settings.n_components
    n_clusters = n_clusters or settings.n_clusters
    random_state = random_state or settings.random_state

    artifacts = fit_pipeline(
        X,
        feature_names=feature_cols,
        n_components=min(n_components, X.shape[0], X.shape[1]),
        n_clusters=min(n_clusters, X.shape[0]),
        random_state=random_state,
    )
    save_pipeline(artifacts, model_dir)
    print(f"Saved model to {model_dir}, anomaly_score_threshold={artifacts['config']['anomaly_score_threshold']:.4f}")
    return artifacts["config"]


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--features", type=str, default=None)
    p.add_argument("--model-dir", type=str, default=None)
    p.add_argument("--n-components", type=int, default=None)
    p.add_argument("--n-clusters", type=int, default=None)
    p.add_argument("--random-state", type=int, default=42)
    args = p.parse_args()
    train(
        features_path=args.features,
        model_dir=args.model_dir,
        n_components=args.n_components,
        n_clusters=args.n_clusters,
        random_state=args.random_state,
    )


if __name__ == "__main__":
    main()
