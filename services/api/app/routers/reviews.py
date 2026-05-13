from uuid import uuid4

from fastapi import APIRouter

from app.schemas.review import ReviewRequestCreate, ReviewRequestResponse
from app.services.queue import get_queue

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/{product_id}/request", response_model=ReviewRequestResponse)
def request_review(product_id: int, payload: ReviewRequestCreate) -> ReviewRequestResponse:
    request_id = str(uuid4())
    queue = get_queue()
    queue.enqueue(
        "services.agents.workers.review_generation_worker.generate_review",
        {
            "request_id": request_id,
            "product_id": product_id,
            "prompt": payload.prompt,
        },
    )
    return ReviewRequestResponse(request_id=request_id, status="queued")
