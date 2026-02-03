"""Build ML feature matrix from transaction DataFrame."""
import pandas as pd
import numpy as np
from typing import Optional

# Columns we expect from fetcher (API or CSV)
EXPECTED_COLS = [
    "transaction_id", "item_id", "item_sku", "item_category",
    "warehouse_id", "warehouse_code", "transaction_type",
    "quantity", "unit_price", "total_amount", "reference_type",
    "created_at", "created_at_ts",
]


def build_feature_matrix(
    df: pd.DataFrame,
    drop_na_rows: bool = True,
) -> pd.DataFrame:
    """
    One row per transaction. Features:
    - quantity (signed), abs_quantity, unit_price, total_amount (fillna 0)
    - hour, day_of_week, day_of_month (from created_at_ts)
    - item_id, warehouse_id (numeric ids for tree models / scaling)
    - transaction_type_* one-hot or single label-encoded
    - item_category (label-encoded if present)
    """
    if df.empty:
        return pd.DataFrame()

    for c in ["transaction_id", "quantity", "created_at_ts", "item_id", "warehouse_id"]:
        if c not in df.columns:
            raise ValueError(f"Missing column: {c}")

    out = pd.DataFrame(index=df.index)
    out["transaction_id"] = df["transaction_id"].astype(np.int64)

    # Numeric
    out["quantity"] = df["quantity"].astype(float)
    out["abs_quantity"] = np.abs(out["quantity"])
    out["unit_price"] = df["unit_price"].fillna(0).astype(float)
    out["total_amount"] = df["total_amount"].fillna(0).astype(float)

    # Time from timestamp
    ts = df["created_at_ts"].astype(float)
    dt = pd.to_datetime(ts, unit="s", utc=True)
    out["hour"] = dt.dt.hour.astype(float)
    out["day_of_week"] = dt.dt.dayofweek.astype(float)
    out["day_of_month"] = dt.dt.day.astype(float)

    # Categorical: label encode for simplicity (tree/scale-friendly)
    out["item_id"] = df["item_id"].astype(np.int64)
    out["warehouse_id"] = df["warehouse_id"].astype(np.int64)

    tx_type = df["transaction_type"].fillna("unknown").astype(str)
    uniq = tx_type.unique()
    mapping = {v: i for i, v in enumerate(sorted(uniq))}
    out["transaction_type_enc"] = tx_type.map(mapping).astype(float)

    if "item_category" in df.columns:
        cat = df["item_category"].fillna("unknown").astype(str)
        cat_uniq = cat.unique()
        cat_map = {v: i for i, v in enumerate(sorted(cat_uniq))}
        out["item_category_enc"] = cat.map(cat_map).astype(float)
    else:
        out["item_category_enc"] = 0.0

    feature_cols = get_feature_columns()
    if drop_na_rows:
        out = out.dropna(subset=feature_cols).copy()

    return out


def get_feature_columns() -> list[str]:
    """Column names used as model input (no transaction_id)."""
    return [
        "quantity", "abs_quantity", "unit_price", "total_amount",
        "hour", "day_of_week", "day_of_month",
        "item_id", "warehouse_id", "transaction_type_enc", "item_category_enc",
    ]
