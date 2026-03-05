from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.carousel import Carousel
from app.models.generation_job import GenerationJob
from app.schemas.generation import GenerationCreate, GenerationOut
from app.services.generation import generation_service

router = APIRouter(prefix="/generations", tags=["generations"])


@router.post("", response_model=GenerationOut, status_code=status.HTTP_201_CREATED)
async def create_generation(
    payload: GenerationCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
) -> GenerationOut:
    carousel = await session.get(Carousel, payload.carousel_id)
    if not carousel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carousel not found")

    job = await generation_service.enqueue(
        session=session, carousel=carousel, background_tasks=background_tasks
    )
    return GenerationOut.model_validate(job)


@router.get("/{generation_id}", response_model=GenerationOut)
async def get_generation(
    generation_id: str, session: AsyncSession = Depends(get_session)
) -> GenerationOut:
    job = await session.get(GenerationJob, generation_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Generation job not found"
        )
    return GenerationOut.model_validate(job)


@router.get("/by-carousel/{carousel_id}/latest", response_model=GenerationOut)
async def get_latest_generation_for_carousel(
    carousel_id: str, session: AsyncSession = Depends(get_session)
) -> GenerationOut:
    job = await session.scalar(
        select(GenerationJob)
        .where(GenerationJob.carousel_id == carousel_id)
        .order_by(GenerationJob.created_at.desc())
        .limit(1)
    )
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation job not found",
        )
    return GenerationOut.model_validate(job)
