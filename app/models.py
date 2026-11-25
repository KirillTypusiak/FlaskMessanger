import flask_login
from app.database import DATABASE as DB
from app.settings import LOGIN_MANAGER

class User(DB.Model, flask_login.UserMixin):
    id = DB.Column(DB.Integer, primary_key = True)
    email = DB.Column(DB.String, unique = True, nullable=False)
    
    password_hash = DB.Column(DB.String, nullable=False)

    first_name = DB.Column(DB.String)
    last_name = DB.Column(DB.String)
    username = DB.Column(DB.String, unique=True)
    gender = DB.Column(DB.Boolean)
    birth_date = DB.Column(DB.Date)
    avatar_path = DB.Column(DB.String)
    is_verified = DB.Column(DB.Boolean, default=False, nullable=False)
    last_verification_sent_at = DB.Column(DB.DateTime, nullable=True)


@LOGIN_MANAGER.user_loader
def load_user(user_id):
    return DB.session.get(User, int(user_id))
 