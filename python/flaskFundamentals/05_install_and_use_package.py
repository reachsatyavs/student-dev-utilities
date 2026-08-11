"""
05 - Installing and using an external package
================================================
A module you write yourself (like greetings.py) only needs an import.
A package someone ELSE wrote has to be installed first, with pip
(Python's package installer), before you can import it.

Install it first:
    pip install requests

`requests` is one of the most common Python packages -- it lets your code
fetch data from a URL on the internet, the same way a browser would.

Run this file with:
    python 05_install_and_use_package.py
"""

import requests  # only works because we installed it with pip above

# dummyjson.com is a free, no-signup API that returns fake sample data --
# useful for practicing without needing a real account or API key anywhere.
response = requests.get("https://dummyjson.com/quotes/1")

# The response comes back as JSON (text that looks like a Python dict).
# .json() converts it into an actual Python dict we can work with.
data = response.json()

print("Raw dict:", data)
print("Just the quote:", data["quote"])
print("Just the author:", data["author"])

# --- Try it yourself ---
# 1. Change the URL to https://dummyjson.com/quotes/2 and see a different quote.
# 2. Try https://dummyjson.com/quotes/random -- run the file a few times,
#    notice the quote changes each time.
