"""
10b - The same page, served by Flask

The HTML below is copied from 10a_movie_page.html, unchanged.

Run:    python 10b_flask_same_page.py
Open:   http://127.0.0.1:5000
"""

from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    return """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>KGF Chapter 4</title>
  <style>
    body { font-family: sans-serif; background: #f2f2f2; padding: 30px; }
    .card { display: inline-block; background: white; width: 160px;
            padding: 10px; margin: 8px; border-radius: 8px; text-align: center; }
    .card img { width: 140px; height: 140px; object-fit: cover; border-radius: 6px; }
  </style>
</head>
<body>

  <h1>KGF Chapter 4 2027</h1>

  <h2>Cast</h2>

  <div class="card">
    <img src="static/images/yash.svg">
    <h3>Yash</h3>
    <p>Hero</p>
  </div>

  <div class="card">
    <img src="static/images/radhika.svg">
    <h3>Radhika Pandit</h3>
    <p>Heroine</p>
  </div>

  <div class="card">
    <img src="static/images/sudeep.svg">
    <h3>Kiccha Sudeep</h3>
    <p>Villain</p>
  </div>

  <div class="card">
    <img src="static/images/prashanth.svg">
    <h3>Prashanth Neel</h3>
    <p>Director</p>
  </div>

  <div class="card">
    <img src="static/images/vijay.svg">
    <h3>Vijay Kiragandur</h3>
    <p>Producer</p>
  </div>

</body>
</html>
"""


if __name__ == "__main__":
    app.run(debug=True)
