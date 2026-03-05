import pytest

pytest.importorskip("sqlalchemy")

from app.services.rendering import render_service


def test_apply_case_keeps_natural_mode_unchanged() -> None:
    text = "hELLo WoRLD 123"
    assert render_service._apply_case(text, "title") == text


def test_overlay_alpha_respects_dimming_strength() -> None:
    tokens = {
        "background": {
            "dimming": {
                "enabled": True,
                "strength": 0.35,
            }
        }
    }
    assert render_service._overlay_alpha(0.2, tokens) == 0.55


def test_pattern_css_generates_grid_layers() -> None:
    css = render_service._pattern_css(
        {
            "accent_color": "#3B37D2",
            "background": {
                "pattern": {
                    "enabled": True,
                    "type": "grid",
                    "opacity": 0.2,
                    "scale": 1.0,
                }
            },
        }
    )
    assert "repeating-linear-gradient(0deg" in css
    assert "repeating-linear-gradient(90deg" in css
