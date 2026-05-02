import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-prod')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'meesho.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 4 * 1024 * 1024  # 4 MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # Stripe — set real keys via env vars in production
    # Get test keys from https://dashboard.stripe.com/test/apikeys
    STRIPE_PUBLIC_KEY  = os.environ.get('STRIPE_PUBLIC_KEY',  'pk_test_YOUR_KEY')
    STRIPE_SECRET_KEY  = os.environ.get('STRIPE_SECRET_KEY',  'sk_test_YOUR_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', '')
