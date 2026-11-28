import flask
import os
from datetime import timedelta

main_app = flask.Flask(
    import_name = "app",
)

main_app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=7)
main_app.config["REMEMBER_COOKIE_REFRESH_EACH_REQUEST"] = True
