"""A short, local-only guided tour of ScamSpotter."""

import html
import time

import streamlit as st

from result_view import analyze_message, render_result


# Keep these scenes as editable data so the demo story can be changed easily.
SCENES = [
    {
        "caption": "Welcome — this demo checks suspicious messages locally.",
        "message": None,
        "wait_time": 1.0,
    },
    {
        "caption": "Scams often create urgency or ask people to share private details.",
        "message": None,
        "wait_time": 1.2,
    },
    {
        "caption": "Example: a fictional bank KYC warning asks for an OTP.",
        "message": "Urgent: MangoLeaf Bank KYC expires today. Share your OTP immediately to avoid account block.",
        "expected_label": "scam",
        "wait_time": 1.4,
    },
    {
        "caption": "Scam wording can mix English and Hindi.",
        "message": "Aapka naam lucky draw mein hai! Rs 8,000 jeetne ke liye processing fee bhejo abhi.",
        "expected_label": "scam",
        "wait_time": 1.4,
    },
    {
        "caption": "A genuine-sounding transaction alert can mention a bank without asking you to act.",
        "message": "Bank alert: Rs 450 debited at Cobalt Cafe. Your available balance is Rs 2,300.",
        "expected_label": "safe",
        "wait_time": 1.4,
    },
    {
        "caption": "The simple explanation uses the model score and detected red flags.",
        "message": "Your BlueKite Bank account is blocked. Share your OTP now to restore access.",
        "wait_time": 1.4,
        "show_explanation": True,
        "expected_label": "scam",
    },
    {
        "caption": "The app combines a local text model with readable rules.",
        "message": None,
        "wait_time": 1.2,
    },
    {
        "caption": "Pasted messages stay in this app session; the demo does not save or log them.",
        "message": None,
        "wait_time": 1.2,
    },
    {
        "caption": "This is guidance only. A low score does not prove a message is safe.",
        "message": None,
        "wait_time": 1.2,
    },
    {
        "caption": "Thanks for watching. Verify suspicious claims through official channels.",
        "message": None,
        "wait_time": 1.0,
    },
]


def wait(seconds: float, speed: float, on_tick=None) -> None:
    """Pause in one place, update the visible clock, and scale delay by speed."""
    remaining = max(0.0, seconds) * speed
    while remaining > 0:
        tick = min(0.1, remaining)
        time.sleep(tick)
        remaining -= tick
        if on_tick is not None:
            on_tick()


def _show_typed_message(message: str, placeholder, speed: float, update_clock) -> None:
    """Reveal fictional demo text a character at a time in a text-box style."""
    for end in range(1, len(message) + 1):
        visible_text = html.escape(message[:end])
        placeholder.markdown(
            '<div style="border:1px solid #aab4c0; border-radius:0.5rem; '
            'padding:0.8rem; min-height:4rem; white-space:pre-wrap; '
            'background:rgba(128,128,128,0.06);">'
            f"{visible_text}</div>",
            unsafe_allow_html=True,
        )
        update_clock()
        wait(0.018, speed, update_clock)


def run_demo(speed: float = 1.0) -> None:
    """Play the guided demo using only fictional examples and local analysis."""
    if speed < 0:
        raise ValueError("speed must be zero or greater")

    started_at = time.monotonic()
    total_steps = len(SCENES)
    caption_placeholder = st.empty()
    progress_bar = st.progress(0.0)
    scene_placeholder = st.empty()
    message_placeholder = st.empty()
    result_placeholder = st.empty()

    def update_caption(step_number: int, caption: str) -> None:
        elapsed = time.monotonic() - started_at
        caption_placeholder.caption(
            f"Guided demo · Step {step_number}/{total_steps}: {caption} · "
            f"Elapsed {elapsed:.1f}s"
        )

    for index, scene in enumerate(SCENES, start=1):
        progress_bar.progress(index / total_steps)
        update_caption(index, scene["caption"])
        scene_placeholder.info(scene["caption"])
        message_placeholder.empty()
        result_placeholder.empty()

        message = scene["message"]
        if message:
            _show_typed_message(
                message,
                message_placeholder,
                speed,
                lambda: update_caption(index, scene["caption"]),
            )
            # Demo and manual checks share the same analyzer and result renderer.
            analysis = analyze_message(message)
            render_result(
                message,
                result_placeholder,
                show_explanation=scene.get("show_explanation", False),
                analysis=analysis,
            )
            update_caption(index, scene["caption"])

        wait(
            scene["wait_time"],
            speed,
            lambda: update_caption(index, scene["caption"]),
        )

    # Remove the tour's temporary UI so the normal input form is ready below.
    caption_placeholder.empty()
    progress_bar.empty()
    scene_placeholder.empty()
    message_placeholder.empty()
    result_placeholder.empty()
    st.success("Demo complete. Try your own message below.")
