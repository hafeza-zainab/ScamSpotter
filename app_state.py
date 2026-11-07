"""Small helpers for keeping checked-message state across Streamlit reruns."""

RESULT_TEXT_KEY = "checked_message"
RESULT_ANALYSIS_KEY = "checked_analysis"
EXPLANATION_KEY = "simple_explanation"


def remember_result(state, text: str, analysis: dict | None) -> None:
    """Save the exact text and analysis shown in the result panel."""
    state[RESULT_TEXT_KEY] = text
    state[RESULT_ANALYSIS_KEY] = analysis


def clear_result(state) -> None:
    """Remove stale analysis and reset the optional explanation toggle."""
    state.pop(RESULT_TEXT_KEY, None)
    state.pop(RESULT_ANALYSIS_KEY, None)
    state[EXPLANATION_KEY] = False
