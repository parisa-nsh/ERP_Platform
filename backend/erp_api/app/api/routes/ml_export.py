"""ML-ready export and inference endpoints."""
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, Request, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database import get_db
from app.models.user import User
from app.models.inventory_transaction import InventoryTransaction, TransactionType
from app.models.item import Item
from app.models.warehouse import Warehouse
from app.schemas.ml_export import MLTransactionRow, MLExportResponse
from app.core.deps import get_current_active_user, require_roles
from app.models.user import Role
from app.config import get_settings

router = APIRouter(prefix="/ml", tags=["ml-export"])
settings = get_settings()


class ScoreRequest(BaseModel):
    """Either transaction_ids (fetch from DB) or transactions (inline ML-export rows)."""
    transaction_ids: list[int] | None = Field(None, description="Score these DB transaction IDs")
    transactions: list[dict] | None = Field(None, description="Inline transaction rows (ML export format)")


class ScoreResultItem(BaseModel):
    transaction_id: int
    anomaly_score: float
    cluster_id: int
    is_anomaly: bool


class ScoreResponse(BaseModel):
    results: list[ScoreResultItem]
    model_loaded: bool


@router.get("/export", response_model=MLExportResponse)
def export_ml_transactions(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.ADMIN, Role.MANAGER, Role.VIEWER))],
    offset: int = Query(0, ge=0),
    limit: int = Query(10_000, ge=1, le=100_000),
):
    """
    Export inventory transactions in ML-ready flat format (denormalized).
    For SageMaker training / feature engineering: item_sku, warehouse_code,
    transaction_type, quantity (signed), timestamps, etc.
    """
    max_rows = min(limit, settings.ml_export_max_rows)
    # Join to get item + warehouse attributes
    q = (
        db.query(
            InventoryTransaction.id.label("transaction_id"),
            InventoryTransaction.item_id,
            Item.sku.label("item_sku"),
            Item.category.label("item_category"),
            InventoryTransaction.warehouse_id,
            Warehouse.code.label("warehouse_code"),
            InventoryTransaction.transaction_type,
            InventoryTransaction.quantity,
            InventoryTransaction.unit_price,
            InventoryTransaction.total_amount,
            InventoryTransaction.reference_type,
            InventoryTransaction.created_at,
        )
        .join(Item, InventoryTransaction.item_id == Item.id)
        .join(Warehouse, InventoryTransaction.warehouse_id == Warehouse.id)
        .order_by(InventoryTransaction.created_at.asc())
    )
    total_count = db.query(func.count(InventoryTransaction.id)).scalar() or 0
    rows_query = q.offset(offset).limit(max_rows)
    rows_data = rows_query.all()

    # Build ML rows with signed quantity and timestamp
    rows = []
    for r in rows_data:
        qty = float(r.quantity)
        if r.transaction_type == TransactionType.OUT:
            qty = -qty
        elif r.transaction_type == TransactionType.ADJUST:
            # Keep raw; pipeline can treat separately
            pass
        ts = r.created_at
        created_at_ts = ts.timestamp() if ts else 0.0
        rows.append(
            MLTransactionRow(
                transaction_id=r.transaction_id,
                item_id=r.item_id,
                item_sku=r.item_sku,
                item_category=r.item_category,
                warehouse_id=r.warehouse_id,
                warehouse_code=r.warehouse_code,
                transaction_type=r.transaction_type.value,
                quantity=qty,
                unit_price=float(r.unit_price) if r.unit_price is not None else None,
                total_amount=float(r.total_amount) if r.total_amount is not None else None,
                reference_type=r.reference_type,
                created_at=ts,
                created_at_ts=created_at_ts,
            )
        )

    return MLExportResponse(
        rows=rows,
        total_count=total_count,
        offset=offset,
        limit=len(rows),
        has_more=(offset + len(rows)) < total_count,
    )


def _export_rows_for_transaction_ids(db: Session, transaction_ids: list[int]) -> list[dict]:
    """Fetch given transaction IDs and return list of dicts in ML export row format."""
    if not transaction_ids:
        return []
    q = (
        db.query(
            InventoryTransaction.id.label("transaction_id"),
            InventoryTransaction.item_id,
            Item.sku.label("item_sku"),
            Item.category.label("item_category"),
            InventoryTransaction.warehouse_id,
            Warehouse.code.label("warehouse_code"),
            InventoryTransaction.transaction_type,
            InventoryTransaction.quantity,
            InventoryTransaction.unit_price,
            InventoryTransaction.total_amount,
            InventoryTransaction.reference_type,
            InventoryTransaction.created_at,
        )
        .join(Item, InventoryTransaction.item_id == Item.id)
        .join(Warehouse, InventoryTransaction.warehouse_id == Warehouse.id)
        .filter(InventoryTransaction.id.in_(transaction_ids))
    )
    rows_data = q.all()
    out = []
    for r in rows_data:
        qty = float(r.quantity)
        if r.transaction_type == TransactionType.OUT:
            qty = -qty
        ts = r.created_at
        created_at_ts = ts.timestamp() if ts else 0.0
        out.append({
            "transaction_id": r.transaction_id,
            "item_id": r.item_id,
            "item_sku": r.item_sku,
            "item_category": r.item_category,
            "warehouse_id": r.warehouse_id,
            "warehouse_code": r.warehouse_code,
            "transaction_type": r.transaction_type.value,
            "quantity": qty,
            "unit_price": float(r.unit_price) if r.unit_price is not None else None,
            "total_amount": float(r.total_amount) if r.total_amount is not None else None,
            "reference_type": r.reference_type,
            "created_at_ts": created_at_ts,
        })
    return out


@router.post("/score", response_model=ScoreResponse)
def score_transactions(
    request: Request,
    body: ScoreRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(Role.ADMIN, Role.MANAGER, Role.VIEWER))],
):
    """
    Run anomaly detection on transactions. Requires ML model loaded (set ML_MODEL_DIR).
    Provide either transaction_ids (fetch from DB) or transactions (inline ML-export format).
    """
    inference: Any = getattr(request.app.state, "ml_inference", None)
    if not inference:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML model not loaded. Set ML_MODEL_DIR to the trained model directory.",
        )
    if body.transaction_ids is not None and body.transactions is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provide only transaction_ids or transactions")
    if body.transaction_ids is None and body.transactions is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provide transaction_ids or transactions")

    if body.transaction_ids is not None:
        rows = _export_rows_for_transaction_ids(db, body.transaction_ids)
    else:
        rows = body.transactions or []

    if not rows:
        return ScoreResponse(results=[], model_loaded=True)

    results = inference.score_transactions(rows)
    return ScoreResponse(
        results=[ScoreResultItem(**r) for r in results],
        model_loaded=True,
    )
