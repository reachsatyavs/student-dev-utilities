import random

from flask import current_app, render_template
from flask_mail import Message

from extensions import mail


def generate_otp():
    return f"{random.randint(0, 999999):06d}"


def send_otp_email(to_email, otp_code):
    """Send the password-reset OTP. If mail isn't configured, fall back to
    printing it to the console so the flow can still be tested end-to-end.
    """
    if not current_app.config.get("MAIL_USERNAME"):
        current_app.logger.warning("MAIL_USERNAME not set - printing OTP instead of emailing it.")
        print(f"[DEV] Password reset OTP for {to_email}: {otp_code}")
        return

    msg = Message(
        subject="Your password reset code",
        recipients=[to_email],
        body=render_template("email/otp_email.txt", otp_code=otp_code),
    )
    mail.send(msg)
