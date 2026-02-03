"""Item request/response schemas."""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    sku: str = Field(..., min_length=1, max_length=64)
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1024)
    category: Optional[str] = Field(None, max_length=128)
    unit_cost: Optional[Decimal] = None
    unit_of_measure: str = Field("EA", max_length=32)


class ItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1024)
    category: Optional[str] = Field(None, max_length=128)
    unit_cost: Optional[Decimal] = None
    unit_of_measure: Optional[str] = Field(None, max_length=32)
    is_active: Optional[bool] = None


class ItemResponse(BaseModel):
    id: int
    sku: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    unit_cost: Optional[Decimal] = None
    unit_of_measure: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
