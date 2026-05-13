from fastapi import APIRouter, Depends

from app.deps.auth import get_current_admin
from app.schemas.admin import PendingReview
from app.schemas.review import ReviewDecision

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(get_current_admin)])

PENDING_REVIEWS: dict[str, dict] = {
    "seed-review-1": {"review_id": "seed-review-1", "product_id": 1, "score": 0.88, "status": "pending_approval"}
}


@router.get("/reviews/pending", response_model=list[PendingReview])
def list_pending_reviews() -> list[PendingReview]:
    return [PendingReview(**review) for review in PENDING_REVIEWS.values() if review["status"] == "pending_approval"]


@router.post("/reviews/{review_id}/approve")
def approve_review(review_id: str, _: ReviewDecision | None = None) -> dict:
    if review_id in PENDING_REVIEWS:
        PENDING_REVIEWS[review_id]["status"] = "approved"
    return {"review_id": review_id, "status": "approved"}


@router.post("/reviews/{review_id}/request_edit")
def request_edit(review_id: str, payload: ReviewDecision) -> dict:
    if review_id in PENDING_REVIEWS:
        PENDING_REVIEWS[review_id]["status"] = "edit_requested"
    return {"review_id": review_id, "status": "edit_requested", "note": payload.note}


@router.get("/telemetry/site")
def admin_site_telemetry() -> dict:
    return {
        "site_metrics": {
            "views_24h": 0,
            "affiliate_clicks_24h": 0,
        },
        "agent_metrics": {
            "queued_jobs": 0,
            "avg_generation_score": 0.0,
        },
    }
