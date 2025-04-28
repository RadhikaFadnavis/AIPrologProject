# spam_detector.py
from gmailconnect import fetch_unread_emails  # Import the function
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

def check_sender_blacklist(sender):
    prolog = Prolog()
    prolog.consult('blacklist.pl')
    query = list(prolog.query(f"blacklisted_sender('{sender}')"))
    return bool(query)


def clean_text(text):
    return re.sub(r'\W+', ' ', text).lower()

def predict_spam_ml(message):
    print("Inside predict_spam_ml")
    processed_message = clean_text(message)
    print("ml_model.predict([processed_message])", ml_model.predict([processed_message]))
    return ml_model.predict([processed_message])[0]

def classify_message(message, sender=None):
    # If sender is blacklisted, immediately classify as Spam
    if sender and check_sender_blacklist(sender):
        print("Blacklisted sender, declaring spam")
        return "Spam"
    
    if check_prolog_spam(get_matched_rules(message)):
        print("Prolog rules matched")
        return "Spam"
    else:
        print("Prolog rules not matched. Running ML models.")

    is_spam = predict_spam_ml(message)

    if is_spam:
        print("Spam detected by ML model. Updating Prolog rules...")
        return "Spam (ML Model used)"

    return "Not Spam"

# === MAIN DRIVER ===
if __name__ == "__main__":
    print("Fetching unread emails...")
    emails = fetch_unread_emails()  # Get unread messages

    for idx, msg in enumerate(emails):
        print(f"\n>> EMAIL #{idx+1} <<")
        print(f"Content: {msg[:900]}")  # Optional: limit long text
        result = classify_message(msg)
        print(f"==> Classification Result: {result}")
