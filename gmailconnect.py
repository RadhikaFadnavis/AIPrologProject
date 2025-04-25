# email_fetcher.py
import imaplib
import email
from email.header import decode_header
import html2text

def fetch_unread_emails():
    EMAIL = "aiprojectfinalyear@gmail.com"
    APP_PASSWORD = "tpih yjxj gsib eixs"

    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(EMAIL, APP_PASSWORD)
    imap.select("inbox")

    status, messages = imap.search(None, 'UNSEEN')
    email_ids = messages[0].split()
    print(f"Found {len(email_ids)} new email(s)")

    fetched_emails = []

    for mail_id in email_ids:
        res, msg_data = imap.fetch(mail_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or "utf-8")
                from_ = msg.get("From")
                
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        ctype = part.get_content_type()
                        if ctype == "text/plain" and "attachment" not in part.get("Content-Disposition", ""):
                            body = part.get_payload(decode=True).decode()
                            break
                        elif ctype == "text/html":
                            html = part.get_payload(decode=True).decode()
                            body = html2text.html2text(html)
                            break
                else:
                    body = msg.get_payload(decode=True).decode()

                print("\n--- EMAIL ---")
                print("From:", from_)
                print("Subject:", subject)
                print("Body:\n", body[:900])  # Show only first 900 chars

                # Update fetched_emails.append(body) to:
                fetched_emails.append({
                    "from": from_,
                    "subject": subject,
                    "body": body,
                    "headers": dict(msg.items())
                })


    imap.logout()
    return fetched_emails
