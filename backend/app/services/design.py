from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from app.schemas.design import DesignPatch
from app.services.style_tokens import deep_merge_dicts, normalize_style_tokens

if TYPE_CHECKING:
    from app.models.carousel_design import CarouselDesign


def apply_design_patch(design: "CarouselDesign", patch: DesignPatch) -> None:
    if patch.template is not None:
        design.template = patch.template
    if patch.bg is not None:
        design.bg_type = patch.bg.type
        design.bg_value = patch.bg.value
        design.bg_overlay = patch.bg.overlay
    if patch.layout is not None:
        design.layout_padding = patch.layout.padding
        design.align_x = patch.layout.align_x
        design.align_y = patch.layout.align_y
    if patch.header is not None:
        design.show_header = patch.header.show
        design.header_text = patch.header.text
    if patch.footer is not None:
        design.show_footer = patch.footer.show
        design.footer_text = patch.footer.text

    current_tokens = normalize_style_tokens(getattr(design, "style_tokens", None))
    if patch.style_tokens is not None:
        incoming = patch.style_tokens.model_dump(exclude_none=True)
        merged = deep_merge_dicts(current_tokens, incoming)
        design.style_tokens = normalize_style_tokens(merged)
    else:
        design.style_tokens = current_tokens

    if patch.apply_to_all:
        design.apply_all_updated_at = datetime.now(timezone.utc)


def extract_apply_to_all_overrides(patch: DesignPatch) -> dict[str, Any]:
    updates: dict[str, Any] = {}
    if patch.template is not None:
        updates["template"] = patch.template
    if patch.bg is not None:
        updates["bg_type"] = patch.bg.type
        updates["bg_value"] = patch.bg.value
        updates["bg_overlay"] = patch.bg.overlay
    if patch.style_tokens is not None:
        updates["style_tokens"] = patch.style_tokens.model_dump(exclude_none=True)
    return updates


def merge_slide_overrides(
    current: dict[str, Any] | None, patch: dict[str, Any]
) -> dict[str, Any]:
    result = dict(current or {})
    for key, value in patch.items():
        if (
            key == "style_tokens"
            and isinstance(value, dict)
            and isinstance(result.get("style_tokens"), dict)
        ):
            result["style_tokens"] = deep_merge_dicts(result["style_tokens"], value)
        else:
            result[key] = value
    return result
