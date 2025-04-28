from flask import Flask, render_template, request, redirect, url_for, jsonify
from pyswip import Prolog
from spam_detector import classify_message, get_matched_rules, check_sender_blacklist
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
    for email_data in emails:
        message_text = email_data["body"]  # ✅ get just the message
        sender_email = email_data["sender"]  # ✅ get sender

        classification = classify_message(message_text, sender_email)

        rules = get_matched_rules(message_text)
        blacklisted = check_sender_blacklist(sender_email)
        results.append({
            "message": message_text[:300] + "...",  # Truncate body
            "sender": sender_email,                 # Pass sender
            "result": classification,
            "rules": rules,
            "blacklisted": blacklisted
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

@app.route('/blacklist', methods=['POST'])
def blacklist_sender():
    sender = request.form['sender']
    
    # Append to blacklist.pl
    with open('blacklist.pl', 'a') as f:
        f.write(f"blacklisted_sender('{sender}').\n")
    
    # Reconsult Prolog so new rules are loaded
    Prolog.consult('blacklist.pl')
    
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
