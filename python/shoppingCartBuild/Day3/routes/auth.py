from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from extensions import db
from models import User


def register_routes(app):
    @app.route("/register", methods=["GET", "POST"])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            username = request.form.get("username", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            confirm_password = request.form.get("confirm_password", "")

            if not username or not email or not password:
                flash("All fields are required.", "danger")
                return render_template("auth/register.html")

            if password != confirm_password:
                flash("Passwords do not match.", "danger")
                return render_template("auth/register.html")

            if len(password) < 8:
                flash("Password must be at least 8 characters.", "danger")
                return render_template("auth/register.html")

            if User.query.filter_by(username=username).first():
                flash("That username is already taken.", "danger")
                return render_template("auth/register.html")

            if User.query.filter_by(email=email).first():
                flash("That email is already registered.", "danger")
                return render_template("auth/register.html")

            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            flash("Account created. Please log in.", "success")
            return redirect(url_for("login"))

        return render_template("auth/register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")

            user = User.query.filter_by(username=username).first()

            if user and user.check_password(password):
                login_user(user)
                return redirect(url_for("dashboard"))

            flash("Invalid username or password.", "danger")

        return render_template("auth/login.html")

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("login"))
