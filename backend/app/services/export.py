from __future__ import annotations

from datetime import datetime
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile

from fastapi import BackgroundTasks
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.asset import Asset
from app.models.carousel import Carousel
from app.models.carousel_design import CarouselDesign
from app.models.export_job import ExportJob
from app.models.slide import Slide
from app.services.rendering import render_service
from app.services.storage import storage_service


class ExportService:
    async def enqueue(
        self,
        *,
        session: AsyncSession,
        carousel: Carousel,
        image_format: str,
        background_tasks: BackgroundTasks,
    ) -> ExportJob:
        slides_count = await session.scalar(
            select(func.count(Slide.id)).where(Slide.carousel_id == carousel.id)
        )
        if slides_count is None:
            slides_count = 0

        job = ExportJob(
            carousel_id=carousel.id,
            status="queued",
            format=image_format,
            slides_count=int(slides_count),
        )
        session.add(job)
        await session.commit()
        await session.refresh(job)
        background_tasks.add_task(self.process_job, job.id)
        return job

    async def process_job(self, job_id: str) -> None:
        async with SessionLocal() as session:
            claimed = await session.scalar(
                update(ExportJob)
                .where(ExportJob.id == job_id, ExportJob.status == "queued")
                .values(status="running", started_at=datetime.utcnow())
                .returning(ExportJob.id)
            )
            if not claimed:
                # Job is already being/has been processed by another runner.
                await session.rollback()
                return
            await session.commit()

            job = await session.get(ExportJob, job_id)
            if not job:
                return
            carousel = await session.get(Carousel, job.carousel_id)
            if not carousel:
                job.status = "failed"
                job.error = "Carousel not found"
                job.finished_at = datetime.utcnow()
                await session.commit()
                return

            try:
                slides = (
                    await session.scalars(
                        select(Slide)
                        .where(Slide.carousel_id == carousel.id)
                        .order_by(Slide.order.asc())
                    )
                ).all()
                if not slides:
                    raise ValueError("No slides to export")

                design = await session.get(CarouselDesign, carousel.id)
                if not design:
                    design = CarouselDesign(carousel_id=carousel.id)
                    session.add(design)
                    await session.commit()
                    await session.refresh(design)

                asset_urls = await self._build_asset_url_map(
                    session=session, design=design, slides=slides
                )
                archive = await self._render_archive(
                    slides=slides,
                    design=design,
                    image_format=job.format,
                    asset_urls=asset_urls,
                )
                object_key = f"exports/{carousel.id}/{job.id}.zip"
                await storage_service.upload_bytes(
                    bucket=settings.S3_BUCKET_EXPORTS,
                    object_key=object_key,
                    body=archive,
                    content_type="application/zip",
                )
                asset = Asset(
                    kind="export_zip",
                    bucket=settings.S3_BUCKET_EXPORTS,
                    object_key=object_key,
                    mime="application/zip",
                    size=len(archive),
                )
                session.add(asset)
                await session.flush()

                job.zip_asset_id = asset.id
                job.slides_count = len(slides)
                job.status = "done"
                job.finished_at = datetime.utcnow()
                await session.commit()
            except Exception as exc:
                job.status = "failed"
                job.error = str(exc)
                job.finished_at = datetime.utcnow()
                await session.commit()

    async def _render_archive(
        self,
        *,
        slides: list[Slide],
        design: CarouselDesign,
        image_format: str,
        asset_urls: dict[str, str] | None = None,
    ) -> bytes:
        with TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            images_dir = base / "images"
            image_paths = await render_service.render_slides(
                slides=slides,
                design=design,
                output_dir=images_dir,
                image_format=image_format,
                asset_urls=asset_urls,
            )

            archive_buffer = BytesIO()
            with ZipFile(archive_buffer, mode="w", compression=ZIP_DEFLATED) as zf:
                for path in image_paths:
                    zf.write(path, path.name)
            return archive_buffer.getvalue()

    async def _build_asset_url_map(
        self,
        *,
        session: AsyncSession,
        design: CarouselDesign,
        slides: list[Slide],
    ) -> dict[str, str]:
        ids: set[str] = set()

        design_tokens = design.style_tokens or {}
        if isinstance(design_tokens, dict):
            bg = design_tokens.get("background")
            if isinstance(bg, dict):
                image_asset_id = bg.get("image_asset_id")
                if isinstance(image_asset_id, str):
                    ids.add(image_asset_id)

        for slide in slides:
            overrides = slide.design_overrides or {}
            style_tokens = overrides.get("style_tokens")
            if not isinstance(style_tokens, dict):
                continue
            bg = style_tokens.get("background")
            if not isinstance(bg, dict):
                continue
            image_asset_id = bg.get("image_asset_id")
            if isinstance(image_asset_id, str):
                ids.add(image_asset_id)

        if not ids:
            return {}

        assets = (
            await session.scalars(select(Asset).where(Asset.id.in_(ids)))
        ).all()
        urls: dict[str, str] = {}
        for asset in assets:
            # Use internal endpoint URLs for worker-side rendering inside Docker network.
            urls[asset.id] = await storage_service.generate_internal_download_url(
                bucket=asset.bucket,
                object_key=asset.object_key,
            )
        return urls

    async def process_queued_once(self) -> bool:
        async with SessionLocal() as session:
            job_id = await session.scalar(
                select(ExportJob.id)
                .where(ExportJob.status == "queued")
                .order_by(ExportJob.created_at.asc())
                .limit(1)
            )
        if not job_id:
            return False
        await self.process_job(job_id)
        return True


export_service = ExportService()
