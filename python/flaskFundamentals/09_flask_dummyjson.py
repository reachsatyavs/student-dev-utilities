"""
09 - Calling an external API from a Flask route
====================================================
This combines two things you've already done separately: fetching data
with requests (05_install_and_use_package.py) and serving a web page with
Flask (06-08). Now a browser visit triggers the fetch, and the result gets
turned into an HTML page instead of just being printed.

Install if you haven't already:
    pip install flask requests

Run this file with:
    python 09_flask_dummyjson.py

Then open:
    http://127.0.0.1:5000
"""

from flask import Flask
import requests

app = Flask(__name__)


@app.route("/")
def quotes():
    # Same requests call as in 05_install_and_use_package.py, just fetching
    # 5 quotes at once instead of 1.
    response = requests.get("https://dummyjson.com/quotes", params={"limit": 5})
    data = response.json()

    # Build up an HTML string piece by piece, one <li> per quote.
    html = "<h1>5 Quotes from dummyjson.com</h1><ul>"
    for q in data["quotes"]:
        html += f"<li>\"{q['quote']}\" &mdash; {q['author']}</li>"
    html += "</ul>"

    return html


if __name__ == "__main__":
    app.run(debug=True)

# --- Try it yourself ---
# 1. Refresh the page a few times -- notice the URL always returns the
#    same first 5 quotes, since the endpoint isn't random (unlike
#    /quotes/random from 05_install_and_use_package.py).
# 2. Change "limit": 5 to "limit": 10.
# 3. Bigger challenge: change the URL to "https://dummyjson.com/products"
#    and print each product's "title" and "price" instead -- this is
#    exactly the pattern the real shoppingCart project's dashboard uses.
