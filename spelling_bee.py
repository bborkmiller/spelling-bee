import json
import re
import urllib.request


class SpellingBee:
    def __init__(self):
        pass

    def read_found_words(self, input_text):
        """Read in pasted text and set the found_words property"""

        self.found_words = [w.upper() for w in input_text.split()]

    def generate_grid(self, words):
        """Generate a grid from a list of words.
        
        The grid is a dictionary with the format
            {'Letter': [list of counts by word length]}
        """

        first_letters = {w[0] for w in words}
        max_len = max([len(w) for w in words])

        # Populate a dummy dictionary
        # Odd construction to make a deep copy of the list of zeroes
        empty_counts = [
            ([0] * (max_len - 3)).copy() for i in range(0, len(first_letters))
        ]
        grid = dict(zip(first_letters, empty_counts))

        for word in words:
            grid[word[0]][len(word) - 4] += 1

        return grid

    def generate_two_letter_list(self, words):
        """Count words by their first two letters"""

        # Populate a dummy dictionary for the two letter list
        tl_combos = {w[:2] for w in words}
        two_letter_list = dict(zip(tl_combos, [0] * len(tl_combos)))

        # Loop through found words and fill in counts
        for word in words:
            two_letter_list[word[:2]] += 1

        return two_letter_list

    def generate_player_grid(self):

        try:
            found = self.found_words
        except AttributeError:
            raise AttributeError(
                "No record of found words. Run read_found_words on your word list first."
            )

        self.player_grid = self.generate_grid(found)
        
    def generate_player_tll(self):
        
        try:
            found = self.found_words
        except AttributeError:
            raise AttributeError(
                "No record of found words. Run read_found_words on your word list first."
            )
            
        self.two_letter_list = generate_two_letter_list(found)

    def format_grid(self, grid):
        """Format a grid dictionary into a string for printing"""

        grid_output = ""
        max_len = len(list(grid.values())[0]) + 3

        header = (
            "  " + "".join([str(l).rjust(3) for l in range(4, max_len + 1)]) + "   Σ\n"
        )
        grid_output += self.bold(header)

        # Format the letter rows
        for letter in sorted(grid):
            counts = "".join([str(count).rjust(3) for count in grid[letter]]).replace(
                "0", "-"
            )
            letter_sum = self.bold(str(sum(grid[letter])).rjust(4))
            grid_output += f"{self.bold(letter)}:{counts}{letter_sum}\n"

        # Generate the summary row
        length_sums = [sum(i) for i in zip(*grid.values())]
        total = str(sum(length_sums)).rjust(4)
        sum_string = "".join([str(sum).rjust(3) for sum in length_sums])
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

        # Check for a missing index, if counts go e.g. 4 5 6 8
        header = [int(i) for i in lines[0].split("\t")[:-1]]
        full_range = list(range(4, max(header) + 1))
        index_compare = set(full_range) - set(header)
        if index_compare:
            missing_index = sorted(list(index_compare))

        # Parse the grid text into a dictionary
        grid = {}
        for line in lines[1:-1]:
            letter, counts_str = line.split(":")
            counts_str = counts_str.strip().split("\t")[:-1]
            counts = [int(count) if "-" not in count else 0 for count in counts_str]
            if index_compare:
                for mi in missing_index:
                    counts.insert(mi - 4, 0)
            grid[letter] = counts

        self.official_grid = grid

        # Parse two letter list text into a dictionary
        if tll_text:
            tll_items = [line.split() for line in tll_text.split("\n")]
            tll_items = [item for sublist in tll_items for item in sublist]
            two_letter_list = {}
            for item in tll_items:
                two_letter_list[item[:2]] = int(item[3:])

            self.official_two_letter_list = two_letter_list

    def compare_grids(self):
        """Compares the player's grid to the official grid"""
        official_grid = self.official_grid
        grid = self.player_grid

        # Pad out player's grid if necessary
        len_diff = len(list(official_grid.values())[0]) - len(list(grid.values())[0])
        if len_diff:
            for letter in grid.keys():
                grid[letter] = grid[letter] + [0] * len_diff

        diffs = {}
        for letter in sorted(official_grid):
            if letter in grid:
                diff = [a - b for a, b in zip(official_grid[letter], grid[letter])]
            else:
                diff = official_grid[letter]

            diffs[letter] = diff

        self.grid_comparison = diffs

    def compare_two_letter_lists(self):
        official_tll = self.official_two_letter_list
        player_tll = self.two_letter_list

        diffs = {}
        for combo in sorted(official_tll):
            diff = official_tll[combo] - player_tll.get(combo, 0)
            diffs[combo] = diff

        self.two_letter_list_comparison = diffs

    def print_player_grid(self):
        print(self.bold("- Player's Grid"))
        try:
            grid = self.player_grid
        except AttributeError:
            self.generate_player_grid()
            grid = self.player_grid

        print(self.format_grid(grid))

    def print_official_grid(self):
        print(self.bold("- Official Grid"))
        print(self.format_grid(self.official_grid))

    def print_two_letter_list(self):
        try:
            tll = self.two_letter_list
        except AttributeError:
            self.generate_two_letter_list()
            tll = self.two_letter_list

        print(self.format_two_letter_list(tll))

    def print_official_two_letter_list(self):
        print(self.format_two_letter_list(self.official_two_letter_list))

    def print_counts(self):
        self.print_player_grid()
        print()
        self.print_two_letter_list()

    def print_official_counts(self):
        self.print_official_grid()
        print()
        self.print_official_two_letter_list()

    def print_grid_comparison(self):
        print(self.bold("- Grid Comparison"))
        try:
            grid = self.grid_comparison
        except AttributeError:
            self.compare_grids()
            grid = self.grid_comparison

        print(self.format_grid(grid))

    def print_two_letter_list_comparison(self, only_nonzero=True):
        try:
            comparison = self.two_letter_list_comparison
        except AttributeError:
            self.compare_two_letter_lists()
            comparison = self.two_letter_list_comparison

        print(self.bold("- Two Letter List Comparison"))
        print(self.format_two_letter_list(comparison, only_nonzero))

    def bold(self, input):
        """Bold a word (for output purposes)"""
        return "\033[1m" + input + "\033[0m"

    def import_puzzle(self):
        """
        Read in answers directly from nytimes.com

        Logic borrowed from/inspired by https://github.com/thisisparker/nytsb/blob/main/nytsb.py
        """
        url = "https://www.nytimes.com/puzzles/spelling-bee"
        res = urllib.request.urlopen(url)

        pattern = re.compile("window.gameData = .*?}}")

        scripts = re.findall(pattern, res.read().decode("utf-8"))
        data = json.loads(scripts[0][len("wondow.gameData = ") :])

        self.answers = [w.upper() for w in data["today"]["answers"]]
        
        self.official_grid = self.generate_grid(self.answers)
        self.official_two_letter_list = self.generate_two_letter_list(self.answers)
        