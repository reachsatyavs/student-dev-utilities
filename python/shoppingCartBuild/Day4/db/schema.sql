-- Session 1: run this once to create shopping_cart.db and its tables by
-- hand, in plain SQL. Flask-SQLAlchemy (init_db.py) creates these same
-- tables from models.py, so you do NOT have to run this script for the app
-- to work -- it exists so students can see the schema in plain SQL before
-- it's expressed as Python classes.
--
-- Run it with:
--   sqlite3 shopping_cart.db < db/schema.sql
--
-- Unlike SQL Server, there's no separate "CREATE DATABASE" step: the file
-- shopping_cart.db *is* the database, and sqlite3 creates it the moment you
-- point it at a filename that doesn't exist yet.

PRAGMA foreign_keys = ON;

CREATE TABLE users (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    username       VARCHAR(80)  NOT NULL UNIQUE,
    email          VARCHAR(120) NOT NULL UNIQUE,
    password_hash  VARCHAR(255) NOT NULL,
    is_admin       BOOLEAN      NOT NULL DEFAULT 0,
    created_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    external_id    INTEGER,
    title          VARCHAR(200)   NOT NULL,
    description    VARCHAR(1000),
    category       VARCHAR(100),
    price          DECIMAL(10,2)  NOT NULL,
    stock          INTEGER        NOT NULL DEFAULT 0,
    thumbnail_url  VARCHAR(500),
    created_at     DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE cart_items (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    product_id  INTEGER NOT NULL REFERENCES products(id),
    quantity    INTEGER NOT NULL DEFAULT 1,
    added_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, product_id)
);

CREATE TABLE orders (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL REFERENCES users(id),
    total_amount  DECIMAL(10,2) NOT NULL,
    status        VARCHAR(20) NOT NULL DEFAULT 'placed',
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_items (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id            INTEGER NOT NULL REFERENCES orders(id),
    product_id          INTEGER NOT NULL REFERENCES products(id),
    quantity            INTEGER NOT NULL,
    price_at_purchase   DECIMAL(10,2) NOT NULL
);
