from pydantic import BaseModel


class UploadResponse(BaseModel):
    request_id: str
    matches: list[dict]
    queued: bool
