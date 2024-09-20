import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
login = LoginManager()
login.login_view = 'main.login'

def create_app(config_class=Config):
    app = Flask(__name__, template_folder='../templates')  # Убедитесь, что путь к шаблонам правильный
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login.init_app(app)

    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app