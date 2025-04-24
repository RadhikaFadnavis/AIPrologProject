import pandas as pd
import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split

# Load dataset from CSV
df = pd.read_csv("emails.csv")  # Ensure 'emails.csv' is in the same directory

# Check if dataset has required columns
if "text" not in df.columns or "spam" not in df.columns:
    raise ValueError("CSV file must contain 'text' and 'spam' columns.")

# Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(df["text"], df["spam"], test_size=0.2, random_state=42)

# Create Text Processing + Naive Bayes Model Pipeline
model = make_pipeline(CountVectorizer(), MultinomialNB())

# Train Model
model.fit(X_train, y_train)

# Save Model
joblib.dump(model, "spam_model.pkl")

print("Spam detection model trained and saved as 'spam_model.pkl'.")
