from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.carousel import Carousel
from app.models.carousel_design import CarouselDesign
from app.models.slide import Slide
from app.schemas.carousel import (
    CarouselCreate,
    CarouselListItem,
    CarouselListOut,
    CarouselOut,
    CarouselPatch,
    CarouselPreview,
)
from app.schemas.design import DesignOut

router = APIRouter(prefix="/carousels", tags=["carousels"])


def _to_design_out(design: CarouselDesign | None) -> DesignOut | None:
    if not design:
        return None
    return DesignOut.model_validate(design)


def _to_preview(slide: Slide | None) -> CarouselPreview | None:
    if not slide:
        return None
    return CarouselPreview(title=slide.title, body=slide.body)


async def _first_slide(session: AsyncSession, carousel_id: str) -> Slide | None:
    return await session.scalar(
        select(Slide).where(Slide.carousel_id == carousel_id).order_by(Slide.order.asc()).limit(1)
    )


@router.get("", response_model=CarouselListOut)
async def list_carousels(
    status_filter: str | None = Query(default=None, alias="status"),
    lang: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> CarouselListOut:
    query = select(Carousel)
    count_query = select(func.count(Carousel.id))

    if status_filter:
        query = query.where(Carousel.status == status_filter)
        count_query = count_query.where(Carousel.status == status_filter)
    if lang:
        query = query.where(func.lower(Carousel.language) == lang.lower())
        count_query = count_query.where(func.lower(Carousel.language) == lang.lower())

    total = int((await session.scalar(count_query)) or 0)
    carousels = (
        await session.scalars(
            query.order_by(Carousel.created_at.desc()).offset(offset).limit(limit)
        )
    ).all()

    items: list[CarouselListItem] = []
    for carousel in carousels:
        first = await _first_slide(session, carousel.id)
        items.append(
            CarouselListItem(
                id=carousel.id,
                title=carousel.title,
                status=carousel.status,
                language=carousel.language,
                slides_count=carousel.slides_count,
                created_at=carousel.created_at,
                preview=_to_preview(first),
            )
        )

    return CarouselListOut(items=items, total=total, limit=limit, offset=offset)


@router.get("/{carousel_id}", response_model=CarouselOut)
async def get_carousel(
    carousel_id: str, session: AsyncSession = Depends(get_session)
) -> CarouselOut:
    carousel = await session.get(Carousel, carousel_id)
    if not carousel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carousel not found")
    preview = await _first_slide(session, carousel.id)
    design = await session.get(CarouselDesign, carousel.id)

    return CarouselOut(
        id=carousel.id,
        title=carousel.title,
        status=carousel.status,
        source_type=carousel.source_type,
        source_payload=carousel.source_payload,
        language=carousel.language,
        slides_count=carousel.slides_count,
        style_hint=carousel.style_hint,
        created_at=carousel.created_at,
        updated_at=carousel.updated_at,
        preview=_to_preview(preview),
        design=_to_design_out(design),
    )


@router.post("", response_model=CarouselOut, status_code=status.HTTP_201_CREATED)
async def create_carousel(
    payload: CarouselCreate, session: AsyncSession = Depends(get_session)
) -> CarouselOut:
    carousel = Carousel(
        title=payload.title,
        source_type=payload.source_type,
        source_payload=payload.source_payload,
        language=payload.format.language,
        slides_count=payload.format.slides_count,
        style_hint=payload.format.style_sample_text,
        status="draft",
    )
    session.add(carousel)
    await session.flush()

    design = CarouselDesign(carousel_id=carousel.id)
    session.add(design)
    await session.commit()
    await session.refresh(carousel)
    await session.refresh(design)

    return CarouselOut(
        id=carousel.id,
        title=carousel.title,
        status=carousel.status,
        source_type=carousel.source_type,
        source_payload=carousel.source_payload,
        language=carousel.language,
        slides_count=carousel.slides_count,
        style_hint=carousel.style_hint,
        created_at=carousel.created_at,
        updated_at=carousel.updated_at,
        preview=None,
        design=_to_design_out(design),
    )


@router.patch("/{carousel_id}", response_model=CarouselOut)
async def patch_carousel(
    carousel_id: str,
    payload: CarouselPatch,
    session: AsyncSession = Depends(get_session),
) -> CarouselOut:
    carousel = await session.get(Carousel, carousel_id)
    if not carousel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carousel not found")

    if payload.title is not None:
        carousel.title = payload.title
    if payload.format is not None:
        carousel.language = payload.format.language
        carousel.slides_count = payload.format.slides_count
        carousel.style_hint = payload.format.style_sample_text

    await session.commit()
    await session.refresh(carousel)
    preview = await _first_slide(session, carousel.id)
    design = await session.get(CarouselDesign, carousel.id)

    return CarouselOut(
        id=carousel.id,
        title=carousel.title,
        status=carousel.status,
        source_type=carousel.source_type,
        source_payload=carousel.source_payload,
        language=carousel.language,
        slides_count=carousel.slides_count,
        style_hint=carousel.style_hint,
        created_at=carousel.created_at,
        updated_at=carousel.updated_at,
        preview=_to_preview(preview),
        design=_to_design_out(design),
    )

