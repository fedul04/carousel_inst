from __future__ import annotations

import logging
from typing import Iterable

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from app.core.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    def __init__(self) -> None:
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
            config=Config(signature_version="s3v4"),
        )
        public_endpoint = settings.S3_PUBLIC_ENDPOINT_URL or settings.S3_ENDPOINT_URL
        self.public_client = boto3.client(
            "s3",
            endpoint_url=public_endpoint,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
            config=Config(signature_version="s3v4"),
        )

    async def ensure_buckets(self, buckets: Iterable[str]) -> None:
        for bucket in buckets:
            self._ensure_bucket(bucket)

    def _ensure_bucket(self, bucket: str) -> None:
        try:
            self.client.head_bucket(Bucket=bucket)
        except ClientError:
            self.client.create_bucket(Bucket=bucket)

    async def upload_bytes(
        self, *, bucket: str, object_key: str, body: bytes, content_type: str
    ) -> None:
        self.client.put_object(
            Bucket=bucket, Key=object_key, Body=body, ContentType=content_type
        )

    async def generate_download_url(
        self, *, bucket: str, object_key: str, expires_seconds: int | None = None
    ) -> str:
        expires = expires_seconds or settings.S3_PRESIGNED_TTL_SECONDS
        return self.public_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": object_key},
            ExpiresIn=expires,
        )

    async def generate_internal_download_url(
        self, *, bucket: str, object_key: str, expires_seconds: int | None = None
    ) -> str:
        expires = expires_seconds or settings.S3_PRESIGNED_TTL_SECONDS
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": object_key},
            ExpiresIn=expires,
        )

    async def download_bytes(self, *, bucket: str, object_key: str) -> tuple[bytes, str | None]:
        response = self.client.get_object(Bucket=bucket, Key=object_key)
        body = response["Body"].read()
        content_type = response.get("ContentType")
        return body, content_type

    async def safe_init(self) -> None:
        try:
            await self.ensure_buckets(
                [settings.S3_BUCKET_ASSETS, settings.S3_BUCKET_EXPORTS]
            )
        except Exception as exc:  # pragma: no cover - non-critical on boot
            logger.warning("Unable to ensure S3 buckets on startup: %s", exc)


storage_service = StorageService()
