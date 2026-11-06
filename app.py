"""Streamlit interface for private, local scam-message guidance."""

import streamlit as st

from result_view import render_result as _render_result
from demo import run_demo

st.set_page_config(page_title="ScamSpotter", page_icon="🛡️", layout="centered")
st.title("🛡️ ScamSpotter")
st.write("Paste a suspicious SMS, WhatsApp message, or email to review its warning signs.")
st.caption("Messages are checked in this app and are not stored or logged by the app.")

def render_result(text: str, container) -> None:
    """Render the shared live model-and-rules result in the requested container."""
    _render_result(text, container)

def _start_demo() -> None:
    """Mark the walkthrough as requested before Streamlit reruns the page."""
    st.session_state["demo_running"] = True
    st.session_state["demo_requested"] = True

def _stop_demo() -> None:
    """Stop the current walkthrough when Streamlit handles the next interaction."""
    st.session_state["demo_running"] = False
    st.session_state["demo_requested"] = False
    st.session_state["demo_stop_requested"] = True

st.session_state.setdefault("demo_running", False)
demo_running = st.session_state["demo_running"]
demo_columns = st.columns([2, 2, 1])
with demo_columns[0]:
    st.button(
        "▶ Run demo",
        key="run_demo_button",
        on_click=_start_demo,
        disabled=demo_running,
        use_container_width=True,
    )
with demo_columns[1]:
    demo_speed_label = st.selectbox(
        "Demo speed",
        ["Slow", "Normal", "Fast"],
        index=1,
        key="demo_speed",
        disabled=demo_running,
    )
with demo_columns[2]:
    if demo_running:
        st.button(
            "■ Stop demo",
            key="stop_demo_button",
            on_click=_stop_demo,
            use_container_width=True,
        )
st.caption("See the app working on fictional sample messages.")

if st.session_state.pop("demo_stop_requested", False):
    st.info("Demo stopped. You can continue with your own message below.")
elif st.session_state.pop("demo_finished", False):
    st.success("Demo complete. Try your own message below.")
elif st.session_state.pop("demo_requested", False):
    speed_values = {"Slow": 1.8, "Normal": 1.0, "Fast": 0.35}
    try:
        run_demo(speed=speed_values[demo_speed_label])
    finally:
        st.session_state["demo_running"] = False
    # Refresh the button states and carry the completion message into the rerun.
    st.session_state["demo_finished"] = True
    st.rerun()
elif st.session_state.get("demo_running", False):
    # Any page interaction reruns Streamlit and interrupts the active demo.
    st.session_state["demo_running"] = False
    st.info("Demo interrupted. You can continue with your own message below.")

EXAMPLES = {
    "Fake KYC warning": "Urgent: Your MangoLeaf Bank KYC expires today. Share your OTP immediately to avoid account blocked. Update at https://verify.example/kyc",
    "Fake UPI refund": "Your UPI refund is ready. Enter your UPI PIN at https://claim.example/now to receive Rs 1,250.",
    "Safe OTP notice": "Your login OTP is 572913. Do not share this code with anyone, including support staff.",
    "Delivery update": "Your Orbit Parcel is out for delivery today. Track it in the official app; no action is needed.",
    "Hinglish prize claim": "Aapka naam lucky draw mein hai! Rs 8,000 jeetne ke liye processing fee bhejo abhi.",
}

def choose_example(example_name: str) -> None:
    """Place a sample in the input box; it remains only in session memory."""
    st.session_state["message_input"] = EXAMPLES[example_name]

st.subheader("Try an example")
example_columns = st.columns(2)
for index, example_name in enumerate(EXAMPLES):
    with example_columns[index % 2]:
        st.button(
            example_name,
            key=f"example_{index}",
            on_click=choose_example,
            args=(example_name,),
            use_container_width=True,
        )

message = st.text_area(
    "Message to check",
    key="message_input",
    height=170,
    placeholder="Paste the message here...",
)

if st.button("Check message", type="primary", use_container_width=True):
    render_result(message, st.container())

st.divider()
st.caption(
    "Disclaimer: This tool gives guidance only and can make mistakes. A Low result "
    "does not guarantee that a message is safe. The app does not store or log pasted messages."
)
