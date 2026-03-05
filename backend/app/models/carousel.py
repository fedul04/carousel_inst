from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import CarouselStatus, SourceType

if TYPE_CHECKING:
    from app.models.carousel_design import CarouselDesign
    from app.models.export_job import ExportJob
    from app.models.generation_job import GenerationJob
    from app.models.slide import Slide


class Carousel(Base, TimestampMixin):
    __tablename__ = "carousels"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default=CarouselStatus.DRAFT.value
    )
    source_type: Mapped[str] = mapped_column(
        String(32), nullable=False, default=SourceType.TEXT.value
    )
    source_payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    language: Mapped[str] = mapped_column(String(8), nullable=False, default="RU")
    slides_count: Mapped[int] = mapped_column(Integer, nullable=False, default=8)
    style_hint: Mapped[str | None] = mapped_column(Text, nullable=True)

    slides: Mapped[list["Slide"]] = relationship(
        "Slide",
        back_populates="carousel",
        cascade="all, delete-orphan",
        order_by="Slide.order",
    )
    design: Mapped["CarouselDesign"] = relationship(
        "CarouselDesign",
        back_populates="carousel",
        cascade="all, delete-orphan",
        uselist=False,
    )
    generation_jobs: Mapped[list["GenerationJob"]] = relationship(
        "GenerationJob", back_populates="carousel", cascade="all, delete-orphan"
    )
    export_jobs: Mapped[list["ExportJob"]] = relationship(
        "ExportJob", back_populates="carousel", cascade="all, delete-orphan"
    )

