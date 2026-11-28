import flask_login
import os
from dotenv import load_dotenv
from .settings import main_app
from .models import User
from .database import DATABASE

load_dotenv()

main_app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

LOGIN_MANAGER = flask_login.LoginManager(
    app = main_app
)

LOGIN_MANAGER.login_view = "chat.render_auth"
LOGIN_MANAGER.login_message = None

@LOGIN_MANAGER.user_loader 
def load_user(user_id):
    user = DATABASE.session.get(User, int(user_id))
    if user is not None and user.is_verified:
        return User.query.get(user_id)