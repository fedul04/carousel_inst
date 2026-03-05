from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.schemas.design import StyleTokens

DEFAULT_STYLE_TOKENS: dict[str, Any] = StyleTokens().model_dump()


def deep_merge_dicts(base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(base)
    for key, value in patch.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    return result


def normalize_style_tokens(raw: dict[str, Any] | None) -> dict[str, Any]:
    merged = deep_merge_dicts(DEFAULT_STYLE_TOKENS, raw or {})
    return StyleTokens.model_validate(merged).model_dump()
