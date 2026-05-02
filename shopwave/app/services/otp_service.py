"""
OTP Service — mobile-based passwordless login.
Rate limit: max OTP_RATE_LIMIT requests per mobile per rolling hour.
OTP expires after OTP_EXPIRY_MINUTES minutes.
"""
import random
from datetime import datetime, timedelta
from flask import current_app
from app import db
from app.models import OTPCode


def can_request_otp(mobile: str) -> bool:
    """Return True if the mobile is allowed to request a new OTP."""
    limit = current_app.config.get('OTP_RATE_LIMIT', 3)
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    count = OTPCode.query.filter(
        OTPCode.mobile == mobile,
        OTPCode.created_at >= one_hour_ago
    ).count()
    return count < limit


def generate_otp(mobile: str) -> str:
    """
    Generate a 6-digit OTP, persist it, and return the code.
    In DEBUG mode the code is printed to console (no SMS sent).
    """
    expiry_minutes = current_app.config.get('OTP_EXPIRY_MINUTES', 10)
    code = str(random.randint(100000, 999999))
    expires_at = datetime.utcnow() + timedelta(minutes=expiry_minutes)
    db.session.add(OTPCode(mobile=mobile, code=code, expires_at=expires_at))
    db.session.commit()
    if current_app.debug:
        print(f'[DEV OTP] {mobile} → {code}  (expires {expires_at.strftime("%H:%M:%S")})')
    # Production: integrate Twilio / MSG91 here
    return code


def verify_otp(mobile: str, code: str) -> bool:
    """
    Verify the submitted OTP.
    Returns True and marks the record used on success; False otherwise.
    """
    now = datetime.utcnow()
    record = (
        OTPCode.query
        .filter_by(mobile=mobile, code=code, is_used=False)
        .filter(OTPCode.expires_at > now)
        .order_by(OTPCode.created_at.desc())
        .first()
    )
    if not record:
        return False
    record.is_used = True
    db.session.commit()
    return True
