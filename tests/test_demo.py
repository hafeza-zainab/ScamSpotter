"""Ensure demo message labels match the real local rules and classifier."""

import pytest

import model
from demo import SCENES, analyze_message as analyze_demo_message
from result_view import analyze_message as analyze_manual_message


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
    result = analyze_demo_message(scene["message"])
    manual_result = analyze_manual_message(scene["message"])
    assert result == manual_result
    assert result["model_available"] is True
    if scene["expected_label"] == "scam":
        assert result["risk"] in {"High", "Medium"}
    else:
        assert scene["expected_label"] == "safe"
        assert result["risk"] == "Low"


def test_missing_model_trains_and_caches(monkeypatch):
    missing_model = model.MODEL_FILE.with_name("model_auto_train_test.pkl")
    model.get_model.clear()
    monkeypatch.setattr(model, "MODEL_FILE", missing_model)

    try:
        probability = model.predict("Please share your OTP with the agent")
        assert missing_model.exists()
        assert 0.0 <= probability <= 1.0
    finally:
        model.get_model.clear()
        missing_model.unlink(missing_ok=True)


def test_missing_model_and_training_data_fall_back_to_rules(monkeypatch):
    model.get_model.clear()
    monkeypatch.setattr(
        model, "MODEL_FILE", model.MODEL_FILE.with_name("missing_test_model.pkl")
    )
    monkeypatch.setattr(
        model, "DATA_FILE", model.DATA_FILE.with_name("missing_test_messages.csv")
    )

    result = analyze_manual_message("Please share your OTP with the agent")

    assert result["model_available"] is False
    assert result["model_probability"] is None
    assert result["red_flags"]
    assert result["risk"] == "Medium"
    model.get_model.clear()
