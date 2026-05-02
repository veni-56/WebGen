from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import os

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    from app.routes.auth     import auth_bp
    from app.routes.seller   import seller_bp
    from app.routes.customer import customer_bp
    from app.routes.admin    import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(seller_bp,   url_prefix='/seller')
    app.register_blueprint(customer_bp)
    app.register_blueprint(admin_bp,    url_prefix='/admin')

    @app.errorhandler(403)
    def forbidden(e):
        return "<h2>403 — Forbidden</h2><a href='/'>Home</a>", 403

    @app.errorhandler(404)
    def not_found(e):
        return "<h2>404 — Page Not Found</h2><a href='/'>Home</a>", 404

    return app
