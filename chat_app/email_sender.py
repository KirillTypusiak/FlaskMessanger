import smtplib
import os
from email.message import EmailMessage
from dotenv import load_dotenv
from flask import render_template
from pathlib import Path

load_dotenv()

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

def send_verification_email(recipient_email, verification_url):
    message = EmailMessage()
    message["From"] = SMTP_EMAIL
    message["To"] = recipient_email
    message["Subject"] = "Підтвердження електронної пошти"
    
    
    context = {
        "verification_url": verification_url,
        "image_url": "cid:children_image"
    }
    html_content = render_template("verification_email.html", **context)
    
    message.set_content(f"""
            Вас вітає команда World IT !
            Щоб завершити реєстрацію та переконатися, що саме ви є власником цієї електронної адреси, будь ласка, підтвердіть свою пошту.

            Підтвердити пошту
            {verification_url}
            
            Якщо у вас виникнуть питання - ми завжди раді допомогти!
            З найкращими побажаннями, команда World IT Academy
                        """)
    message.add_alternative(html_content, subtype="html")
    
    image_path = Path(__file__).resolve().parent.parent / "app" / "static" / "images" / "ChildrenWithPc.png"
    
    with open(image_path, mode="rb") as file:
        img = file.read()
        html_part = message.get_payload()[-1]
        html_part.add_related(
            img,
            maintype="image",
            subtype="png",
            cid="<children_image>"
        )
    
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(message)

