from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter(prefix="/telemetry", tags=["telemetry"])


@router.get("/site")
def site_telemetry() -> dict:
    return {
        "active_users": 0,
        "queued_reviews": 0,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
