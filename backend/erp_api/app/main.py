"""ML-Enabled ERP Inventory Intelligence API - FastAPI application."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, engine
from app.api.routes import auth, items, warehouses, inventory_transactions, ml_export

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist (for dev; use Alembic in production)
    Base.metadata.create_all(bind=engine)
    # Optional: load ML inference model if ML_MODEL_DIR is set
    from app.services.inference import load_inference_service
    app.state.ml_inference = load_inference_service(settings.ml_model_dir)
    yield
    # Shutdown
    app.state.ml_inference = None


app = FastAPI(
    title=settings.app_name,
    description="Backend API: ERP inventory data source + ML-ready export for SageMaker pipeline",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API v1
prefix = settings.api_v1_prefix
app.include_router(auth.router, prefix=prefix)
app.include_router(items.router, prefix=prefix)
app.include_router(warehouses.router, prefix=prefix)
app.include_router(inventory_transactions.router, prefix=prefix)
app.include_router(ml_export.router, prefix=prefix)


@app.get("/health")
def health():
    return {"status": "ok", "service": "erp-inventory-api"}


@app.get("/")
def root():
    return {
        "service": settings.app_name,
        "docs": "/docs",
        "health": "/health",
        "api": prefix,
    }
