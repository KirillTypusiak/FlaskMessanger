from flask import render_template
import flask
from .app import chat_app_blueprint
import werkzeug.security
from app.database import DATABASE
from app.models import User
import flask_login
from .tokens import generate_token, verify_token
from .email_sender import send_verification_email
from .mail_provider import get_mail_url
from datetime import datetime, timedelta, timezone
import smtplib
import math


@chat_app_blueprint.route("/reg", methods=["GET", "POST"])
def render_registration():
    if flask_login.current_user.is_authenticated:
        return flask.redirect("/")

    user_id = flask.session.get("pending_user_id")

    if user_id is not None:
        user = DATABASE.session.get(User, user_id)
        if user is not None:
            return flask.redirect("/waiting")
        else:
            flask.session.pop("pending_user_id", None)
        
    if flask.request.method == "POST":
        email = flask.request.form.get("email")
        password = flask.request.form.get("password")
        confirm_password = flask.request.form.get("confirm_password")
        
        if email and password and confirm_password:
            if password != confirm_password:
                data = {
                    "error": "Паролі не збігаються",
                    "email": email,
                }
                return flask.render_template("register.html", **data)
            if len(password) < 8:
                data = {
                    "error": "Пароль має містити щонайменше 8 символів.",
                    "email": email,
                }
                return flask.render_template("register.html", **data)
            
            existing_user = User.query.filter_by(email=email).first()
            if existing_user is not None:
                data = {
                    "error": "Ця електронна пошта вже зареєстрована.",
                    "email": email,
                }
                return flask.render_template("register.html", **data)
            
            password_hash = werkzeug.security.generate_password_hash(password)
            
            user = User(
                email = email, 
                password_hash = password_hash
            )
            
            DATABASE.session.add(user)
            DATABASE.session.commit()
            
            flask.session["pending_user_id"] = user.id
            
            
            token = generate_token(user.id)
            access_url = flask.url_for("chat.verify_email", token=token, _external=True)
            
            try:
                send_verification_email(user.email, access_url)
            except (smtplib.SMTPException, OSError) as error:
                flask.flash("Не вдалося надіслати лист. Спробуйте ще раз.", "error")
            else:
                user.last_verification_sent_at = datetime.now(timezone.utc).replace(tzinfo=None)
                DATABASE.session.commit()
            
            return flask.redirect(flask.url_for("chat.waiting_verification"))
        else:
            data = {
                "error": "Заполните все обязательные поля",
                "email": email,
            }
            return flask.render_template("register.html", **data)
        
    return render_template("register.html")

@chat_app_blueprint.route("/")
@flask_login.login_required
def render_home():
    return render_template("home.html")

@chat_app_blueprint.route("/verify/<token>")
def verify_email(token):
    user_id = verify_token(token)
    if user_id is None:
        return render_template(
            "verification_result.html",
            title="Помилка",
            description="Посилання недійсне або термін його дії минув.",
            success=False
        ), 400
    
    user = DATABASE.session.get(User, user_id)
    
    if user is None:
        return render_template(
            "verification_result.html",
            title="Помилка",
            description="Обліковий запис не знайдено.",
            success=False
        ), 404
    
    if user.is_verified:
        return render_template(
            "verification_result.html",
            title="Пошту підтверджено",
            description="Ви вже підтвердили свою електронну пошту.",
            success=True
        )
    
    user.is_verified = True
    DATABASE.session.commit()
    return render_template(
        "verification_result.html",
        title="Успіх",
        description="Вашу електронну пошту успішно підтверджено!",
        success=True
    )

@chat_app_blueprint.route("/waiting")
def waiting_verification():
    remaining_seconds = 0
    if flask_login.current_user.is_authenticated:
        return flask.redirect("/")
    
    user_id = flask.session.get("pending_user_id")
    if user_id is None:
        return flask.redirect("/reg")
    
    user = DATABASE.session.get(User, user_id)
    
    if user is None:
        flask.session.pop("pending_user_id", None)
        return flask.redirect("/reg")
    
    if not user.is_verified:
        if user.last_verification_sent_at is not None:
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            elapsed = (now - user.last_verification_sent_at).total_seconds()
            remaining_seconds = max(0, math.ceil(60 - elapsed))
        mail_url = get_mail_url(user.email)
        data = {
            "mail_url": mail_url,
            "remaining_seconds": remaining_seconds
        }
        return render_template("waiting_screen.html", **data)
    
    else:
        flask_login.login_user(user)
        flask.session.pop("pending_user_id", None)
        return flask.redirect("/")
    
@chat_app_blueprint.route("/verification_status")
def verification_status():
    user_id = flask.session.get("pending_user_id")
    
    if user_id is None:
        return flask.jsonify({"error": "user_id not found"}), 401
    
    user = DATABASE.session.get(User, user_id)
    
    if user is None:
        return flask.jsonify({"error": "user is not found"}), 404 
    
    return flask.jsonify({"verified": user.is_verified})

@chat_app_blueprint.route("/resend_verification", methods=["POST"])
def resend_verification():
    user_id = flask.session.get("pending_user_id")
    
    if user_id is None:
        return flask.jsonify({"error": "user_id not found"}), 401
    
    user = DATABASE.session.get(User, user_id)
    
    if user is None:
        return flask.jsonify({"error": "user is not found"}), 404 
    
    if user.is_verified:
        return flask.jsonify({"error": "Email already verified"}), 409
    
    if user.last_verification_sent_at is not None:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        elapsed = now - user.last_verification_sent_at
        
        if elapsed < timedelta(seconds=60):
            remaining_seconds = max(0, math.ceil(60 - elapsed.total_seconds()))
            return flask.jsonify({"error": "Too many requests", "remaining_seconds": remaining_seconds}), 429
        
    token = generate_token(user_id)
    access_url = flask.url_for("chat.verify_email", token=token, _external=True)
    try:
        send_verification_email(user.email, access_url)
        
    except (smtplib.SMTPException, OSError) as error:
        return flask.jsonify({"error": "Failed to send email"}), 503
    else:
        user.last_verification_sent_at = datetime.now(timezone.utc).replace(tzinfo=None)
        DATABASE.session.commit()
    return flask.jsonify({"success": True})