# spam_detector.py
from gmailconnect import fetch_unread_emails  # Import the function
from email_security_checks import analyze_headers
from pyswip import Prolog
import joblib
import re

prolog = Prolog()
prolog.consult("spam_rules.pl")
ml_model = joblib.load("spam_model.pkl")

# def check_prolog_spam(message):
#     query = f'is_spam("{message.lower()}").'
#     return bool(list(prolog.query(query)))

def check_prolog_spam(matched_rules):
    
    if len(matched_rules) >= 2:
        print("Matched Prolog Rules:", ", ".join(matched_rules))
        
    else:
        return False
    

def get_matched_rules(message):
    """Check if a message is spam using Prolog rules and print matched rules."""
    message_escaped = message.replace('"', '')  # Escape quotes
    rules_to_check = [
        "contains_spam_keyword",
        "contains_link",
        "all_caps",
        "excessive_punctuation",
        "contains_currency_symbol",
        "contains_phone_number"
    ]

    matched_rules = []

    for rule in rules_to_check:
        query = f'{rule}("{message_escaped}")'
        try:
            result = list(prolog.query(query))
            if result:
                matched_rules.append(rule)
        except Exception as e:
            print(f"Error querying {rule}: {e}")

    return matched_rules

    


def clean_text(text):
    return re.sub(r'\W+', ' ', text).lower()

def predict_spam_ml(message):
    print("Inside predict_spam_ml")
    processed_message = clean_text(message)
    print("ml_model.predict([processed_message])", ml_model.predict([processed_message]))
    return ml_model.predict([processed_message])[0]

def classify_message(message):
    if check_prolog_spam(get_matched_rules(message)):
        return "Spam (Prolog Rules Matched)"
    else:
        print("Prolog rules not matched. Running ML models.")

    is_spam = predict_spam_ml(message)

    if is_spam:
        print("Spam detected by ML model. Updating Prolog rules...")
        return "Spam (ML Model Detected & Updated Prolog)"

    return "Not Spam"


sample_email = {
    "from": "Amazon Security <support@amaz0n-secure.com>",
    "subject": "URGENT: Update your credit card information now!",
    "body": """
        Dear Customer,

        Your account has been temporarily suspended due to suspicious activity.
        To restore access, please update your credit card information immediately.

        Click here: http://amaz0n-secure.com/verify

        Thank you,
        Amazon Security Team
    """,
    "headers": {
        "From": "Amazon Security <support@amaz0n-secure.com>",
        "Return-Path": "<spoofed@otherdomain.xyz>",
        "Authentication-Results": "spf=fail smtp.mailfrom=otherdomain.xyz; dkim=fail header.d=amaz0n-secure.com;",
        "Received-SPF": "fail (gmail.com: domain of otherdomain.xyz does not designate 123.456.789.000 as permitted sender)"
    }
}

# === MAIN DRIVER ===
if __name__ == "__main__":
    print("Fetching unread emails...")
    emails = [sample_email]  # Get unread messages

    for idx, email_data in enumerate(emails):
        print(f"\n>> EMAIL #{idx+1} <<")
        sender = email_data["from"]
        subject = email_data["subject"]
        body = email_data["body"]
        headers = email_data["headers"]

        # Combine for classification
        full_message = f"{sender}\n{subject}\n{body}"

        # Check Prolog + ML + Header analysis
        rules_triggered = get_matched_rules(full_message)

        # Add spoofing/header rules
        spoof_flags = analyze_headers(headers)
        rules_triggered.extend(spoof_flags)

        result = classify_message(full_message)  # Update this to accept rules_triggered if needed
        print(f"==> Classification Result: {result}")

