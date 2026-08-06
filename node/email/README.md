# Email Utility (Gmail + Nodemailer)

A minimal, copy-paste-friendly example of sending email from a Node.js app
using a Google (Gmail) account. Includes a simple HTML form so you can see
the full flow: **form → server → Gmail → inbox**.

## Folder structure

```
email/
├── mailer.js          # Reusable module - the only file you need to copy into another project
├── server.js           # Express server: serves the form and handles /send-email
├── public/
│   └── index.html      # Simple form page
├── .env.example         # Copy to .env and fill in your credentials
└── package.json
```

## 1. Packages needed

```bash
npm install express nodemailer dotenv
```

## 2. Get a Gmail App Password

Gmail does not allow sign-in with your normal password from apps like this.
You need an **App Password**:

1. Go to your [Google Account security page](https://myaccount.google.com/security).
2. Turn on **2-Step Verification** if it isn't already on (app passwords are hidden until this is enabled).
3. Go directly to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
   (or search "App passwords" in the Google Account search bar).
4. Under "App name," type something like `Utilities Email` and click **Create**.
5. Google shows a **16-character code** (grouped like `abcd efgh ijkl mnop`).
   Copy it now — it is shown only once and can't be viewed again later.
   If you lose it, delete the entry on that page and create a new one.

## 3. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your real values (remove spaces from the app password):

```
GMAIL_USER=your-email@gmail.com
GMAIL_APP_PASSWORD=abcdefghijklmnop
PORT=3000
```

`.env` is listed in `.gitignore`, so it will not be committed.

## 4. Run it

```bash
npm install
npm start
```

You should see `Server running at http://localhost:3000` in the terminal.

## 5. Test it

**Option A — Web form:**
Open [http://localhost:3000](http://localhost:3000), fill in the To/Subject/Message fields, and submit.
You should see a "Email sent!" message, and the recipient should receive the mail.

**Option B — curl** (in a separate terminal, while the server is running):

```bash
curl -X POST http://localhost:3000/send-email \
  -H "Content-Type: application/json" \
  -d '{"to":"your-email@gmail.com","subject":"Test Email","message":"Hello from the email utility!"}'
```

A successful response looks like:

```json
{"success":true,"message":"Email sent!"}
```

Then check the recipient's inbox (and spam folder).

### Troubleshooting

- **`EADDRINUSE` / "address already in use"** — something is already running on port 3000.
  Find and stop it: `lsof -i :3000` to see the process, then stop that terminal/process (or change `PORT` in `.env`).
- **"Invalid login" / `535-5.7.8` error from Google** — the app password is wrong, has spaces in it,
  or 2-Step Verification isn't enabled. Regenerate the app password (step 2) and update `.env`.
- **Nothing arrives** — check spam/junk, and confirm `GMAIL_USER` in `.env` matches the account the app password was created for.

## 5. Using `mailer.js` in your own project

`mailer.js` is fully self-contained and framework-agnostic. To reuse it:

1. Copy `mailer.js` into your project.
2. Install its dependencies: `npm install nodemailer dotenv`.
3. Add `GMAIL_USER` and `GMAIL_APP_PASSWORD` to your `.env`.
4. Import and call it wherever you need to send mail:

```js
const { sendEmail } = require("./mailer");

await sendEmail({
  to: "someone@example.com",
  subject: "Hello!",
  text: "This is a plain-text email.",
  // html: "<b>Or send HTML instead</b>"
});
```

That's it — no other setup required. Swap `service: "gmail"` in `mailer.js`
for any other provider Nodemailer supports if you outgrow Gmail.
