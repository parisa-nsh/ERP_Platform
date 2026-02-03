"""ML-ready export schemas - flat rows for feature engineering pipeline."""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class MLTransactionRow(BaseModel):
    """One row per transaction, denormalized for ML (SageMaker training / inference)."""
    transaction_id: int
    item_id: int
    item_sku: str
    item_category: Optional[str] = None
    warehouse_id: int
    warehouse_code: str
    transaction_type: str
    quantity: float = Field(..., description="Signed for feature engineering: +in, -out, etc.")
    unit_price: Optional[float] = None
    total_amount: Optional[float] = None
    reference_type: Optional[str] = None
    created_at: datetime
    created_at_ts: float = Field(..., description="Unix timestamp for time-series features")

    model_config = {"from_attributes": True}


class MLExportResponse(BaseModel):
    """Response for /api/v1/ml/export - paginated ML-ready transaction data."""
    rows: list[MLTransactionRow]
    total_count: int
    offset: int
    limit: int
    has_more: bool
