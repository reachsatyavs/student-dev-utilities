"""
02 - Data Types
===============
Every value in Python has a type, which determines what you can do with
it. Python figures out the type automatically from the value you assign --
you never have to declare it yourself. `type(x)` tells you what type a
value is.

Run this file with:
    python 02_data_types.py
"""

# str (string) - text, written inside quotes
name = "Priya"
print(name, "->", type(name))

# int (integer) - a whole number, no decimal point
age = 22
print(age, "->", type(age))

# float - a number with a decimal point
height_in_meters = 1.68
print(height_in_meters, "->", type(height_in_meters))

# bool (boolean) - only two possible values: True or False
is_student = True
print(is_student, "->", type(is_student))

# list - an ordered, changeable collection of values, in square brackets
favorite_subjects = ["Math", "Physics", "Computer Science"]
print(favorite_subjects, "->", type(favorite_subjects))
print("First subject:", favorite_subjects[0])  # lists start counting at 0

# dict (dictionary) - key/value pairs, in curly braces
student = {
    "name": "Priya",
    "age": 22,
    "is_student": True,
}
print(student, "->", type(student))
print("Name from the dict:", student["name"])

# --- Try it yourself ---
# 1. Make a list called `numbers` with five int values, then print it.
# 2. Make a dict called `book` with keys "title" and "pages", then print
#    book["title"] on its own.
# 3. Print type(3.0) and type(3) and compare -- why are they different?
