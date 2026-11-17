from flask import render_template
from .app import chat_app_blueprint

@chat_app_blueprint.route("/reg")
def render_registration():
    return render_template("register.html")

@chat_app_blueprint.route("/home")
def render_home():
    return render_template("home.html")