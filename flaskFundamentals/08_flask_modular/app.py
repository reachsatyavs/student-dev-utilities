"""
08 - Splitting routes into their own file
=============================================
Open auth.py in this same folder first -- that's where the actual login
route now lives. Then read products.py, a second feature built the exact
same way. This file just creates the app, imports those two, and tells
each one to register its routes.

This file is the only place that knows the whole app exists. Each feature
file knows only about itself.

Run this file with (from inside the 08_flask_modular folder):
    python app.py

Then open:
    http://127.0.0.1:5000
"""

from flask import Flask

import auth  # this imports auth.py, which sits right next to this file
import products  # and this imports products.py, same folder

app = Flask(__name__)

# Hand our app to each feature file so it can attach its own routes to it.
# Adding a whole new feature costs exactly one line here -- that is the
# payoff of splitting the files up.
auth.register_routes(app)
products.register_routes(app)


@app.route("/")
def home():
    return """
        <h1>Home</h1>
        <p><a href="/login">Go to login</a></p>
        <p><a href="/products">Browse products</a></p>
    """


if __name__ == "__main__":
    app.run(debug=True)

# --- Try it yourself ---
# 1. Confirm /login still works exactly like it did in 07_flask_login_page.py.
# 2. Add a new function to auth.py's register_routes(app), e.g. a /logout
#    route that just returns "You have been logged out." -- no changes to
#    app.py needed, since it's already calling register_routes(app).
# 3. Add a fourth product to the PRODUCTS list in products.py and refresh
#    /products. Notice you never opened app.py or auth.py to do it.
# 4. Comment out the products.register_routes(app) line above and reload
#    /products -- you get a 404, but /login still works fine. Each feature
#    plugs in (and unplugs) on its own.
# 5. Now make a third file, orders.py, with its own register_routes(app)
#    and an /orders route. You already know every step: copy the shape of
#    products.py, then add two lines here (the import and the call).
