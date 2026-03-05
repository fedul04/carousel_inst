from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.carousel import Carousel
from app.models.carousel_design import CarouselDesign
from app.models.slide import Slide
from app.schemas.design import DesignOut, DesignPatch
from app.services.design import (
    apply_design_patch,
    extract_apply_to_all_overrides,
    merge_slide_overrides,
)

router = APIRouter(prefix="/carousels/{carousel_id}/design", tags=["design"])


@router.get("", response_model=DesignOut)
async def get_design(
    carousel_id: str, session: AsyncSession = Depends(get_session)
) -> DesignOut:
    design = await session.get(CarouselDesign, carousel_id)
    if not design:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Design not found")
    return DesignOut.model_validate(design)


@router.patch("", response_model=DesignOut)
async def patch_design(
    carousel_id: str,
    payload: DesignPatch,
    session: AsyncSession = Depends(get_session),
) -> DesignOut:
    carousel = await session.get(Carousel, carousel_id)
    if not carousel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carousel not found")

    design = await session.get(CarouselDesign, carousel_id)
    if not design:
        design = CarouselDesign(carousel_id=carousel_id)
        session.add(design)
        await session.flush()

    apply_design_patch(design, payload)

    if payload.apply_to_all:
        updates = extract_apply_to_all_overrides(payload)
        if updates:
            slides = (
                await session.scalars(select(Slide).where(Slide.carousel_id == carousel_id))
            ).all()
            for slide in slides:
                slide.design_overrides = merge_slide_overrides(slide.design_overrides, updates)

    await session.commit()
    await session.refresh(design)
    return DesignOut.model_validate(design)

