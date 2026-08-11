"""
04 - Writing and using your own module
=======================================
Any .py file can be imported by another .py file, as long as they're in
the same folder (or Python otherwise knows where to find it). This lets
you split code across files instead of writing one giant script.

Open greetings.py in this same folder first -- it just defines two plain
functions, nothing special about it.

Run this file with:
    python 04_your_own_module.py
"""

import greetings  # this imports greetings.py, no install needed -- it's
                   # right here in the same folder

message = greetings.say_hello("Priya")
print(message)

print(greetings.say_goodbye("Priya"))

# You can also import specific functions directly, so you don't have to
# type "greetings." every time.
from greetings import say_hello

print(say_hello("Ravi"))

# --- Try it yourself ---
# 1. Add a new function to greetings.py, e.g. def say_welcome(name): ...
# 2. Import and call it from here.
