# Utilities

Small, modular, copy-paste-friendly utility functions for integrating common
third-party services into your own projects — email, WhatsApp, Razorpay, and
more. Organized by language.

Each service folder is **self-contained**: it has its own dependency file,
its own README with setup steps, and a single core module you can drop
straight into another project without dragging the rest of this repo along.

## Structure

```
Utilities/
├── node/     # Node.js utilities
└── python/   # Python utilities
```

## node/

| Folder | Status | What it does |
|---|---|---|
| [`node/email/`](./node/email) | ✅ Ready | Send email from a Node.js app using a Gmail account (Nodemailer), with a simple HTML form demo |
| [`node/whatsapp/`](./node/whatsapp) | 🚧 Coming soon | Send WhatsApp messages programmatically |
| [`node/razorpay/`](./node/razorpay) | 🚧 Coming soon | Accept payments using Razorpay |

## python/

🚧 Coming soon.

## How to use this repo

1. Pick the language folder (`node/` or `python/`), then the integration you need (e.g. `node/email/`).
2. Read that folder's `README.md` — it lists the exact packages to install
   and the credentials/setup required for that service.
3. Copy the core module file (e.g. `mailer.js`) into your own project, or
   copy the whole folder to run it standalone as a demo.

Each module is intentionally kept minimal — one core file that does one job,
plus an optional demo server/form to see it working end-to-end.

## Requirements

- Node.js utilities: [Node.js](https://nodejs.org/) 18+ and npm (comes with Node.js)
- Python utilities: Python 3.10+ and pip

Start here: [`node/email/README.md`](./node/email/README.md)
