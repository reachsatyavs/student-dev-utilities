"""
07 - A simple login page
==========================
A real login checks a username/password against a database (that comes
later, in the shoppingCart project). For now, the "correct" username and
password are just hardcoded values in this file -- enough to learn how a
form works.

Run this file with:
    python 07_flask_login_page.py

Then open:
    http://127.0.0.1:5000
"""

from flask import Flask, request

app = Flask(__name__)

CORRECT_USERNAME = "student"
CORRECT_PASSWORD = "python123"


@app.route("/", methods=["GET", "POST"])
def login():
    # request.method tells us whether the browser is just loading the
    # page (GET) or submitting the form (POST).
    if request.method == "POST":
        # request.form holds whatever the user typed into the form fields,
        # keyed by each field's "name" attribute below.
        username = request.form.get("username")
        password = request.form.get("password")

        if username == CORRECT_USERNAME and password == CORRECT_PASSWORD:
            return f"<h1>Welcome, {username}!</h1><p>Login successful.</p>"
        else:
            return "<h1>Login failed</h1><p>Wrong username or password. <a href='/'>Try again</a></p>"

    # GET request: just show the form.
    return """
        <h1>Login</h1>
        <form method="POST">
            <label>Username: <input type="text" name="username"></label><br><br>
            <label>Password: <input type="password" name="password"></label><br><br>
            <button type="submit">Log in</button>
        </form>
    """


if __name__ == "__main__":
    app.run(debug=True)

# --- Try it yourself ---
# 1. Log in with the wrong password on purpose -- confirm you see "Login failed".
# 2. Log in with student / python123 -- confirm you see "Welcome, student!".
# 3. Change CORRECT_PASSWORD to something else, save, and try the old
#    password again.
