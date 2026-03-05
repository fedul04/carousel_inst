from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import AppBaseSchema

PatternType = Literal["dots", "texture2", "squares", "lines", "grid", "bubbles"]
FontName = Literal[
    "inter",
    "fira_code",
    "roboto_condensed",
    "jost",
    "caveat",
    "source_sans_3",
]
TextCase = Literal["upper", "title", "lower"]
TemplatePreset = Literal[
    "classic",
    "bold",
    "minimal",
    "neon",
    "soft",
    "noir",
    "aurora",
    "sunset",
    "synthwave",
    "paper",
    "matrix",
    "candy",
    "lava",
    "frost",
    "mono",
    "velvet",
    "blueprint",
    "hologram",
    "cosmos",
    "ember",
    "oasis",
    "graphite",
    "citrus",
    "vintage",
]


class BackgroundSettings(BaseModel):
    type: Literal["color", "image"] = "color"
    value: str = "#F4F1E9"
    overlay: float = Field(default=0.0, ge=0.0, le=1.0)


class LayoutSettings(BaseModel):
    padding: int = Field(default=64, ge=0, le=160)
    align_x: Literal["left", "center", "right"] = "left"
    align_y: Literal["top", "center", "bottom"] = "top"


class HeaderSettings(BaseModel):
    show: bool = True
    text: str = "@username"


class FooterSettings(BaseModel):
    show: bool = True
    text: str = "Draft AI"


class PatternSettings(BaseModel):
    enabled: bool = False
    type: PatternType = "dots"
    opacity: float = Field(default=0.18, ge=0.0, le=1.0)
    scale: float = Field(default=1.0, ge=0.4, le=2.5)


class DimmingSettings(BaseModel):
    enabled: bool = False
    strength: float = Field(default=0.0, ge=0.0, le=1.0)


class BackgroundStyleTokens(BaseModel):
    pattern: PatternSettings = Field(default_factory=PatternSettings)
    dimming: DimmingSettings = Field(default_factory=DimmingSettings)
    image_asset_id: str | None = None


class TypographyTokens(BaseModel):
    font: FontName = "inter"
    size: int = Field(default=82, ge=14, le=180)
    line_height: float = Field(default=1.0, ge=0.7, le=2.0)
    letter_spacing: float = Field(default=0.0, ge=-6.0, le=20.0)
    weight: int = Field(default=700, ge=100, le=900)
    case: TextCase = "title"


class StyleTokens(BaseModel):
    accent_color: str = "#3B37D2"
    highlight_color: str = "#3B37D2"
    background: BackgroundStyleTokens = Field(default_factory=BackgroundStyleTokens)
    title: TypographyTokens = Field(
        default_factory=lambda: TypographyTokens(
            font="inter",
            size=82,
            line_height=0.98,
            letter_spacing=0.0,
            weight=800,
            case="title",
        )
    )
    body: TypographyTokens = Field(
        default_factory=lambda: TypographyTokens(
            font="inter",
            size=44,
            line_height=1.28,
            letter_spacing=0.0,
            weight=500,
            case="title",
        )
    )


class PatternSettingsPatch(BaseModel):
    enabled: bool | None = None
    type: PatternType | None = None
    opacity: float | None = Field(default=None, ge=0.0, le=1.0)
    scale: float | None = Field(default=None, ge=0.4, le=2.5)


class DimmingSettingsPatch(BaseModel):
    enabled: bool | None = None
    strength: float | None = Field(default=None, ge=0.0, le=1.0)


class BackgroundStyleTokensPatch(BaseModel):
    pattern: PatternSettingsPatch | None = None
    dimming: DimmingSettingsPatch | None = None
    image_asset_id: str | None = None


class TypographyTokensPatch(BaseModel):
    font: FontName | None = None
    size: int | None = Field(default=None, ge=14, le=180)
    line_height: float | None = Field(default=None, ge=0.7, le=2.0)
    letter_spacing: float | None = Field(default=None, ge=-6.0, le=20.0)
    weight: int | None = Field(default=None, ge=100, le=900)
    case: TextCase | None = None


class StyleTokensPatch(BaseModel):
    accent_color: str | None = None
    highlight_color: str | None = None
    background: BackgroundStyleTokensPatch | None = None
    title: TypographyTokensPatch | None = None
    body: TypographyTokensPatch | None = None


class DesignPatch(BaseModel):
    template: TemplatePreset | None = None
    bg: BackgroundSettings | None = None
    layout: LayoutSettings | None = None
    header: HeaderSettings | None = None
    footer: FooterSettings | None = None
    style_tokens: StyleTokensPatch | None = None
    apply_to_all: bool = False


class DesignOut(AppBaseSchema):
    carousel_id: str
    template: str
    bg_type: str
    bg_value: str
    bg_overlay: float
    layout_padding: int
    align_x: str
    align_y: str
    show_header: bool
    show_footer: bool
    header_text: str
    footer_text: str
    style_tokens: StyleTokens
    apply_all_updated_at: datetime | None
