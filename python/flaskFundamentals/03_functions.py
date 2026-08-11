"""
03 - Functions
==============
A function is a named, reusable block of code. You write it once, then
"call" it (run it) as many times as you want, with different inputs
(called parameters/arguments) each time.

Run this file with:
    python 03_functions.py
"""


# A function with no parameters -- it always does the same thing.
def say_hello():
    print("Hello there!")


say_hello()  # calling the function runs the code inside it
say_hello()  # you can call it again, as many times as you like


# A function with parameters -- values you pass in when you call it.
def add(a, b):
    result = a + b
    return result  # `return` sends a value back to whoever called the function


total = add(3, 5)
print("3 + 5 =", total)
print("10 + 20 =", add(10, 20))  # you can use the result directly, too


# A function can have a default value for a parameter, used if the caller
# doesn't provide one.
def greet(name="student"):
    return f"Welcome, {name}!"


print(greet("Ravi"))
print(greet())  # no argument passed, so it falls back to "student"


# print() displays something; return sends a value back to be used later.
# Mixing them up is a common beginner bug -- a function that only prints
# and forgets to return can't have its result stored in a variable.
def add_and_print(a, b):
    print(a + b)  # only prints -- the caller gets nothing back


nothing = add_and_print(2, 2)  # prints "4"
print("What add_and_print gave back:", nothing)  # prints "None"

# --- Try it yourself ---
# 1. Write a function `multiply(a, b)` that returns a * b, then call it.
# 2. Write a function `is_even(n)` that returns True if n is even, else False.
#    (Hint: n % 2 == 0 checks whether n divides evenly by 2.)
