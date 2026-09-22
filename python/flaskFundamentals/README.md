# Python & Flask Fundamentals ("Session 0")

Warm-up material to run **before** [`../shoppingCart/`](../shoppingCart)'s
Session 1. Eleven small files, run in order, each one small enough to
read top to bottom. No database, no templates, no project structure yet —
just Python, one installed package, and a first web page.

## How to use this folder

1. Make sure Python 3.10+ is installed (`python3 --version`). See
   [`../shoppingCart/README.md`](../shoppingCart/README.md) if you need
   install steps.
2. (Recommended) create a virtual environment so the packages you install
   here don't spill into every other project on your machine:
   ```bash
   cd python/flaskFundamentals
   python3 -m venv .venv
   source .venv/bin/activate      # Windows: .venv\Scripts\activate
   ```
3. Work through the files in order. Each one says at the top what to
   install (if anything) before running it, and how to run it.

## Order

| # | File | What it teaches |
|---|---|---|
| 1 | `01_variables.py` | What a variable is, assignment, naming |
| 2 | `02_data_types.py` | `str`, `int`, `float`, `bool`, `list`, `dict`, `type()` |
| 3 | `03_functions.py` | `def`, parameters, `return`, calling a function |
| 4 | `04_your_own_module.py` (+ `greetings.py`) | What a module/package is, writing and importing your own |
| 5 | `05_install_and_use_package.py` | Installing an external package (`requests`) and using it |
| 6 | `06_flask_hello_world.py` | Installing Flask, `@app.route`, your first web page |
| 7 | `07_flask_login_page.py` | A form, `GET` vs `POST`, reading form data |
| 8 | `08_flask_modular/` (`app.py` + `auth.py`) | Splitting routes into their own file |
| 9 | `09_flask_dummyjson.py` | Calling an external API from inside a Flask route |
| 10a | `10a_movie_page.html` | Plain HTML, no Python — open it by double-clicking the file |
| 10b | `10b_flask_same_page.py` | The exact same HTML, sent by Flask instead |
| 10 | `10_flask_movie_cast.py` | The same page built from Python data — add movies, add stars, upload photos |
| 11 | `11_python_collections.ipynb` | Deep dive on `list`, `set`, `tuple`, `dict` — 15 operations each, told as a movie shoot (Yash, Sudeep, Puneeth Rajkumar, cricketers and more) |

Each of 6-10 prints a URL to open in your browser once you run it
(`python 06_flask_hello_world.py`, etc.) — press `Ctrl+C` in the terminal to
stop the server before running the next one.

## Lesson 11 — Jupyter notebook

`11_python_collections.ipynb` is a notebook, not a `.py` file — it mixes
explanation and runnable code in one place, cell by cell, instead of one big
script. Open it with:

```bash
python -m pip install notebook
python -m jupyter notebook
```

then click `11_python_collections.ipynb` in the browser tab that opens.
(VS Code and PyCharm can also open `.ipynb` files directly, with no extra
install, if you'd rather stay in your editor.) Run cells top to bottom with
`Shift+Enter`; the explanation for each concept is right above the code that
demonstrates it.

## Lesson 10 — static HTML, then dynamic

Run these three in order. They are the same page three times over, and the
whole point is what changes between them.

**10a — `10a_movie_page.html`.** No Python at all. Double-click the file and
it opens in your browser. This is what a web page *is*: a text file. Notice
that the five cast cards are five near-identical blocks of HTML, typed out
by hand. Adding a sixth star means typing a sixth block.

**10b — `10b_flask_same_page.py`.** Run it, open http://127.0.0.1:5000. The
page looks identical, because the HTML inside the file is a straight copy of
`10a`. Nothing is generated — Flask is just handing over the same text. This
is the whole idea of a web server, and nothing more.

**10 — `10_flask_movie_cast.py`.** Now the HTML is *built* from Python data.
Nobody typed the cards; a loop made one per entry in a list. That is the only
difference — and it is why you can now add a movie and a star from the
browser without editing a single line of code.

### The data

```python
MOVIES = [
    {"name": "KGF Chapter 4", "year": "2027", "cast": [
        {"role": "Hero",    "name": "Yash",   "photo": "yash.png"},
        {"role": "Villain", "name": "Sudeep", "photo": "sudeep.png"},
    ]},
    {"name": "Kantara 2", "year": "2026", "cast": []},
]
```

A **list** of movies, because there can be many. Each movie is a **dict**,
because one movie has several facts about it. One of those facts, `cast`, is
itself a list of dicts — many stars, each with a role, a name and a photo.

### Exercises

1. Add two movies. Then add stars to each one, and check they land under the
   right movie.
2. Add `"Music Director"` to the `ROLES` list, save the file, refresh. It
   appears in every dropdown straight away.
3. Save a few star photos from the internet and upload them. The placeholder
   pictures in `static/images/` are only there for `10a` — replace them with
   real ones if you like.
4. Restart the server and reload the page. Everything is gone — `MOVIES` is
   an ordinary Python list living in memory, so it disappears when the
   program stops. That is exactly the problem a database solves, and it is
   what the shoppingCart project does next.
5. **Build the RCB squad.** Copy the file to `11_flask_rcb_squad.py` and
   change one line:

   ```python
   ROLES = ["Batter", "Bowler", "All-rounder", "Captain", "Coach"]
   ```

   That is the only code change. Add "RCB 2026" as the movie, then add Virat
   Kohli, Rajat Patidar, Devdutt Padikkal and the rest with their photos.
   Same program, different subject — that is the point.

## After this

Once all ten make sense, move on to
[`../shoppingCart/COURSE_PLAN.md`](../shoppingCart/COURSE_PLAN.md) Session 1
— the real project starts there, and it reuses ideas from here directly:
routes split into their own file per feature (like `08_flask_modular/`
here), and pulling data from a public API (like `09_flask_dummyjson.py`
here, but from `dummyjson.com/products` instead of `/quotes`).
