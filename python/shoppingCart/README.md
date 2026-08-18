# Shopping Cart — Flask + SQLite Teaching Project

A complete, working reference implementation of a shopping-cart web app, built
for a 5–6 session / ~12-hour Flask course. The full curriculum (what to build
each session, in what order, with clear session boundaries) is in
[`COURSE_PLAN.md`](./COURSE_PLAN.md). This README covers setup only.

> **On Windows?** Follow [`SETUP_WINDOWS.md`](./SETUP_WINDOWS.md) instead of
> the setup steps below. The commands here are macOS/Linux; several of them
> (`cp`, `source`, `<` redirection) do not work in PowerShell.

## Features

- User registration & login (hashed passwords, Flask-Login sessions)
- Dashboard with a product catalog synced from [dummyjson.com](https://dummyjson.com/products)
- Add to cart, update quantities, remove items, checkout into an order
- Admin panel: list all users + reset any user's password directly
- Admin panel: add/remove products (manually or synced from the API)

Not included on purpose, to keep the code beginner-simple: CSRF protection,
login rate limiting, and self-service password reset via emailed OTP codes.
These are real, worth having in a production app, and are covered as an
optional add-on in [`COURSE_PLAN.md`](./COURSE_PLAN.md) once the basics feel
comfortable — but they pull in more moving parts (extra libraries, tokens,
timed codes), so the base project skips them. For now, an admin resets a
forgotten password directly from the Admin: Users page.

## Tech stack

- Python 3.10+, Flask 3
- Flask-SQLAlchemy (ORM), Flask-Login (sessions) — that's the whole list
- **SQLite** — the entire database is one file (`shopping_cart.db`), created
  automatically the first time the app runs. No server to install, no
  username/password, nothing to start or stop. Python has talked to SQLite
  out of the box (via the built-in `sqlite3` module) since Python 2.5.

## Project layout

Every route file has one job: a `register_routes(app)` function that adds a
few `@app.route(...)` views to the app. No Blueprints, no app-factory
indirection — `app.py` just calls each one.

```
shoppingCart/
├── app.py                 # creates the Flask app, wires up extensions + routes
├── config.py               # env-driven configuration
├── extensions.py           # db, login_manager singletons
├── models.py                # User, Product, CartItem, Order, OrderItem
├── init_db.py                # creates tables + seeds admin (+ optional product sync)
├── shopping_cart.db          # the SQLite database file (created on first run, gitignored)
├── routes/
│   ├── auth.py               # register, login, logout
│   ├── dashboard.py          # product listing/search
│   ├── cart.py                # add/update/remove/checkout
│   └── admin.py               # user list/reset, product management
├── services/
│   └── product_api.py        # fetch + sync products from dummyjson.com
├── utils/
│   └── decorators.py          # @admin_required
├── templates/                # Jinja2 + Bootstrap 5 (via CDN)
├── static/css/style.css
├── db/schema.sql              # same schema as models.py, in plain SQL (for teaching)
├── Dockerfile / docker-compose.yml / docker-entrypoint.sh
└── requirements.txt
```

## 1. Install Python

Check what you already have:

```bash
python3 --version   # need 3.10 or newer. Windows: `python --version`
```

If that fails or shows an older version, install Python 3.12 from
[python.org/downloads](https://www.python.org/downloads/). On Windows, tick
**"Add python.exe to PATH"** during install. On macOS you can also use
`brew install python@3.12` if you have Homebrew.

## 2. Install SQLite

**You almost certainly don't need to install anything** — SQLite ships
inside Python itself (the `sqlite3` module), which is what this app actually
uses to talk to the database. Confirm it's there:

```bash
python3 -c "import sqlite3; print(sqlite3.sqlite_version)"
```

That should print a version number (e.g. `3.45.1`) with no errors. If it
does, skip to step 3.

Optionally, install the **`sqlite3` command-line tool** too, so you can open
`shopping_cart.db` directly and poke around outside of Python/Flask:

- **macOS**: already installed (`sqlite3 --version` in Terminal). If not,
  `brew install sqlite`.
- **Windows**: download the "sqlite-tools" zip from
  [sqlite.org/download.html](https://www.sqlite.org/download.html), unzip it
  somewhere, and add that folder to your PATH.
- **Linux**: `sudo apt install sqlite3` (Debian/Ubuntu) or
  `sudo dnf install sqlite` (Fedora).

Also handy, especially if you'd rather click around than type SQL: install
[**DB Browser for SQLite**](https://sqlitebrowser.org/) — a free GUI that
opens a `.db` file and lets you browse tables, run queries, and edit rows.

## 3. Install Python packages

```bash
cd python/shoppingCart
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 4. Configure environment

```bash
cp .env.example .env
# Nothing in .env is required to get started -- every value already has a
# working default.
```

## 5. Create the database + tables

Two ways to get the same result — worth doing **both** once, so the
SQL-vs-ORM mapping is concrete:

**A. By hand, in plain SQL** (this is what Session 1 walks through):

```bash
sqlite3 shopping_cart.db < db/schema.sql
```

Then poke around to confirm it worked:

```bash
sqlite3 shopping_cart.db
sqlite> .tables
sqlite> .schema users
sqlite> .quit
```

Delete that file before the next step (`rm shopping_cart.db`) — you don't
want the two approaches fighting over the same file.

**B. Via the app itself**, using Flask-SQLAlchemy's `db.create_all()`, which
reads the schema from the Python classes in `models.py`:

```bash
python init_db.py                    # creates tables, seeds the admin user
python init_db.py --sync-products    # also pulls a product catalog from the API
```

`init_db.py` is what you'll actually run day to day — approach A is a
one-time detour to see the raw SQL before it's hidden behind the ORM.

Default admin login: whatever you set for `ADMIN_USERNAME` / `ADMIN_PASSWORD`
in `.env` (defaults to `admin` / `Admin@123`).

## 6. Run the app

```bash
python -m flask --app app run --debug
```

Visit http://127.0.0.1:5000.

## Running with Docker instead

```bash
touch shopping_cart.db   # first time only, so Docker mounts a file, not a folder
docker compose up --build
```

This builds the app image, creates tables + seeds the admin + syncs
products on startup, and serves it on http://127.0.0.1:5000.
`shopping_cart.db` is bind-mounted into the container, so the data is a
plain file on your machine you can open with DB Browser for SQLite even
while the container is running. See [`COURSE_PLAN.md`](./COURSE_PLAN.md)
Session 6 for a walkthrough of how this is wired together.
