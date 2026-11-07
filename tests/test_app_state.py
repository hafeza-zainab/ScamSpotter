"""Tests for cached message state and rerun-safe result rendering."""

import pytest

pytest.importorskip("streamlit")

import result_view
from app_state import clear_result, remember_result


def test_remember_result_saves_message_and_analysis():
    state = {}
    analysis = {"risk": "High", "red_flags": []}

    remember_result(state, "Suspicious text", analysis)

    assert state["checked_message"] == "Suspicious text"
    assert state["checked_analysis"] is analysis


def test_clearing_result_removes_old_text_and_resets_explanation():
    state = {
        "checked_message": "Old text",
        "checked_analysis": {"risk": "High"},
        "simple_explanation": True,
    }

    clear_result(state)

    assert "checked_message" not in state
    assert "checked_analysis" not in state
    assert state["simple_explanation"] is False


def test_cached_result_renders_explanation_without_reanalysis(monkeypatch):
    ui_messages = []
    checkbox_keys = []

    class FakeContainer:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

    def unexpected_analysis(_text):
        raise AssertionError("cached analysis should be reused on rerun")

    monkeypatch.setattr(result_view, "analyze_message", unexpected_analysis)
    monkeypatch.setattr(result_view.st, "divider", lambda: None)
    monkeypatch.setattr(result_view.st, "subheader", lambda text: ui_messages.append(text))
    monkeypatch.setattr(result_view.st, "markdown", lambda text, **_kwargs: ui_messages.append(text))
    monkeypatch.setattr(result_view.st, "caption", lambda text: ui_messages.append(text))
    monkeypatch.setattr(result_view.st, "write", lambda text: ui_messages.append(text))
    monkeypatch.setattr(result_view.st, "checkbox", lambda _label, key: checkbox_keys.append(key) or True)
    monkeypatch.setattr(result_view.st, "info", lambda text: ui_messages.append(text))

    cached_analysis = {
        "red_flags": [
            {
                "name": "Sensitive information request",
                "explanation": "It asks you to share an OTP.",
            }
        ],
        "model_probability": 0.82,
        "model_available": True,
        "risk_score": 0.67,
        "risk": "Medium",
    }
    result_view.render_result("Share OTP", FakeContainer(), analysis=cached_analysis)

    assert checkbox_keys == ["simple_explanation"]
    assert any("local model gives this a 82%" in text for text in ui_messages)
    assert "Result" in ui_messages
