from __future__ import annotations

from datetime import datetime

from fastapi import BackgroundTasks
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.carousel import Carousel
from app.models.generation_job import GenerationJob
from app.models.slide import Slide
from app.schemas.llm import GeneratedSlide
from app.services.llm import llm_service
from app.services.source_ingest import source_ingest_service
from app.services.token_estimator import estimate_tokens


class GenerationService:
    async def enqueue(
        self,
        *,
        session: AsyncSession,
        carousel: Carousel,
        background_tasks: BackgroundTasks,
    ) -> GenerationJob:
        estimated_tokens = estimate_tokens(
            str(carousel.source_payload),
            carousel.style_hint or "",
        )
        job = GenerationJob(
            carousel_id=carousel.id,
            status="queued",
            estimated_tokens=estimated_tokens,
        )
        carousel.status = "generating"
        session.add(job)
        await session.commit()
        await session.refresh(job)

        background_tasks.add_task(self.process_job, job.id)
        return job

    async def process_job(self, job_id: str) -> None:
        async with SessionLocal() as session:
            job = await session.get(GenerationJob, job_id)
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
                job.status = "running"
                job.started_at = datetime.utcnow()
                await session.commit()

                prepared_payload = await source_ingest_service.prepare_payload(
                    source_type=carousel.source_type,
                    source_payload=carousel.source_payload,
                    language=carousel.language,
                )

                generated, usage = await llm_service.generate_slides(
                    source_payload=prepared_payload,
                    language=carousel.language,
                    slides_count=carousel.slides_count,
                    style_hint=carousel.style_hint,
                )
                normalized = self._normalize_count(
                    generated.slides, carousel.slides_count, carousel.language
                )

                await session.execute(delete(Slide).where(Slide.carousel_id == carousel.id))
                for slide in normalized:
                    session.add(
                        Slide(
                            carousel_id=carousel.id,
                            order=slide.order,
                            title=slide.title,
                            body=slide.body,
                            footer_cta=slide.footer_cta,
                            design_overrides={},
                        )
                    )

                job.prompt_tokens = usage.prompt_tokens
                job.completion_tokens = usage.completion_tokens
                job.total_tokens = usage.total_tokens
                if usage.total_tokens is not None:
                    job.cost_usd_estimate = round(
                        (usage.total_tokens / 1000) * settings.LLM_COST_PER_1K_TOKENS_USD,
                        6,
                    )
                job.result_json = {
                    "slides": [s.model_dump() for s in normalized],
                    "artifacts": generated.artifacts.model_dump(),
                    "ingestion": prepared_payload.get("ingestion", {}),
                }
                job.status = "done"
                job.finished_at = datetime.utcnow()
                carousel.status = "ready"
                await session.commit()
            except Exception as exc:
                job.status = "failed"
                job.error = str(exc)
                job.finished_at = datetime.utcnow()
                carousel.status = "failed"
                await session.commit()

    @staticmethod
    def _normalize_count(
        slides: list[GeneratedSlide], target_count: int, language: str
    ) -> list[GeneratedSlide]:
        normalized = sorted(slides, key=lambda x: x.order)[:target_count]
        while len(normalized) < target_count:
            idx = len(normalized) + 1
            if language == "RU":
                title = f"\u0421\u043b\u0430\u0439\u0434 {idx}"
                body = (
                    "\u0414\u043e\u0431\u0430\u0432\u044c\u0442\u0435 "
                    "\u043e\u043f\u0438\u0441\u0430\u043d\u0438\u0435 \u0441\u043b\u0430\u0439\u0434\u0430."
                )
            elif language == "FR":
                title = f"Diapositive {idx}"
                body = "Ajoutez la description de cette diapositive."
            else:
                title = f"Slide {idx}"
                body = "Add slide description."
            normalized.append(
                GeneratedSlide(order=idx, title=title, body=body, footer_cta=None)
            )

        for index, slide in enumerate(normalized, start=1):
            slide.order = index
        return normalized

    async def process_queued_once(self) -> bool:
        async with SessionLocal() as session:
            job_id = await session.scalar(
                select(GenerationJob.id)
                .where(GenerationJob.status == "queued")
                .order_by(GenerationJob.created_at.asc())
                .limit(1)
            )
        if not job_id:
            return False
        await self.process_job(job_id)
        return True


generation_service = GenerationService()
