# Day 1 — Environment Setup + Database Design

Session 1 of [`COURSE_PLAN.md`](../../shoppingCart/COURSE_PLAN.md). A Flask
app with one route, talking to a SQLite database with `users` and `products`
tables.

## What's here

- `config.py`, `extensions.py` — configuration and the bare `db = SQLAlchemy()`
- `models.py` — `User` and `Product` only (no login logic yet — that's Day2)
- `app.py` — a single `/` route that returns `"Hello, Flask!"`
- `init_db.py` — creates the tables and seeds one admin user
- `db/schema.sql` — the same two tables, in plain SQL, for comparison

## Run it

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python init_db.py
python -m flask --app app run --debug
```

Optional, before `python init_db.py` — build the same schema by hand once,
to see it in plain SQL:

```bash
sqlite3 shopping_cart.db < db/schema.sql
sqlite3 shopping_cart.db ".tables"
rm shopping_cart.db   # then let init_db.py create it again from models.py
```

## Checkpoint

- http://127.0.0.1:5000 shows "Hello, Flask!"
- `shopping_cart.db` exists and has `users` (with one seeded admin row) and
  `products` tables — check with `sqlite3 shopping_cart.db ".tables"`

## Next

Day2 adds registration and login.
