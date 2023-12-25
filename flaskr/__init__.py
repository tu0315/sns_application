# __init__.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# ログインマネージャー作成
login_magager = LoginManager()
login_magager.login_view = "app.view"
login_magager.login_message = "ログインしてください"

basedir = os.path.abspath(os.path.dirname(__name__))
db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "mysite"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
        basedir, "data.sqlite"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    from flaskr.views import bp

    app.register_blueprint(bp)
    db.init_app(app)
    migrate.init_app(app, db)
    login_magager.init_app(app)
    return app
