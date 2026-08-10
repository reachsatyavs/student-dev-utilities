# Day 5 (optional) — Security Hardening

Session 5 of [`COURSE_PLAN.md`](../../shoppingCart/COURSE_PLAN.md). Builds
on Day4 with the security features that
[`../../shoppingCart/`](../../shoppingCart) deliberately leaves out of the
core app (see that project's README for why). Do this once Day1–4 feel
solid — it's not required to have a working shopping cart app.

## What's new since Day4

- `extensions.py` — adds `limiter` (Flask-Limiter), `csrf` (Flask-WTF),
  `mail` (Flask-Mail)
- Every existing POST form gets a hidden `csrf_token` input
- `models.py` — `User` gains `failed_login_attempts` / `locked_until` and
  lockout helper methods; adds `PasswordResetOTP`
- `routes/auth.py` — `login` is rate-limited (`5 per minute` per IP) and
  locks an account after too many failed attempts
- `utils/email_utils.py` — generates and emails a 6-digit OTP (falls back to
  printing it to the console if `MAIL_USERNAME` isn't set in `.env`)
- `routes/password_reset.py` — `forgot_password` → `verify_otp` →
  `reset_password`, as three separate steps
- `templates/auth/forgot_password.html`, `verify_otp.html`,
  `reset_password.html`

## Run it

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python init_db.py --sync-products
python -m flask --app app run --debug
```

Leave `MAIL_USERNAME` blank in `.env` to have OTP codes print to the
terminal instead of emailing — no SMTP account needed to test the flow.

## Checkpoint

- 6 wrong login attempts in a row locks the account (a 7th attempt is
  rejected even with the correct password) for the configured lockout window
- Requesting a password reset, entering the code (from the console or your
  inbox), and setting a new password logs back in with the new password —
  and the old one no longer works
