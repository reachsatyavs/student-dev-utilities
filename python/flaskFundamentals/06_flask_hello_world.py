"""
06 - Your first web server
=============================
Flask is a package for building web servers in Python -- a program that
listens for requests from a browser and sends back a response.

Install it first:
    pip install flask

Run this file with:
    python 06_flask_hello_world.py

Then open this in your browser:
    http://127.0.0.1:5000
"""

from flask import Flask

# Flask(__name__) creates the web application. __name__ just tells Flask
# which file it's running from -- you'll write this exact line in every
# Flask project.
app = Flask(__name__)


# @app.route("/") is a "decorator" -- it tells Flask "when someone visits
# this URL path, run the function right below it, and send back whatever
# it returns as the web page."
@app.route("/")
def home():
    return "Hello, Flask!"


# You can have as many routes as you want, each at a different URL path.
@app.route("/about")
def about():
    return "This is a tiny Flask app for learning the basics."


if __name__ == "__main__":
    # debug=True auto-reloads the server whenever you save a change to
    # this file, and shows helpful error pages if something breaks.
    app.run(debug=True)

# --- Try it yourself ---
# 1. Visit http://127.0.0.1:5000/about in your browser.
# 2. Add a third route, e.g. /contact, that returns your own message.
#    Save the file -- Flask reloads automatically, just refresh the page.
