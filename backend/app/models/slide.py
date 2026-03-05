from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.carousel import Carousel


class Slide(Base, TimestampMixin):
    __tablename__ = "slides"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    carousel_id: Mapped[str] = mapped_column(
        ForeignKey("carousels.id", ondelete="CASCADE"), nullable=False, index=True
    )
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    footer_cta: Mapped[str | None] = mapped_column(String(300), nullable=True)
    design_overrides: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    carousel: Mapped["Carousel"] = relationship("Carousel", back_populates="slides")

