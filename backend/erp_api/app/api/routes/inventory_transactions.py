"""Inventory transactions CRUD - core ML data source."""
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.item import Item
from app.models.warehouse import Warehouse
from app.models.inventory_transaction import InventoryTransaction, TransactionType as ModelTxType
from app.schemas.inventory_transaction import (
    InventoryTransactionCreate,
    InventoryTransactionUpdate,
    InventoryTransactionResponse,
    TransactionType as SchemaTxType,
)
from app.core.deps import get_current_active_user, require_roles
from app.models.user import Role

router = APIRouter(prefix="/inventory-transactions", tags=["inventory-transactions"])


def _schema_type_to_model(t: SchemaTxType) -> ModelTxType:
    return ModelTxType(t.value)


@router.get("", response_model=list[InventoryTransactionResponse])
def list_transactions(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    item_id: int | None = None,
    warehouse_id: int | None = None,
    transaction_type: SchemaTxType | None = None,
):
    q = db.query(InventoryTransaction)
    if item_id is not None:
        q = q.filter(InventoryTransaction.item_id == item_id)
    if warehouse_id is not None:
        q = q.filter(InventoryTransaction.warehouse_id == warehouse_id)
    if transaction_type is not None:
        q = q.filter(InventoryTransaction.transaction_type == _schema_type_to_model(transaction_type))
    q = q.order_by(InventoryTransaction.created_at.desc())
    return q.offset(skip).limit(limit).all()


@router.get("/{transaction_id}", response_model=InventoryTransactionResponse)
def get_transaction(
    transaction_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    tx = db.query(InventoryTransaction).filter(InventoryTransaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return tx


@router.post("", response_model=InventoryTransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: InventoryTransactionCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.ADMIN, Role.MANAGER))],
):
    item = db.query(Item).filter(Item.id == payload.item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    wh = db.query(Warehouse).filter(Warehouse.id == payload.warehouse_id).first()
    if not wh:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found")

    total = (payload.unit_price * payload.quantity) if payload.unit_price is not None else None
    tx = InventoryTransaction(
        item_id=payload.item_id,
        warehouse_id=payload.warehouse_id,
        transaction_type=_schema_type_to_model(payload.transaction_type),
        quantity=payload.quantity,
        unit_price=payload.unit_price,
        total_amount=total,
        reference_type=payload.reference_type,
        reference_id=payload.reference_id,
        notes=payload.notes,
        created_by=current_user.id,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


@router.patch("/{transaction_id}", response_model=InventoryTransactionResponse)
def update_transaction(
    transaction_id: int,
    payload: InventoryTransactionUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.ADMIN, Role.MANAGER))],
):
    tx = db.query(InventoryTransaction).filter(InventoryTransaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(tx, k, v)
    if "quantity" in data or "unit_price" in data:
        tx.total_amount = (tx.unit_price * tx.quantity) if tx.unit_price else None
    db.commit()
    db.refresh(tx)
    return tx


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.ADMIN))],
):
    tx = db.query(InventoryTransaction).filter(InventoryTransaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    db.delete(tx)
    db.commit()
    return None
