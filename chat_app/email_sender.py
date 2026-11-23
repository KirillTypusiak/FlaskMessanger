"""
Відправка листа з підтвердженням email.

Головна функція модуля:
    send_verification_email(recipient_email, verification_url)

Усі SMTP-дані (сервер, порт, логін, пароль, відправник) беруться ТІЛЬКИ
зі змінних середовища або з файлу .env (він доданий у .gitignore).
У коді жодних паролів і логінів немає.

Змінні середовища (див. .env.example):
    SMTP_HOST       - адреса SMTP-сервера, напр. smtp.gmail.com     (обов'язково)
    SMTP_USER       - логін                                         (обов'язково)
    SMTP_PASSWORD   - пароль (для Gmail - пароль застосунку)        (обов'язково)
    SMTP_PORT       - порт: 587 для STARTTLS, 465 для SSL           (за замовч. 587)
    SMTP_SENDER     - адреса відправника                            (за замовч. = SMTP_USER)
    SMTP_USE_SSL    - "true" для порту 465                          (за замовч. false)
"""

import os
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import make_msgid
from pathlib import Path

from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader, select_autoescape

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
IMAGE_PATH = BASE_DIR.parent / "app" / "static" / "images" / "ChildrenWithPc.png"

# Власний Jinja-оточення, щоб функція працювала і без контексту Flask
# (наприклад, із фонового завдання або тесту).
_jinja_env = Environment(
    loader = FileSystemLoader(TEMPLATES_DIR),
    autoescape = select_autoescape(["html"]),
)


def _get_smtp_settings() -> dict:
    """Зчитує налаштування SMTP зі змінних середовища."""
    host = os.getenv("SMTP_HOST")
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")

    missing = [
        name for name, value in (
            ("SMTP_HOST", host),
            ("SMTP_USER", user),
            ("SMTP_PASSWORD", password),
        ) if not value
    ]
    if missing:
        raise RuntimeError(
            f"Не задані змінні середовища для SMTP: {', '.join(missing)}"
        )

    return {
        "host": host,
        "port": int(os.getenv("SMTP_PORT", "587")),
        "user": user,
        "password": password,
        "sender": os.getenv("SMTP_SENDER") or user,
        "use_ssl": os.getenv("SMTP_USE_SSL", "false").strip().lower() in ("1", "true", "yes"),
    }


def _build_message(sender: str, recipient_email: str, verification_url: str) -> EmailMessage:
    """Збирає лист: текстова версія + HTML з кнопкою + вкладена картинка."""
    message = EmailMessage()
    message["Subject"] = "Підтвердження електронної пошти"
    message["From"] = sender
    message["To"] = recipient_email

    # Текстова версія - для клієнтів, які не показують HTML
    message.set_content(
        "Вас вітає команда World IT!\n\n"
        "Щоб завершити реєстрацію та переконатися, що саме ви є власником "
        "цієї електронної адреси, підтвердіть свою пошту за посиланням:\n"
        f"{verification_url}\n\n"
        "Якщо ви не реєструвалися, просто проігноруйте цей лист.\n\n"
        "З найкращими побажаннями, команда World IT Academy"
    )

    has_image = IMAGE_PATH.is_file()
    image_cid = make_msgid(domain = "flaskmessanger")  # вигляд: <...@flaskmessanger>

    html = _jinja_env.get_template("verification_email.html").render(
        verification_url = verification_url,
        image_url = f"cid:{image_cid[1:-1]}" if has_image else None,
    )
    message.add_alternative(html, subtype = "html")

    # Картинка вбудовується в лист, тому показується без завантаження з інтернету
    if has_image:
        html_part = message.get_payload()[-1]
        html_part.add_related(
            IMAGE_PATH.read_bytes(),
            maintype = "image",
            subtype = "png",
            cid = image_cid,
        )

    return message


def send_verification_email(recipient_email: str, verification_url: str) -> None:
    """
    Відправляє лист із кнопкою підтвердження пошти.

    :param recipient_email: email отримувача
    :param verification_url: посилання підтвердження (на нього веде кнопка)
    :raises ValueError: якщо не передано email або посилання
    :raises RuntimeError: якщо не задані SMTP-налаштування у змінних середовища
    :raises smtplib.SMTPException | OSError: якщо лист не вдалося відправити
    """
    if not recipient_email or not verification_url:
        raise ValueError("Потрібно передати email отримувача і посилання підтвердження")

    settings = _get_smtp_settings()
    message = _build_message(settings["sender"], recipient_email, verification_url)
    context = ssl.create_default_context()

    if settings["use_ssl"]:
        with smtplib.SMTP_SSL(settings["host"], settings["port"], context = context, timeout = 15) as server:
            server.login(settings["user"], settings["password"])
            server.send_message(message)
    else:
        with smtplib.SMTP(settings["host"], settings["port"], timeout = 15) as server:
            server.starttls(context = context)
            server.login(settings["user"], settings["password"])
            server.send_message(message)
