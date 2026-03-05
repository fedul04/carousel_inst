from app.schemas.design import (
    BackgroundSettings,
    DesignPatch,
    StyleTokensPatch,
    TypographyTokensPatch,
)
from app.services.design import (
    apply_design_patch,
    extract_apply_to_all_overrides,
    merge_slide_overrides,
)


class DummyDesign:
    def __init__(self) -> None:
        self.template = "classic"
        self.bg_type = "color"
        self.bg_value = "#ffffff"
        self.bg_overlay = 0.0
        self.layout_padding = 64
        self.align_x = "left"
        self.align_y = "top"
        self.show_header = True
        self.show_footer = True
        self.header_text = "@username"
        self.footer_text = "Draft AI"
        self.style_tokens = {}
        self.apply_all_updated_at = None


def test_apply_design_patch_updates_background_and_template() -> None:
    design = DummyDesign()
    patch = DesignPatch(
        template="bold",
        bg=BackgroundSettings(type="color", value="#123456", overlay=0.4),
        apply_to_all=True,
    )
    apply_design_patch(design, patch)
    assert design.template == "bold"
    assert design.bg_type == "color"
    assert design.bg_value == "#123456"
    assert design.bg_overlay == 0.4
    assert design.apply_all_updated_at is not None


def test_extract_and_merge_slide_overrides() -> None:
    patch = DesignPatch(
        template="minimal",
        bg=BackgroundSettings(type="image", value="https://cdn/img.png", overlay=0.1),
        apply_to_all=True,
    )
    extracted = extract_apply_to_all_overrides(patch)
    merged = merge_slide_overrides({"template": "classic"}, extracted)
    assert merged["template"] == "minimal"
    assert merged["bg_type"] == "image"
    assert merged["bg_value"] == "https://cdn/img.png"


def test_style_tokens_patch_merges_and_apply_to_all_payload() -> None:
    design = DummyDesign()
    patch = DesignPatch(
        style_tokens=StyleTokensPatch(
            title=TypographyTokensPatch(size=90, case="upper"),
            accent_color="#1122FF",
        ),
        apply_to_all=True,
    )
    apply_design_patch(design, patch)
    assert design.style_tokens["title"]["size"] == 90
    assert design.style_tokens["title"]["case"] == "upper"
    assert design.style_tokens["accent_color"] == "#1122FF"

    extracted = extract_apply_to_all_overrides(patch)
    merged = merge_slide_overrides({"style_tokens": {"body": {"size": 40}}}, extracted)
    assert merged["style_tokens"]["title"]["size"] == 90
    assert merged["style_tokens"]["body"]["size"] == 40
