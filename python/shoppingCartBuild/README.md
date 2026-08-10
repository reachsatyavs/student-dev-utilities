# Shopping Cart — Day-by-Day Build

Companion to [`../shoppingCart/`](../shoppingCart), which is the complete,
finished app. This folder is the same project broken into daily checkpoints,
matching the sessions in [`../shoppingCart/COURSE_PLAN.md`](../shoppingCart/COURSE_PLAN.md).
Use it in class, or hand it to students to try on their own between sessions.

## How this folder works

**Each `DayN/` (Day1–Day5) is a complete, standalone, runnable app** — not a
diff. `cd` into any day, install its `requirements.txt`, run `init_db.py`,
and start the server: that day's features work, and nothing from later days
is there yet. You don't need to work through earlier days first to run a
later one.

| Folder | What's new | Session |
|---|---|---|
| [`Day1/`](./Day1) | Env setup, SQLite schema, "Hello, Flask!" | 1 |
| [`Day2/`](./Day2) | Registration, login, logout | 2 |
| [`Day3/`](./Day3) | Product dashboard (synced from an API), shopping cart | 3 |
| [`Day4/`](./Day4) | Checkout, admin panel (users + products) | 4 |
| [`Day5/`](./Day5) | CSRF protection, login rate limiting, OTP email password reset | 5 (optional) |
| [`Day6/`](./Day6) | Docker files only — see below | 6 (optional) |

Each `DayN/` folder has its own short README with what's new that day, how
to run it, and that day's checkpoint. For the full explanation of *why* each
piece exists, see [`../shoppingCart/COURSE_PLAN.md`](../shoppingCart/COURSE_PLAN.md)
— these folders are the code; that file is the narrative.

**Day6 is different from the others**: since Day4 + Docker already equals
`../shoppingCart/` almost exactly, `Day6/` isn't a full duplicate app — it's
just the 3 Docker files (`Dockerfile`, `docker-compose.yml`,
`docker-entrypoint.sh`). Copy them into your `Day4/` folder to containerize
it. See [`Day6/README.md`](./Day6/README.md).

## A note on Day5

Day5 is optional and is the one exception to "each day builds on the day
before in the main `shoppingCart/` project" — `../shoppingCart/` intentionally
does **not** include CSRF/rate-limiting/OTP reset (see its README for why).
`Day5/` here is where that code actually lives, built on top of Day4, for
students who want to see it working once the fundamentals feel solid.

## Keeping this in sync

These folders were generated to match `../shoppingCart/` and `COURSE_PLAN.md`
as of when this was written. If the main project or course plan changes
later in a way that affects earlier sessions, these snapshots need a manual
refresh — they won't update themselves.
