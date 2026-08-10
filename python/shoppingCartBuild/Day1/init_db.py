"""Session 1: run this once to create tables (via SQLAlchemy, from models.py)
and seed the admin account.

Usage:
    python init_db.py
"""

from werkzeug.security import generate_password_hash

from app import app
from extensions import db
from models import User


def main():
    with app.app_context():
        db.create_all()
        print("Tables created (or already existed).")

        admin_username = app.config["ADMIN_USERNAME"]
        if not User.query.filter_by(username=admin_username).first():
            admin = User(
                username=admin_username,
                email=app.config["ADMIN_EMAIL"],
                # Hashing it by hand here since User doesn't have a
                # set_password() helper yet -- that arrives in Day2.
                password_hash=generate_password_hash(app.config["ADMIN_PASSWORD"]),
                is_admin=True,
            )
            db.session.add(admin)
            db.session.commit()
            print(f"Seeded admin user '{admin_username}'.")
        else:
            print(f"Admin user '{admin_username}' already exists, skipping.")


if __name__ == "__main__":
    main()
