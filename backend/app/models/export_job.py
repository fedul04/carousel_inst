from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import ExportStatus

if TYPE_CHECKING:
    from app.models.asset import Asset
    from app.models.carousel import Carousel


class ExportJob(Base):
    __tablename__ = "export_jobs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    carousel_id: Mapped[str] = mapped_column(
        ForeignKey("carousels.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default=ExportStatus.QUEUED.value
    )
    format: Mapped[str] = mapped_column(String(8), nullable=False, default="png")
    slides_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    zip_asset_id: Mapped[str | None] = mapped_column(
        ForeignKey("assets.id", ondelete="SET NULL"), nullable=True
    )
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    carousel: Mapped["Carousel"] = relationship("Carousel", back_populates="export_jobs")
    zip_asset: Mapped["Asset | None"] = relationship("Asset")

