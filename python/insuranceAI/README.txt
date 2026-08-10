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
- MySQL server + phpMyAdmin. On macOS without XAMPP/MAMP/WAMP, this is
  Homebrew MySQL + Homebrew phpMyAdmin served by PHP's own built-in
  server (no Apache needed) - see section 2.
- A free Groq API key from https://console.groq.com/keys
  (sign up, no credit card needed for the free tier; rate limits apply and
  can change over time - check the current terms on the Groq console.)

--------------------------------------------------------------------
2. Set up MySQL + phpMyAdmin
--------------------------------------------------------------------
Install and start MySQL:
    brew install mysql
    brew services start mysql
    mysql_secure_installation      # first time only, sets the root password

Install phpMyAdmin + PHP, and serve it with PHP's built-in server (this
avoids needing Apache/httpd, which recent macOS no longer ships usably):
    brew install php phpmyadmin

Set phpMyAdmin's cookie-auth secret (one-time, required or login will fail):
    php -r "echo bin2hex(random_bytes(32));"
Copy that output into $cfg['blowfish_secret'] = '...'; in
/opt/homebrew/etc/phpmyadmin.config.inc.php (Apple Silicon path - use
/usr/local/etc/... on Intel Macs).

Start phpMyAdmin whenever you want the UI:
    cd /opt/homebrew/share/phpmyadmin
    php -S 127.0.0.1:8080

Open http://127.0.0.1:8080 and log in with your MySQL root username/password
(the same ones you'll put in .env in step 4). Then:
1. Click "New" in the left sidebar.
2. Database name: insurance_ai
3. Collation: utf8mb4_general_ci (or leave default)
4. Click "Create".

You do not need to create tables manually - step 5 below does that for you.
phpMyAdmin is just for browsing/editing rows afterward (e.g. checking what
got saved to the claims table, or clearing test data).

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
    GROQ_MODEL=qwen/qwen3.6-27b

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
Option A - not sure which category to pick? Ask the AI Advisor first:
1. Log in.
2. Click "AI Advisor" in the nav bar.
3. Paste one of the sample claims from samples/claims/ (claim_1.txt ...
   claim_5.txt) into "What happened?", or write your own.
4. Optionally attach one of the sample medical reports from
   samples/medical_reports/ (medical_report_1.txt ... medical_report_5.txt).
5. Click "Ask AI for a Suggestion". You'll get a suggested category, a
   short reason, and a numbered checklist of what to do on the New Claim
   form. See samples/CATEGORY_GUIDE.txt for which sample lands in which
   category.
6. Click "Start This Claim" to jump to New Claim with your description,
   category, and medical report already carried over.
7. Fill in the remaining fields and submit (see steps 3-7 below).

Option B - go straight to New Claim:
1. Log in.
2. Click "New Claim".
3. Fill in age / location / gender, and optionally pick a category.
4. For the description, copy-paste one of the sample claims in
   samples/claims/ (claim_1.txt ... claim_5.txt), or write your own.
5. Optionally attach a photo (any .png/.jpg) as the "incident photo".
6. Optionally attach one of the sample medical reports in
   samples/medical_reports/ (medical_report_1.txt ... medical_report_5.txt)
   as the "medical report" file.
7. Submit. You'll be taken to the claim detail page, which shows your
   category and the AI-generated claim summary underneath your submitted
   details.
8. Go back to "Dashboard" to see all your submitted claims.
9. Click "Logout" to end the session.

--------------------------------------------------------------------
8. Project structure
--------------------------------------------------------------------
app.py                      - Flask routes (login, logout, dashboard, claims, advisor)
config.py                   - reads settings from .env
extensions.py                - Flask-SQLAlchemy / Flask-Login setup
models.py                    - User and Claim database models, CLAIM_CATEGORIES list
ai_claim.py                  - calls Groq AI to summarize a claim and to suggest a
                               category + next steps (both with an offline fallback)
init_db.py                   - creates tables + demo user
templates/                   - HTML pages (Jinja2), including advisor.html
static/style.css             - minimal styling
uploads/                      - uploaded images/reports are stored here (gitignored)
samples/claims/               - 5 sample claim descriptions to copy-paste
samples/CATEGORY_GUIDE.txt    - which sample claim/report pair maps to which category
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
- AI Advisor always suggests "Other / Not Sure" with a generic checklist -
  same causes as above (missing/invalid GROQ_API_KEY, or the model doesn't
  support the response_format/JSON mode this feature relies on).
