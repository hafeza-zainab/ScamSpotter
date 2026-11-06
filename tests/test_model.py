"""Pytest checks for risk levels and empty-message handling."""

import pytest

pytest.importorskip("sklearn")
pytest.importorskip("joblib")

import model


def test_obvious_scam_is_high_risk(monkeypatch):
    monkeypatch.setattr(model, "predict", lambda _text: 0.40)
    result = model.check_message(
        "Urgent: bank KYC blocked. Share OTP immediately at https://tiny.example/a"
    )
    assert result["risk"] == "High"
    assert result["red_flags"]


def test_suspicious_message_is_at_least_medium(monkeypatch):
    monkeypatch.setattr(model, "predict", lambda _text: 0.35)
    result = model.check_message("Share your OTP to verify")
    assert result["risk"] in {"Medium", "High"}


def test_safe_message_is_low(monkeypatch):
    monkeypatch.setattr(model, "predict", lambda _text: 0.05)
    result = model.check_message("Your appointment is confirmed for Tuesday at 10 am.")
    assert result["risk"] == "Low"


def test_short_genuine_chat_is_low(monkeypatch):
    monkeypatch.setattr(model, "predict", lambda _text: 0.58)
    result = model.check_message("Hi, reached home?")
    assert result["risk"] == "Low"


def test_empty_input_returns_a_guidance_result_without_prediction(monkeypatch):
    def prediction_must_not_run(_text):
        raise AssertionError("empty input should be handled before model prediction")

    monkeypatch.setattr(model, "predict", prediction_must_not_run)
    result = model.check_message("  ")
    assert result["risk"] == "Low"
    assert result["red_flags"] == []
    assert "Enter a message" in result["summary"]
