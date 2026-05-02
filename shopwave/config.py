import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'shopwave-secret-2025')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'shopwave.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # OTP settings
    OTP_EXPIRY_MINUTES = int(os.environ.get('OTP_EXPIRY_MINUTES', 10))
    OTP_RATE_LIMIT     = int(os.environ.get('OTP_RATE_LIMIT', 3))

    # WhatsApp contact
    WHATSAPP_NUMBER = os.environ.get('WHATSAPP_NUMBER', '919876543210')

    # Referral reward (wallet credit in ₹)
    REFERRAL_REWARD = float(os.environ.get('REFERRAL_REWARD', 50))
