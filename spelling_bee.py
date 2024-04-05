import json
import re
import urllib.request
from collections import Counter


class SpellingBee:
    def __init__(self, found_words=None):
        if found_words:
            self.found_words = [w.upper() for w in found_words.split()]
        else:
            self.found_words = None

        self.answers = None
        self.official_grid = None
        self.official_two_letter_list = None

        self.two_letter_list = None
        self.player_grid = None

        self.grid_comparison = None
        self.two_letter_list_comparison = None

    def bold(self, input):
        """Bold a word (for output purposes)"""
        return "\033[1m" + input + "\033[0m"

    def read_found_words(self, input_text):
        """Read in pasted text and set the found_words property"""

        self.found_words = [w.upper() for w in input_text.split()]

    def import_puzzle(self):
        """
        Read in answers directly from nytimes.com

        Logic borrowed from/inspired by https://github.com/thisisparker/nytsb/blob/main/nytsb.py
        """
        url = "https://www.nytimes.com/puzzles/spelling-bee"
        res = urllib.request.urlopen(url)

        pattern = re.compile("window.gameData = .*?}}")

        scripts = re.findall(pattern, res.read().decode("utf-8"))
        data = json.loads(scripts[0][len("window.gameData = ") :])

        self.answers = [w.upper() for w in data["today"]["answers"]]

        self.official_grid = self.generate_grid(self.answers)
        self.official_two_letter_list = self.generate_two_letter_list(self.answers)

    def generate_grid(self, words):
        """Generate a word count grid from a list of words.

        The grid is a dictionary with the format
            {'letter': Counter(length:count...)}
        """

        first_letters = {w[0] for w in words}

        grid = {}
        for letter in first_letters:
            grid[letter] = Counter([len(w) for w in words if w[0] == letter])

        return grid

    def generate_two_letter_list(self, words):
        """Count words by their first two letters"""

        two_letter_list = Counter([w[0:2] for w in words])

        return two_letter_list

    def generate_player_grid(self):
        """Initialize the player's word count grid"""

        if self.found_words is None:
            raise AttributeError(
                "No record of found words. Run read_found_words on your word list first."
            )
        else:
            self.player_grid = self.generate_grid(self.found_words)

    def generate_player_tll(self):
        """Initialize the player's two-letter list"""

        if self.found_words is None:
            raise AttributeError(
                "No record of found words. Run read_found_words on your word list first."
            )
        else:
            self.two_letter_list = self.generate_two_letter_list(self.found_words)

    def format_grid(self, grid):
        """Format a grid dictionary into a string for printing"""

        grid_output = ""

        # Get max word length
        max_len = max([max(c.keys()) for c in grid.values() if len(c) > 0])

        header = f"  {''.join([str(l).rjust(3) for l in range(4, max_len + 1)])}   Σ\n"
        grid_output += self.bold(header)

        # Format the letter rows
        default_counts = dict.fromkeys(range(4, max_len + 1), 0)
        length_sums = dict.fromkeys(range(4, max_len + 1), 0)
        for letter, counts in sorted(grid.items()):
            full_counts = default_counts | counts
            counts_text = "".join([str(c).rjust(3) for c in list(full_counts.values())])
            letter_sum = self.bold(str(sum(counts.values())).rjust(4))
            grid_output += f"{letter.upper()}:{counts_text}{letter_sum}\n"

            # Add count by word length to length_sums
            for k, v in counts.items():
                length_sums[k] += v

        # Generate the summary row
        total = str(sum(length_sums.values())).rjust(4)
        sum_string = "".join([str(sum).rjust(3) for sum in length_sums.values()])
        summary = self.bold(f"Σ:{sum_string}{total}")
        grid_output += summary

        return grid_output

    def format_two_letter_list(self, tll, only_nonzero=False):
        """Format a TLL into a string for printing"""

        if only_nonzero:
            tll = {k: v for (k, v) in tll.items() if v > 0}

        if len(tll) == 0:
            tll_output = "No combos to display"

        else:
            tll_output = ""
            prev_key = sorted(tll)[0]
            for key in sorted(tll):
                if key[0] != prev_key[0]:
                    tll_output += "\n"
                tll_output += f"{key}-{tll[key]} "
                prev_key = key

        return tll_output

    def read_official_grid(self, input_text):
        """Parse pasted text of the official grid. Also parse the official two
        letter list, if that's part of the pasted text."""

        # Split off the two letter list, if found
        try:
            grid_text, tll_text = input_text.split("Two letter list:\n")
        except ValueError:
            grid_text = input_text

        lines = grid_text.split("\n")

        # Eliminate any extra blank rows at the beginning or end
        lines = [line for line in lines if line]

        header = [int(i) for i in lines[0].split("\t")[:-1] if i]

        # Parse the grid text into a dictionary
        grid = {}
        for line in lines[1:-1]:
            letter, counts_str = line.split(":")
            counts_str = counts_str.strip().split("\t")[:-1]
            counts = [int(count) if count != "-" else 0 for count in counts_str]
            grid[letter] = Counter(dict(zip(header, counts)))

        self.official_grid = grid

        # Parse two letter list text into a dictionary
        if tll_text:
            tll_items = [line.split() for line in tll_text.split("\n")]
            tll_items = [item for sublist in tll_items for item in sublist]
            two_letter_list = Counter()
            for item in tll_items:
                two_letter_list[item[:2]] = int(item[3:])

            self.official_two_letter_list = two_letter_list

    def compare_grids(self):
        """Compares the player's grid to the official grid"""

        if self.player_grid is None:
            self.generate_player_grid()

        if self.official_grid is None:
            self.import_puzzle()

        diffs = {}
        for letter in sorted(self.official_grid):
            diff = self.official_grid[letter] - self.player_grid.get(letter, Counter())
            diffs[letter] = diff

        self.grid_comparison = diffs

    def compare_two_letter_lists(self):
        """Compares the player's two-letter list to the official one"""

        if self.two_letter_list is None:
            self.generate_player_tll()

        if self.official_two_letter_list is None:
            self.import_puzzle()

        self.two_letter_list_comparison = (
            self.official_two_letter_list - self.two_letter_list
        )

    def print_grid(self, type="player"):
        if type == "player":
            if self.player_grid is None:
                self.generate_player_grid()

            grid = self.player_grid
            print(self.bold("- Player's Grid"))

        elif type == "official":
            if self.official_grid is None:
                self.import_puzzle()

            grid = self.official_grid
            print(self.bold("- Official Grid"))

        else:
            raise ValueError("type={type} - Valid types are 'player' and 'official'")

        print(self.format_grid(grid))

    def print_two_letter_list(self, type="player"):
        if type == "player":
            if self.two_letter_list is None:
                self.generate_player_tll()
            tll = self.two_letter_list

        elif type == "official":
            if self.official_two_letter_list is None:
                self.import_puzzle()
            tll = self.official_two_letter_list

        else:
            raise ValueError("type={type} - Valid types are 'player' and 'official'")

        print(self.format_two_letter_list(tll))

    def print_counts(self, type="player"):
        if type not in ["player", "official"]:
            raise ValueError("type={type} - Valid types are 'player' and 'official'")

        self.print_grid(type=type)
        print()
        self.print_two_letter_list(type=type)

    def print_grid_comparison(self):
        if self.grid_comparison is None:
            self.compare_grids()

        print(self.bold("- Grid Comparison"))
        print(self.format_grid(self.grid_comparison))

    def print_two_letter_list_comparison(self, only_nonzero=True):
        if self.two_letter_list_comparison is None:
            self.compare_two_letter_lists()

        print(self.bold("- Two Letter List Comparison"))
        print(
            self.format_two_letter_list(self.two_letter_list_comparison, only_nonzero)
        )

    def print_comparison(self):
        self.print_grid_comparison()
        print()
        self.print_two_letter_list_comparison()
