# Shopping Cart — Windows Setup (Student Handout)

Follow these steps in order. Every command goes in **PowerShell** (the
terminal built into VS Code, or the Windows Terminal app).

The README uses macOS/Linux commands. This file is the Windows version —
several commands are genuinely different, and are marked where they matter.

By the end you'll have the app running at http://127.0.0.1:5000 and be
logged in as the admin.

---

## Step 1 — Check Python

```powershell
python --version
```

You need **3.10 or newer**. If you see an error, or a version like 3.8,
install Python from [python.org/downloads](https://www.python.org/downloads/).

> During install, tick **"Add python.exe to PATH"** on the first screen.
> It is easy to miss and everything else fails without it.

Close and reopen PowerShell after installing, then check the version again.

---

## Step 2 — Get the code

```powershell
cd d:\project
git clone https://github.com/reachsatyavs/student-dev-utilities.git
cd student-dev-utilities\python\shoppingCart
```

No Git? Download the ZIP from the same page on GitHub ("Code" → "Download
ZIP"), extract it, and `cd` into the `python\shoppingCart` folder inside.

Confirm you are in the right folder — this must list `app.py`:

```powershell
ls
```

**Every remaining command runs from this folder.**

---

## Step 3 — Create a virtual environment

A "venv" is a private folder of packages for this project only, so this
app's libraries never clash with another project's.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Your prompt should now start with `(.venv)`. That prefix is how you know
it worked.

### If activation fails with "running scripts is disabled on this system"

This is Windows blocking PowerShell scripts by default. Allow them for
your own account (safe, and does not need admin):

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Answer `Y`, then run `.venv\Scripts\Activate.ps1` again.

> Note: the activation path is `.venv\Scripts\` on Windows, not
> `.venv/bin/` as shown in most tutorials.

---

## Step 4 — Install the packages

```powershell
pip install -r requirements.txt
```

Installs Flask, Flask-SQLAlchemy, Flask-Login, python-dotenv and requests.
Needs an internet connection. Takes about 30 seconds.

Check it worked:

```powershell
pip list
```

---

## Step 5 — Create your settings file

```powershell
Copy-Item .env.example .env
```

> PowerShell has no `cp` command in the way the README shows — use
> `Copy-Item`.

You do not need to edit `.env`. Every setting already has a working
default. It exists so you can change things later without touching code.

---

## Step 6 — Create the database

```powershell
python init_db.py --sync-products
```

This does three things:

1. Creates `shopping_cart.db` — the entire database, one single file
2. Creates the tables (`users`, `products`, `cart_items`, `orders`, `order_items`)
3. Creates the admin account, and downloads ~30 products from dummyjson.com

You should see output ending with `Synced 30 new product(s) from the API.`

> No internet? Run `python init_db.py` without the flag. The app works,
> but the product list starts empty.

---

## Step 7 — Run the app

```powershell
python -m flask --app app run --debug
```

Leave this window open — the server runs until you stop it. Open your
browser to:

**http://127.0.0.1:5000**

Press **Ctrl+C** in the terminal to stop the server when you're done.

---

## Step 8 — Log in

Use the admin account created in Step 6:

| Field    | Value       |
| -------- | ----------- |
| Username | `admin`     |
| Password | `Admin@123` |

Then try the app end to end:

1. Browse the products on the dashboard
2. Add something to your cart, change the quantity, check out
3. Visit **Admin → Users** (admin only) to see registered accounts
4. Log out, click **Register**, make your own student account, and log in
   as that instead — note it has no admin menu

---

## Coming back later

Steps 1–6 are one-time. Each new session, you only need:

```powershell
cd d:\project\student-dev-utilities\python\shoppingCart
.venv\Scripts\Activate.ps1
python -m flask --app app run --debug
```

---

## Troubleshooting

| What you see | What it means | Fix |
| --- | --- | --- |
| `python : The term 'python' is not recognized` | Python isn't on PATH | Reinstall Python with "Add python.exe to PATH" ticked |
| `running scripts is disabled on this system` | PowerShell blocks scripts | `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` |
| `ModuleNotFoundError: No module named 'flask'` | venv not activated | Run `.venv\Scripts\Activate.ps1` — look for `(.venv)` in the prompt |
| `Address already in use` / port 5000 busy | Server already running elsewhere | Close the other terminal, or run with `--port 5001` |
| Dashboard shows no products | Products never synced | `python init_db.py --sync-products` |
| `no such table: users` | Step 6 skipped | Run `python init_db.py` |
| Login fails as admin | Password was changed in `.env` | Delete `shopping_cart.db`, rerun Step 6 |
| `The '<' operator is reserved for future use` | Used a Linux command in PowerShell | See "Looking inside the database" below |

---

## Optional — Looking inside the database

You do **not** need this to run the app. Python talks to SQLite through
its own built-in `sqlite3` module, which is always present.

This is only if you want to open the `.db` file and run SQL by hand.

**Easiest:** install [DB Browser for SQLite](https://sqlitebrowser.org/) and
open `shopping_cart.db` — a spreadsheet-like view of every table.

**Command line:** download the **sqlite-tools** zip (not the DLL zip) from
[sqlite.org/download.html](https://www.sqlite.org/download.html), unzip to
a folder such as `D:\project\sqlite`, and add that folder to your PATH via
*Start → "environment variables" → Edit → User variables → Path → New*.
**Restart VS Code afterwards**, not just the terminal.

Then:

```powershell
sqlite3 shopping_cart.db
```
```
sqlite> .tables
sqlite> SELECT username, email, is_admin FROM users;
sqlite> .quit
```

To run a `.sql` file, note that **PowerShell does not support the `<`
operator** used in most tutorials. Use sqlite's own `.read` instead:

```powershell
sqlite3 shopping_cart.db ".read db/schema.sql"
```
