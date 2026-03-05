from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.design import DesignOut


class CarouselFormatInput(BaseModel):
    slides_count: int = Field(default=8, ge=6, le=10)
    language: Literal["RU", "EN", "FR"] = "RU"
    style_sample_text: str | None = Field(default=None, max_length=5000)


class CarouselCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    source_type: Literal["text", "video", "links"]
    source_payload: dict = Field(default_factory=dict)
    format: CarouselFormatInput


class CarouselPatch(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    format: CarouselFormatInput | None = None


class CarouselPreview(BaseModel):
    title: str
    body: str


class CarouselListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    status: str
    language: str
    slides_count: int
    created_at: datetime
    preview: CarouselPreview | None = None


class CarouselListOut(BaseModel):
    items: list[CarouselListItem]
    total: int
    limit: int
    offset: int


class CarouselOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    status: str
    source_type: str
    source_payload: dict
    language: str
    slides_count: int
    style_hint: str | None
    created_at: datetime
    updated_at: datetime
    preview: CarouselPreview | None = None
    design: DesignOut | None = None
