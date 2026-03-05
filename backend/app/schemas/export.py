from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class ExportCreate(BaseModel):
    carousel_id: str
    format: Literal["png", "jpg"] = "png"


class ExportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    carousel_id: str
    status: str
    format: str
    slides_count: int
    zip_asset_id: str | None
    download_url: str | None = None
    error: str | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None

