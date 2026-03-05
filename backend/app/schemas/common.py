from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AppBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    detail: str


class TimestampedOut(AppBaseSchema):
    created_at: datetime
    updated_at: datetime

