import pytest

from app.services.source_ingest import SourceIngestService


def test_extract_youtube_video_id_variants() -> None:
    service = SourceIngestService()
    assert (
        service._extract_youtube_video_id("https://youtu.be/dQw4w9WgXcQ")
        == "dQw4w9WgXcQ"
    )
    assert (
        service._extract_youtube_video_id(
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=43s"
        )
        == "dQw4w9WgXcQ"
    )
    assert (
        service._extract_youtube_video_id(
            "https://www.youtube.com/shorts/dQw4w9WgXcQ"
        )
        == "dQw4w9WgXcQ"
    )


def test_normalize_links_deduplicates_and_keeps_order() -> None:
    service = SourceIngestService()
    links = service._normalize_links(
        [
            "https://example.com/a",
            "https://example.com/a",
            "https://example.com/b",
            "",
        ]
    )
    assert links == ["https://example.com/a", "https://example.com/b"]


@pytest.mark.asyncio
async def test_prepare_text_payload_sets_source_text() -> None:
    service = SourceIngestService()
    payload = await service.prepare_payload(
        source_type="text",
        source_payload={"text": "  Hello world  "},
        language="EN",
    )
    assert payload["source_text"] == "Hello world"
    assert payload["text"] == "Hello world"
    assert payload["ingestion"]["mode"] == "text"
