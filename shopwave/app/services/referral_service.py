"""
Referral Service — code generation, application, and reward crediting.
"""
import random
import string
from flask import current_app
from app import db
from app.models import User, Referral, Notification


def generate_referral_code(user_id: int) -> str:
    """
    Generate a unique 8-char alphanumeric referral code and store it on the User.
    Returns the generated code.
    """
    user = User.query.get(user_id)
    if not user:
        raise ValueError('User not found.')
    if user.referral_code:
        return user.referral_code

    chars = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(random.choices(chars, k=8))
        if not User.query.filter_by(referral_code=code).first():
            break

    user.referral_code = code
    db.session.commit()
    return code


def apply_referral(new_user: User, referral_code: str) -> bool:
    """
    Apply a referral code at signup.
    Creates a Referral record with reward_given=False.
    Returns True on success, False if code invalid or self-referral.
    """
    referrer = User.query.filter_by(referral_code=referral_code.upper()).first()
    if not referrer:
        return False
    if referrer.id == new_user.id:
        return False  # self-referral rejected

    # Already referred?
    if Referral.query.filter_by(referred_id=new_user.id).first():
        return False

    db.session.add(Referral(
        referrer_id=referrer.id,
        referred_id=new_user.id,
        reward_given=False,
    ))
    db.session.commit()
    return True


def credit_referral_reward(referral_id: int) -> None:
    """
    Credit the referral reward to the referrer's wallet (notification only in MVP).
    Called after the referred user places their first order.
    """
    referral = Referral.query.get(referral_id)
    if not referral or referral.reward_given:
        return

    reward = current_app.config.get('REFERRAL_REWARD', 50)
    referral.reward_given = True

    db.session.add(Notification(
        user_id=referral.referrer_id,
        message=f'🎉 You earned ₹{reward:.0f} referral reward! Your friend joined ShopWave.',
        link='/seller/earnings',
    ))
    db.session.commit()
