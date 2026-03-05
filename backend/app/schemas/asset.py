from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AssetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    kind: str
    bucket: str
    object_key: str
    mime: str
    size: int
    created_at: datetime
    url: str | None = None

