"""Model components: scaler, PCA (embeddings), KMeans, anomaly scoring."""
import json
from pathlib import Path
from typing import Any

import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans


FEATURE_COLS_KEY = "feature_columns"
CONFIG_KEY = "config"


def fit_pipeline(
    X: np.ndarray,
    feature_names: list[str],
    n_components: int = 8,
    n_clusters: int = 5,
    random_state: int = 42,
) -> dict[str, Any]:
    """
    Fit scaler → PCA → KMeans. Return artifacts and config.
    Anomaly score = reconstruction error (PCA) + distance to nearest centroid.
    """
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    pca = PCA(n_components=n_components, random_state=random_state)
    X_embed = pca.fit_transform(X_scaled)

    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    kmeans.fit(X_embed)
    labels = kmeans.labels_
    centroids = kmeans.cluster_centers_

    # Per-sample: reconstruction error (from PCA) + distance to own centroid
    X_recon = pca.inverse_transform(X_embed)
    recon_error = np.mean((X_scaled - X_recon) ** 2, axis=1)
    dist_to_centroid = np.linalg.norm(X_embed - centroids[labels], axis=1)
    # Combined score (higher = more anomalous)
    anomaly_score = recon_error + 0.5 * (dist_to_centroid / (np.std(dist_to_centroid) + 1e-8))

    config = {
        "n_components": n_components,
        "n_clusters": n_clusters,
        "random_state": random_state,
        "feature_columns": feature_names,
        "anomaly_score_threshold": float(np.percentile(anomaly_score, 95)),  # top 5% = anomaly
    }

    return {
        "scaler": scaler,
        "pca": pca,
        "kmeans": kmeans,
        "config": config,
        "anomaly_scores_train": anomaly_score,
        "labels_train": labels,
    }


def save_pipeline(artifacts: dict[str, Any], model_dir: str | Path) -> None:
    """Save scaler, pca, kmeans, and config to model_dir."""
    model_dir = Path(model_dir)
    model_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifacts["scaler"], model_dir / "scaler.joblib")
    joblib.dump(artifacts["pca"], model_dir / "pca.joblib")
    joblib.dump(artifacts["kmeans"], model_dir / "kmeans.joblib")
    with open(model_dir / "config.json", "w") as f:
        json.dump(artifacts["config"], f, indent=2)


def load_pipeline(model_dir: str | Path) -> tuple[Any, Any, Any, dict]:
    """Load scaler, pca, kmeans, config. Return (scaler, pca, kmeans, config)."""
    model_dir = Path(model_dir)
    scaler = joblib.load(model_dir / "scaler.joblib")
    pca = joblib.load(model_dir / "pca.joblib")
    kmeans = joblib.load(model_dir / "kmeans.joblib")
    with open(model_dir / "config.json") as f:
        config = json.load(f)
    return scaler, pca, kmeans, config


def predict_anomaly_scores(
    X: np.ndarray,
    scaler: Any,
    pca: Any,
    kmeans: Any,
) -> tuple[np.ndarray, np.ndarray]:
    """
    X: (n_samples, n_features). Returns (anomaly_scores, cluster_labels).
    """
    X_scaled = scaler.transform(X)
    X_embed = pca.transform(X_scaled)
    labels = kmeans.predict(X_embed)
    centroids = kmeans.cluster_centers_
    X_recon = pca.inverse_transform(X_embed)
    recon_error = np.mean((X_scaled - X_recon) ** 2, axis=1)
    dist_to_centroid = np.linalg.norm(X_embed - centroids[labels], axis=1)
    scale = np.std(dist_to_centroid) + 1e-8
    anomaly_score = recon_error + 0.5 * (dist_to_centroid / scale)
    return anomaly_score, labels
