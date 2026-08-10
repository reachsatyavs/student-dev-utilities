# Course Plan: Build a Shopping Cart App with Flask + SQLite

6 sessions × 2 hours = 12 hours hands-on. Each session ends with something
that **runs**, so a student who only shows up for some sessions still leaves
with a working app at their level. The finished reference implementation for
every session lives in this folder (`python/shoppingCart/`) — use it as your
instructor answer key and to generate diffs/handouts, not as something
students clone on day 1.

## How to run the class

- Students start from an **empty folder** and build up file by file. Don't
  hand them this repo directly — either live-code each file with them, or
  give out session-specific starter/solution snapshots.
- Every session has a **checkpoint**: a concrete "it works when..." test.
  Don't move to the next session until that passes — that's the hard
  boundary between sessions.
- Sessions 1–4 build the core app, kept deliberately plain: no Blueprints, no
  app-factory pattern, no CSRF/rate-limiting/email libraries. Each route file
  just exposes a `register_routes(app)` function with a few `@app.route(...)`
  views, called once from `app.py`. Session 5 is optional and adds the
  security features back in as a guided add-on once the fundamentals are
  solid. Session 6 is optional/bonus (Docker). Cut 5 and 6 first if you're
  short on time — the app is fully functional after Session 4.

## Prerequisites (send this before Session 1)

Students should arrive with:

1. **Python 3.10+** installed (`python3 --version`) — see the detailed
   install steps in [`README.md`](./README.md) if they need them
2. **A code editor** (VS Code recommended, with the Python extension)
3. **Git** (to save their own progress between sessions)
4. Nothing else. This course uses **SQLite**, which ships inside Python
   itself (the `sqlite3` module) — no database server to install, no
   Docker required just to have a database, no username/password to
   configure. If Python is installed, the database already works.
5. A free [dummyjson.com](https://dummyjson.com/products) account is **not**
   needed — it's a public, no-auth API used for sample product data.
6. Docker Desktop is only needed for the optional Session 6 — fine to skip
   installing it until then.

Have them run this one command before class to confirm SQLite is ready:

```bash
python3 -c "import sqlite3; print(sqlite3.sqlite_version)"
```

If that prints a version number, they're set.

---

## Session 1 (2h): Environment Setup + Database Design

**Goal:** a running Flask "Hello World" that successfully queries a SQLite
database, plus a database file the class built by hand in raw SQL before
letting the ORM take over.

### Part A — Install Python (15 min)

```bash
python3 --version
```

Need 3.10+. If missing or too old, install from
[python.org/downloads](https://www.python.org/downloads/) (Windows: tick
"Add python.exe to PATH" during setup) or `brew install python@3.12` on
macOS. Confirm again with `python3 --version`.

Create the project folder and a virtual environment (isolates this
project's packages from anything else on the machine):

```bash
mkdir shoppingCart && cd shoppingCart
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
```

Their prompt should now show `(.venv)` — that's the signal every later
`pip install` in this course goes into this project only.

### Part B — Install SQLite (10 min)

The important thing to teach here: **there is no SQLite server to install.**
SQLite is a library, not a service — the entire database is one file on
disk, and Python already knows how to read/write it via the built-in
`sqlite3` module. Prove it:

```bash
python3 -c "import sqlite3; print(sqlite3.sqlite_version)"
```

That's the whole install for what the *app* needs. Separately, install the
**`sqlite3` command-line tool**, so the class can inspect the database file
directly, outside of Python:

- macOS: already present (`sqlite3 --version`). If missing, `brew install sqlite`.
- Windows: grab the "sqlite-tools" zip from
  [sqlite.org/download.html](https://www.sqlite.org/download.html), unzip,
  add the folder to PATH.
- Linux: `sudo apt install sqlite3`.

Optional but worth showing once: [DB Browser for SQLite](https://sqlitebrowser.org/),
a free GUI for opening a `.db` file, browsing tables, and running queries
without typing SQL by hand.

### Part C — Design the schema (30 min)

Whiteboard first, code second. Draw four tables and their foreign keys
before typing anything:

```
users ──< cart_items >── products
users ──< orders ──< order_items >── products
```

- `users`: id, username, email, password_hash, is_admin, timestamps
- `products`: id, title, description, category, price, stock, thumbnail_url
- `cart_items`: links a user + product + quantity (one row per product per
  user's cart)
- `orders` / `order_items`: what a cart becomes after checkout

### Part D — Create the database, by hand, in raw SQL (25 min)

```bash
sqlite3 shopping_cart.db < db/schema.sql
```

There's no `CREATE DATABASE` step like a server-based database needs — the
file `shopping_cart.db` *is* the database, and `sqlite3` creates it the
moment you point it at a filename that doesn't exist yet.

Confirm it worked:

```bash
sqlite3 shopping_cart.db
sqlite> .tables
sqlite> .schema users
sqlite> INSERT INTO users (username, email, password_hash) VALUES ('test', 'test@example.com', 'x');
sqlite> SELECT * FROM users;
sqlite> .quit
```

Then delete that file (`rm shopping_cart.db`) — Part E creates it again, and
you don't want two competing table definitions.

### Part E — Same schema, as Python classes (30 min)

```bash
pip install flask flask-sqlalchemy python-dotenv
```

1. `config.py` — reads `.env`, builds the `sqlite:///shopping_cart.db`
   connection string (point out: this is the *only* line that would change
   if you swapped databases later — everything downstream just talks to
   SQLAlchemy)
2. `extensions.py` — the bare `db = SQLAlchemy()` singleton
3. `models.py` — just `User` and `Product` for now as SQLAlchemy classes
   (add the rest in Sessions 3–4 as they're needed) — walk through each
   column and have students point out its match in `db/schema.sql`
4. `app.py` — a plain `app = Flask(__name__)` at module level (no factory
   function — keep it as flat and readable top-to-bottom as possible), a
   single `/` route that returns `"Hello, Flask!"`
5. `init_db.py` — calls `db.create_all()`, which reads `models.py` and
   creates the same tables again, then seeds one admin user

```bash
python init_db.py
sqlite3 shopping_cart.db ".tables"   # same tables as Part D
```

**Checkpoint:** `python -m flask --app app run` serves `/`, and
`shopping_cart.db` has `users` and `products` tables (with one seeded admin
row in `users`) visible via `sqlite3` or DB Browser for SQLite.

**Reference files:** `config.py`, `extensions.py`, `models.py` (User +
Product only at this point), `app.py`, `init_db.py`, `db/schema.sql`

---

## Session 2 (2h): User Registration & Login

**Goal:** a student can register, log out, and log back in — with a real
hashed password in the database, not plaintext.

**Covers:**
- `Flask-Login` for session management (`login_user`, `logout_user`,
  `login_required`, `current_user`)
- `werkzeug.security` for password hashing (`generate_password_hash` /
  `check_password_hash`) — **never store plaintext passwords**, and this is
  the moment to say that explicitly
- Splitting routes into `routes/auth.py` instead of one giant `app.py` — one
  file per feature area, each exposing a `register_routes(app)` function
  that adds its `@app.route(...)` views directly to the shared `app` object.
  No Blueprint objects, no `url_for('auth.login')`-style prefixes to
  remember — just `url_for('login')`, same as if it were one file
- Server-side form validation + `flash()` messages
- Base template (`templates/base.html`) with Bootstrap via CDN, so the rest
  of the course isn't spent hand-writing CSS

**Build, in order:**
1. Add `password_hash`, `set_password()`, `check_password()` to `User` in
   `models.py`; add `UserMixin`
2. `extensions.py` — add `login_manager = LoginManager()`
3. `routes/auth.py` — a `register_routes(app)` function containing the
   `register`, `login`, `logout` views
4. `templates/base.html`, `templates/auth/register.html`,
   `templates/auth/login.html`
5. In `app.py`: `login_manager.init_app(app)` + `@login_manager.user_loader`,
   then `from routes import auth` and `auth.register_routes(app)`

**Checkpoint:** register a new account, see the hashed password in the
`users` table (not the plaintext), log out, log back in with the same
credentials, and get redirected to a (still empty) `/dashboard` if it exists,
or a placeholder page.

**Reference files:** `routes/auth.py`, `templates/auth/register.html`,
`templates/auth/login.html`, `templates/base.html`

---

## Session 3 (2h): Dashboard + Shopping Cart

**Goal:** a logged-in user sees a product catalog (pulled from a real API)
and can add items to a cart.

**Covers:**
- Calling an external JSON API with `requests` — https://dummyjson.com/products
  is used here specifically because it needs no API key and returns realistic
  product data (title, price, category, thumbnail, description)
- "Sync, don't fetch live every time": pulling the API data into your own
  `products` table once (`services/product_api.py`), rather than calling the
  API on every page load
- Modeling a cart: `CartItem` links a `User` to a `Product` with a quantity;
  a unique constraint on `(user_id, product_id)` so "add to cart" either
  creates a row or bumps the quantity
- Search/filter with SQLAlchemy `.ilike()` and `.filter_by()`

**Build, in order:**
1. Add `CartItem` to `models.py`
2. `services/product_api.py` — `fetch_products_from_api()` +
   `sync_products_from_api()`
3. A one-off script or Flask shell command to run the sync and confirm
   products land in the table
4. `routes/dashboard.py` — a `register_routes(app)` with product listing,
   search box, category filter
5. `templates/dashboard.html` — product grid with an "Add to cart" form per
   card
6. `routes/cart.py` — a `register_routes(app)` with `view_cart`,
   `add_to_cart`, `update_quantity`, `remove_from_cart` (checkout comes in
   Session 4)
7. `templates/cart.html`
8. In `app.py`: `from routes import dashboard, cart` and call both modules'
   `register_routes(app)`

**Checkpoint:** dashboard shows real products from dummyjson.com; adding the
same product twice increases its quantity instead of creating a duplicate
row; the cart page shows correct line totals and a grand total.

**Reference files:** `services/product_api.py`, `routes/dashboard.py`,
`routes/cart.py` (minus `checkout`/`order_confirmation`),
`templates/dashboard.html`, `templates/cart.html`

---

## Session 4 (2h): Checkout + Admin Panel

**Goal:** a user can place an order from their cart, and an admin can manage
users and products.

**Covers:**
- Turning a cart into an order: `Order` + `OrderItem` models, and why order
  line items **copy** the price at purchase time (`price_at_purchase`)
  instead of pointing at the live `Product.price` — so later price changes
  don't rewrite history
- A DB transaction that must succeed or fail together: create the order,
  create its line items, delete the cart rows — one commit
- Role-based access: an `is_admin` flag on `User` + an `@admin_required`
  decorator (`utils/decorators.py`) that `abort(403)`s non-admins
- Admin views: list all users with a per-user "reset password" form; list/add/
  remove products, plus a button to re-run the dummyjson.com sync

**Build, in order:**
1. Add `Order`, `OrderItem` to `models.py`
2. `routes/cart.py` — add `checkout` and `order_confirmation`
3. `templates/order_confirmation.html`
4. `utils/decorators.py` — `admin_required`
5. Seed one admin user (already done by `init_db.py` from Session 1 — revisit
   it here and point out the `is_admin=True` seed)
6. `routes/admin.py` — a `register_routes(app)` with `admin_users`,
   `admin_reset_user_password`, `admin_products`, `admin_add_product`,
   `admin_delete_product`, `admin_sync_products` (all under `/admin/...`
   URLs — since there's no Blueprint to prefix them automatically, the
   `/admin` prefix is just typed into each route string, and the `admin_`
   prefix on function names keeps them from colliding with any other route)
7. `templates/admin/users.html`, `templates/admin/products.html`
8. In `app.py`: `from routes import admin` and `admin.register_routes(app)`

**Checkpoint:** checking out empties the cart and creates a visible order;
logging in as the seeded admin shows every registered user and lets you
reset one of their passwords; the admin can add a product by hand and delete
one that isn't referenced by any past order.

**Reference files:** `models.py` (Order/OrderItem), `routes/cart.py`
(checkout), `utils/decorators.py`, `routes/admin.py`,
`templates/admin/users.html`, `templates/admin/products.html`

---

## Session 5 (2h, optional — do this once the basics feel solid): Security Hardening

**This session's code is intentionally NOT in the base reference project.**
Sessions 1–4 leave out CSRF protection, login rate limiting, and self-service
password reset on purpose — those add real, worthwhile complexity (extra
libraries, timed tokens, an SMTP account), and the goal through Session 4 is
a student who can read every line of their own app. Once that's solid,
Session 5 layers security back in as a deliberate, well-understood addition
— not something copy-pasted in from the start without knowing why it's there.

**Goal:** the login form resists brute-forcing, forms are protected from
CSRF, and users can recover a forgotten password without an admin's help.

**Covers:**
- `Flask-Limiter`: capping login attempts per IP (`@limiter.limit("5 per
  minute")`) — explain the difference between IP-based rate limiting and
  the account-level lockout below (they solve different attacks)
- Account lockout: `failed_login_attempts` + `locked_until` added to `User`,
  incremented on bad password, reset on success
- CSRF protection with `Flask-WTF`'s `CSRFProtect` — every POST form needs a
  hidden `csrf_token` field, explain why (without it, any other site could
  submit forms as the logged-in user)
- The OTP password-reset flow, as three separate views/pages:
  `forgot_password` (request a code) → `verify_otp` (enter the code) →
  `reset_password` (set a new password) — and why it's 3 steps, not 1
  (you never let someone set a password until they've proven code ownership)
- `Flask-Mail` + an SMTP provider (Gmail App Passwords are the easiest for a
  classroom demo) — with a dev fallback: if `MAIL_USERNAME` isn't set, print
  the OTP to the server console instead of emailing it, so students without
  SMTP configured can still test the whole flow

**Build, in order:**
1. `pip install flask-limiter flask-wtf flask-mail`
2. `extensions.py` — add `limiter = Limiter(...)`, `csrf = CSRFProtect()`,
   `mail = Mail()`; call `.init_app(app)` for each in `app.py`
3. Add a hidden `<input type="hidden" name="csrf_token" value="{{
   csrf_token() }}">` to every existing form (register, login, cart forms,
   admin forms) — a good moment to grep the templates together as a class
4. Add `failed_login_attempts` / `locked_until` columns to `User` in
   `models.py`; update `routes/auth.py`'s `login` view to check/increment
   them, and add `@limiter.limit("5 per minute")` above the `login` route
5. `models.py` — a new `PasswordResetOTP` model (user_id, otp_code,
   expires_at, used)
6. `utils/email_utils.py` — `generate_otp()`, `send_otp_email()`
7. `routes/password_reset.py` — a `register_routes(app)` with the
   three-view flow, registered from `app.py` like every other route file
8. `templates/auth/forgot_password.html`, `verify_otp.html`,
   `reset_password.html`

**Checkpoint:** 6 wrong login attempts in a row locks the account (7th
attempt is rejected even with the right password) for the configured
lockout window; requesting a password reset, entering the code (from email
or the console), and setting a new password logs back in successfully with
the new password and not the old one.

---

## Session 6 (2h, optional/bonus): Dockerize the App

**Goal:** the app starts with one command, on any machine, with no local
Python install at all.

Because the database is just a file, this session is a lot lighter than a
typical "containerize your app + your database server" walkthrough — there's
no second container, no healthcheck to wait on, no driver to install inside
the image. That's worth calling out explicitly: it's one of the practical
tradeoffs of SQLite vs. a server-based database like MSSQL/Postgres/MySQL.

**Covers:**
- Why containerize a *teaching* app at all: reproducibility ("works on my
  machine" goes away) and a preview of how real teams ship this app
- Writing a `Dockerfile`: base image, installing `requirements.txt`, copying
  the code — about as plain as a Python Dockerfile gets
- An entrypoint script (`docker-entrypoint.sh`) that runs `init_db.py` (create
  tables + seed admin + sync products) then starts the server — the
  containerized equivalent of the manual Session 1 setup steps
- `docker-compose.yml`: one `web` service, and **bind-mounting**
  `shopping_cart.db` into the container so the database is a plain file on
  the host machine, survives `docker compose down`, and can be opened with
  DB Browser for SQLite while the container is still running — contrast this
  with a named volume, which hides the data inside Docker's storage
- What to do differently for a real deployment vs. this classroom setup
  (don't bake secrets into the image, consider whether SQLite's single-file,
  single-writer model is still appropriate at production scale — many small
  apps run it in production fine, but concurrent-write-heavy apps usually
  move to Postgres/MySQL, and that's a good discussion prompt here, add a
  WSGI server like `gunicorn`/`waitress` instead of the Flask dev server)

**Build, in order:**
1. `Dockerfile` — Python base image, install requirements, copy code
2. `docker-entrypoint.sh` — `init_db.py --sync-products` → start the server
3. `docker-compose.yml` — one `web` service, bind-mount `shopping_cart.db`
4. `touch shopping_cart.db` (so Docker mounts a file, not a folder) then
   `docker compose up --build`

**Checkpoint:** `docker compose down && docker compose up --build` on a
clean machine produces a fully working app at http://127.0.0.1:5000, and
`shopping_cart.db` on the host has real data in it you can open with
`sqlite3` or DB Browser for SQLite.

**Reference files:** `Dockerfile`, `docker-compose.yml`,
`docker-entrypoint.sh`

**If you have extra time in Session 6, or want a Session 7:** pick from the
stretch goals below.

---

## Stretch goals / homework (pick what fits your students' pace)

Roughly ordered easiest → hardest:

- **Product detail page** — a dedicated `/products/<id>` route+template
  instead of only a card on the dashboard
- **Order history** — a `/orders` page listing a user's past orders
  (`Order.query.filter_by(user_id=...)`), linking to `order_confirmation.html`
  for each
- **Stock enforcement** — decrement `Product.stock` on checkout, refuse to
  add to cart (or checkout) past available stock
- **Pagination** on the dashboard once there are 100+ products
- **"Remember me"** on login (`login_user(user, remember=True)`)
- **Admin product edit** (currently only add/remove — add an edit form)
- **Unit tests** with `pytest` + Flask's test client, pointed at an
  in-memory SQLite database (`sqlite:///:memory:`) so tests don't touch
  `shopping_cart.db`
- **Environment-specific config** (`DevConfig`/`ProdConfig` classes) and a
  production-ready WSGI server (`waitress` or `gunicorn`) in the Dockerfile
