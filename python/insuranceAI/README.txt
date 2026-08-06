InsuranceAI - Simple Flask + AI Insurance Claim Demo
=====================================================

This is a teaching demo, not a production app. It is intentionally simple:
a student logs in, submits a claim with a text description plus an optional
photo and/or medical report, and an AI model hosted on Groq reads the inputs
and writes a short claim summary.

Note: Groq (the fast-inference API host, used here) is a different company
from Grok (xAI's own model). Groq hosts open models like Llama and offers a
free tier with no credit card required, which is why it's used here.

--------------------------------------------------------------------
1. Prerequisites
--------------------------------------------------------------------
- Python 3.10 or later
- MySQL server + phpMyAdmin (e.g. via XAMPP / MAMP / WAMP, or a
  standalone MySQL install with phpMyAdmin)
- A free Groq API key from https://console.groq.com/keys
  (sign up, no credit card needed for the free tier; rate limits apply and
  can change over time - check the current terms on the Groq console.)

--------------------------------------------------------------------
2. Create the database in phpMyAdmin
--------------------------------------------------------------------
1. Open phpMyAdmin in your browser (usually http://localhost/phpmyadmin).
2. Click "New" in the left sidebar.
3. Database name: insurance_ai
4. Collation: utf8mb4_general_ci (or leave default)
5. Click "Create".

You do not need to create tables manually - step 5 below does that for you.

--------------------------------------------------------------------
3. Set up the Python environment
--------------------------------------------------------------------
    cd python/insuranceAI
    python -m venv venv
    source venv/bin/activate        (Windows: venv\Scripts\activate)
    pip install -r requirements.txt

--------------------------------------------------------------------
4. Configure environment variables
--------------------------------------------------------------------
    cp .env.example .env

Edit .env:
    SECRET_KEY=any-random-string
    DB_HOST=127.0.0.1
    DB_PORT=3306
    DB_USER=root                (your MySQL/phpMyAdmin username)
    DB_PASSWORD=                (your MySQL/phpMyAdmin password)
    DB_NAME=insurance_ai
    GROQ_API_KEY=your-groq-api-key
    GROQ_BASE_URL=https://api.groq.com/openai/v1
    GROQ_MODEL=meta-llama/llama-4-scout-17b-16e-instruct

If you don't have a Groq API key yet, leave GROQ_API_KEY empty - the app
will still run and will fall back to a simple auto-generated summary
instead of calling the AI, so the demo works offline too.

Model note: Groq's available models (and which ones support reading images)
can change - check https://console.groq.com/docs/models for the current
list and swap GROQ_MODEL in .env if the one above is no longer offered.

--------------------------------------------------------------------
5. Create the database tables + a demo login
--------------------------------------------------------------------
    python init_db.py

This creates the "users" and "claims" tables in the insurance_ai database
and a demo user:
    username: student
    password: student123

--------------------------------------------------------------------
6. Run the app
--------------------------------------------------------------------
    python app.py

Open http://localhost:5000 and log in with the demo user above.

--------------------------------------------------------------------
7. Try it out
--------------------------------------------------------------------
1. Log in.
2. Click "New Claim".
3. Fill in age / location / gender.
4. For the description, copy-paste one of the sample claims in
   samples/claims/ (claim_1.txt ... claim_5.txt), or write your own.
5. Optionally attach a photo (any .png/.jpg) as the "incident photo".
6. Optionally attach one of the sample medical reports in
   samples/medical_reports/ (medical_report_1.txt ... medical_report_5.txt)
   as the "medical report" file.
7. Submit. You'll be taken to the claim detail page, which shows the
   AI-generated claim summary underneath your submitted details.
8. Go back to "Dashboard" to see all your submitted claims.
9. Click "Logout" to end the session.

--------------------------------------------------------------------
8. Project structure
--------------------------------------------------------------------
app.py                      - Flask routes (login, logout, dashboard, claims)
config.py                   - reads settings from .env
extensions.py                - Flask-SQLAlchemy / Flask-Login setup
models.py                    - User and Claim database models
ai_claim.py                  - calls Groq AI to summarize a claim (with offline fallback)
init_db.py                   - creates tables + demo user
templates/                   - HTML pages (Jinja2)
static/style.css             - minimal styling
uploads/                      - uploaded images/reports are stored here (gitignored)
samples/claims/               - 5 sample claim descriptions to copy-paste
samples/medical_reports/       - 5 sample dummy medical reports to upload

--------------------------------------------------------------------
9. Notes / limitations (read before you extend this)
--------------------------------------------------------------------
- This is a classroom demo: no CSRF tokens beyond Flask defaults, no rate
  limiting, no email verification, no password reset flow.
- Passwords are hashed (werkzeug), but there's no "forgot password" flow.
- All sample medical reports and claims are entirely fictional dummy data
  written for testing - they are not real patient records.
- Uploaded files are served back without virus scanning - fine for a local
  demo, not fine for production.
- Never commit your real .env file or API key - .env is already listed in
  .gitignore.

--------------------------------------------------------------------
10. Troubleshooting
--------------------------------------------------------------------
- "Can't connect to MySQL server" - check DB_HOST/DB_PORT/DB_USER/
  DB_PASSWORD in .env match what phpMyAdmin's "Server" info shows.
- "Access denied for user" - your MySQL user/password in .env is wrong,
  or that user doesn't have privileges on the insurance_ai database.
- AI summary always shows "[Offline demo summary...]" - GROQ_API_KEY is
  missing/invalid, or the Groq API call failed; check the error text
  appended to the summary for details.
- "model not found" / "model decommissioned" error from Groq - the model
  in GROQ_MODEL is no longer available; pick a current one from
  https://console.groq.com/docs/models and update .env.
