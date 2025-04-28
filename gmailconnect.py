# gmailconnect.py
import imaplib
import email
from email.header import decode_header
import html2text

def fetch_unread_emails():
    EMAIL = "aiprojectfinalyear@gmail.com"
    APP_PASSWORD = "tpih yjxj gsib eixs"  # Replace with your real app password

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
                
                # Decode subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or "utf-8")
                
                # Get sender
                from_ = msg.get("From")
                # Optional: clean up sender (only email address)
                if "<" in from_ and ">" in from_:
                    from_ = from_.split("<")[1].split(">")[0].strip()

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

                # Append both sender and body
                fetched_emails.append({
                    "sender": from_,
                    "body": body
                })

    imap.logout()
    return fetched_emails
