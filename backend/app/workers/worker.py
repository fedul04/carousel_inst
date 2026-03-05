import asyncio
import logging

from app.core.config import settings
from app.services.export import export_service
from app.services.generation import generation_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def worker_loop() -> None:
    logger.info("Worker started with poll interval %.1fs", settings.WORKER_POLL_INTERVAL_SECONDS)
    while True:
        handled_generation = await generation_service.process_queued_once()
        handled_export = await export_service.process_queued_once()
        if not handled_generation and not handled_export:
            await asyncio.sleep(settings.WORKER_POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    asyncio.run(worker_loop())

