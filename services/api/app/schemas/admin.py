from pydantic import BaseModel


class PendingReview(BaseModel):
    review_id: str
    product_id: int
    score: float
    status: str
