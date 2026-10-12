# Day 4 — Checkout + Admin Panel

Session 4 of [`COURSE_PLAN.md`](../../shoppingCart/COURSE_PLAN.md). Adds
checkout (turning a cart into an order) and an admin panel on top of Day3.

This is the last required day — **Day4 is functionally the same app as
[`../../shoppingCart/`](../../shoppingCart)**, just without the Docker files
(see [`../Day6/`](../Day6) for those). Day5 (security hardening) is optional.

## What's new since Day3

- `models.py` — adds `Order`, `OrderItem`
- `routes/cart.py` — adds `checkout` and `order_confirmation`
- `utils/decorators.py` — `@admin_required`
- `routes/admin.py` — list users + reset a user's password directly; list,
  add, and remove products; re-sync from the API
- `templates/order_confirmation.html`, `templates/admin/users.html`,
  `templates/admin/products.html`, `templates/403.html`

## Run it

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python init_db.py --sync-products
python -m flask --app app run --debug
```

## Checkpoint

- Checking out empties the cart and creates a visible order
- Logging in as the seeded admin (see `.env` for credentials) shows every
  registered user, with a working "reset password" form per user
- The admin can add a product by hand and remove one that isn't referenced
  by any past order

## Next

- Day5 (optional): CSRF protection, login rate limiting, OTP email password
  reset
- Day6 (optional): Docker
