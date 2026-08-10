from datetime import datetime, timedelta

from flask import current_app, flash, redirect, render_template, request, session, url_for

from extensions import db, limiter
from models import PasswordResetOTP, User
from utils.email_utils import generate_otp, send_otp_email


def register_routes(app):
    @app.route("/forgot-password", methods=["GET", "POST"])
    @limiter.limit("5 per minute")
    def forgot_password():
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            user = User.query.filter_by(email=email).first()

            # Always show the same message, whether or not the email exists,
            # so this endpoint can't be used to guess which emails are registered.
            if user:
                otp_code = generate_otp()
                expires_at = datetime.utcnow() + timedelta(minutes=current_app.config["OTP_EXPIRY_MINUTES"])
                db.session.add(PasswordResetOTP(user_id=user.id, otp_code=otp_code, expires_at=expires_at))
                db.session.commit()
                send_otp_email(user.email, otp_code)
                session["reset_email"] = email

            flash("If that email is registered, a 6-digit code has been sent to it.", "info")
            return redirect(url_for("verify_otp"))

        return render_template("auth/forgot_password.html")

    @app.route("/verify-otp", methods=["GET", "POST"])
    @limiter.limit("10 per minute")
    def verify_otp():
        email = session.get("reset_email")
        if not email:
            return redirect(url_for("forgot_password"))

        if request.method == "POST":
            otp_code = request.form.get("otp_code", "").strip()
            user = User.query.filter_by(email=email).first()

            otp_entry = (
                PasswordResetOTP.query.filter_by(user_id=user.id, otp_code=otp_code, used=False)
                .order_by(PasswordResetOTP.created_at.desc())
                .first()
                if user
                else None
            )

            if not otp_entry or not otp_entry.is_valid():
                flash("That code is invalid or has expired.", "danger")
                return render_template("auth/verify_otp.html")

            otp_entry.used = True
            db.session.commit()
            session["reset_verified_user_id"] = user.id
            return redirect(url_for("reset_password"))

        return render_template("auth/verify_otp.html")

    @app.route("/reset-password", methods=["GET", "POST"])
    def reset_password():
        user_id = session.get("reset_verified_user_id")
        if not user_id:
            return redirect(url_for("forgot_password"))

        if request.method == "POST":
            password = request.form.get("password", "")
            confirm_password = request.form.get("confirm_password", "")

            if len(password) < 8:
                flash("Password must be at least 8 characters.", "danger")
                return render_template("auth/reset_password.html")

            if password != confirm_password:
                flash("Passwords do not match.", "danger")
                return render_template("auth/reset_password.html")

            user = User.query.get_or_404(user_id)
            user.set_password(password)
            user.register_successful_login()  # also clears any existing lockout
            db.session.commit()

            session.pop("reset_verified_user_id", None)
            session.pop("reset_email", None)

            flash("Password updated. Please log in.", "success")
            return redirect(url_for("login"))

        return render_template("auth/reset_password.html")
