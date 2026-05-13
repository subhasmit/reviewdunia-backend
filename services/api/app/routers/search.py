from fastapi import APIRouter, Query

router = APIRouter(prefix="/search", tags=["search"])


@router.get("")
def search(q: str = Query(..., min_length=2), limit: int = Query(default=10, ge=1, le=50)) -> dict:
    return {"query": q, "total": 0, "results": [], "limit": limit}
