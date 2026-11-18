DOMENS = {
    "gmail.com": "https://mail.google.com/",
    "ukr.net": "https://mail.ukr.net/",
    "outlook.com": "https://outlook.live.com/mail/",
    "hotmail.com": "https://outlook.live.com/mail/",
    "yahoo.com": "https://mail.yahoo.com/",
    "icloud.com": "https://www.icloud.com/mail/",
    "proton.me": "https://mail.proton.me/"
}

def get_mail_url(email: str):
    return DOMENS.get(email.split("@")[-1].lower(), None)