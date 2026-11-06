# Scam Message Checker

An educational project for the Community Impact student AI hackathon. The app helps people pause and review suspicious SMS, WhatsApp, and email messages before they respond.

## The problem

Scam messages can impersonate banks, government services, courier companies, and employers. They may pressure people to share an OTP or UPI PIN, pay a fee, open a link, or install an app. These messages can be difficult to judge, especially when they use urgent language or mix English and Hindi.

## The solution

Paste a message into the local Streamlit app to get a Low, Medium, or High risk estimate, readable red flags, and practical next steps. The app combines a scikit-learn text classifier with editable keyword and regular-expression rules. It runs without a paid API; pasted text is not saved or sent to an outside service by the app.

## Features

- Color-coded Low, Medium, and High risk results.
- Red flags with names and plain-English explanations.
- Optional “Explain in simple words” summary based only on the model score and detected flags.
- Guided demo that types fictional examples and runs each through the live rules and model.
- Practical advice about links, OTPs, official bank contact details, and reporting cybercrime in India.
- Clickable sample messages, including safe notices and Hinglish examples.
- Local TF-IDF word and character features with Logistic Regression.
- Training metrics and a separate tricky-message benchmark.

## Install and run

Use Python 3.10 or newer. Open a terminal in the project folder and run:

~~~powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python data/generate_dataset.py
python model.py
streamlit run app.py
~~~

The generator writes 400 synthetic examples (200 scam and 200 safe) to data/messages.csv. The training command prints accuracy, scam precision and recall, confusion matrices, evaluates the separate challenge set, and saves the trained classifier to model.pkl.

In the app, select “Start guided demo” to see the example walkthrough. It uses fictional messages, the same live result renderer as the regular checker, and does not save or log message text.

Optional tests:

~~~powershell
pip install pytest
python -m pytest -q
~~~

## Tech stack

- Python for the application and data-generation script.
- Streamlit for the user interface.
- scikit-learn for TF-IDF features, Logistic Regression, and evaluation metrics.
- joblib for saving and loading the fitted classifier.
- Python's csv and re modules for reading the dataset and applying rules.

## Dataset

data/generate_dataset.py creates fictional messages using editable templates and fictional names, brands, amounts, and example domains. The generated data includes fake KYC and account warnings, OTP and UPI requests, prize claims, job offers, courier alerts, and safe delivery, transaction, OTP, appointment, and chat messages. Some examples use Hinglish.

data/challenge_messages.csv is a separate, small set of tricky examples. It includes genuine-sounding bank alerts, a safe OTP notice, a completed UPI payment, a delivery message, a very short chat, link-free scams, Hinglish, and very short scam text. These challenge examples are kept separate from the generated training data.

All examples are synthetic. They do not represent real people, companies, or actual messages.

## Model performance

In the latest local run:

- Generated-data held-out split: 100% accuracy, 100% scam precision, and 100% scam recall on 80 messages (40 safe and 40 scam).
- Separate tricky-message set: 100% risk accuracy on 10 messages (5 safe and 5 scam).

These are small educational checks, not evidence of real-world accuracy. The generated examples share templates, so the random held-out split can be overly optimistic. The challenge set is also too small to represent the variety of real messages. Treat both scores as snapshots of these specific examples, not a guarantee of performance.

## Limitations

- The model learns from a small, synthetic dataset and may not recognize new scam tactics, local language variations, or misspellings.
- Rules can produce false positives or miss subtle requests. A message with no detected flags is not necessarily safe.
- A risk score is guidance, not proof. Always verify through an organization's official app, website, or independently sourced phone number.
- No real-world, privacy-reviewed message corpus has been used to measure this project.
- The app does not store or log pasted messages, but users should still avoid entering private information into demos they do not control.

## AI tools used

OpenAI Codex was used as a coding assistant for project scaffolding, synthetic dataset generation, red-flag rules, tests, and app/documentation improvements. I reviewed, tested, and modified the code and checked the behavior against sample messages.

## What I learned

- TF-IDF turns text into numeric features a traditional machine-learning model can use.
- Word and character patterns help catch both familiar phrases and spelling variations.
- Simple rules make model results easier to explain, but broad rules can also create false alarms.
- A random train/test split can look excellent when examples are very similar; separate tricky examples help reveal weaknesses.
- A model score is an estimate and should be paired with careful, practical safety advice.

## What I'd build next

- Collect a larger, carefully reviewed dataset with consent and privacy protections.
- Add more regional-language and transliterated Hinglish examples.
- Evaluate on a larger, independently collected test set and report precision, recall, and false-positive rates by message type.
- Improve handling of message context, such as the difference between an OTP request and a safe “do not share your OTP” notice.
- Add clear feedback controls so users can report incorrect classifications without saving their original message.
- Explore a free, local language model behind the existing explanation interface, while keeping message text on-device.

## Credits

- Streamlit — app interface.
- scikit-learn — text features, classifier, and evaluation metrics.
- joblib — model persistence.
- pandas — Python data-analysis library acknowledged here; the current project reads CSV files with Python's built-in csv module and does not require pandas.
