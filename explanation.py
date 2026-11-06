"""Local, template-based explanations using only flags and a model score.

Keep this small interface stable if a free local LLM is added later. Do not
pass the original message to this function or send it to another service.
"""

def explain_in_simple_words(red_flags: list[dict[str, str]], model_score: float | None) -> str:
    """Create a short friendly explanation without inspecting message text."""
    reasons = [flag["explanation"] for flag in red_flags]
    if model_score is None:
        if reasons:
            return "I noticed these warning signs: " + " ".join(reasons[:2]) + (
                " Please pause and check through an official channel."
            )
        return (
            "I didn't find common warning signs. The local model isn't trained yet, "
            "so this check is limited; please verify anything unexpected."
        )

    score_percent = round(max(0.0, min(1.0, model_score)) * 100)
    if model_score >= 0.70:
        opening = f"The local model gives this a {score_percent}% scam score, which is high."
    elif model_score >= 0.40:
        opening = f"The local model gives this a {score_percent}% scam score, so it's worth checking carefully."
    else:
        opening = f"The local model gives this a {score_percent}% scam score, which is low."

    if reasons:
        reason_text = " ".join(reasons[:2])
        if len(reasons) > 2:
            reason_text += f" I also found {len(reasons) - 2} more warning sign(s)."
        return f"{opening} {reason_text} Verify through an official channel before acting."
    return (
        f"{opening} The rule checks found no common red flags, but that doesn't "
        "guarantee the message is safe."
    )
