from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)

    from app.dashboard import bp as dashboard_bp
    from app.clients import bp as clients_bp
    from app.progress import bp as progress_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(clients_bp, url_prefix="/clients")
    app.register_blueprint(progress_bp, url_prefix="/progress")

    with app.app_context():
        from app import models
        db.create_all()

    return app
