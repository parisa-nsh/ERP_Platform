"""Inventory transaction request/response and ML-friendly schemas."""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TransactionType(str, Enum):
    in_ = "in"
    out = "out"
    adjust = "adjust"
    transfer = "transfer"


class InventoryTransactionCreate(BaseModel):
    item_id: int
    warehouse_id: int
    transaction_type: TransactionType
    quantity: Decimal = Field(..., gt=0)
    unit_price: Optional[Decimal] = None
    reference_type: Optional[str] = Field(None, max_length=64)
    reference_id: Optional[str] = Field(None, max_length=128)
    notes: Optional[str] = Field(None, max_length=512)


class InventoryTransactionUpdate(BaseModel):
    quantity: Optional[Decimal] = Field(None, gt=0)
    unit_price: Optional[Decimal] = None
    notes: Optional[str] = Field(None, max_length=512)


class InventoryTransactionResponse(BaseModel):
    id: int
    item_id: int
    warehouse_id: int
    transaction_type: str
    quantity: Decimal
    unit_price: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None
    reference_type: Optional[str] = None
    reference_id: Optional[str] = None
    notes: Optional[str] = None
    created_by: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}
