import flask_login
from app.database import DATABASE as DB

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
    
    # chat = DB.relationship(
    #     "Chat",
    #     back_populates = "user",
    #     uselist = False
    # )
    
    # messages = DB.relationship(
    #     "Message",
    #     back_populates = "user",
    #     uselist = True
    # )
    
# class Chat(DB.Model):
#     id = DB.Column(DB.Integer, primary_key = True)
#     title = DB.Column(DB.String)
    
#     user_id = DB.Column(
#         DB.Integer, 
#         DB.ForeignKey("user.id", name="fk_chat_user_id")
#     )
    
#     user = DB.relationship(
#         "User",
#         back_populates = "chat"
#     )


# class Message(DB.Model):
#     id = DB.Column(DB.Integer, primary_key = True)
#     content = DB.Column(DB.String)
    
#     user_id = DB.Column(
#         DB.Integer, 
#         DB.ForeignKey("user.id", name="fk_message_user_id")
#     )
    
#     user = DB.relationship(
#         "User",
#         back_populates = "messages"
#     )