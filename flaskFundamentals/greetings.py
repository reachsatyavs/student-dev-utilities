"""
This file is a MODULE -- just a plain .py file containing functions that
another script can import and reuse. A PACKAGE is the next step up: a
folder full of modules with an `__init__.py` file inside it, so Python
knows to treat the whole folder as one importable unit
(you'll see a folder-shaped example of that in 08_flask_modular/).

This file isn't meant to be run directly -- open 04_your_own_module.py
instead, which imports the functions below.
"""


def say_hello(name):
    return f"Hello, {name}!"


def say_goodbye(name):
    return f"Goodbye, {name}, see you soon!"
