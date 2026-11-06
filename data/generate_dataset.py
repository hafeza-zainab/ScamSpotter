"""Generate a balanced, fictional message dataset for the demo classifier.

Run from the project root with: python data/generate_dataset.py
The fixed seed makes the output repeatable for learning and debugging.
"""

import csv
import random
from pathlib import Path

OUTPUT_FILE = Path(__file__).with_name("messages.csv")
RANDOM_SEED = 2026

# Templates use only invented brands, placeholder domains, and fictional values.
SCAM_TEMPLATES = [
    "{brand}: your KYC update is pending. Visit {link} today or account access stops.",
    "KYC adhura hai! {brand} account band ho jayega. Abhi {link} par details update karo.",
    "Dear {name}, KYC failed. Share OTP {code} with our agent now to keep your account active.",
    "Aapka wallet KYC pending hai, warna service block hogi. OTP {code} bhejo jaldi.",
    "{brand} security: enter your UPI PIN at {link} to receive your Rs {amount} refund.",
    "UPI payment reverse karne ke liye apna PIN {code} share karo. Request urgent hai.",
    "Your payment is stuck. Read OTP {code} to support to release Rs {amount}.",
    "Refund pending hai. Paise receive karne ke liye UPI PIN daalo at {link}.",
    "Congratulations! You won the {brand} lucky draw worth Rs {amount}. Claim at {link}.",
    "Aapka naam prize list mein hai! Rs {amount} jeetne ke liye processing fee bhejo.",
    "Lottery winner notice: pay Rs {fee} tax before collecting your {brand} reward.",
    "Final prize notice: claim Rs {amount} now by sending your bank OTP {code}.",
    "Work from home: earn Rs {amount} daily with no interview. Pay joining fee first.",
    "Selected for a {brand} job! Deposit Rs {fee} for a refundable ID card today.",
    "Ghar baithe daily income pakki! Registration ke liye Rs {fee} bhejo, limited seats.",
    "Easy part-time job available. Send details and OTP {code} to start earning.",
    "Your courier parcel is held. Pay Rs {fee} customs charge at {link} immediately.",
    "Delivery failed for parcel {parcel}. Confirm your address at {link} within 30 minutes.",
    "Aapka parcel rok diya gaya hai. Fee pay karo warna return ho jayega: {link}.",
    "Bank alert: suspicious activity. Verify your card PIN at {link} to prevent debit.",
    "Your {brand} account is blocked. Call {phone} and share OTP {code} to restore it.",
    "URGENT: account access ends today. Login at {link} or funds will be frozen.",
    "Aaj hi bank account band hoga! OTP {code} batao aur turant unblock karao.",
    "Your SIM-linked bank account will be suspended. Confirm details now: {link}.",
    "Security team found a failed login. Install support app from {link} to secure account.",
    "Last warning: {brand} account freeze in 10 minutes. Verify at {shortlink}.",
    "Claim pending cashback at {shortlink}; offer expires in 15 minutes.",
    "Parcel needs address correction. Open {shortlink} and pay Rs {fee}.",
    "KYC update ke liye short link kholo {shortlink}, account safe ho jayega.",
    "Bank refund ready hai, short link {shortlink} par OTP {code} enter karo.",
    "Electricity service disconnect today. Pay bill at {shortlink} immediately.",
    "Your {brand} card will expire. Verify your password and OTP at {link}.",
    "Send Rs {fee} now and we will return Rs {amount} in ten minutes. Offer only for today.",
    "Apna OTP {code} batao, main bank se bol raha hoon. Account verify karna hai.",
    "Account block ho gaya hai. UPI PIN bhejo, refund turant aa jayega.",
    "Your bank team needs your CVV to cancel a failed transaction. Reply now.",
    "Parcel release ke liye Rs {fee} bhejo. Customs agent wait kar raha hai.",
    "OTP do",
    "PIN bhejo",
    "Install our support app to remove the account hold. Download the APK from {shortlink}.",
    "Your account is frozen. Call our bank officer at {phone} and read the OTP.",
]

SAFE_TEMPLATES = [
    "Your {brand} order is out for delivery today. Track it in the official app.",
    "Parcel update: your package is expected tomorrow around {time}.",
    "Aapka parcel kal deliver hoga. Tracking official app mein dekh sakte ho.",
    "Delivery attempted for parcel {parcel}. The courier will try again tomorrow.",
    "Your {brand} parcel was delivered to the building reception at {time}.",
    "OTP {code} is for sign-in. Do not share this code with anyone, including support staff.",
    "Your one-time code is {code}. Do not share it; our team will never ask for it.",
    "Login OTP {code} requested. If this wasn't you, ignore this message and do not share it.",
    "Aapka OTP {code} login ke liye hai. Kisi ke saath share mat karna.",
    "Bank notice: Rs {amount} spent at {shop} using your card ending {digits}.",
    "Your UPI payment of Rs {amount} to {shop} is complete at {time}.",
    "Rs {amount} credited to your {brand} account. Check the official banking app.",
    "Transaction alert: Rs {amount} withdrawn from account ending {digits}.",
    "Aapke account mein Rs {amount} jama hue. Details official bank app mein check karo.",
    "Your appointment at {clinic} is confirmed for {day} at {time}.",
    "Reminder: your check-up at {clinic} is tomorrow at {time}.",
    "Doctor {name} ke saath appointment {day}, {time} par hai. Clinic ko call karein.",
    "Your library study room booking is confirmed for {day} at {time}.",
    "Hey {name}, chai after class today? Meet near the campus garden around {time}.",
    "Thanks for sharing the notes! I will return your book tomorrow.",
    "Kal movie ke liye free ho? Main tickets le lunga, baad mein decide karte hain.",
    "I left your lunch box with the front desk. Pick it up when you get back.",
    "Aaj class ke baad library chalna? Exam ke notes revise karne hain.",
    "Study group is meeting in room {room} at {time}. See you there!",
    "Your electricity bill receipt for Rs {amount} is in the official provider app.",
    "The {brand} branch will be closed on {day} for a public holiday.",
    "Your salary credit of Rs {amount} is recorded. View the statement in the bank app.",
    "Parcel pickup is available with your order receipt at the post counter.",
    "Your class registration is complete. The timetable is on the college portal.",
    "Meeting reminder: community club gathering at {time} in the campus hall.",
    "Aapka appointment confirm hai. Clinic par {time} se 10 minute pehle aa jaana.",
    "Your card payment at {shop} was declined. Contact your bank using the number on your card.",
    "Hi, reached home? Let me know when you can.",
    "Okay, see you soon. Bring the blue notebook.",
    "Your bank alert: Rs {amount} was debited at {shop}. This is an automated transaction notice.",
    "Your account was credited Rs {amount}. No action is needed; check the official banking app.",
    "Your UPI payment of Rs {amount} to {shop} is complete. Keep this receipt for your records.",
    "OTP {code} is for your sign-in. Do not share it with anyone; our team will never ask for it.",
    "Aapke khate se Rs {amount} kat gaye at {shop}. Yeh transaction alert hai, reply karne ki zaroorat nahi.",
    "Courier update: parcel {parcel} is arriving tomorrow. No payment is due.",
    "The bank will never ask you to share an OTP. This message is a safety reminder.",
    "Your appointment is confirmed for {day} at {time}. Please bring your booking reference.",
    "Rs {amount} received from {shop}. See the transaction in your official app.",
    "Reminder: your parcel is ready for pickup. Bring the receipt to the post counter.",
]

VALUES = {
    "brand": ["MangoLeaf Bank", "BlueKite Wallet", "Nila Post", "CedarPay", "Orbit Parcel", "Saffron Credit"],
    "name": ["Aarav", "Meera", "Kabir", "Tara", "Ishaan", "Naina", "Dev", "Pihu"],
    "link": ["https://verify.example/kyc", "https://help.example/check", "https://claim.example/now"],
    "shortlink": ["https://t.example/a7Q", "https://x.example/9mP", "https://s.example/k2B"],
    "code": ["184206", "572913", "630481", "291750", "804362"],
    "amount": ["450", "1,250", "8,000", "21,500", "999"],
    "fee": ["49", "99", "250", "499", "1,000"],
    "phone": ["+91-00000-10001", "+91-00000-20002", "+91-00000-30003"],
    "parcel": ["EX-1042", "EX-2718", "EX-6305", "EX-8119"],
    "time": ["9:30 AM", "11:00 AM", "2:15 PM", "4:45 PM", "6:00 PM"],
    "shop": ["Cobalt Cafe", "Paper Boat Books", "Juniper Mart", "Campus Canteen"],
    "digits": ["1042", "2718", "6305", "8119"],
    "clinic": ["Lotus Lane Clinic", "Cedar Grove Dental", "Blue Sky Health Centre"],
    "day": ["Monday", "Tuesday", "Wednesday", "Friday", "Saturday"],
    "room": ["204", "B-12", "3A", "Library 2"],
}

def make_messages(templates: list[str], label: str, count: int, rng: random.Random) -> list[dict[str, str]]:
    """Fill templates with fictional values and avoid duplicate messages."""
    messages: set[str] = set()
    while len(messages) < count:
        template = rng.choice(templates)
        values = {key: rng.choice(options) for key, options in VALUES.items()}
        message = template.format(**values)
        if rng.random() < 0.35:
            message = rng.choice([message, message.lower(), message.replace(".", "!", 1)])
        messages.add(message)
    return [{"text": message, "label": label} for message in messages]

def main() -> None:
    """Write 400 balanced rows and print class counts."""
    rng = random.Random(RANDOM_SEED)
    rows = make_messages(SCAM_TEMPLATES, "scam", 200, rng)
    rows.extend(make_messages(SAFE_TEMPLATES, "safe", 200, rng))
    rng.shuffle(rows)
    with OUTPUT_FILE.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["text", "label"])
        writer.writeheader()
        writer.writerows(rows)
    counts = {label: sum(row["label"] == label for row in rows) for label in ("scam", "safe")}
    print(f"Wrote {len(rows)} messages to {OUTPUT_FILE}")
    print(f"Label counts: scam={counts['scam']}, safe={counts['safe']}")

if __name__ == "__main__":
    main()
