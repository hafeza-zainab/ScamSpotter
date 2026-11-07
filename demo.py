"""A short, local-only guided tour of ScamSpotter."""

import html
import time
from pathlib import Path

import streamlit as st

from result_view import analyze_message, render_result

AUDIO_DIR = Path(__file__).parent / "assets" / "audio"
VOICE = "en-IN-NeerjaNeural"

# Keep these scenes as editable data so the demo story can be changed easily.
SCENES = [
    {
        "caption": "Welcome — this demo checks suspicious messages locally.",
        "narration": "Welcome to ScamSpotter. This demo checks messages locally.",
        "message": None,
        "wait_time": 1.0,
    },
    {
        "caption": "Scams often create urgency or ask people to share private details.",
        "narration": "Scam messages often create urgency or ask people to share private details.",
        "message": None,
        "wait_time": 1.2,
    },
    {
        "caption": "Example: a fictional bank KYC warning asks for an OTP.",
        "narration": "Here is a fictional bank KYC warning asking for a one-time password.",
        "message": "Urgent: MangoLeaf Bank KYC expires today. Share your OTP immediately to avoid account block.",
        "expected_label": "scam",
        "wait_time": 1.4,
    },
    {
        "caption": "Scam wording can mix English and Hindi.",
        "narration": "Scam wording can mix English and Hindi.",
        "message": "Aapka naam lucky draw mein hai! Rs 8,000 jeetne ke liye processing fee bhejo abhi.",
        "expected_label": "scam",
        "wait_time": 1.4,
    },
    {
        "caption": "A genuine-sounding transaction alert can mention a bank without asking you to act.",
        "narration": "A genuine transaction alert can mention a bank without asking you to take action.",
        "message": "Bank alert: Rs 450 debited at Cobalt Cafe. Your available balance is Rs 2,300.",
        "expected_label": "safe",
        "wait_time": 1.4,
    },
    {
        "caption": "The simple explanation uses the model score and detected red flags.",
        "narration": "The simple explanation uses the model score and detected red flags.",
        "message": "Your BlueKite Bank account is blocked. Share your OTP now to restore access.",
        "wait_time": 1.4,
        "show_explanation": True,
        "expected_label": "scam",
    },
    {
        "caption": "The app combines a local text model with readable rules.",
        "narration": "The app combines a local text model with clear, readable rules.",
        "message": None,
        "wait_time": 1.2,
    },
    {
        "caption": "Pasted messages stay in this app session; the demo does not save or log them.",
        "narration": "Pasted messages stay in this app session. The demo does not save or log them.",
        "message": None,
        "wait_time": 1.2,
    },
    {
        "caption": "This is guidance only. A low score does not prove a message is safe.",
        "narration": "This tool gives guidance only. A low score does not prove a message is safe.",
        "message": None,
        "wait_time": 1.2,
    },
    {
        "caption": "Thanks for watching. Verify suspicious claims through official channels.",
        "narration": "Thanks for watching. Verify suspicious claims through official channels.",
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

def scene_audio_path(scene_number: int) -> Path:
    """Return the generated audio path for this one-based scene number."""
    return AUDIO_DIR / f"scene_{scene_number:02d}.mp3"

def audio_duration_seconds(audio_path: Path) -> float:
    """Read MP3 frame headers to estimate duration without extra app packages."""
    audio_bytes = audio_path.read_bytes()
    offset = 0
    if audio_bytes.startswith(b"ID3") and len(audio_bytes) >= 10:
        tag = audio_bytes[6:10]
        tag_size = (tag[0] << 21) | (tag[1] << 14) | (tag[2] << 7) | tag[3]
        offset = 10 + tag_size + (10 if audio_bytes[5] & 0x10 else 0)

    mpeg1_layer3 = [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 0]
    mpeg2_layer3 = [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160, 0]
    sample_rates = [44100, 48000, 32000]
    duration = 0.0
    while offset + 4 <= len(audio_bytes):
        header = int.from_bytes(audio_bytes[offset : offset + 4], "big")
        if header >> 21 != 0x7FF:
            offset += 1
            continue

        version = (header >> 19) & 0b11
        layer = (header >> 17) & 0b11
        bitrate_index = (header >> 12) & 0b1111
        sample_rate_index = (header >> 10) & 0b11
        if version == 0b01 or layer != 0b01 or bitrate_index in (0, 15) or sample_rate_index == 3:
            offset += 1
            continue

        mpeg1 = version == 0b11
        sample_rate = sample_rates[sample_rate_index] // (1 if mpeg1 else 2 if version == 0b10 else 4)
        bitrate = (mpeg1_layer3 if mpeg1 else mpeg2_layer3)[bitrate_index] * 1000
        padding = (header >> 9) & 1
        frame_length = int((144 if mpeg1 else 72) * bitrate / sample_rate) + padding
        if frame_length < 4 or offset + frame_length > len(audio_bytes):
            offset += 1
            continue

        duration += (1152 if mpeg1 else 576) / sample_rate
        offset += frame_length

    if duration > 0:
        return duration
    # Edge TTS uses a 48 kbit/s MP3 stream by default; this is a safe fallback
    # for a valid but unusual frame layout that the small parser cannot read.
    return len(audio_bytes) * 8 / 48000


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


def run_demo(speed: float = 1.0, sound_enabled: bool = True) -> None:
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
    audio_placeholder = st.empty()
    st.markdown(
        "<style>div[data-testid='stAudio']{margin:0;padding:0;max-height:2rem;"
        "overflow:hidden}div[data-testid='stAudio'] audio{height:2rem}</style>",
        unsafe_allow_html=True,
    )

    def update_caption(step_number: int, caption: str) -> None:
        elapsed = time.monotonic() - started_at
        caption_placeholder.caption(
            f"Guided demo · Step {step_number}/{total_steps}: {caption} · "
            f"Elapsed {elapsed:.1f}s"
        )

    try:
        for index, scene in enumerate(SCENES, start=1):
            scene_started = time.monotonic()
            progress_bar.progress(index / total_steps)
            update_caption(index, scene["caption"])
            scene_placeholder.info(scene["caption"])
            message_placeholder.empty()
            result_placeholder.empty()
            audio_placeholder.empty()

            audio_duration = 0.0
            if sound_enabled:
                audio_file = scene_audio_path(index)
                if audio_file.is_file():
                    try:
                        audio_duration = audio_duration_seconds(audio_file)
                        audio_placeholder.audio(
                            audio_file.read_bytes(),
                            format="audio/mp3",
                            autoplay=True,
                        )
                    except (OSError, ValueError):
                        # Missing or unreadable narration is optional; continue silently.
                        audio_duration = 0.0
                        audio_placeholder.empty()

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
            elapsed = time.monotonic() - scene_started
            # Scale normal waits by speed, but always allow the audio to finish.
            audio_target = audio_duration + 0.25 if audio_duration else 0.0
            target_duration = max(scene["wait_time"] * speed, audio_target)
            wait(
                max(0.0, target_duration - elapsed),
                1.0,
                lambda: update_caption(index, scene["caption"]),
            )

    finally:
        # Clearing the player stops audio on completion and on interruption.
        caption_placeholder.empty()
        progress_bar.empty()
        scene_placeholder.empty()
        message_placeholder.empty()
        result_placeholder.empty()
        audio_placeholder.empty()

    st.success("Demo complete. Try your own message below.")
