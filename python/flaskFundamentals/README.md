# Python & Flask Fundamentals ("Session 0")

Warm-up material to run **before** [`../shoppingCart/`](../shoppingCart)'s
Session 1. Nine plain `.py` scripts, run in order, each one small enough to
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

Each of 6-9 prints a URL to open in your browser once you run it
(`python 06_flask_hello_world.py`, etc.) — press `Ctrl+C` in the terminal to
stop the server before running the next one.

## After this

Once all nine make sense, move on to
[`../shoppingCart/COURSE_PLAN.md`](../shoppingCart/COURSE_PLAN.md) Session 1
— the real project starts there, and it reuses ideas from here directly:
routes split into their own file per feature (like `08_flask_modular/`
here), and pulling data from a public API (like `09_flask_dummyjson.py`
here, but from `dummyjson.com/products` instead of `/quotes`).
