#!/usr/bin/env python3
"""
Crossword generator for "HIER NAAR LINKS" dropping puzzle.
Each word's first letter contributes to the secret message.
"""

import random
import os

# Pad relatief aan dit script — werkt op elke machine
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_JSON = os.path.join(SCRIPT_DIR, 'crossword_data.json')

# Words and their metadata
# Secret message: H-I-E-R-N-A-A-R-L-I-N-K-S
WORDS_DATA = [
    {"word": "HOLIDAY",    "secret_pos": 0, "clue": "Madonna (1983)",                   "secret": "H"},
    {"word": "INTOTHEGROOVE", "secret_pos": 0, "clue": "Madonna (1985)",               "secret": "I"},
    {"word": "EVERYWHERE", "secret_pos": 0, "clue": "Fleetwood Mac (1987)",             "secret": "E"},
    {"word": "RELAX",      "secret_pos": 0, "clue": "Frankie Goes to Hollywood (1983)", "secret": "R"},
    {"word": "NIKITA",     "secret_pos": 0, "clue": "Elton John (1985)",                "secret": "N"},
    {"word": "AFRICA",     "secret_pos": 0, "clue": "Toto (1982)",                      "secret": "A"},
    {"word": "ALONE",      "secret_pos": 0, "clue": "Heart (1987)",                     "secret": "A"},
    {"word": "RESPECTABLE", "secret_pos": 0, "clue": "Mel & Kim (1987)",               "secret": "R"},
    {"word": "LUKA",       "secret_pos": 0, "clue": "Suzanne Vega (1987)",              "secret": "L"},
    {"word": "IWANTTOBREAKFREE", "secret_pos": 0, "clue": "Queen (1984)",              "secret": "I"},
    {"word": "NOTORIOUS",  "secret_pos": 0, "clue": "Duran Duran (1986)",               "secret": "N"},
    {"word": "KYRIE",      "secret_pos": 0, "clue": "Mr. Mister (1985)",                "secret": "K"},
    {"word": "SHOUT",      "secret_pos": 0, "clue": "Tears for Fears (1984)",           "secret": "S"},
]

SIZE = 25

def make_grid(size):
    return [['.' for _ in range(size)] for _ in range(size)]

def can_place(grid, word, row, col, direction, size):
    dr, dc = (0, 1) if direction == 'A' else (1, 0)
    end_r = row + dr * (len(word) - 1)
    end_c = col + dc * (len(word) - 1)

    if end_r >= size or end_c >= size or row < 0 or col < 0:
        return False

    # Check cell before word
    br, bc = row - dr, col - dc
    if 0 <= br < size and 0 <= bc < size and grid[br][bc] != '.':
        return False

    # Check cell after word
    ar, ac = row + dr * len(word), col + dc * len(word)
    if 0 <= ar < size and 0 <= ac < size and grid[ar][ac] != '.':
        return False

    has_cross = False

    for i, letter in enumerate(word):
        r = row + dr * i
        c = col + dc * i
        cell = grid[r][c]

        if cell == letter:
            has_cross = True
        elif cell != '.':
            return False
        else:
            # Check sides (perpendicular) - no adjacent parallel words
            if direction == 'A':
                if r > 0 and grid[r-1][c] != '.' and cell == '.':
                    return False
                if r < size-1 and grid[r+1][c] != '.' and cell == '.':
                    return False
            else:
                if c > 0 and grid[r][c-1] != '.' and cell == '.':
                    return False
                if c < size-1 and grid[r][c+1] != '.' and cell == '.':
                    return False

    return has_cross

def place_word(grid, word, row, col, direction):
    dr, dc = (0, 1) if direction == 'A' else (1, 0)
    for i, letter in enumerate(word):
        grid[row + dr*i][col + dc*i] = letter

def find_placements(grid, word, placed, size):
    placements = []
    for pw, pr, pc, pd in placed:
        # Find common letters
        for i, pl in enumerate(pw):
            for j, wl in enumerate(word):
                if pl == wl:
                    # Try to cross
                    if pd == 'A':
                        # placed is across, new word goes down
                        new_row = pr - j
                        new_col = pc + i
                        new_dir = 'D'
                    else:
                        # placed is down, new word goes across
                        new_row = pr + i
                        new_col = pc - j
                        new_dir = 'A'

                    if can_place(grid, word, new_row, new_col, new_dir, size):
                        placements.append((new_row, new_col, new_dir))
    return placements

def generate_crossword(words_data, size=SIZE, attempts=100):
    best_placed = []

    for attempt in range(attempts):
        words = [w['word'] for w in words_data]
        random.shuffle(words)

        grid = make_grid(size)
        placed = []

        # Place first word in center, across
        first = words[0]
        cr = size // 2
        cc = size // 2 - len(first) // 2
        place_word(grid, first, cr, cc, 'A')
        placed.append((first, cr, cc, 'A'))

        for word in words[1:]:
            placements = find_placements(grid, word, placed, size)
            if placements:
                r, c, d = random.choice(placements)
                place_word(grid, word, r, c, d)
                placed.append((word, r, c, d))

        if len(placed) > len(best_placed):
            best_placed = placed[:]
            best_grid = [row[:] for row in grid]
            if len(placed) == len(words):
                break

    return best_grid, best_placed

def trim_grid(grid, placed, size):
    # Find bounding box of placed words
    min_r, max_r, min_c, max_c = size, 0, size, 0
    for row in range(size):
        for col in range(size):
            if grid[row][col] != '.':
                min_r = min(min_r, row)
                max_r = max(max_r, row)
                min_c = min(min_c, col)
                max_c = max(max_c, col)

    # Add 1 cell border
    min_r = max(0, min_r - 1)
    min_c = max(0, min_c - 1)
    max_r = min(size-1, max_r + 1)
    max_c = min(size-1, max_c + 1)

    new_grid = []
    for r in range(min_r, max_r+1):
        new_grid.append(grid[r][min_c:max_c+1])

    new_placed = []
    for word, r, c, d in placed:
        new_placed.append((word, r - min_r, c - min_c, d))

    return new_grid, new_placed

def print_grid(grid):
    for row in grid:
        print(' '.join(row))

def main():
    random.seed(42)

    grid, placed = generate_crossword(WORDS_DATA, SIZE, attempts=200)
    grid, placed = trim_grid(grid, placed, SIZE)

    print(f"\nPlaced {len(placed)} / {len(WORDS_DATA)} words\n")
    print_grid(grid)

    rows = len(grid)
    cols = len(grid[0]) if grid else 0
    print(f"\nGrid size: {rows} x {cols}")

    # Map word -> (row, col, direction)
    placed_map = {w: (r, c, d) for w, r, c, d in placed}

    print("\nPlaced words:")
    for wd in WORDS_DATA:
        word = wd['word']
        if word in placed_map:
            r, c, d = placed_map[word]
            direction = "Across" if d == 'A' else "Down"
            print(f"  {word:12s} ({direction}) at ({r},{c}), secret='{wd['secret']}'")
        else:
            print(f"  {word:12s} *** NOT PLACED ***")

    # Output JSON for HTML use
    import json

    result = {
        "grid": grid,
        "rows": rows,
        "cols": cols,
        "words": []
    }

    # Assign clue numbers
    # A cell gets a number if it starts an across or down word
    cell_numbers = {}
    clue_num = 1

    # Collect start cells
    start_cells = set()
    for wd in WORDS_DATA:
        word = wd['word']
        if word in placed_map:
            r, c, d = placed_map[word]
            start_cells.add((r, c))

    # Number cells in reading order (top-left to bottom-right)
    for r in range(rows):
        for c in range(cols):
            if (r, c) in start_cells:
                cell_numbers[(r, c)] = clue_num
                clue_num += 1

    secret_order = 1
    for wd in WORDS_DATA:
        word = wd['word']
        if word in placed_map:
            r, c, d = placed_map[word]
            num = cell_numbers.get((r, c), 0)
            secret_cell_r = r + (wd['secret_pos'] if d == 'D' else 0)
            secret_cell_c = c + (wd['secret_pos'] if d == 'A' else 0)

            result["words"].append({
                "word": word,
                "row": r,
                "col": c,
                "direction": "across" if d == 'A' else "down",
                "clue_num": num,
                "clue": wd['clue'],
                "secret_pos": wd['secret_pos'],
                "secret_letter": wd['secret'],
                "secret_order": secret_order,
                "secret_row": secret_cell_r,
                "secret_col": secret_cell_c,
            })
            secret_order += 1

    # Sort by clue number
    result["words"].sort(key=lambda x: x["clue_num"])

    with open(OUTPUT_JSON, 'w') as f:
        json.dump(result, f, indent=2)

    print("\nJSON saved to crossword_data.json")
    print("\nSecret message letters in order:")
    for wd in WORDS_DATA:
        word = wd['word']
        if word in placed_map:
            print(f"  {wd['secret']} from {word}")

if __name__ == '__main__':
    main()
