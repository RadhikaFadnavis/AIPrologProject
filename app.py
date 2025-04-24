from flask import Flask, render_template, request, redirect, url_for, jsonify
from spam_detector import classify_message, get_matched_rules
from gmailconnect import fetch_unread_emails

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    message = ''
    matched_rules = []

    if request.method == 'POST':
        message = request.form['message']
        result = classify_message(message)
        matched_rules = get_matched_rules(message)

    return render_template('index.html', result=result, message=message, matched_rules=matched_rules)


@app.route('/fetch_emails')
def fetch_emails():
    emails = fetch_unread_emails()
    results = []
    for email_body in emails:
        classification = classify_message(email_body)
        rules = get_matched_rules(email_body)
        results.append({
            "message": email_body[:300] + "...",
            "result": classification,
            "rules": rules
        })
    return render_template('email_results.html', results=results)


@app.route('/stats_data')
def stats_data():
    emails = fetch_unread_emails()
    spam_count = 0
    not_spam_count = 0
    for email_body in emails:
        res = classify_message(email_body)
        if "Spam" in res:
            spam_count += 1
        else:
            not_spam_count += 1
    return jsonify({"spam": spam_count, "not_spam": not_spam_count})


@app.route('/stats_chart')
def stats_chart():
    return render_template('chart.html')

if __name__ == '__main__':
    app.run(debug=True)
