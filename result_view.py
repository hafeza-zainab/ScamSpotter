"""Shared Streamlit result renderer for the regular app and guided demo."""

import streamlit as st

from explanation import explain_in_simple_words
from model import MODEL_FILE, combine_score, predict, risk_from_score
from rules import find_red_flags


def analyze_message(text: str) -> dict:
    """Return risk details, falling back to rules if the saved model is absent."""
    if not text.strip():
        return {
            "red_flags": [],
            "model_probability": None,
            "model_available": False,
            "risk_score": 0.0,
            "risk": "Low",
        }

    flags = find_red_flags(text)
    try:
        model_probability = predict(text)
        model_available = True
    except FileNotFoundError:
        model_probability = None
        model_available = False

    risk_score = combine_score(model_probability or 0.0, len(flags))
    if not model_available and flags:
        # Without model evidence, make a direct rule hit at least a Medium risk.
        risk_score = max(risk_score, 0.40)
    return {
        "red_flags": flags,
        "model_probability": model_probability,
        "model_available": model_available,
        "risk_score": risk_score,
        "risk": risk_from_score(risk_score),
    }


def render_result(
    text: str,
    container,
    show_explanation: bool | None = None,
    analysis: dict | None = None,
) -> None:
    """Render cached or newly analyzed risk, flags, advice, and explanation."""
    # A placeholder itself is a single slot: successive writes can replace one
    # another. A child container groups the full result as one placeholder item.
    with container.container():
        if not text.strip():
            st.warning("Paste a message or choose an example first.")
            return

        if analysis is None:
            if not MODEL_FILE.exists():
                with st.spinner("Training the local model for its first use..."):
                    result = analyze_message(text)
            else:
                result = analyze_message(text)
        else:
            # The main page supplies the result computed when Check was clicked.
            result = analysis
        flags = result["red_flags"]
        model_probability = result["model_probability"]
        model_available = result["model_available"]
        risk = result["risk"]
        if risk == "High":
            color = "#b42318"
            risk_message = "Treat this message as suspicious."
        elif risk == "Medium":
            color = "#b54708"
            risk_message = "Pause and verify through an official channel."
        else:
            color = "#067647"
            risk_message = "Few common warning signs were found; this does not prove the message is safe."

        st.divider()
        st.subheader("Result")
        st.markdown(
            f'<div style="padding: 1rem; border-radius: 0.6rem; '
            f'background: {color}16; border-left: 6px solid {color};">'
            f'<span style="font-size: 0.85rem;">RISK LEVEL</span><br>'
            f'<strong style="font-size: 1.7rem; color: {color};">{risk}</strong><br>'
            f'{risk_message}</div>',
            unsafe_allow_html=True,
        )
        if model_available:
            st.caption(f"Model scam probability: {model_probability:.0%} · Rule signals: {len(flags)}")
        else:
            st.info(
                "The saved model is not available yet. This result uses the red-flag "
                "rules only. Run 'python model.py' after installing the requirements "
                "to train and save the model."
            )

        st.subheader("Red flags found")
        if flags:
            for flag in flags:
                st.markdown(f"- **{flag['name']}** — {flag['explanation']}")
        else:
            st.write("No configured red flags matched this message.")

        if show_explanation is None:
            explanation_on = st.checkbox("Explain in simple words", key="simple_explanation")
        else:
            explanation_on = show_explanation
            if show_explanation:
                st.markdown("☑ **Explain in simple words**")
        if explanation_on:
            st.info(explain_in_simple_words(flags, model_probability))

        st.subheader("What should I do?")
        advice = [
            "Don't click links or open attachments in an unexpected message. Find the official app or website yourself.",
            "Never share an OTP, UPI PIN, CVV, password, or verification code with anyone.",
            "If it claims to be from a bank, call the official number printed on your card or shown in its official app.",
            "If you have lost money to cyber fraud in India, report it at cybercrime.gov.in or call 1930 promptly.",
        ]
        for item in advice:
            st.markdown(f"- {item}")
