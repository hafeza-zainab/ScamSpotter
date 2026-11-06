"""Editable keyword and regex rules for common English and Hinglish scam signals."""

import re

# Keep patterns readable so beginners can add or remove phrases easily.
# Each tuple contains a flag name, explanation, and regex for matching message text.
RED_FLAG_RULES = [
    (
        "Urgency or threat",
        "The message pressures you to act quickly or threatens to block an account.",
        r"\b(immediately|urgent|urgently|within\s+24\s+hours|within\s+24\s+ghante|act\s+now|last\s+chance|right\s+away|today\s+only|turant|abhi|jaldi|fauran|khata\s+band|account\s+band|account\s+blocked|account\s+block|block\s+ho\s+jayega|band\s+ho\s+jayega)\b",
    ),
    (
        "Sensitive information request",
        "It asks for an OTP, PIN, CVV, password, or verification code. These should stay private.",
        r"\b(share|send|provide|tell|read|reply\s+with|enter|type|submit|reveal|bhejo|batao|daalo|likho|do)\b.{0,35}\b(otp|one[\s-]?time\s+password|verification\s+code|cvv|password|passcode|upi\s+pin|atm\s+pin|pin|secret\s+code)\b|\b(otp|one[\s-]?time\s+password|verification\s+code|cvv|password|passcode|upi\s+pin|atm\s+pin|pin|secret\s+code)\b.{0,35}\b(share|send|provide|tell|read|reply|enter|type|submit|reveal|bhejo|batao|daalo|likho|do)\b",
    ),
    (
        "Money or UPI payment request",
        "It asks you to send money, pay a fee, or make a UPI payment.",
        r"\b(send\s+money|transfer\s+(?:money|funds)|pay(?:ment)?\s+(?:now|fee|charge|first)|pay\s+(?:via|using|through)\s+upi|upi\s+(?:transfer|request|collect|bhejo|se\s+pay)|payment\s+request|scan\s+(?:this\s+)?qr|deposit\s+(?:money|fee)|processing\s+fee|registration\s+fee|customs\s+fee|paise\s+bhejo|paisa\s+bhejo|paise\s+bhej[oa]|payment\s+karo|pay\s+karo|fee\s+bhar[oa]|rupaye\s+bhejo|upi\s+se\s+pay)\b|\b(pay|send|transfer|deposit|bhejo|bhar[oa])\b.{0,25}\b(rs\.?|rupees?|inr|₹|money|paise|paisa|amount|fee)\b",
    ),
    (
        "Link included or shortened link",
        "It includes a link or mentions a short link. Check the domain independently before opening it.",
        r"(?:https?://|www\.)[^\s<>]+|\b(bit\.ly|tinyurl|t\.co|is\.gd|cutt\.ly|shorturl|short\s+link|shortened\s+link|chhota\s+link|link\s+par\s+click|link\s+khol|link\s+open\s+karo)\b",
    ),
    (
        "Possible company or government impersonation",
        "It claims to represent a bank, government office, or courier service. Verify through its official app or number.",
        r"\b(we\s+are\s+from|calling\s+from|official\s+(?:bank|government|courier)|bank\s+(?:security\s+team|support\s+team|officer|agent)|government\s+(?:officer|department|agent)|courier\s+(?:agent|department|support)|aadhaar\s+(?:office|department)|income\s+tax\s+department|rbi\s+officer|sarkari\s+adhikari|bank\s+ki\s+taraf\s+se)\b",
    ),
    (
        "Prize or lottery claim",
        "It says you won a prize or lottery, which can be used to lure you into sharing details or paying a fee.",
        r"\b(prize|lottery|lucky\s+draw|winner|won|congratulations|reward|cashback\s+claim|inaam|inaam\s+jeeta|jeet\s+gaye|puraskar|lucky\s+winner|claim\s+(?:your\s+)?reward)\b",
    ),
    (
        "Request to install an app",
        "It asks you to install an app or file. Unrequested apps can steal information or give someone access to your device.",
        r"\b(install|download|setup)\b.{0,40}\b(app|application|apk|software|anydesk|teamviewer|screen\s*share)\b|\b(app|application|apk|anydesk|teamviewer)\b.{0,40}\b(install|download|setup|karo|kar lo|karna)\b|\b(app\s+install\s+karo|apk\s+download\s+karo)\b",
    ),
]

def find_red_flags(text: str) -> list[dict[str, str]]:
    """Return matching flags as dictionaries with a name and plain-English explanation."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    found = []
    safe_secret_notice = re.search(
        r"\b(do\s+not|don't|never|cannot|can't)\s+share\b|"
        r"\b(don't|do\s+not)\s+tell\b|"
        r"\b(kisi\s+ke\s+saath\s+share\s+mat|kisi\s+ko\s+mat\s+batana)\b",
        text,
        flags=re.IGNORECASE,
    )
    direct_secret_request = re.search(
        r"\b(share|send|provide|tell|read|reply\s+with|enter|type|submit|reveal)"
        r"\s+(your\s+)?(otp|pin|cvv|password|verification\s+code)\b|"
        r"\b(otp|pin|cvv|password)\s+(bhejo|batao|daalo|likho|do)\b",
        text,
        flags=re.IGNORECASE,
    )
    for name, explanation, pattern in RED_FLAG_RULES:
        # An OTP notice often mentions the word "share" to warn users. Treat
        # it as safe unless the message also contains a direct request for it.
        if name == "Sensitive information request" and safe_secret_notice and not direct_secret_request:
            continue
        if re.search(pattern, text, flags=re.IGNORECASE):
            found.append({"name": name, "explanation": explanation})
    return found
