import flask
import flask_login
import os
import dotenv
 
dotenv.load_dotenv()
 
main_app = flask.Flask(
    import_name = "app",
)
 
main_app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
 
LOGIN_MANAGER = flask_login.LoginManager(main_app)

LOGIN_MANAGER.login_view = "chat.render_login"
 