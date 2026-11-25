from flask import render_template, request, redirect, url_for
from flask_login import login_user, login_required
from werkzeug.security import check_password_hash

from app.models import User
from .app import chat_app_blueprint


@chat_app_blueprint.route("/reg")
def render_registration():
    return render_template("register.html")


@chat_app_blueprint.route("/home")
def render_home():
    return render_template("home.html")


@chat_app_blueprint.route("/login")
def render_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            return render_template("login.html", error="Заповніть усі поля")

        user = User.query.filter_by(email=email).first()

        if user is None or not check_password_hash(user.password_hash, password):
            return render_template("login.html", error="Невірний email або пароль")

        login_user(user)
        return redirect(url_for("chat.render_chat"))

    return render_template("login.html")


@chat_app_blueprint.route("/chat")
@login_required
def render_chat():
    return render_template("chat.html")