import os
import uuid
from flask import Flask, render_template, redirect, url_for, request, flash, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

from config import Config
from extensions import db, login_manager
from models import User, Claim, CLAIM_CATEGORIES
from ai_claim import generate_claim_summary, suggest_claim_category


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    def allowed_file(filename, allowed_extensions):
        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower() in allowed_extensions
        )

    def save_upload(file_storage, allowed_extensions):
        if not file_storage or file_storage.filename == "":
            return None
        if not allowed_file(file_storage.filename, allowed_extensions):
            flash(f"File type not allowed: {file_storage.filename}")
            return None
        filename = f"{uuid.uuid4().hex}_{secure_filename(file_storage.filename)}"
        file_storage.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        return filename

    @app.route("/")
    def index():
        return redirect(url_for("dashboard") if current_user.is_authenticated else url_for("login"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                return redirect(url_for("dashboard"))
            flash("Invalid username or password")
        return render_template("login.html")

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("login"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        claims = (
            Claim.query.filter_by(user_id=current_user.id)
            .order_by(Claim.created_at.desc())
            .all()
        )
        return render_template("dashboard.html", claims=claims)

    @app.route("/claims/advisor", methods=["GET", "POST"])
    @login_required
    def claims_advisor():
        suggestion = None
        description = ""
        medical_filename = None

        if request.method == "POST":
            description = request.form.get("description", "").strip()
            if not description:
                flash("Describe what happened first, then ask for a suggestion.")
                return render_template("advisor.html", description=description)

            medical_filename = save_upload(
                request.files.get("medical_report"), app.config["ALLOWED_MEDICAL_REPORT_EXTENSIONS"]
            )
            medical_path = (
                os.path.join(app.config["UPLOAD_FOLDER"], medical_filename) if medical_filename else None
            )

            suggestion = suggest_claim_category(description, medical_path)

        return render_template(
            "advisor.html",
            description=description,
            medical_filename=medical_filename,
            suggestion=suggestion,
        )

    @app.route("/claims/new", methods=["GET", "POST"])
    @login_required
    def new_claim():
        if request.method == "POST":
            age = request.form.get("age", type=int)
            location = request.form.get("location", "").strip()
            gender = request.form.get("gender", "").strip()
            category = request.form.get("category", "").strip() or None
            description = request.form.get("description", "").strip()

            if not (age and location and gender and description):
                flash("Please fill in age, location, gender, and a description.")
                return render_template(
                    "new_claim.html",
                    categories=CLAIM_CATEGORIES,
                    prefill_category=category or "",
                    prefill_description=description,
                    existing_medical_report_filename=request.form.get("existing_medical_report_filename", ""),
                )

            image_filename = save_upload(
                request.files.get("image"), app.config["ALLOWED_IMAGE_EXTENSIONS"]
            )
            medical_filename = save_upload(
                request.files.get("medical_report"), app.config["ALLOWED_MEDICAL_REPORT_EXTENSIONS"]
            )
            # If the advisor already saved a medical report and the user
            # didn't attach a new one here, reuse that one instead of
            # making them upload the same file twice.
            if not medical_filename:
                medical_filename = request.form.get("existing_medical_report_filename") or None

            image_path = (
                os.path.join(app.config["UPLOAD_FOLDER"], image_filename) if image_filename else None
            )
            medical_path = (
                os.path.join(app.config["UPLOAD_FOLDER"], medical_filename) if medical_filename else None
            )

            ai_summary = generate_claim_summary(
                age, location, gender, description, image_path, medical_path
            )

            claim = Claim(
                user_id=current_user.id,
                age=age,
                location=location,
                gender=gender,
                category=category,
                description=description,
                image_filename=image_filename,
                medical_report_filename=medical_filename,
                ai_summary=ai_summary,
            )
            db.session.add(claim)
            db.session.commit()
            return redirect(url_for("claim_detail", claim_id=claim.id))

        return render_template(
            "new_claim.html",
            categories=CLAIM_CATEGORIES,
            prefill_category=request.args.get("category", ""),
            prefill_description=request.args.get("description", ""),
            existing_medical_report_filename=request.args.get("medical_filename", ""),
        )

    @app.route("/claims/<int:claim_id>")
    @login_required
    def claim_detail(claim_id):
        claim = Claim.query.get_or_404(claim_id)
        if claim.user_id != current_user.id:
            flash("You cannot view another user's claim.")
            return redirect(url_for("dashboard"))
        return render_template("claim_detail.html", claim=claim)

    @app.route("/uploads/<path:filename>")
    @login_required
    def uploaded_file(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
