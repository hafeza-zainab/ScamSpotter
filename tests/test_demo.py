"""Ensure demo message labels match the real local rules and classifier."""

import pytest

import model
from demo import SCENES
from result_view import analyze_message


MESSAGE_SCENES = [scene for scene in SCENES if scene["message"]]


@pytest.fixture(scope="module", autouse=True)
def ensure_trained_model():
    """Train the local model when tests are run from a fresh clone."""
    if not model.MODEL_FILE.exists():
        model.train_model()


@pytest.mark.parametrize(
    "scene",
    MESSAGE_SCENES,
    ids=[scene["caption"] for scene in MESSAGE_SCENES],
)
def test_demo_message_matches_its_expected_risk(scene):
    result = analyze_message(scene["message"])
    assert result["model_available"] is True
    if scene["expected_label"] == "scam":
        assert result["risk"] in {"High", "Medium"}
    else:
        assert scene["expected_label"] == "safe"
        assert result["risk"] == "Low"


def test_missing_model_uses_rules_and_shows_fallback_state(monkeypatch):
    missing_model = model.MODEL_FILE.with_name("missing_test_model.pkl")
    monkeypatch.setattr(model, "MODEL_FILE", missing_model)

    result = analyze_message("Please share your OTP with the agent")

    assert result["model_available"] is False
    assert result["model_probability"] is None
    assert result["red_flags"]
    assert result["risk"] == "Medium"
