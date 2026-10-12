# Day 6 (optional) — Dockerize the App

Session 6 of [`COURSE_PLAN.md`](../../shoppingCart/COURSE_PLAN.md).

Unlike Day1–Day5, this folder is **not** a standalone app — it's just the 3
Docker files. Day4 (or Day5, if you did that too) plus these three files
*is* Day6; duplicating the whole app again would just be a copy of a folder
that already exists.

## What's here

- `Dockerfile` — Python base image, installs `requirements.txt`, copies the
  code, runs `docker-entrypoint.sh`
- `docker-entrypoint.sh` — runs `init_db.py --sync-products`, then starts
  the server
- `docker-compose.yml` — one `web` service, bind-mounting `shopping_cart.db`
  into the container so the database is a plain file on your host machine

## Use it

Copy all three files into your `Day4/` folder (or `Day5/`, if you built
that too):

```bash
cp Dockerfile docker-entrypoint.sh docker-compose.yml ../Day4/
cd ../Day4
touch shopping_cart.db   # first time only, so Docker mounts a file, not a folder
docker compose up --build
```

## Checkpoint

`docker compose down && docker compose up --build` produces a fully working
app at http://127.0.0.1:5000 with no manual setup step, and
`shopping_cart.db` on your host has real data you can open with `sqlite3` or
DB Browser for SQLite.
