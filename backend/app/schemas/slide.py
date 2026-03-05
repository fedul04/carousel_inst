from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SlideOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    carousel_id: str
    order: int
    title: str
    body: str
    footer_cta: str | None
    design_overrides: dict
    created_at: datetime
    updated_at: datetime


class SlidePatch(BaseModel):
    title: str | None = Field(default=None, max_length=180)
    body: str | None = Field(default=None, max_length=1200)
    footer_cta: str | None = Field(default=None, max_length=200)
    design_overrides: dict | None = None


class SlidesListOut(BaseModel):
    items: list[SlideOut]

