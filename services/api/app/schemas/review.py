from pydantic import BaseModel, Field


class ReviewRequestCreate(BaseModel):
    prompt: str = Field(min_length=5, max_length=2000)


class ReviewRequestResponse(BaseModel):
    request_id: str
    status: str


class ReviewDecision(BaseModel):
    note: str | None = None
