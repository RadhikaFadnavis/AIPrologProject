# email_security_checks.py
import re
from email.utils import parseaddr

def extract_email(address):
    """Extract email from a full From/Return-Path line."""
    return parseaddr(address)[1].lower()

def is_spoofed_email(from_header, return_path_header):
    from_email = extract_email(from_header)
    return_path_email = extract_email(return_path_header)
    return from_email and return_path_email and from_email != return_path_email

def check_spf_dkim(auth_results_header):
    """Return SPF and DKIM status based on Authentication-Results header."""
    auth_results = auth_results_header.lower()
    spf_failed = "spf=fail" in auth_results
    dkim_failed = "dkim=fail" in auth_results
    return spf_failed, dkim_failed

def looks_like_typosquatting(email):
    """Detects domain name manipulation (basic check)."""
    legit_domains = ["amazon.com", "google.com", "paypal.com"]
    domain = email.split('@')[-1].lower()
    for legit in legit_domains:
        if (legit.replace('o', '0') in domain or
            legit.replace('a', '@') in domain or
            legit.replace('l', '1') in domain):
            return True
    return False

def analyze_headers(headers):
    """Run all spoofing checks and return matched issues."""
    matched_rules = []
    
    from_email = headers.get("From", "")
    return_path = headers.get("Return-Path", "")
    auth_results = headers.get("Authentication-Results", "")

    if is_spoofed_email(from_email, return_path):
        matched_rules.append("spoofed_address")

    spf_failed, dkim_failed = check_spf_dkim(auth_results)
    if spf_failed:
        matched_rules.append("spf_failed")
    if dkim_failed:
        matched_rules.append("dkim_failed")

    sender_email = extract_email(from_email)
    if looks_like_typosquatting(sender_email):
        matched_rules.append("typo_domain")

    return matched_rules
