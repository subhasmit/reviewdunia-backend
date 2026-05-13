from fastapi import FastAPI

from app.core.config import settings
from app.db.postgres import SessionLocal
from app.models import Base
from app.db.postgres import engine
from app.models.product import Product
from app.routers import admin, products, reviews, search, telemetry, upload

app = FastAPI(title="ReviewDunia Backend", version="0.1.0")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seeded = db.get(Product, 1)
        if seeded is None:
            db.add(
                Product(
                    id=1,
                    name="Demo Product",
                    description="Seed product for UI integration and local development.",
                    category_id=None,
                )
            )
            db.commit()


app.include_router(upload.router, prefix=settings.api_v1_prefix)
app.include_router(products.router, prefix=settings.api_v1_prefix)
app.include_router(reviews.router, prefix=settings.api_v1_prefix)
app.include_router(admin.router, prefix=settings.api_v1_prefix)
app.include_router(search.router, prefix=settings.api_v1_prefix)
app.include_router(telemetry.router, prefix=settings.api_v1_prefix)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
