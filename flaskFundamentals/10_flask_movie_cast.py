"""
10 - Movie cast board

Run:    python 10_flask_movie_cast.py
Open:   http://127.0.0.1:5000
"""

import os

from flask import Flask, request, redirect
from werkzeug.utils import secure_filename

app = Flask(__name__)

ROLES = ["Hero", "Heroine", "Villain", "Director", "Producer"]

MOVIES = []

UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():
    options = ""
    for role in ROLES:
        options += f"<option>{role}</option>"

    blocks = ""
    for index, movie in enumerate(MOVIES):
        cards = ""
        for member in movie["cast"]:
            cards += f"""
                <div class="card">
                    <img src="/static/uploads/{member['photo']}">
                    <h3>{member['name']}</h3>
                    <p>{member['role']}</p>
                </div>
            """

        if not movie["cast"]:
            cards = "<p>No stars yet.</p>"

        blocks += f"""
            <div class="movie">
                <h2>{movie['name']} {movie['year']}</h2>

                <div>{cards}</div>

                <form method="POST" action="/add" enctype="multipart/form-data">
                    <input type="hidden" name="movie" value="{index}">
                    <select name="role">{options}</select>
                    <input type="text" name="name" placeholder="Star name" required>
                    <input type="file" name="photo" required>
                    <button type="submit">Add star</button>
                </form>
            </div>
        """

    if not MOVIES:
        blocks = "<p>No movies yet. Add the first one above.</p>"

    return f"""
        <style>
            body {{ font-family: sans-serif; background: #f2f2f2; padding: 30px; }}
            .movie {{ background: #e8e8e8; padding: 15px; margin-bottom: 25px; border-radius: 10px; }}
            .card {{ display: inline-block; background: white; width: 160px;
                     padding: 10px; margin: 8px; border-radius: 8px; text-align: center; }}
            .card img {{ width: 140px; height: 140px; object-fit: cover; border-radius: 6px; }}
            form {{ background: white; padding: 15px; border-radius: 8px; display: inline-block; }}
        </style>

        <h1>My Movies</h1>

        <form method="POST" action="/movie">
            <input type="text" name="name" placeholder="Movie name" required>
            <input type="text" name="year" placeholder="Year">
            <button type="submit">Add movie</button>
        </form>

        {blocks}
    """


@app.route("/movie", methods=["POST"])
def movie():
    MOVIES.append({
        "name": request.form["name"],
        "year": request.form["year"],
        "cast": [],
    })

    return redirect("/")


@app.route("/add", methods=["POST"])
def add():
    photo = request.files["photo"]
    filename = secure_filename(photo.filename)
    photo.save(os.path.join(UPLOAD_FOLDER, filename))

    index = int(request.form["movie"])

    MOVIES[index]["cast"].append({
        "role": request.form["role"],
        "name": request.form["name"],
        "photo": filename,
    })

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
