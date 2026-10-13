#!/bin/bash
# Program 5: grep menu
#   1 -> lines with exactly two characters
#   2 -> lines with more than one blank space
# Usage: bash prog5.sh <filename>

# Step 1: make sure a file name was given
if [ $# -lt 1 ]
then
    echo "Usage: bash prog5.sh <filename>"
    exit 1
fi

# Step 2: save the file name
file1="$1"

# Step 3: show the menu and read the choice
echo "Enter the number"
echo "1: Lines with exactly two characters"
echo "2: Lines with more than one blank space"
read userinput

# Step 4 + 5: run the matching grep
case $userinput in
    1)
        grep '^..$' "$file1"
        ;;
    2)
        grep ' .* ' "$file1"
        ;;
    *)
        echo "Invalid choice. Enter 1 or 2."
        ;;
esac
