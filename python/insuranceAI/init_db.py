from app import app
from extensions import db
from models import User

DEMO_USERNAME = "student"
DEMO_PASSWORD = "student123"

with app.app_context():
    db.create_all()

    if not User.query.filter_by(username=DEMO_USERNAME).first():
        user = User(username=DEMO_USERNAME)
        user.set_password(DEMO_PASSWORD)
        db.session.add(user)
        db.session.commit()
        print(f"Created demo user: {DEMO_USERNAME} / {DEMO_PASSWORD}")
    else:
        print("Demo user already exists.")

    print("Database tables created.")
