"""
08 - Splitting routes into their own file
=============================================
Open auth.py in this same folder first -- that's where the actual login
route now lives. This file just creates the app, imports auth.py, and
tells it to register its routes.

Run this file with (from inside the 08_flask_modular folder):
    python app.py

Then open:
    http://127.0.0.1:5000
"""

from flask import Flask

import auth  # this imports auth.py, which sits right next to this file

app = Flask(__name__)

# Hand our app to auth.py so it can attach its /login route to it.
auth.register_routes(app)


@app.route("/")
def home():
    return '<h1>Home</h1><p><a href="/login">Go to login</a></p>'


if __name__ == "__main__":
    app.run(debug=True)

# --- Try it yourself ---
# 1. Confirm /login still works exactly like it did in 07_flask_login_page.py.
# 2. Add a new function to auth.py's register_routes(app), e.g. a /logout
#    route that just returns "You have been logged out." -- no changes to
#    app.py needed, since it's already calling register_routes(app).
