from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GenerationCreate(BaseModel):
    carousel_id: str


class GenerationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    carousel_id: str
    status: str
    estimated_tokens: int
    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None
    cost_usd_estimate: float | None
    error: str | None
    result_json: dict | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None

