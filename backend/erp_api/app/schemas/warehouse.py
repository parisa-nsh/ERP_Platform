"""Warehouse request/response schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class WarehouseCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=32)
    name: str = Field(..., min_length=1, max_length=255)
    location: Optional[str] = Field(None, max_length=255)


class WarehouseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    location: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None


class WarehouseResponse(BaseModel):
    id: int
    code: str
    name: str
    location: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
