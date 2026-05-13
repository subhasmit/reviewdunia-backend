from pydantic import BaseModel


class ProductBase(BaseModel):
    name: str
    description: str | None = None
    category_id: int | None = None


class ProductResponse(ProductBase):
    id: int

    model_config = {"from_attributes": True}
