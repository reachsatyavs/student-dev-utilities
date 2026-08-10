from flask import Flask, redirect, render_template, url_for
from flask_login import current_user

from config import Config
from extensions import db, login_manager
from models import User

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


from routes import admin, auth, cart, dashboard

auth.register_routes(app)
dashboard.register_routes(app)
cart.register_routes(app)
admin.register_routes(app)


@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.errorhandler(403)
def forbidden(_error):
    return render_template("403.html"), 403


if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])
