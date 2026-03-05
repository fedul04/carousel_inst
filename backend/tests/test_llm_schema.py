import pytest
from pydantic import ValidationError

from app.schemas.llm import GeneratedSlidesSchema


def test_generated_slides_schema_validates_orders() -> None:
    payload = {
        "slides": [
            {"order": 1, "title": "Title 1", "body": "Body 1", "footer_cta": "CTA"},
            {"order": 2, "title": "Title 2", "body": "Body 2", "footer_cta": None},
        ]
    }
    parsed = GeneratedSlidesSchema.model_validate(payload)
    assert len(parsed.slides) == 2


def test_generated_slides_schema_rejects_duplicate_order() -> None:
    payload = {
        "slides": [
            {"order": 1, "title": "Title 1", "body": "Body 1"},
            {"order": 1, "title": "Title 2", "body": "Body 2"},
        ]
    }
    with pytest.raises(ValidationError):
        GeneratedSlidesSchema.model_validate(payload)

