"""Train and use a local scam-message classifier.

Run python model.py to evaluate the data and save model.pkl.
"""

import csv
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import FeatureUnion, Pipeline

from rules import find_red_flags

DATA_FILE = Path(__file__).parent / "data" / "messages.csv"
CHALLENGE_FILE = Path(__file__).parent / "data" / "challenge_messages.csv"
MODEL_FILE = Path(__file__).parent / "model.pkl"

def combine_score(scam_probability: float, red_flag_count: int) -> float:
    """Blend the model estimate and explicit warning signs into one risk score."""
    return min(1.0, scam_probability * 0.55 + min(0.66, red_flag_count * 0.22))

def risk_from_score(score: float) -> str:
    """Map a combined score to the app's three risk levels."""
    if score >= 0.70:
        return "High"
    if score >= 0.40:
        return "Medium"
    return "Low"

def load_training_data():
    """Read the bundled examples; no network or external service is used."""
    with DATA_FILE.open(encoding="utf-8", newline="") as data_file:
        rows = list(csv.DictReader(data_file))
    return [row["text"] for row in rows], [row["label"] for row in rows]

def build_classifier() -> Pipeline:
    """Create word/character TF-IDF features followed by logistic regression."""
    # TF-IDF turns words or character chunks into numbers. Common words count
    # less, while useful distinctive patterns count more. Character chunks help
    # recognize spelling variations, short tokens, and mixed-language text.
    features = FeatureUnion([
        ("word_tfidf", TfidfVectorizer(
            analyzer="word", ngram_range=(1, 2), lowercase=True,
            strip_accents="unicode", sublinear_tf=True,
        )),
        ("char_tfidf", TfidfVectorizer(
            analyzer="char", ngram_range=(2, 5), lowercase=True,
            strip_accents="unicode", min_df=1, sublinear_tf=True,
        )),
    ])
    # Logistic regression learns weights for the numeric patterns and combines
    # them into class probabilities. It is a simple, fast classification model.
    return Pipeline([
        ("features", features),
        ("classifier", LogisticRegression(
            max_iter=1500, class_weight="balanced", random_state=42,
        )),
    ])

def train_model() -> Pipeline:
    """Evaluate on a held-out split, then fit all rows and save model.pkl."""
    messages, labels = load_training_data()
    x_train, x_test, y_train, y_test = train_test_split(
        messages, labels, test_size=0.2, random_state=42, stratify=labels,
    )
    evaluation_model = build_classifier()
    evaluation_model.fit(x_train, y_train)
    predictions = evaluation_model.predict(x_test)
    print(f"Accuracy:  {accuracy_score(y_test, predictions):.3f}")
    print(f"Precision: {precision_score(y_test, predictions, pos_label='scam', zero_division=0):.3f}")
    print(f"Recall:    {recall_score(y_test, predictions, pos_label='scam', zero_division=0):.3f}")
    print("Confusion matrix (rows=true [safe, scam], columns=predicted [safe, scam]):")
    print(confusion_matrix(y_test, predictions, labels=["safe", "scam"]))

    # Refit on every example after evaluation so the saved model learns from
    # all available data. The reported metrics come only from the held-out set.
    final_model = build_classifier()
    final_model.fit(messages, labels)
    joblib.dump(final_model, MODEL_FILE)
    print(f"Saved trained model to {MODEL_FILE}")
    evaluate_challenge_set(final_model)
    return final_model

def evaluate_challenge_set(classifier: Pipeline) -> None:
    """Report risk accuracy on separate tricky examples not used for training."""
    with CHALLENGE_FILE.open(encoding="utf-8", newline="") as challenge_file:
        rows = list(csv.DictReader(challenge_file))
    texts = [row["text"] for row in rows]
    labels = [row["label"] for row in rows]
    scam_index = list(classifier.classes_).index("scam")
    probabilities = classifier.predict_proba(texts)[:, scam_index]
    predictions = []
    for text, probability in zip(texts, probabilities):
        flags = find_red_flags(text)
        score = combine_score(float(probability), len(flags))
        predictions.append("scam" if risk_from_score(score) != "Low" else "safe")
    print(f"Tricky-message risk accuracy: {accuracy_score(labels, predictions):.3f} ({len(rows)} messages)")
    print("Tricky-message confusion matrix (rows=true [safe, scam], columns=predicted [safe, scam]):")
    print(confusion_matrix(labels, predictions, labels=["safe", "scam"]))

def predict(text: str) -> float:
    """Return the model's scam probability as a number from 0.0 to 1.0."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if not MODEL_FILE.exists():
        # First use in a fresh checkout trains locally and caches the pipeline.
        train_model()
    if not MODEL_FILE.exists():
        raise FileNotFoundError(f"Training did not create the model at {MODEL_FILE}.")
    classifier = joblib.load(MODEL_FILE)
    scam_index = list(classifier.classes_).index("scam")
    return float(classifier.predict_proba([text])[0][scam_index])

def check_message(message: str) -> dict:
    """Return a risk, the reasons found, and practical next steps."""
    if not isinstance(message, str):
        raise TypeError("message must be a string")
    if not message.strip():
        return {
            "risk": "Low",
            "score": 0.0,
            "red_flags": [],
            "summary": "Enter a message to check its warning signs.",
            "advice": [],
        }
    flags = find_red_flags(message)
    scam_probability = predict(message)
    # Blend the model with explicit rules; requests and other direct signals
    # have a strong effect, while harmless wording alone is less likely to alarm.
    score = combine_score(scam_probability, len(flags))
    risk = risk_from_score(score)
    if risk == "High":
        summary = "This message has several strong warning signs. Treat it as suspicious."
    elif risk == "Medium":
        summary = "This message has some warning signs. Verify it before taking action."
    else:
        summary = "Few common scam signals were found, but a low score cannot confirm safety."
    advice = [
        "Do not share an OTP, UPI PIN, password, or card details, and do not install remote-access apps.",
        "Avoid links and phone numbers in the message. Contact the bank, courier, or employer using its official app or website.",
    ]
    if risk == "High":
        advice.append("If you already paid or shared details, contact your bank immediately and report cyber financial fraud by calling 1930 in India.")
    return {"risk": risk, "score": round(score, 3), "red_flags": flags, "summary": summary, "advice": advice}

if __name__ == "__main__":
    train_model()
