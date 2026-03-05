from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.slide import Slide
from app.schemas.slide import SlideOut, SlidePatch, SlidesListOut

router = APIRouter(prefix="/carousels/{carousel_id}/slides", tags=["slides"])


@router.get("", response_model=SlidesListOut)
async def list_slides(
    carousel_id: str, session: AsyncSession = Depends(get_session)
) -> SlidesListOut:
    slides = (
        await session.scalars(
            select(Slide).where(Slide.carousel_id == carousel_id).order_by(Slide.order.asc())
        )
    ).all()
    return SlidesListOut(items=[SlideOut.model_validate(slide) for slide in slides])


@router.patch("/{slide_id}", response_model=SlideOut)
async def patch_slide(
    carousel_id: str,
    slide_id: str,
    payload: SlidePatch,
    session: AsyncSession = Depends(get_session),
) -> SlideOut:
    slide = await session.get(Slide, slide_id)
    if not slide or slide.carousel_id != carousel_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Slide not found")

    if payload.title is not None:
        slide.title = payload.title
    if payload.body is not None:
        slide.body = payload.body
    if payload.footer_cta is not None:
        slide.footer_cta = payload.footer_cta
    if payload.design_overrides is not None:
        slide.design_overrides = payload.design_overrides

    await session.commit()
    await session.refresh(slide)
    return SlideOut.model_validate(slide)

