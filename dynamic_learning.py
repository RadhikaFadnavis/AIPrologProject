# dynamic_learning.py


import joblib
import re
from sklearn.feature_extraction.text import TfidfVectorizer


ml_model = joblib.load('spam_model.pkl')


def clean_text(text):
    return re.sub(r'\W+', ' ', text).lower()


def predict_spam_ml(message):
    processed_message = clean_text(message)
    return ml_model.predict([processed_message])[0]


def extract_important_keywords(text, top_n=3):
    """Extract top N keywords using TF-IDF."""
    text = clean_text(text)
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform([text])
    feature_array = tfidf.get_feature_names_out()
    tfidf_sorting = tfidf_matrix.toarray().flatten().argsort()[::-1]
    top_keywords = [feature_array[i] for i in tfidf_sorting[:top_n]]
    return top_keywords


def keyword_already_exists(keyword):
    """Check if a keyword rule already exists."""
    try:
        with open('keywords.pl', 'r') as f:
            rules = f.read()
            return keyword.lower() in rules.lower()
    except FileNotFoundError:
        return False


def update_prolog_rules(new_keywords):
    """Add new spam keywords to Prolog rules, avoiding duplicates."""
    try:
        with open('keywords.pl', 'a') as f:
            for keyword in new_keywords:
                if not keyword_already_exists(keyword):
                    rule = f'spam_keyword("{keyword}").\n'
                    f.write(rule)
                    print(f"✅ Added new Prolog rule for keyword: '{keyword}'")
                else:
                    print(f"⚡ Keyword '{keyword}' already exists. Skipping.")
    except Exception as e:
        print(f"Error updating Prolog rules: {e}")
