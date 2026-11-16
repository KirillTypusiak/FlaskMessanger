from .settings import main_app
from chat_app.app import chat_app_blueprint
from chat_app import views

main_app.register_blueprint(blueprint = chat_app_blueprint)