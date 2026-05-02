from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
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

    from app.auth.routes     import auth_bp
    from app.admin.routes    import admin_bp
    from app.seller.routes   import seller_bp
    from app.customer.routes import customer_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp,    url_prefix='/admin')
    app.register_blueprint(seller_bp,   url_prefix='/seller')
    app.register_blueprint(customer_bp)

    # ── Context Processors ────────────────────────────────────────────────────

    @app.context_processor
    def inject_globals():
        """Inject unread notification count, pending KYC count, and config into all templates."""
        unread_count = 0
        pending_kyc  = 0
        if current_user.is_authenticated:
            from app.models import Notification, User as _User
            unread_count = Notification.query.filter_by(
                user_id=current_user.id, is_read=False
            ).count()
            if current_user.role == 'admin':
                pending_kyc = _User.query.filter_by(
                    kyc_status='pending', role='seller'
                ).count()
        return dict(
            unread_count=unread_count,
            pending_kyc=pending_kyc,
            config=app.config,
        )

    # ── Error Handlers ────────────────────────────────────────────────────────

    @app.errorhandler(403)
    def forbidden(e):
        from flask import render_template
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template('errors/404.html'), 404

    return app
