from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "database2.db"


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "chandualle"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:lightpink143@localhost/instance_schema'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking

    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    from .models import User, Post, Like, Follow, Saves

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app