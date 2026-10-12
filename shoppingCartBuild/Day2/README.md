# Day 2 — User Registration & Login

Session 2 of [`COURSE_PLAN.md`](../../shoppingCart/COURSE_PLAN.md). Adds
account creation and session-based login on top of Day1.

## What's new since Day1

- `models.py` — `User` gains `set_password()`, `check_password()`, and
  `UserMixin` (for Flask-Login)
- `extensions.py` — adds `login_manager`
- `routes/auth.py` — `register`, `login`, `logout`, as a `register_routes(app)`
  function (no Blueprints, no app-factory — just `app.route(...)` added
  directly to the shared `app` object)
- `templates/base.html`, `templates/auth/register.html`,
  `templates/auth/login.html`

## Run it

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python init_db.py
python -m flask --app app run --debug
```

## Checkpoint

- Register a new account — its password is hashed in `shopping_cart.db`,
  not stored as plaintext
- Log out, log back in with the same credentials
- Visiting `/` while logged in shows a "Hello, {username}!" greeting (the
  real dashboard arrives in Day3)

## Next

Day3 adds the product dashboard and shopping cart.
