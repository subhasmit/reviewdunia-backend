from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, UploadFile

from app.core.config import settings
from app.schemas.upload import UploadResponse
from app.services.queue import get_queue

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/screenshot", response_model=UploadResponse)
def upload_screenshot(file: UploadFile = File(...)) -> UploadResponse:
    request_id = str(uuid4())
    upload_root = Path(settings.upload_volume_path)
    upload_root.mkdir(parents=True, exist_ok=True)

    destination = upload_root / f"{request_id}_{file.filename}"
    destination.write_bytes(file.file.read())

    queue = get_queue()
    queue.enqueue("services.agents.workers.review_generation_worker.process_upload_job", {
        "request_id": request_id,
        "file_path": str(destination),
    })

    return UploadResponse(request_id=request_id, matches=[], queued=True)
