from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_session
from app.models.asset import Asset
from app.schemas.asset import AssetOut
from app.services.storage import storage_service

router = APIRouter(prefix="/assets", tags=["assets"])


@router.post("/upload", response_model=AssetOut, status_code=status.HTTP_201_CREATED)
async def upload_asset(
    file: UploadFile = File(...), session: AsyncSession = Depends(get_session)
) -> AssetOut:
    content = await file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file")

    object_key = f"uploads/{uuid4()}-{file.filename or 'asset.bin'}"
    content_type = file.content_type or "application/octet-stream"
    await storage_service.upload_bytes(
        bucket=settings.S3_BUCKET_ASSETS,
        object_key=object_key,
        body=content,
        content_type=content_type,
    )

    asset = Asset(
        kind="background",
        bucket=settings.S3_BUCKET_ASSETS,
        object_key=object_key,
        mime=content_type,
        size=len(content),
    )
    session.add(asset)
    await session.commit()
    await session.refresh(asset)

    signed_url = await storage_service.generate_download_url(
        bucket=asset.bucket, object_key=asset.object_key
    )
    return AssetOut.model_validate(asset).model_copy(update={"url": signed_url})


@router.get("/{asset_id}/content")
async def get_asset_content(
    asset_id: str, session: AsyncSession = Depends(get_session)
) -> Response:
    asset = await session.get(Asset, asset_id)
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    body, content_type = await storage_service.download_bytes(
        bucket=asset.bucket,
        object_key=asset.object_key,
    )
    return Response(
        content=body,
        media_type=content_type or asset.mime or "application/octet-stream",
        headers={
            "Cache-Control": "public, max-age=300",
        },
    )
