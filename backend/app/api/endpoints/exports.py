from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.asset import Asset
from app.models.carousel import Carousel
from app.models.export_job import ExportJob
from app.schemas.export import ExportCreate, ExportOut
from app.services.export import export_service
from app.services.storage import storage_service

router = APIRouter(prefix="/exports", tags=["exports"])


@router.post("", response_model=ExportOut, status_code=status.HTTP_201_CREATED)
async def create_export(
    payload: ExportCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
) -> ExportOut:
    carousel = await session.get(Carousel, payload.carousel_id)
    if not carousel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carousel not found")

    job = await export_service.enqueue(
        session=session,
        carousel=carousel,
        image_format=payload.format,
        background_tasks=background_tasks,
    )
    return ExportOut.model_validate(job)


@router.get("/{export_id}", response_model=ExportOut)
async def get_export(
    export_id: str, request: Request, session: AsyncSession = Depends(get_session)
) -> ExportOut:
    job = await session.get(ExportJob, export_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export job not found")

    out = ExportOut.model_validate(job)
    if job.status == "done" and job.zip_asset_id:
        asset = await session.get(Asset, job.zip_asset_id)
        if asset:
            url = str(request.url_for("download_export_asset", export_id=job.id))
            out = out.model_copy(update={"download_url": url})
    return out


@router.get("/{export_id}/download", name="download_export_asset")
async def download_export_asset(
    export_id: str, session: AsyncSession = Depends(get_session)
) -> Response:
    job = await session.get(ExportJob, export_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export job not found")
    if job.status != "done" or not job.zip_asset_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Export is not ready yet",
        )

    asset = await session.get(Asset, job.zip_asset_id)
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export asset not found")

    body, content_type = await storage_service.download_bytes(
        bucket=asset.bucket,
        object_key=asset.object_key,
    )
    filename = f"carousel_{job.carousel_id}_{job.id}.zip"
    return Response(
        content=body,
        media_type=content_type or asset.mime or "application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
