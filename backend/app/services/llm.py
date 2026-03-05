from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from openai import AsyncOpenAI

from app.core.config import settings
from app.schemas.llm import GeneratedArtifacts, GeneratedSlide, GeneratedSlidesSchema
from app.services.token_estimator import estimate_tokens


@dataclass
class LLMUsage:
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


class LLMService:
    def __init__(self) -> None:
        self._client: AsyncOpenAI | None = None
        if settings.LLM_API_KEY:
            self._client = AsyncOpenAI(
                api_key=settings.LLM_API_KEY,
                base_url=settings.LLM_BASE_URL,
                timeout=120.0,
            )

    async def generate_slides(
        self,
        *,
        source_payload: dict[str, Any],
        language: str,
        slides_count: int,
        style_hint: str | None,
    ) -> tuple[GeneratedSlidesSchema, LLMUsage]:
        if not self._client:
            return self._mock_generate(
                source_payload=source_payload,
                language=language,
                slides_count=slides_count,
                style_hint=style_hint,
            )

        prompt = self._build_prompt(
            source_payload=source_payload,
            language=language,
            slides_count=slides_count,
            style_hint=style_hint,
        )

        completion = await self._client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You generate Instagram carousel slides and creative artifacts. "
                        "Return valid JSON only. Keep text concise and readable on cards."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.45,
            max_tokens=settings.LLM_MAX_OUTPUT_TOKENS,
            response_format={"type": "json_object"},
        )

        content = completion.choices[0].message.content or ""
        payload = self._extract_json(content)
        slides = GeneratedSlidesSchema.model_validate(payload)
        usage = LLMUsage(
            prompt_tokens=getattr(completion.usage, "prompt_tokens", None),
            completion_tokens=getattr(completion.usage, "completion_tokens", None),
            total_tokens=getattr(completion.usage, "total_tokens", None),
        )
        return slides, usage

    def _mock_generate(
        self,
        *,
        source_payload: dict[str, Any],
        language: str,
        slides_count: int,
        style_hint: str | None,
    ) -> tuple[GeneratedSlidesSchema, LLMUsage]:
        source_text = (
            source_payload.get("text")
            or source_payload.get("source_text")
            or source_payload.get("video_url")
            or source_payload.get("notes")
            or "Main idea"
        )
        sentences = [s.strip() for s in re.split(r"[.!?]\s+", source_text) if s.strip()]
        if not sentences:
            sentences = ["Key point"]

        slides: list[GeneratedSlide] = []
        for index in range(slides_count):
            body = sentences[index % len(sentences)]
            if style_hint:
                body = f"{body}\n\nStyle hint: {style_hint[:120]}"
            if language == "RU":
                title = f"\u0421\u043b\u0430\u0439\u0434 {index + 1}"
                footer = "\u041f\u043e\u0434\u0440\u043e\u0431\u043d\u0435\u0435 \u0432 \u043f\u0440\u043e\u0444\u0438\u043b\u0435"
            elif language == "FR":
                title = f"Diapositive {index + 1}"
                footer = "Voir le profil"
            else:
                title = f"Slide {index + 1}"
                footer = "See profile for more"

            slides.append(
                GeneratedSlide(
                    order=index + 1,
                    title=title,
                    body=body[:900],
                    footer_cta=footer,
                )
            )

        artifacts = self._mock_artifacts(
            source_text=source_text,
            language=language,
            style_hint=style_hint,
            slides=slides,
        )

        usage = LLMUsage(
            prompt_tokens=estimate_tokens(source_text, style_hint),
            completion_tokens=estimate_tokens(
                " ".join(slide.body for slide in slides),
                " ".join(artifacts.hook_variants),
                " ".join(artifacts.hashtags),
                " ".join(artifacts.opening_lines),
                " ".join(artifacts.post_caption_variants),
            ),
            total_tokens=estimate_tokens(
                source_text,
                style_hint,
                " ".join(slide.body for slide in slides),
                " ".join(artifacts.hook_variants),
                " ".join(artifacts.hashtags),
                " ".join(artifacts.opening_lines),
                " ".join(artifacts.post_caption_variants),
            ),
        )
        return GeneratedSlidesSchema(slides=slides, artifacts=artifacts), usage

    def _build_prompt(
        self,
        *,
        source_payload: dict[str, Any],
        language: str,
        slides_count: int,
        style_hint: str | None,
    ) -> str:
        source_text = source_payload.get("text") or source_payload.get("source_text")
        video_url = source_payload.get("video_url")
        links = source_payload.get("links")
        notes = source_payload.get("notes")

        return (
            "Generate carousel slides with strict JSON output.\n\n"
            f"language={language}\n"
            f"slides_count={slides_count}\n"
            f"source_text={source_text or ''}\n"
            f"video_url={video_url or ''}\n"
            f"links={links or []}\n"
            f"notes={notes or ''}\n"
            f"style_hint={style_hint or ''}\n\n"
            "Rules:\n"
            "- Return object with keys `slides` and `artifacts`.\n"
            "- `slides` is array of objects: order, title, body, footer_cta.\n"
            "- `artifacts` is object with keys: summary, hook_variants, title_variants, "
            "cta_variants, opening_lines, post_caption_variants, image_prompts, "
            "audience_pains, hashtags, keywords, visual_directions.\n"
            "- order starts at 1 and increments by 1.\n"
            "- title max 70 chars.\n"
            "- body max 350 chars.\n"
            "- footer_cta optional max 60 chars.\n"
            "- hook/title/cta/opening/caption lists: 3-6 concise variants each.\n"
            "- image_prompts: 3-6 visual prompts for image generation.\n"
            "- audience_pains: 3-6 concrete pain points the post solves.\n"
            "- hashtags list: 6-12 short tags without #.\n"
            "- keywords list: 6-12 entries.\n"
            "- visual_directions list: 3-6 concise creative prompts.\n"
            "- Keep content meaningful and concise.\n"
        )

    def _mock_artifacts(
        self,
        *,
        source_text: str,
        language: str,
        style_hint: str | None,
        slides: list[GeneratedSlide],
    ) -> GeneratedArtifacts:
        clean = re.sub(r"\s+", " ", source_text).strip()
        summary = clean[:280] if clean else "Main idea"

        words = re.findall(r"[A-Za-z\u0400-\u04FF0-9]{4,}", clean)
        keywords: list[str] = []
        seen: set[str] = set()
        for word in words:
            low = word.lower()
            if low in seen:
                continue
            seen.add(low)
            keywords.append(word)
            if len(keywords) >= 12:
                break
        if not keywords:
            keywords = ["automation", "content", "growth"]

        if language == "RU":
            hooks = [
                "\u041f\u0435\u0440\u0435\u0441\u0442\u0430\u043d\u044c\u0442\u0435 \u0442\u0435\u0440\u044f\u0442\u044c \u0432\u0440\u0435\u043c\u044f \u043d\u0430 \u0440\u0443\u0442\u0438\u043d\u0443",
                "\u0427\u0442\u043e \u0438\u0437\u043c\u0435\u043d\u0438\u0442\u0441\u044f \u0443\u0436\u0435 \u0437\u0430 7 \u0434\u043d\u0435\u0439",
                "\u041f\u043e\u0448\u0430\u0433\u043e\u0432\u044b\u0439 \u043f\u043b\u0430\u043d \u0431\u0435\u0437 \u0432\u043e\u0434\u044b",
                "\u041a\u0435\u0439\u0441 \u0441 \u0438\u0437\u043c\u0435\u0440\u0438\u043c\u044b\u043c \u0440\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442\u043e\u043c",
            ]
            ctas = [
                "\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u0435, \u0447\u0442\u043e\u0431\u044b \u0432\u043d\u0435\u0434\u0440\u0438\u0442\u044c \u0441\u0435\u0433\u043e\u0434\u043d\u044f",
                "\u041e\u0442\u043f\u0440\u0430\u0432\u044c\u0442\u0435 \u0432 \u0440\u0430\u0431\u043e\u0447\u0438\u0439 \u0447\u0430\u0442",
                "\u0417\u0430\u0431\u0435\u0440\u0438\u0442\u0435 \u0448\u0430\u0431\u043b\u043e\u043d \u0438\u0437 \u043f\u0440\u043e\u0444\u0438\u043b\u044f",
                "\u041f\u0440\u043e\u0442\u0435\u0441\u0442\u0438\u0440\u0443\u0439\u0442\u0435 \u043d\u0430 \u043e\u0434\u043d\u043e\u043c \u043f\u0440\u043e\u0446\u0435\u0441\u0441\u0435",
            ]
            visuals = [
                "\u041a\u0440\u0443\u043f\u043d\u0430\u044f \u0442\u0438\u043f\u043e\u0433\u0440\u0430\u0444\u0438\u043a\u0430 + \u043a\u043e\u043d\u0442\u0440\u0430\u0441\u0442\u043d\u044b\u0439 \u0430\u043a\u0446\u0435\u043d\u0442",
                "\u0421\u0435\u0442\u043e\u0447\u043d\u044b\u0439 \u0444\u043e\u043d \u0441 \u043d\u0430\u043f\u0440\u0430\u0432\u043b\u044f\u044e\u0449\u0438\u043c\u0438 \u043b\u0438\u043d\u0438\u044f\u043c\u0438",
                "\u041c\u044f\u0433\u043a\u0438\u0435 glow-\u043f\u044f\u0442\u043d\u0430 \u043d\u0430 \u0442\u0435\u043c\u043d\u043e\u0439 \u0431\u0430\u0437\u0435",
                "\u041c\u0438\u043d\u0438\u043c\u0430\u043b\u0438\u0437\u043c \u0441 \u043e\u0434\u043d\u0438\u043c \u0446\u0432\u0435\u0442\u043e\u0432\u044b\u043c \u0430\u043a\u0446\u0435\u043d\u0442\u043e\u043c",
            ]
            opening_lines = [
                "\u0415\u0441\u043b\u0438 \u0432\u0430\u0448 \u0434\u0435\u043d\u044c \u0443\u0442\u043e\u043f\u0430\u0435\u0442 \u0432 \u0440\u0443\u0442\u0438\u043d\u0435, \u044d\u0442\u043e \u0434\u043b\u044f \u0432\u0430\u0441",
                "\u041e\u0434\u0438\u043d \u043f\u0440\u043e\u0441\u0442\u043e\u0439 \u0444\u0440\u0435\u0439\u043c\u0432\u043e\u0440\u043a, \u043a\u043e\u0442\u043e\u0440\u044b\u0439 \u044d\u043a\u043e\u043d\u043e\u043c\u0438\u0442 \u0447\u0430\u0441\u044b",
                "\u0412\u043d\u0435\u0434\u0440\u0438\u0442\u0435 \u044d\u0442\u043e \u0437\u0430 1 \u043d\u0435\u0434\u0435\u043b\u044e \u0431\u0435\u0437 \u043d\u0430\u043d\u0438\u043c\u0430\u043d\u0438\u044f \u043a\u043e\u043c\u0430\u043d\u0434\u044b",
            ]
            captions = [
                "\u0420\u0430\u0437\u0431\u043e\u0440 \u043f\u043e \u0448\u0430\u0433\u0430\u043c: \u0447\u0442\u043e \u0434\u0435\u043b\u0435\u0433\u0438\u0440\u043e\u0432\u0430\u0442\u044c AI \u0443\u0436\u0435 \u0441\u0435\u0433\u043e\u0434\u043d\u044f.",
                "\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u0435 \u043f\u043e\u0441\u0442 \u0438 \u043f\u0440\u043e\u0439\u0434\u0438\u0442\u0435 \u0447\u0435\u043a-\u043b\u0438\u0441\u0442 \u043a \u043a\u043e\u043d\u0446\u0443 \u0434\u043d\u044f.",
                "\u0413\u043b\u0430\u0432\u043d\u043e\u0435 \u043f\u0440\u0430\u0432\u0438\u043b\u043e: \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0437\u0438\u0440\u0443\u0435\u043c \u0442\u043e, \u0447\u0442\u043e \u043f\u043e\u0432\u0442\u043e\u0440\u044f\u0435\u0442\u0441\u044f.",
            ]
            pains = [
                "\u041d\u0435 \u0445\u0432\u0430\u0442\u0430\u0435\u0442 \u0432\u0440\u0435\u043c\u0435\u043d\u0438 \u043d\u0430 \u0441\u0442\u0440\u0430\u0442\u0435\u0433\u0438\u044e",
                "\u041a\u043e\u043d\u0442\u0435\u043d\u0442 \u0434\u0435\u043b\u0430\u0435\u0442\u0441\u044f \u0434\u043e\u043b\u0433\u043e \u0438 \u043d\u0435\u0440\u043e\u0432\u043d\u043e",
                "\u041a\u043e\u043c\u0430\u043d\u0434\u0430 \u0442\u043e\u043d\u0435\u0442 \u0432 \u0440\u0443\u0447\u043d\u044b\u0445 \u0437\u0430\u0434\u0430\u0447\u0430\u0445",
            ]
            image_prompts = [
                "Editorial poster, bold sans-serif typography, diagonal grid, high contrast, clean layout",
                "Modern AI workflow board, glowing nodes, dark gradient background, minimalist style",
                "Business process map with accents, geometric blocks, print-ready carousel composition",
            ]
            hashtags = [
                "автоматизация",
                "бизнес",
                "ai",
                "маркетинг",
                "контент",
                "эффективность",
                "стратегия",
                "процессы",
            ]
        elif language == "FR":
            hooks = [
                "Arretez les taches repetitives",
                "Ce qui change en 7 jours",
                "Methode simple et concrete",
                "Framework pret a appliquer",
            ]
            ctas = [
                "Enregistrez ce carrousel",
                "Partagez avec votre equipe",
                "Testez une etape aujourd'hui",
                "Appliquez ce framework maintenant",
            ]
            visuals = [
                "Typographie forte + contraste net",
                "Degrades lumineux et structure claire",
                "Grille editoriale minimaliste",
                "Palette froide avec un accent chaud",
            ]
            opening_lines = [
                "Si vos journees disparaissent dans l'operationnel, ce plan est pour vous",
                "Une methode simple pour produire plus vite sans sacrifier la qualite",
                "Passez de l'idee au contenu publie en une semaine",
            ]
            captions = [
                "Voici un cadre concret pour accelerer votre creation de contenu.",
                "Sauvegardez ce post et appliquez une etape des aujourd'hui.",
                "Le principe cle: automatiser ce qui se repete chaque semaine.",
            ]
            pains = [
                "Manque de temps pour la strategie",
                "Production de contenu trop lente",
                "Charge operationnelle trop elevee",
            ]
            image_prompts = [
                "Clean French editorial design, typographic hierarchy, soft gradients, modern business style",
                "AI productivity concept, structured grid, minimalist shapes, premium look",
                "Carousel cover with bold heading and refined accent color, social media ready",
            ]
            hashtags = [
                "automatisation",
                "business",
                "ia",
                "marketing",
                "productivite",
                "strategie",
                "contenu",
            ]
        else:
            hooks = [
                "Stop wasting hours on repetitive work",
                "What changes in just 7 days",
                "A practical framework you can copy",
                "How teams scale this workflow",
            ]
            ctas = [
                "Save this and apply today",
                "Share with your team",
                "Try one step right now",
                "Use this as your weekly playbook",
            ]
            visuals = [
                "Bold typography with high contrast",
                "Soft glow gradients on dark base",
                "Grid-backed editorial composition",
                "Minimal card with one strong accent",
            ]
            opening_lines = [
                "If your week disappears into repetitive tasks, this is for you",
                "A simple framework to speed up content production",
                "Implement this in one week without a bigger team",
            ]
            captions = [
                "A step-by-step framework to automate repetitive content workflows.",
                "Save this post and apply one part today.",
                "The core rule: automate what repeats every week.",
            ]
            pains = [
                "No time left for strategy work",
                "Content output is inconsistent",
                "Manual operations overload the team",
            ]
            image_prompts = [
                "Editorial social carousel, high-contrast typography, modern geometric layout, premium startup branding",
                "AI automation concept art, dark gradient with neon accents, clean composition, no clutter",
                "Minimal business design, grid background, bold heading area, optimized for 4:5 post",
            ]
            hashtags = [
                "automation",
                "ai",
                "business",
                "marketing",
                "productivity",
                "content",
                "workflows",
            ]

        if style_hint:
            visuals = [f"{item} ({style_hint[:46]})" for item in visuals]
            image_prompts = [f"{item}. Style hint: {style_hint[:46]}" for item in image_prompts]

        return GeneratedArtifacts(
            summary=summary,
            hook_variants=hooks[:6],
            title_variants=[slide.title for slide in slides[:6]],
            cta_variants=ctas[:6],
            opening_lines=opening_lines[:6],
            post_caption_variants=captions[:6],
            image_prompts=image_prompts[:6],
            audience_pains=pains[:6],
            hashtags=hashtags[:12],
            keywords=keywords[:12],
            visual_directions=visuals[:6],
        )

    @staticmethod
    def _extract_json(raw: str) -> dict[str, Any]:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            start = raw.find("{")
            end = raw.rfind("}")
            if start >= 0 and end > start:
                return json.loads(raw[start : end + 1])
            raise


llm_service = LLMService()
