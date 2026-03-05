from __future__ import annotations

import asyncio
import re
from typing import Any
from urllib.parse import parse_qs, urlparse

import httpx
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi

MAX_SOURCE_TEXT_CHARS = 14_000
MAX_WEB_TEXT_CHARS = 4_200
MAX_LINKS_TO_FETCH = 5


class SourceIngestService:
    async def prepare_payload(
        self,
        *,
        source_type: str,
        source_payload: dict[str, Any] | None,
        language: str,
    ) -> dict[str, Any]:
        payload = dict(source_payload or {})
        normalized_type = (source_type or "text").lower()
        if normalized_type == "video":
            return await self._prepare_video_payload(payload=payload, language=language)
        if normalized_type == "links":
            return await self._prepare_links_payload(payload=payload)
        return self._prepare_text_payload(payload=payload)

    def _prepare_text_payload(self, *, payload: dict[str, Any]) -> dict[str, Any]:
        text = self._clean_text(payload.get("text") or payload.get("source_text") or "")
        if not text:
            text = self._clean_text(payload.get("notes") or "")
        payload["text"] = text
        payload["source_text"] = text
        payload.setdefault("ingestion", {})
        payload["ingestion"]["mode"] = "text"
        payload["ingestion"]["source_text_chars"] = len(text)
        return payload

    async def _prepare_video_payload(
        self, *, payload: dict[str, Any], language: str
    ) -> dict[str, Any]:
        video_url = self._clean_text(payload.get("video_url") or payload.get("url") or "")
        notes = self._clean_text(payload.get("notes") or "")
        extracted_text = ""
        ingest_meta: dict[str, Any] = {"mode": "video", "video_url": video_url}

        if self._is_web_url(video_url):
            youtube_video_id = self._extract_youtube_video_id(video_url)
            if youtube_video_id:
                ingest_meta["youtube_video_id"] = youtube_video_id
                ingest_meta["youtube_transcript_attempted"] = True
                transcript = await self._fetch_youtube_transcript(
                    youtube_video_id=youtube_video_id,
                    language=language,
                )
                if transcript:
                    extracted_text = transcript
                    ingest_meta["source"] = "youtube_transcript"
                    ingest_meta["youtube_transcript_found"] = True
                    ingest_meta["youtube_transcript_chars"] = len(transcript)
                else:
                    ingest_meta["youtube_transcript_found"] = False

            if not extracted_text:
                page_text = await self._fetch_page_text(video_url)
                if page_text:
                    extracted_text = page_text
                    ingest_meta["source"] = "web_page_text"

        combined = self._join_blocks(
            [
                extracted_text,
                notes,
            ],
            limit=MAX_SOURCE_TEXT_CHARS,
        )
        if not combined:
            combined = self._truncate(notes or video_url, MAX_SOURCE_TEXT_CHARS)

        payload["video_url"] = video_url
        payload["notes"] = notes
        payload["source_text"] = combined
        ingest_meta["source_text_chars"] = len(combined)
        payload["ingestion"] = ingest_meta
        return payload

    async def _prepare_links_payload(self, *, payload: dict[str, Any]) -> dict[str, Any]:
        links = self._normalize_links(payload.get("links"))
        notes = self._clean_text(payload.get("notes") or "")
        digest_blocks: list[str] = []
        fetched = 0

        for link in links[:MAX_LINKS_TO_FETCH]:
            if not self._is_web_url(link):
                continue
            page_text = await self._fetch_page_text(link)
            if not page_text:
                continue
            fetched += 1
            digest_blocks.append(f"URL: {link}\n{page_text}")

        if not digest_blocks and links:
            digest_blocks.append("Links:\n" + "\n".join(links))

        combined = self._join_blocks([notes, *digest_blocks], limit=MAX_SOURCE_TEXT_CHARS)
        if not combined:
            combined = self._truncate("\n".join(links), MAX_SOURCE_TEXT_CHARS)

        payload["links"] = links
        payload["notes"] = notes
        payload["source_text"] = combined
        payload["ingestion"] = {
            "mode": "links",
            "links_total": len(links),
            "links_fetched": fetched,
            "source_text_chars": len(combined),
        }
        return payload

    async def _fetch_page_text(self, url: str) -> str:
        try:
            async with httpx.AsyncClient(
                timeout=15.0,
                follow_redirects=True,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/124.0.0.0 Safari/537.36"
                    )
                },
            ) as client:
                response = await client.get(url)
        except Exception:
            return ""

        if response.status_code >= 400:
            return ""

        content_type = (response.headers.get("content-type") or "").lower()
        body = response.text or ""
        if "html" not in content_type and "xml" not in content_type:
            return self._truncate(self._clean_text(body), MAX_WEB_TEXT_CHARS)

        soup = BeautifulSoup(body, "html.parser")
        for tag in soup(["script", "style", "noscript", "svg", "canvas"]):
            tag.decompose()

        candidates: list[str] = []
        title = self._clean_text(soup.title.string if soup.title else "")
        if title:
            candidates.append(title)

        description = ""
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            description = self._clean_text(meta_desc.get("content", ""))
        if not description:
            og_desc = soup.find("meta", attrs={"property": "og:description"})
            if og_desc and og_desc.get("content"):
                description = self._clean_text(og_desc.get("content", ""))
        if description:
            candidates.append(description)

        text_nodes = soup.select("article p, article li, main p, main li, h1, h2, h3, p, li")
        for node in text_nodes:
            text = self._clean_text(node.get_text(" ", strip=True))
            if len(text) < 40:
                continue
            candidates.append(text)
            if len(candidates) >= 18:
                break

        dedup: list[str] = []
        seen: set[str] = set()
        for item in candidates:
            key = item.lower()
            if key in seen:
                continue
            seen.add(key)
            dedup.append(item)

        return self._truncate("\n".join(dedup), MAX_WEB_TEXT_CHARS)

    async def _fetch_youtube_transcript(
        self, *, youtube_video_id: str, language: str
    ) -> str:
        preferred_languages = self._preferred_transcript_languages(language)

        def _fetch_sync() -> list[dict[str, Any]]:
            return YouTubeTranscriptApi.get_transcript(
                youtube_video_id,
                languages=preferred_languages,
            )

        try:
            items = await asyncio.to_thread(_fetch_sync)
        except Exception:
            return ""

        text = self._clean_text(" ".join(str(item.get("text", "")) for item in items))
        return self._truncate(text, MAX_SOURCE_TEXT_CHARS)

    @staticmethod
    def _preferred_transcript_languages(language: str) -> list[str]:
        normalized = (language or "").strip().lower()
        if normalized == "ru":
            return ["ru", "ru-RU", "en", "en-US", "fr"]
        if normalized == "fr":
            return ["fr", "fr-FR", "en", "en-US", "ru"]
        return ["en", "en-US", "ru", "fr"]

    @staticmethod
    def _extract_youtube_video_id(url: str) -> str | None:
        parsed = urlparse(url)
        host = (parsed.netloc or "").lower()
        path = parsed.path or ""

        if "youtu.be" in host:
            candidate = path.strip("/").split("/")[0]
            if re.fullmatch(r"[A-Za-z0-9_-]{11}", candidate):
                return candidate

        if "youtube.com" in host or "m.youtube.com" in host:
            query_video = parse_qs(parsed.query).get("v", [None])[0]
            if query_video and re.fullmatch(r"[A-Za-z0-9_-]{11}", query_video):
                return query_video

            for prefix in ("/embed/", "/shorts/", "/live/"):
                if prefix in path:
                    candidate = path.split(prefix, maxsplit=1)[1].split("/")[0]
                    if re.fullmatch(r"[A-Za-z0-9_-]{11}", candidate):
                        return candidate

        return None

    @staticmethod
    def _is_web_url(value: str) -> bool:
        if not value:
            return False
        parsed = urlparse(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)

    def _normalize_links(self, raw_links: Any) -> list[str]:
        if isinstance(raw_links, str):
            candidate_links = [line.strip() for line in raw_links.splitlines()]
        elif isinstance(raw_links, list):
            candidate_links = [self._clean_text(item) for item in raw_links]
        else:
            candidate_links = []

        links: list[str] = []
        for link in candidate_links:
            if not link:
                continue
            if link in links:
                continue
            links.append(link)
        return links

    @staticmethod
    def _clean_text(value: Any) -> str:
        text = str(value or "")
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @staticmethod
    def _join_blocks(blocks: list[str], *, limit: int) -> str:
        parts = [part.strip() for part in blocks if part and part.strip()]
        if not parts:
            return ""
        return SourceIngestService._truncate("\n\n".join(parts), limit)

    @staticmethod
    def _truncate(value: str, limit: int) -> str:
        if len(value) <= limit:
            return value
        return value[: limit - 3].rstrip() + "..."


source_ingest_service = SourceIngestService()
