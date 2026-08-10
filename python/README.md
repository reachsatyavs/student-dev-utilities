# Python Utilities

Same idea as [`../node/`](../node/) — small, self-contained, copy-paste-friendly
Python modules and demo apps for integrating common third-party services into
your own projects.

| Folder | Status | What it does |
|---|---|---|
| [`insuranceAI/`](./insuranceAI) | ✅ Ready | Flask + MySQL (phpMyAdmin) demo app: login/dashboard where a user files an insurance claim (text + optional photo/medical report) and Grok AI (xAI) reads it and writes a claim summary |
| [`shoppingCart/`](./shoppingCart) | ✅ Ready | Flask + SQLite teaching project: registration/login, dashboard + cart synced from a products API, checkout, admin panel. Ships with a 6-session/12-hour course plan |
| [`shoppingCartBuild/`](./shoppingCartBuild) | ✅ Ready | Companion to `shoppingCart/` — the same app broken into `Day1`–`Day6` folders, each a runnable checkpoint matching one course-plan session |

Start here: [`insuranceAI/README.txt`](./insuranceAI/README.txt) or
[`shoppingCart/README.md`](./shoppingCart/README.md) (course instructors:
see [`shoppingCart/COURSE_PLAN.md`](./shoppingCart/COURSE_PLAN.md) and
[`shoppingCartBuild/README.md`](./shoppingCartBuild/README.md))
