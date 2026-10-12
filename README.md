# Student Dev Utilities

Small, self-contained Python/Flask projects and demo apps for college
students — from first scripts through full web apps.

Each folder is **self-contained**: it has its own dependency file and its
own README with setup steps, so you can copy one folder out and run it on
its own.

## Key links

- **Shopping Cart Blueprint** (problem statement → design → features → user
  stories → use cases → test cases, on one page):
  [reachsatyavs.github.io/student-dev-utilities/shoppingCart/PROJECT_BLUEPRINT.html](https://reachsatyavs.github.io/student-dev-utilities/shoppingCart/PROJECT_BLUEPRINT.html)
- **Software Engineering concept slides**:
  [reachsatyavs.github.io/mca-project-lifecycle/sem4_13week_pilot/concepts_slides.html#/19](https://reachsatyavs.github.io/mca-project-lifecycle/sem4_13week_pilot/concepts_slides.html#/19)

## Projects

| Folder | What it does |
|---|---|
| [`flaskFundamentals/`](./flaskFundamentals) | "Session 0" for `shoppingCart/`: standalone scripts covering variables, data types, functions, writing your own module, installing/using a package, a first Flask server, a login page, splitting routes into their own file, and calling an external API from a route |
| [`insuranceAI/`](./insuranceAI) | Flask + MySQL (phpMyAdmin) demo app: login/dashboard where a user files an insurance claim (text + optional photo/medical report) and Grok AI (xAI) reads it and writes a claim summary |
| [`shoppingCart/`](./shoppingCart) | Flask + SQLite teaching project: registration/login, dashboard + cart synced from a products API, checkout, admin panel. Ships with a 6-session/12-hour course plan |
| [`shoppingCartBuild/`](./shoppingCartBuild) | Companion to `shoppingCart/`: the same app broken into `Day1`–`Day6` folders, each a runnable checkpoint matching one course-plan session |

## How to use this repo

1. Pick the project you need (e.g. `shoppingCart/`).
2. Read that folder's README. It lists the packages to install and any
   credentials or setup required.
3. Run it standalone, or copy the folder into your own project.

## Requirements

- Python 3.10+ and pip

## Start here

- New to Python/Flask: [`flaskFundamentals/`](./flaskFundamentals)
- Full app: [`shoppingCart/README.md`](./shoppingCart/README.md) or
  [`insuranceAI/README.txt`](./insuranceAI/README.txt)
- Course instructors: [`shoppingCart/COURSE_PLAN.md`](./shoppingCart/COURSE_PLAN.md)
  and [`shoppingCartBuild/README.md`](./shoppingCartBuild/README.md)
