"""Seed initial admin user and sample inventory data for development."""
import os
import sys
from decimal import Decimal
from pathlib import Path

# Add project root so `app` is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import Base, engine, get_db_context
from app.models.user import User, Role
from app.models.item import Item
from app.models.warehouse import Warehouse
from app.models.inventory_transaction import InventoryTransaction, TransactionType
from app.core.security import get_password_hash


def seed():
    Base.metadata.create_all(bind=engine)
    with get_db_context() as db:
        # Add new @erp.example.com users only if they don't exist
        admin = db.query(User).filter(User.email == "admin@erp.example.com").first()
        if not admin:
            admin = User(
                email="admin@erp.example.com",
                hashed_password=get_password_hash("admin123"),
                full_name="Admin User",
                role=Role.ADMIN,
            )
            db.add(admin)
            db.flush()
            manager = User(
                email="manager@erp.example.com",
                hashed_password=get_password_hash("manager123"),
                full_name="Manager User",
                role=Role.MANAGER,
            )
            db.add(manager)
            db.flush()
            viewer = User(
                email="viewer@erp.example.com",
                hashed_password=get_password_hash("viewer123"),
                full_name="Viewer User",
                role=Role.VIEWER,
            )
            db.add(viewer)
            db.flush()
            print("Added users: admin@erp.example.com, manager@erp.example.com, viewer@erp.example.com")
        else:
            manager = db.query(User).filter(User.email == "manager@erp.example.com").first()
            print("Users already exist. Skip user creation.")

        # Add items/warehouses/transactions only if DB is empty of items
        if db.query(Item).first() is not None:
            print("Items already exist. Skip items/warehouses/transactions.")
            print("Seed done. Log in with admin@erp.example.com / admin123")
            return

        # Items
        items = [
            Item(sku="SKU-001", name="Widget A", category="Electronics", unit_cost=Decimal("19.99")),
            Item(sku="SKU-002", name="Widget B", category="Electronics", unit_cost=Decimal("29.99")),
            Item(sku="SKU-003", name="Gadget X", category="Hardware", unit_cost=Decimal("49.50")),
        ]
        for i in items:
            db.add(i)
        db.flush()

        # Warehouses
        wh1 = Warehouse(code="WH-NYC", name="New York Warehouse", location="New York, NY")
        wh2 = Warehouse(code="WH-LA", name="Los Angeles Warehouse", location="Los Angeles, CA")
        db.add(wh1)
        db.add(wh2)
        db.flush()

        # Transactions (ML-ready stream)
        for i, item in enumerate(items):
            for j, wh in enumerate([wh1, wh2]):
                db.add(
                    InventoryTransaction(
                        item_id=item.id,
                        warehouse_id=wh.id,
                        transaction_type=TransactionType.IN,
                        quantity=Decimal("100"),
                        unit_price=item.unit_cost,
                        total_amount=Decimal("100") * (item.unit_cost or 0),
                        reference_type="po",
                        reference_id=f"PO-{i}-{j}",
                        created_by=admin.id,
                    )
                )
        db.add(
            InventoryTransaction(
                item_id=items[0].id,
                warehouse_id=wh1.id,
                transaction_type=TransactionType.OUT,
                quantity=Decimal("5"),
                unit_price=items[0].unit_cost,
                total_amount=Decimal("5") * (items[0].unit_cost or 0),
                reference_type="order",
                reference_id="ORD-001",
                created_by=manager.id,
            )
        )
        print("Seed done. Users: admin@erp.example.com / admin123, manager@erp.example.com / manager123, viewer@erp.example.com / viewer123")
        print("Sample items, warehouses, and inventory transactions created.")


if __name__ == "__main__":
    seed()
