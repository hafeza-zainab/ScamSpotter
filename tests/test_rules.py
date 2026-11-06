"""Pytest checks for the editable red-flag rules."""

from rules import find_red_flags


def test_detects_otp_request():
    flags = find_red_flags("Please share your OTP to verify your account")
    assert "Sensitive information request" in {flag["name"] for flag in flags}


def test_detects_suspicious_link():
    flags = find_red_flags("Update your details at https://tiny.example/check")
    assert "Link included or shortened link" in {flag["name"] for flag in flags}


def test_detects_urgency_in_hinglish():
    flags = find_red_flags("Abhi karo warna account band ho jayega")
    assert "Urgency or threat" in {flag["name"] for flag in flags}


def test_safe_otp_notice_is_not_a_request():
    flags = find_red_flags("Your login OTP is 572913. Do not share it with anyone.")
    assert "Sensitive information request" not in {flag["name"] for flag in flags}


def test_completed_upi_payment_is_not_a_payment_request():
    flags = find_red_flags("Your UPI payment of Rs 450 to Cobalt Cafe is complete.")
    assert "Money or UPI payment request" not in {flag["name"] for flag in flags}


def test_ordinary_bank_alert_is_not_impersonation_by_itself():
    flags = find_red_flags("Bank alert: Rs 450 was debited at Cobalt Cafe.")
    assert "Possible company or government impersonation" not in {flag["name"] for flag in flags}


def test_plain_message_has_no_flags():
    assert find_red_flags("The library opens at 9 am") == []
