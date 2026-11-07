# What broke

The result panel used to render only inside the “Check message” button branch. Clicking “Explain in simple words” caused Streamlit to rerun the script, so the result disappeared. Earlier rule checks also raised false alarms for safe OTP notices and completed UPI receipts; a short harmless chat could receive Medium risk.

I ran the 20 fictional messages in validation_messages.txt through the current model and rules. All 8 scam examples received Medium or High risk, and all 8 genuine-sounding examples received Low. The 4 context-dependent examples came out as: bank alert with an action — Medium; parcel reschedule — Low; unsolicited job message — Low; UPI collect request — Low. These are ambiguous and need sender/context checks, so I am recording the outputs rather than treating them as definite errors.


# What I changed

I now save the checked text and its analysis in Streamlit session state, then render the saved analysis on later reruns. The explanation checkbox has a stable key. Editing the message, selecting an example, or starting/stopping the demo clears the stored result so it cannot appear beside new text.

The rules were tightened to distinguish OTP requests from “do not share” notices, completed payments from payment requests, and ordinary bank/delivery alerts from impersonation. I added more varied safe and scam training examples and a separate tricky-message set. The new 20-message validation set remains separate from training data.

The test suite passed: 21 tests. It covers result persistence, stale-result clearing helpers, demo scene labels, rule behavior, and missing-model fallback. The 20-message validation run is a small self-authored check, not a representative accuracy estimate.


# What I learned

Streamlit reruns the whole script after a widget interaction. Values needed on the next run must live in session state; otherwise, code guarded by a one-run button condition runs only once. Keeping the analysis alongside the checked text lets the explanation toggle update the display without re-running the classifier.

The messages showed that obvious requests for OTPs, fees, and prize claims can be recognized, while short or context-dependent messages remain uncertain. A Low result for a parcel or job message does not prove it is genuine. Sender identity and the surrounding conversation still matter, and a larger independently collected test set is needed before making real-world accuracy claims.

