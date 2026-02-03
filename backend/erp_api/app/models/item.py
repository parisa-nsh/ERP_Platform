"""Item (product/SKU) model - master data for inventory."""
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.inventory_transaction import InventoryTransaction


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sku: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    category: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    unit_cost: Mapped[Decimal | None] = mapped_column(Numeric(14, 4), nullable=True)
    unit_of_measure: Mapped[str] = mapped_column(String(32), default="EA", nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    transactions: Mapped[list["InventoryTransaction"]] = relationship(
        "InventoryTransaction",
        back_populates="item",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Item(id={self.id}, sku={self.sku}, name={self.name})>"
