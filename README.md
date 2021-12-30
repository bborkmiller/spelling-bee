# Spelling Bee Helper
This program is meant to help with the administrative work of solving the New York Times Spelling Bee game. It won't solve the puzzle for you, but it will count up the words you've already found and compare them to the official grid of answers and two letter combinations.

# Usage
Instantiate a SpellingBee with

```python
bee = SpellingBee()
```
Tell it which words you've found by pasting your found words from the NYTimes game page into a string variable and running the `read_found_words` method:

```python
paste = """
Anew
Awed
Dawn
Dawned
Hawed
"""
bee.read_found_words(paste)
```

At this point, running `bee.print_comparison()` will import the list of answers from nytimes.com, generate grids and two letter lists for the player and the official solution, and print a comparison grid and two letter list:

```
- Grid Comparison
    4  5  6  7  8   Σ
A:  -  -  -  -  -   0
D:  -  -  -  -  -   0
H:  1  1  1  -  2   5
W: 12  6 1-  1  1  30
Σ: 13  7 11  1  3  35

- Two Letter List Comparison
HE-5 
WA-8 WE-8 WH-6 WI-8 
```

There are more granular methods for printing out information:
* `print_grid(type=[player|official])` - Prints a word count grid
* `print_two_letter_list(type=[player|official])` - Prints a two letter list
* `print_counts(type=[player|official])` - Prints both the grid and the TLL
