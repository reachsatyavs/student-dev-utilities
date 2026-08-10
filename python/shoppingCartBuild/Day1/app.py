from flask import Flask

from config import Config
from extensions import db

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


@app.route("/")
def index():
    return "Hello, Flask!"


if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])
