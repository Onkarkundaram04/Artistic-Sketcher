from flask import Flask
from flask_session import Session


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "your_secret_key_here"  # Change for production
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)  # Initialize session

    from app.routes import main_bp

    app.register_blueprint(main_bp)

    return app
