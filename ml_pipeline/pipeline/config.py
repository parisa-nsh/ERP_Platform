"""Pipeline config: data paths, API, model hyperparameters."""
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Data source: API (preferred) or local file
    erp_api_base_url: str = "http://localhost:8000"
    erp_api_token: Optional[str] = None  # JWT for GET /api/v1/ml/export
    ml_export_batch_size: int = 10_000

    # Paths (local or S3 for SageMaker)
    data_dir: str = "data"
    features_dir: str = "features"
    model_dir: str = "model"
    output_dir: str = "output"

    # Feature engineering
    time_window_hours: int = 24  # for rolling-style features if needed
    max_rows: Optional[int] = None  # cap rows for dev (None = all)

    # Training
    n_components: int = 8  # PCA "embedding" size
    n_clusters: int = 5
    anomaly_quantile: float = 0.95  # top (1 - this) fraction labeled anomaly
    random_state: int = 42

    # Inference
    anomaly_score_threshold: Optional[float] = None  # override from training


def get_data_dir(base: Optional[Path] = None) -> Path:
    base = base or Path.cwd()
    return base / "data"


def get_features_dir(base: Optional[Path] = None) -> Path:
    base = base or Path.cwd()
    return base / "features"


def get_model_dir(base: Optional[Path] = None) -> Path:
    base = base or Path.cwd()
    return base / "model"


def get_output_dir(base: Optional[Path] = None) -> Path:
    base = base or Path.cwd()
    return base / "output"
