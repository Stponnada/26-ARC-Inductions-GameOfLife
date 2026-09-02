"""
Living Minefield -- a Minesweeper built on top of Conway's Game of Life.

The core idea: in Minesweeper, every safe tile shows how many bombs sit in its
8 neighbors. In Game of Life, `count_neighbors(grid, r, c)` returns how many
ALIVE cells sit in a cell's 8 neighbors. So if we treat "alive == bomb", the
Minesweeper number for a tile is EXACTLY count_neighbors of that tile -- the
same function written for Task 1, reused with zero changes.

We also reuse Task 2's `compute_next_generation`: instead of scattering bombs
uniformly at random, we start from a random seed and evolve it a few Game of
Life generations. The bombs settle into organic GoL structures (blocks,
blinkers, stray clusters), which makes for a more interesting minefield.

This file does NOT modify solver.py -- it only imports from it, so the graded
task is untouched and this sits cleanly on top of it.
"""

import random

from solver import count_neighbors, compute_next_generation

# ---- Board configuration ----
ROWS = 12
COLS = 12
SEED_DENSITY = 30    # % of cells alive in the initial random seed
EVOLVE_STEPS = 2     # how many GoL generations to run before freezing the mines

# ---- Display glyphs ----
HIDDEN = '.'
FLAG = '\033[91mF\033[0m'      # red F
BOMB = '\033[91m*\033[0m'      # red *
EMPTY = ' '                    # a revealed 0-tile shows blank, like real Minesweeper

# Classic Minesweeper-style colors for the adjacency numbers 1..8.
NUMBER_COLORS = {
    1: '\033[94m', 2: '\033[92m', 3: '\033[91m', 4: '\033[95m',
    5: '\033[93m', 6: '\033[96m', 7: '\033[97m', 8: '\033[90m',
}
RESET = '\033[0m'


def make_minefield(rows, cols):
    """Build the bomb layout by evolving a random Game of Life seed.

    Returns a grid of 1s (bomb) and 0s (safe), reusing compute_next_generation.
    """
    mines = [
        [1 if random.randint(1, 100) <= SEED_DENSITY else 0 for _ in range(cols)]
        for _ in range(rows)
    ]
    for _ in range(EVOLVE_STEPS):
        mines = compute_next_generation(mines)
    return mines


def reveal(mines, revealed, row, col):
    """Reveal a tile and cascade through connected 0-bomb tiles (flood fill).

    Uses an explicit stack instead of recursion. The halting rule is the key:
    we only process a tile if it hasn't been revealed yet, so each tile is
    handled at most once and the cascade always terminates.
    """
    rows = len(mines)
    cols = len(mines[0])
    stack = [(row, col)]

    while stack:
        r, c = stack.pop()

        # Base case: skip anything off-grid or already revealed. Skipping
        # already-revealed tiles is what stops the flood fill from looping.
        if not (0 <= r < rows and 0 <= c < cols):
            continue
        if revealed[r][c]:
            continue

        revealed[r][c] = True

        # count_neighbors treats "alive" as a bomb, so this IS the tile's
        # Minesweeper number. Only cascade outward when it's exactly 0 --
        # a numbered tile borders a bomb, so we must stop and let the player think.
        if count_neighbors(mines, r, c) == 0:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    stack.append((r + dr, c + dc))


def render(mines, revealed, flagged, reveal_bombs=False):
    """Turn the current board state into a printable string."""
    rows = len(mines)
    cols = len(mines[0])

    # Column headers, then each row prefixed with its index.
    header = "    " + " ".join(f"{c:>2}" for c in range(cols))
    lines = [header, "   +" + "---" * cols]

    for r in range(rows):
        cells = []
        for c in range(cols):
            if flagged[r][c] and not reveal_bombs:
                cells.append(FLAG)
            elif not revealed[r][c]:
                # On a loss we expose every bomb; otherwise keep it hidden.
                cells.append(BOMB if (reveal_bombs and mines[r][c] == 1) else HIDDEN)
            elif mines[r][c] == 1:
                cells.append(BOMB)
            else:
                n = count_neighbors(mines, r, c)
                if n == 0:
                    cells.append(EMPTY)
                else:
                    cells.append(f"{NUMBER_COLORS.get(n, '')}{n}{RESET}")
        lines.append(f"{r:>2} | " + "  ".join(cells))

    return "\n".join(lines)


def is_won(mines, revealed):
    """The player wins when every safe (non-bomb) tile has been revealed."""
    for r in range(len(mines)):
        for c in range(len(mines[0])):
            if mines[r][c] == 0 and not revealed[r][c]:
                return False
    return True


def main():
    mines = make_minefield(ROWS, COLS)
    revealed = [[False] * COLS for _ in range(ROWS)]
    flagged = [[False] * COLS for _ in range(ROWS)]

    total_bombs = sum(sum(row) for row in mines)
    print("\n=== LIVING MINEFIELD (Game of Life x Minesweeper) ===")
    print(f"Board: {ROWS}x{COLS}   Bombs: {total_bombs}")
    print("Commands:  <row> <col>  to reveal   |   f <row> <col>  to flag/unflag   |   q  to quit\n")

    while True:
        print(render(mines, revealed, flagged))

        if is_won(mines, revealed):
            print("\n\033[92mYou cleared every safe tile. The machine spirit is appeased.\033[0m\n")
            break

        raw = input("> ").strip().split()
        if not raw:
            continue
        if raw[0].lower() == 'q':
            print("Quitting.")
            break

        # Parse either "f r c" (flag) or "r c" (reveal), guarding bad input.
        flag_mode = raw[0].lower() == 'f'
        coords = raw[1:] if flag_mode else raw
        try:
            r, c = int(coords[0]), int(coords[1])
        except (ValueError, IndexError):
            print("  Bad input. Use 'row col' or 'f row col'.")
            continue
        if not (0 <= r < ROWS and 0 <= c < COLS):
            print("  Out of bounds.")
            continue

        if flag_mode:
            flagged[r][c] = not flagged[r][c]
            continue

        if flagged[r][c]:
            print("  That tile is flagged. Unflag it first with 'f'.")
            continue

        if mines[r][c] == 1:
            print(render(mines, revealed, flagged, reveal_bombs=True))
            print("\n\033[91mBOOM. You detonated a bomb. Servitorization complete.\033[0m\n")
            break

        reveal(mines, revealed, r, c)


if __name__ == '__main__':
    main()
