from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import BgType, TemplatePreset

if TYPE_CHECKING:
    from app.models.carousel import Carousel


class CarouselDesign(Base):
    __tablename__ = "carousel_design"

    carousel_id: Mapped[str] = mapped_column(
        ForeignKey("carousels.id", ondelete="CASCADE"), primary_key=True
    )
    template: Mapped[str] = mapped_column(
        String(32), nullable=False, default=TemplatePreset.CLASSIC.value
    )
    bg_type: Mapped[str] = mapped_column(
        String(16), nullable=False, default=BgType.COLOR.value
    )
    bg_value: Mapped[str] = mapped_column(String(512), nullable=False, default="#F4F1E9")
    bg_overlay: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    layout_padding: Mapped[int] = mapped_column(Integer, nullable=False, default=64)
    align_x: Mapped[str] = mapped_column(String(16), nullable=False, default="left")
    align_y: Mapped[str] = mapped_column(String(16), nullable=False, default="top")
    show_header: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    show_footer: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    header_text: Mapped[str] = mapped_column(String(255), nullable=False, default="@username")
    footer_text: Mapped[str] = mapped_column(String(255), nullable=False, default="Draft AI")
    style_tokens: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    apply_all_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    carousel: Mapped["Carousel"] = relationship("Carousel", back_populates="design")
