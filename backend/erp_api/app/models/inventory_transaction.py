"""Inventory transaction model - core ML-ready event stream."""
import enum
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.item import Item
    from app.models.warehouse import Warehouse


class TransactionType(str, enum.Enum):
    """Transaction direction / type for feature engineering."""
    IN = "in"           # Receipt, purchase
    OUT = "out"         # Shipment, sale
    ADJUST = "adjust"   # Count adjustment, write-off
    TRANSFER = "transfer"  # Move between warehouses


class InventoryTransaction(Base):
    """
    Each row is one inventory event. Primary data source for ML pipeline:
    - Anomaly detection (volume, value, frequency)
    - Clustering (item/warehouse/type patterns)
    """
    __tablename__ = "inventory_transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id", ondelete="RESTRICT"), index=True, nullable=False)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id", ondelete="RESTRICT"), index=True, nullable=False)
    transaction_type: Mapped[TransactionType] = mapped_column(nullable=False, index=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    unit_price: Mapped[Decimal | None] = mapped_column(Numeric(14, 4), nullable=True)
    total_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    reference_type: Mapped[str | None] = mapped_column(String(64), nullable=True)  # e.g. "order", "po", "count"
    reference_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    item: Mapped["Item"] = relationship("Item", back_populates="transactions")
    warehouse: Mapped["Warehouse"] = relationship("Warehouse", back_populates="transactions")
    created_by_user: Mapped["User | None"] = relationship("User", back_populates="transactions_created", foreign_keys=[created_by])

    def __repr__(self) -> str:
        return f"<InventoryTransaction(id={self.id}, item_id={self.item_id}, type={self.transaction_type}, qty={self.quantity})>"
