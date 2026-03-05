from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Any

from playwright.async_api import async_playwright

from app.core.config import settings
from app.models.carousel_design import CarouselDesign
from app.models.slide import Slide
from app.services.style_tokens import deep_merge_dicts, normalize_style_tokens

FONT_FAMILY_MAP: dict[str, str] = {
    "inter": '"Inter", "Segoe UI", Arial, sans-serif',
    "fira_code": '"Fira Code", "Consolas", "Courier New", monospace',
    "roboto_condensed": '"Roboto Condensed", "Arial Narrow", Arial, sans-serif',
    "jost": '"Jost", "Segoe UI", Arial, sans-serif',
    "caveat": '"Caveat", "Segoe UI", Arial, sans-serif',
    "source_sans_3": '"Source Sans 3", "Segoe UI", Arial, sans-serif',
}


class RenderService:
    async def render_slides(
        self,
        *,
        slides: list[Slide],
        design: CarouselDesign,
        output_dir: Path,
        image_format: str,
        asset_urls: dict[str, str] | None = None,
    ) -> list[Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        paths: list[Path] = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(args=["--no-sandbox"])
            page = await browser.new_page(
                viewport={
                    "width": settings.EXPORT_VIEWPORT_WIDTH,
                    "height": settings.EXPORT_VIEWPORT_HEIGHT,
                }
            )

            for index, slide in enumerate(slides, start=1):
                html_doc = self._slide_html(slide=slide, design=design, asset_urls=asset_urls)
                await page.set_content(html_doc, wait_until="networkidle")
                filename = f"slide_{index:02d}.{image_format}"
                file_path = output_dir / filename
                screenshot_type = "jpeg" if image_format == "jpg" else image_format
                await page.screenshot(
                    path=str(file_path), type=screenshot_type, full_page=False
                )
                paths.append(file_path)

            await browser.close()

        return paths

    def _slide_html(
        self,
        *,
        slide: Slide,
        design: CarouselDesign,
        asset_urls: dict[str, str] | None = None,
    ) -> str:
        cfg = self._resolve_slide_config(slide=slide, design=design, asset_urls=asset_urls)
        style_tokens = cfg["style_tokens"]
        title_tokens = style_tokens["title"]
        body_tokens = style_tokens["body"]
        title_size = self._fitted_font_size(
            base_size=float(title_tokens["size"]), text=slide.title, kind="title"
        )
        body_size = self._fitted_font_size(
            base_size=float(body_tokens["size"]), text=slide.body, kind="body"
        )

        title_html = self._render_rich_text(
            slide.title, title_tokens["case"], style_tokens["highlight_color"]
        )
        body_html = self._render_rich_text(
            slide.body, body_tokens["case"], style_tokens["highlight_color"]
        )

        footer = html.escape(slide.footer_cta or cfg["footer_text"])
        header = html.escape(cfg["header_text"])
        pattern_css = self._pattern_css(style_tokens)
        background_css = self._background_css(
            cfg["bg_type"], cfg["bg_value"], cfg["template"], style_tokens
        )
        overlay_alpha = self._overlay_alpha(cfg["bg_overlay"], style_tokens)
        text_color = self._text_color(cfg["template"])

        title_font = FONT_FAMILY_MAP.get(title_tokens["font"], FONT_FAMILY_MAP["inter"])
        body_font = FONT_FAMILY_MAP.get(body_tokens["font"], FONT_FAMILY_MAP["inter"])

        return f"""
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Caveat:wght@400;700&family=Fira+Code:wght@400;500;700&family=Inter:wght@400;500;700;800;900&family=Jost:wght@400;500;700;800&family=Roboto+Condensed:wght@400;500;700&family=Source+Sans+3:wght@400;500;700&display=swap" rel="stylesheet" />
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      width: {settings.EXPORT_VIEWPORT_WIDTH}px;
      height: {settings.EXPORT_VIEWPORT_HEIGHT}px;
      overflow: hidden;
      font-family: "Inter", "Segoe UI", Arial, sans-serif;
    }}
    .canvas {{
      position: relative;
      width: 100%;
      height: 100%;
      overflow: hidden;
      padding: {cfg["layout_padding"]}px;
      {background_css}
      color: {text_color};
      border-radius: 0;
    }}
    .pattern {{
      position: absolute;
      inset: 0;
      {pattern_css}
      pointer-events: none;
    }}
    .overlay {{
      position: absolute;
      inset: 0;
      background: rgba(0, 0, 0, {overlay_alpha});
      pointer-events: none;
    }}
    .content {{
      position: relative;
      z-index: 2;
      height: 100%;
      display: flex;
      flex-direction: column;
      gap: 24px;
    }}
    .header, .footer {{
      font-size: 30px;
      font-weight: 500;
      letter-spacing: 0.01em;
      opacity: 0.95;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-family: "Fira Code", "Consolas", "Courier New", monospace;
    }}
    .main {{
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 26px;
      justify-content: var(--justify);
      align-items: var(--align);
      text-align: var(--text-align);
    }}
    .title {{
      margin: 0;
      max-width: 100%;
      overflow-wrap: anywhere;
      word-break: break-word;
      font-family: {title_font};
      font-size: {title_size:.2f}px;
      line-height: {title_tokens["line_height"]};
      letter-spacing: {title_tokens["letter_spacing"]}px;
      font-weight: {title_tokens["weight"]};
      overflow: hidden;
      display: -webkit-box;
      -webkit-box-orient: vertical;
      -webkit-line-clamp: 4;
    }}
    .body {{
      margin: 0;
      max-width: 100%;
      overflow-wrap: anywhere;
      word-break: break-word;
      font-family: {body_font};
      font-size: {body_size:.2f}px;
      line-height: {body_tokens["line_height"]};
      letter-spacing: {body_tokens["letter_spacing"]}px;
      font-weight: {body_tokens["weight"]};
      overflow: hidden;
      display: -webkit-box;
      -webkit-box-orient: vertical;
      -webkit-line-clamp: 10;
    }}
    .hl {{
      color: {style_tokens["highlight_color"]};
      font-weight: 800;
    }}

    .align-x-left {{ --align: flex-start; --text-align: left; }}
    .align-x-center {{ --align: center; --text-align: center; }}
    .align-x-right {{ --align: flex-end; --text-align: right; }}
    .align-y-top {{ --justify: flex-start; }}
    .align-y-center {{ --justify: center; }}
    .align-y-bottom {{ --justify: flex-end; }}
  </style>
</head>
<body>
  <div class="canvas align-x-{cfg["align_x"]} align-y-{cfg["align_y"]}">
    <div class="pattern"></div>
    <div class="overlay"></div>
    <div class="content">
      {"<div class='header'><span>"+header+"</span><span>"+str(slide.order)+"</span></div>" if cfg["show_header"] else ""}
      <div class="main">
        <h1 class="title">{title_html}</h1>
        <p class="body">{body_html}</p>
      </div>
      {"<div class='footer'><span>"+footer+"</span><span>&rarr;</span></div>" if cfg["show_footer"] else ""}
    </div>
  </div>
</body>
</html>
"""

    def _resolve_slide_config(
        self,
        *,
        slide: Slide,
        design: CarouselDesign,
        asset_urls: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        overrides = slide.design_overrides or {}
        style_tokens = normalize_style_tokens(design.style_tokens)
        if isinstance(overrides.get("style_tokens"), dict):
            style_tokens = normalize_style_tokens(
                deep_merge_dicts(style_tokens, overrides["style_tokens"])
            )

        effective_bg_type = overrides.get("bg_type", design.bg_type)
        effective_bg_value = overrides.get("bg_value", design.bg_value)
        if (
            effective_bg_type == "image"
            and asset_urls
            and isinstance(style_tokens.get("background"), dict)
        ):
            image_asset_id = style_tokens["background"].get("image_asset_id")
            if isinstance(image_asset_id, str) and image_asset_id in asset_urls:
                effective_bg_value = asset_urls[image_asset_id]

        if (
            effective_bg_type == "image"
            and isinstance(effective_bg_value, str)
            and effective_bg_value.startswith("/")
        ):
            base = (settings.FRONTEND_ASSET_BASE_URL or settings.FRONTEND_ORIGIN).rstrip("/")
            effective_bg_value = f"{base}{effective_bg_value}"

        return {
            "template": overrides.get("template", design.template),
            "bg_type": effective_bg_type,
            "bg_value": effective_bg_value,
            "bg_overlay": float(overrides.get("bg_overlay", design.bg_overlay)),
            "layout_padding": int(overrides.get("layout_padding", design.layout_padding)),
            "align_x": overrides.get("align_x", design.align_x),
            "align_y": overrides.get("align_y", design.align_y),
            "show_header": (
                bool(overrides["show_header"])
                if isinstance(overrides.get("show_header"), bool)
                else design.show_header
            ),
            "show_footer": (
                bool(overrides["show_footer"])
                if isinstance(overrides.get("show_footer"), bool)
                else design.show_footer
            ),
            "header_text": overrides.get("header_text", design.header_text),
            "footer_text": overrides.get("footer_text", design.footer_text),
            "style_tokens": style_tokens,
        }

    @staticmethod
    def _overlay_alpha(base_overlay: float, style_tokens: dict[str, Any]) -> float:
        dimming = style_tokens.get("background", {}).get("dimming", {})
        dim_strength = float(dimming.get("strength", 0.0)) if dimming.get("enabled") else 0.0
        return max(0.0, min(1.0, base_overlay + dim_strength))

    @staticmethod
    def _is_dark_template(template: str) -> bool:
        return template in {
            "bold",
            "neon",
            "noir",
            "aurora",
            "synthwave",
            "matrix",
            "lava",
            "mono",
            "velvet",
            "blueprint",
            "cosmos",
            "ember",
            "graphite",
        }

    @classmethod
    def _text_color(cls, template: str) -> str:
        if cls._is_dark_template(template):
            return "#F8F9FB"
        return "#111319"

    @staticmethod
    def _hex_to_rgba(color: str, alpha: float) -> str:
        value = color.strip().lstrip("#")
        if len(value) == 3:
            value = "".join([char * 2 for char in value])
        if len(value) != 6:
            value = "3B37D2"
        r = int(value[0:2], 16)
        g = int(value[2:4], 16)
        b = int(value[4:6], 16)
        return f"rgba({r}, {g}, {b}, {max(0.0, min(1.0, alpha))})"

    def _pattern_css(self, style_tokens: dict[str, Any]) -> str:
        pattern = style_tokens.get("background", {}).get("pattern", {})
        if not pattern.get("enabled"):
            return "display: none;"

        pattern_type = pattern.get("type", "dots")
        opacity = float(pattern.get("opacity", 0.18))
        scale = float(pattern.get("scale", 1.0))
        scale = max(0.4, min(2.5, scale))
        color = self._hex_to_rgba(style_tokens.get("accent_color", "#3B37D2"), opacity)

        if pattern_type == "texture2":
            size = int(28 * scale)
            return (
                f"background-image: repeating-linear-gradient(45deg, {color} 0 1px, transparent 1px {size}px);"
            )
        if pattern_type == "squares":
            size = int(26 * scale)
            return (
                f"background-image: repeating-linear-gradient(0deg, {color} 0 1px, transparent 1px {size}px),"
                f" repeating-linear-gradient(90deg, {color} 0 1px, transparent 1px {size}px);"
            )
        if pattern_type == "lines":
            size = int(24 * scale)
            return (
                f"background-image: repeating-linear-gradient(90deg, {color} 0 1px, transparent 1px {size}px);"
            )
        if pattern_type == "grid":
            size = int(22 * scale)
            return (
                f"background-image: repeating-linear-gradient(0deg, {color} 0 1px, transparent 1px {size}px),"
                f" repeating-linear-gradient(90deg, {color} 0 1px, transparent 1px {size}px);"
            )
        if pattern_type == "bubbles":
            size = int(84 * scale)
            color_soft = self._hex_to_rgba(style_tokens.get("accent_color", "#3B37D2"), opacity * 0.65)
            return (
                "background-image: "
                f"radial-gradient(circle at 18% 22%, {color} 0 18px, transparent 19px),"
                f"radial-gradient(circle at 78% 30%, {color_soft} 0 14px, transparent 15px),"
                f"radial-gradient(circle at 62% 78%, {color} 0 20px, transparent 21px);"
                f" background-size: {size}px {size}px;"
            )

        size = int(24 * scale)
        return (
            f"background-image: radial-gradient(circle, {color} 0 1.5px, transparent 1.8px);"
            f" background-size: {size}px {size}px;"
        )

    @staticmethod
    def _background_css(
        bg_type: str, bg_value: str, template: str, style_tokens: dict[str, Any]
    ) -> str:
        if bg_type == "image":
            return (
                f"background-image: url('{bg_value}'); "
                "background-size: cover; background-position: center;"
            )

        if template == "bold":
            base = RenderService._resolve_template_base(bg_value, "#3B37D2")
            return f"background: {base};"
        if template == "minimal":
            return f"background: {bg_value or '#F4F1E9'};"
        if template == "neon":
            base = RenderService._resolve_template_base(bg_value, "#131A3A")
            accent = style_tokens.get("accent_color", "#3B37D2")
            glow = RenderService._hex_to_rgba(accent, 0.58)
            glow_soft = RenderService._hex_to_rgba(accent, 0.22)
            return (
                "background-image: "
                f"radial-gradient(circle at 18% 18%, {glow} 0 16%, transparent 48%),"
                f"radial-gradient(circle at 82% 74%, {glow_soft} 0 20%, transparent 55%),"
                f"linear-gradient(160deg, {base} 0%, #0d122b 100%);"
            )
        if template == "soft":
            base = RenderService._resolve_template_base(bg_value, "#E9EDF7")
            accent = style_tokens.get("accent_color", "#3B37D2")
            tint = RenderService._hex_to_rgba(accent, 0.22)
            return (
                "background-image: "
                f"radial-gradient(circle at 84% 16%, {tint} 0 28%, transparent 56%),"
                f"linear-gradient(165deg, {base} 0%, #ffffff 66%);"
            )
        if template == "noir":
            base = RenderService._resolve_template_base(bg_value, "#15171D")
            line = RenderService._hex_to_rgba("#FFFFFF", 0.08)
            return (
                f"background-color: {base};"
                "background-image: "
                "linear-gradient(180deg, rgba(255,255,255,0.06) 0%, rgba(0,0,0,0.18) 100%),"
                f"repeating-linear-gradient(90deg, {line} 0 1px, transparent 1px 34px);"
            )
        if template == "aurora":
            base = RenderService._resolve_template_base(bg_value, "#10293F")
            accent = style_tokens.get("accent_color", "#3B37D2")
            glow_a = RenderService._hex_to_rgba(accent, 0.48)
            glow_b = RenderService._hex_to_rgba("#64E8FF", 0.36)
            return (
                "background-image: "
                f"radial-gradient(circle at 18% 18%, {glow_b} 0 18%, transparent 52%),"
                f"radial-gradient(circle at 84% 74%, {glow_a} 0 22%, transparent 58%),"
                f"linear-gradient(160deg, #0b1b2b 0%, {base} 48%, #1d3f55 100%);"
            )
        if template == "sunset":
            base = RenderService._resolve_template_base(bg_value, "#FF955F")
            return (
                "background-image: "
                "radial-gradient(circle at 14% 20%, rgba(255,242,182,0.62) 0 20%, transparent 50%),"
                f"linear-gradient(160deg, #ffd26a 0%, {base} 42%, #ff6f7f 72%, #6f3b9d 100%);"
            )
        if template == "synthwave":
            base = RenderService._resolve_template_base(bg_value, "#1A103F")
            accent = style_tokens.get("accent_color", "#3B37D2")
            neon = RenderService._hex_to_rgba(accent, 0.4)
            return (
                "background-image: "
                "linear-gradient(180deg, rgba(255,255,255,0.05) 0%, rgba(0,0,0,0.46) 100%),"
                f"radial-gradient(circle at 78% 16%, {neon} 0 14%, transparent 44%),"
                f"linear-gradient(145deg, #2b174f 0%, {base} 52%, #0b0f2d 100%);"
            )
        if template == "paper":
            base = RenderService._resolve_template_base(bg_value, "#F7EADB")
            return (
                "background-image: "
                "repeating-linear-gradient(0deg, rgba(50,61,79,0.05) 0 1px, transparent 1px 28px),"
                f"linear-gradient(165deg, #fdf4e8 0%, {base} 56%, #efe0cc 100%);"
            )
        if template == "matrix":
            base = RenderService._resolve_template_base(bg_value, "#0D2F1F")
            grid = RenderService._hex_to_rgba("#86FFB5", 0.14)
            return (
                "background-image: "
                "linear-gradient(180deg, rgba(0,0,0,0.35) 0%, rgba(0,0,0,0.76) 100%),"
                f"repeating-linear-gradient(90deg, {grid} 0 1px, transparent 1px 26px),"
                f"linear-gradient(160deg, #0a1f15 0%, {base} 48%, #15492c 100%);"
            )
        if template == "candy":
            base = RenderService._resolve_template_base(bg_value, "#FF9D73")
            return (
                "background-image: "
                "radial-gradient(circle at 18% 16%, rgba(255,255,255,0.52) 0 16%, transparent 48%),"
                "radial-gradient(circle at 82% 72%, rgba(255,255,255,0.38) 0 18%, transparent 52%),"
                f"linear-gradient(150deg, #ff7db7 0%, {base} 38%, #ffd56c 72%, #8bc6ff 100%);"
            )
        if template == "lava":
            base = RenderService._resolve_template_base(bg_value, "#5E1F1A")
            return (
                "background-image: "
                "radial-gradient(circle at 18% 20%, rgba(255,197,112,0.34) 0 15%, transparent 42%),"
                "radial-gradient(circle at 86% 78%, rgba(255,82,82,0.24) 0 18%, transparent 50%),"
                f"linear-gradient(150deg, #2a1311 0%, {base} 42%, #b53b24 74%, #f26a2a 100%);"
            )
        if template == "frost":
            base = RenderService._resolve_template_base(bg_value, "#C9E8FF")
            return (
                "background-image: "
                "linear-gradient(180deg, rgba(255,255,255,0.36) 0%, rgba(255,255,255,0.08) 100%),"
                "radial-gradient(circle at 12% 18%, rgba(255,255,255,0.66) 0 18%, transparent 50%),"
                f"linear-gradient(160deg, #d9f3ff 0%, {base} 48%, #b1dcff 100%);"
            )
        if template == "mono":
            base = RenderService._resolve_template_base(bg_value, "#262833")
            return (
                "background-image: "
                "repeating-linear-gradient(90deg, rgba(255,255,255,0.08) 0 1px, transparent 1px 30px),"
                f"linear-gradient(165deg, #191a1f 0%, {base} 52%, #111217 100%);"
            )
        if template == "velvet":
            base = RenderService._resolve_template_base(bg_value, "#4F1F60")
            return (
                "background-image: "
                "radial-gradient(circle at 84% 16%, rgba(255,255,255,0.18) 0 16%, transparent 48%),"
                f"linear-gradient(145deg, #2e1038 0%, {base} 46%, #27102f 100%);"
            )
        if template == "blueprint":
            base = RenderService._resolve_template_base(bg_value, "#1B4A87")
            return (
                "background-image: "
                "repeating-linear-gradient(0deg, rgba(209,232,255,0.22) 0 1px, transparent 1px 26px),"
                "repeating-linear-gradient(90deg, rgba(209,232,255,0.2) 0 1px, transparent 1px 26px),"
                f"linear-gradient(165deg, #113463 0%, {base} 52%, #0f2a4f 100%);"
            )
        if template == "hologram":
            return (
                "background-image: "
                "linear-gradient(115deg, rgba(255,255,255,0.18) 0 12%, rgba(255,255,255,0) 12% 100%),"
                "linear-gradient(145deg, #6e57ff 0%, #2fd4ff 34%, #6dffb6 62%, #f9ff7a 100%);"
            )
        if template == "cosmos":
            base = RenderService._resolve_template_base(bg_value, "#17173A")
            return (
                "background-image: "
                "radial-gradient(circle at 18% 14%, rgba(121,156,255,0.54) 0 18%, transparent 52%),"
                "radial-gradient(circle at 84% 76%, rgba(199,110,255,0.46) 0 20%, transparent 56%),"
                f"linear-gradient(160deg, #090b1b 0%, {base} 46%, #0f2c55 100%);"
            )
        if template == "ember":
            base = RenderService._resolve_template_base(bg_value, "#4A1816")
            return (
                "background-image: "
                "radial-gradient(circle at 16% 18%, rgba(255,177,88,0.5) 0 16%, transparent 48%),"
                "radial-gradient(circle at 82% 74%, rgba(255,75,75,0.34) 0 20%, transparent 54%),"
                f"linear-gradient(150deg, #250f0f 0%, {base} 48%, #8a2e24 100%);"
            )
        if template == "oasis":
            base = RenderService._resolve_template_base(bg_value, "#BDF3E7")
            return (
                "background-image: "
                "radial-gradient(circle at 88% 18%, rgba(255,255,255,0.45) 0 20%, transparent 52%),"
                f"linear-gradient(160deg, #d8fff7 0%, {base} 46%, #94decb 100%);"
            )
        if template == "graphite":
            base = RenderService._resolve_template_base(bg_value, "#252A36")
            return (
                "background-image: "
                "repeating-linear-gradient(0deg, rgba(255,255,255,0.06) 0 1px, transparent 1px 26px),"
                f"linear-gradient(165deg, #17191f 0%, {base} 54%, #0f1116 100%);"
            )
        if template == "citrus":
            base = RenderService._resolve_template_base(bg_value, "#D3F45A")
            return (
                "background-image: "
                "radial-gradient(circle at 14% 22%, rgba(255,255,255,0.56) 0 14%, transparent 44%),"
                f"linear-gradient(158deg, #f9f871 0%, {base} 44%, #8de86e 100%);"
            )
        if template == "vintage":
            base = RenderService._resolve_template_base(bg_value, "#E9D7B7")
            return (
                "background-image: "
                "repeating-linear-gradient(90deg, rgba(58,39,20,0.06) 0 1px, transparent 1px 30px),"
                f"linear-gradient(165deg, #f4e6cc 0%, {base} 52%, #d8bf98 100%);"
            )
        return f"background: {bg_value or '#F5ED4D'};"

    @staticmethod
    def _resolve_template_base(bg_value: str, fallback: str) -> str:
        value = (bg_value or "").strip().lower()
        if not value or value in {"#f4f1e9", "#f5ed4d"}:
            return fallback
        return bg_value

    def _render_rich_text(self, raw: str, case_mode: str, highlight_color: str) -> str:
        parts: list[str] = []
        cursor = 0
        pattern = re.compile(r"\*\*(.+?)\*\*", flags=re.DOTALL)

        for match in pattern.finditer(raw):
            if match.start() > cursor:
                parts.append(self._escape_with_breaks(self._apply_case(raw[cursor:match.start()], case_mode)))
            highlighted = self._escape_with_breaks(
                self._apply_case(match.group(1), case_mode)
            )
            parts.append(
                f"<span class='hl' style='color:{html.escape(highlight_color)}'>{highlighted}</span>"
            )
            cursor = match.end()

        if cursor < len(raw):
            parts.append(self._escape_with_breaks(self._apply_case(raw[cursor:], case_mode)))

        if not parts:
            return "&nbsp;"
        return "".join(parts)

    @staticmethod
    def _apply_case(text: str, case_mode: str) -> str:
        if case_mode == "upper":
            return text.upper()
        if case_mode == "lower":
            return text.lower()
        # "Aa" mode means preserve original casing.
        return text

    @staticmethod
    def _fitted_font_size(*, base_size: float, text: str, kind: str) -> float:
        plain = re.sub(r"\*\*(.+?)\*\*", r"\1", text or "", flags=re.DOTALL).strip()
        lines = [line.strip() for line in re.split(r"\n+", plain) if line.strip()]
        words = [word for word in re.split(r"\s+", plain) if word]
        longest_word = max((len(word) for word in words), default=0)
        line_count = max(1, len(lines))
        length = len(plain)

        factor = 1.0
        if kind == "title":
            score = length + (longest_word * 1.9) + (line_count * 34)
            if score > 220:
                factor = 0.58
            elif score > 188:
                factor = 0.66
            elif score > 154:
                factor = 0.74
            elif score > 126:
                factor = 0.84
        else:
            score = length + (longest_word * 1.5) + (line_count * 18)
            if score > 760:
                factor = 0.62
            elif score > 620:
                factor = 0.7
            elif score > 500:
                factor = 0.78
            elif score > 390:
                factor = 0.86
        return max(11.0 if kind == "body" else 14.0, base_size * factor)

    @staticmethod
    def _escape_with_breaks(text: str) -> str:
        return html.escape(text).replace("\n", "<br />")


render_service = RenderService()
