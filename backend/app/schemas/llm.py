from pydantic import BaseModel, Field, field_validator, model_validator


class GeneratedSlide(BaseModel):
    order: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=180)
    body: str = Field(min_length=1, max_length=1200)
    footer_cta: str | None = Field(default=None, max_length=200)

    @field_validator("title", "body", mode="before")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return str(value).strip()


class GeneratedArtifacts(BaseModel):
    summary: str | None = Field(default=None, max_length=360)
    hook_variants: list[str] = Field(default_factory=list, max_length=8)
    title_variants: list[str] = Field(default_factory=list, max_length=8)
    cta_variants: list[str] = Field(default_factory=list, max_length=8)
    opening_lines: list[str] = Field(default_factory=list, max_length=8)
    post_caption_variants: list[str] = Field(default_factory=list, max_length=8)
    image_prompts: list[str] = Field(default_factory=list, max_length=10)
    audience_pains: list[str] = Field(default_factory=list, max_length=10)
    hashtags: list[str] = Field(default_factory=list, max_length=16)
    keywords: list[str] = Field(default_factory=list, max_length=16)
    visual_directions: list[str] = Field(default_factory=list, max_length=8)

    @field_validator(
        "hook_variants",
        "title_variants",
        "cta_variants",
        "opening_lines",
        "post_caption_variants",
        "image_prompts",
        "audience_pains",
        "hashtags",
        "keywords",
        "visual_directions",
        mode="before",
    )
    @classmethod
    def normalize_list(cls, value: list[str] | None) -> list[str]:
        if not value:
            return []
        out: list[str] = []
        for item in value:
            cleaned = str(item).strip()
            if cleaned.startswith("#"):
                cleaned = cleaned[1:].strip()
            if cleaned:
                out.append(cleaned)
        return out

    @field_validator("summary", mode="before")
    @classmethod
    def normalize_summary(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = str(value).strip()
        return cleaned or None


class GeneratedSlidesSchema(BaseModel):
    slides: list[GeneratedSlide]
    artifacts: GeneratedArtifacts = Field(default_factory=GeneratedArtifacts)

    @model_validator(mode="after")
    def validate_orders(self) -> "GeneratedSlidesSchema":
        if not self.slides:
            raise ValueError("slides must not be empty")
        orders = [slide.order for slide in self.slides]
        if len(set(orders)) != len(orders):
            raise ValueError("slide order values must be unique")
        if min(orders) < 1:
            raise ValueError("slide order must start from 1")
        return self
