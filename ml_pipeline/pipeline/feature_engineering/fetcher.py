"""Fetch ML-ready transaction data from ERP API or load from CSV."""
from pathlib import Path
from typing import Iterator

import httpx
import pandas as pd

from pipeline.config import Settings


def fetch_transactions_from_api(
    base_url: str | None = None,
    token: str | None = None,
    batch_size: int = 10_000,
    max_rows: int | None = None,
) -> pd.DataFrame:
    """Pull all pages from GET /api/v1/ml/export and concatenate."""
    settings = Settings()
    base_url = base_url or settings.erp_api_base_url.rstrip("/")
    token = token or settings.erp_api_token
    batch_size = batch_size or settings.ml_export_batch_size

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    rows: list[dict] = []
    offset = 0
    while True:
        with httpx.Client(timeout=60.0) as client:
            r = client.get(
                f"{base_url}/api/v1/ml/export",
                params={"offset": offset, "limit": batch_size},
                headers=headers,
            )
        r.raise_for_status()
        data = r.json()
        batch = data.get("rows") or []
        if not batch:
            break
        for row in batch:
            row["created_at"] = row.get("created_at")  # keep ISO string or parse later
        rows.extend(batch)
        offset += len(batch)
        if data.get("has_more") is False:
            break
        if max_rows and len(rows) >= max_rows:
            rows = rows[:max_rows]
            break

    return _rows_to_dataframe(rows)


def _rows_to_dataframe(rows: list[dict]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"], utc=True)
    return df


def load_transactions_from_csv(path: str | Path) -> pd.DataFrame:
    """Load transactions from a CSV (e.g. exported from feature run)."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"], utc=True)
    return df


def iterate_transactions_from_api(
    base_url: str | None = None,
    token: str | None = None,
    batch_size: int = 10_000,
    max_rows: int | None = None,
) -> Iterator[pd.DataFrame]:
    """Yield one DataFrame per page (for streaming)."""
    settings = Settings()
    base_url = base_url or settings.erp_api_base_url.rstrip("/")
    token = token or settings.erp_api_token
    batch_size = batch_size or settings.ml_export_batch_size
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    offset = 0
    total = 0
    while True:
        with httpx.Client(timeout=60.0) as client:
            r = client.get(
                f"{base_url}/api/v1/ml/export",
                params={"offset": offset, "limit": batch_size},
                headers=headers,
            )
        r.raise_for_status()
        data = r.json()
        batch = data.get("rows") or []
        if not batch:
            break
        df = _rows_to_dataframe(batch)
        yield df
        offset += len(batch)
        total += len(df)
        if data.get("has_more") is False or (max_rows and total >= max_rows):
            break
