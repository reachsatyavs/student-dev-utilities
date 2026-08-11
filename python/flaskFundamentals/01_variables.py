"""
01 - Variables
==============
A variable is a name that points to a value stored in memory. Think of it
as a labeled box: you put something in the box, and later you can look
inside the box (or replace what's in it) just by using its name.

Run this file with:
    python 01_variables.py
"""

# Creating a variable: name = value
student_name = "Asha"
age = 20
is_enrolled = True

print(student_name)
print(age)
print(is_enrolled)

# A variable can be reassigned to a new value at any time.
age = 21
print("After a birthday, age is now:", age)

# Variables can be combined into new values.
greeting = "Hello, " + student_name + "!"
print(greeting)

# Naming rules:
# - names can contain letters, numbers, and underscores
# - names cannot start with a number
# - names are case-sensitive (age and Age are two different variables)
# - use descriptive names: `age` is clearer than `a`
first_name = "Ravi"
last_name = "Kumar"
full_name = first_name + " " + last_name
print(full_name)

# --- Try it yourself ---
# 1. Create a variable called `city` with your city's name and print it.
# 2. Create a variable called `year_born`, then compute and print
#    `2026 - year_born` to get an age.
