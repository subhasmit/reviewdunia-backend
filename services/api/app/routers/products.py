from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.postgres import get_db
from app.models.product import Product
from app.schemas.product import ProductResponse

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/{id}", response_model=ProductResponse)
def get_product(id: int, db: Session = Depends(get_db)) -> ProductResponse:
    product = db.get(Product, id)
    if not product:
        if id == 1:
            product = Product(
                id=1,
                name="Demo Product",
                description="Seed product for UI integration and local development.",
                category_id=None,
            )
            db.add(product)
            db.commit()
            db.refresh(product)
        else:
            raise HTTPException(status_code=404, detail="Product not found")
    return product
