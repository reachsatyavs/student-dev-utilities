"""
This is the SAME login logic as 07_flask_login_page.py, just moved into
its own file. Instead of writing routes directly under @app.route in the
main file, this file defines a register_routes(app) function that ADDS the
routes to whichever `app` gets passed in.

app.py in this same folder imports this file and calls register_routes(app)
once -- that's the whole trick. This exact pattern (one file per feature,
each with a register_routes(app) function) is what the real shoppingCart
project uses too, just with more files.
"""

from flask import request

CORRECT_USERNAME = "student"
CORRECT_PASSWORD = "python123"


def register_routes(app):
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")

            if username == CORRECT_USERNAME and password == CORRECT_PASSWORD:
                return f"<h1>Welcome, {username}!</h1><p>Login successful.</p>"
            else:
                return "<h1>Login failed</h1><p>Wrong username or password. <a href='/login'>Try again</a></p>"

        return """
            <h1>Login</h1>
            <form method="POST">
                <label>Username: <input type="text" name="username"></label><br><br>
                <label>Password: <input type="password" name="password"></label><br><br>
                <button type="submit">Log in</button>
            </form>
        """
