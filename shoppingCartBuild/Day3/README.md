# Day 3 — Dashboard + Shopping Cart

Session 3 of [`COURSE_PLAN.md`](../../shoppingCart/COURSE_PLAN.md). Adds a
product catalog (pulled from a real API) and a working cart on top of Day2.
Checkout isn't wired up yet — that's Day4.

## What's new since Day2

- `models.py` — adds `CartItem`
- `services/product_api.py` — pulls products from
  [dummyjson.com](https://dummyjson.com/products) and syncs them into the
  local `products` table
- `routes/dashboard.py` — product listing, search, category filter
- `routes/cart.py` — view/add/update/remove (no checkout yet)
- `templates/dashboard.html`, `templates/cart.html`

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

- The dashboard shows real products pulled from dummyjson.com
- Adding the same product to your cart twice increases its quantity instead
  of creating a duplicate row
- The cart page shows correct per-item and grand totals

## Next

Day4 adds checkout and the admin panel.
