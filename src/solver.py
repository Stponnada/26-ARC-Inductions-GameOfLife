#---------------------------- TASK 1 ----------------------------
def count_neighbors(grid, row, col):
    """
    Counts the number of alive neighbors for a specific cell in the grid.
    A cell can have up to 8 neighbors (horizontal, vertical, and diagonal).
    
    Args:
        grid (list of lists): The current 2D state of the game.
        row (int): The row index of the cell.
        col (int): The column index of the cell.
        
    Returns:
        int: The total number of alive neighbors (0 to 8).
    """
    
    alive_count = 0

    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    # The 8 neighbors are every (row + dr, col + dc) combination where dr and
    # dc each range over -1, 0, +1 -- except (0, 0), which is the cell itself.
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue  # skip the cell itself; we only want its neighbors

            nr = row + dr
            nc = col + dc

            # Only look at neighbors that actually exist inside the grid.
            # The lower bound (>= 0) is critical: a negative index would
            # silently wrap to the opposite edge instead of being ignored.
            if 0 <= nr < rows and 0 <= nc < cols:
                # A cell's value is already 1 (alive) or 0 (dead), so adding
                # the value directly is the same as "add 1 if alive".
                alive_count += grid[nr][nc]

    return alive_count

#---------------------------- TASK 2 ----------------------------
def compute_next_generation(grid):
    """
    Generates the next state of the grid based on Conway's rules.
    
    Args:
        grid (list of lists): The current 2D state of the game.
        
    Returns:
        list of lists: A BRAND NEW 2D grid representing the next generation.
        
    Note:
        - Do NOT modify the original `grid` directly while iterating through it. 
          You must create a new grid to store the updated states, otherwise 
          your changes will mess up the neighbor counts for subsequent cells!
    """
    
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    
    # Create a new blank grid of the same size, filled with 0s (dead cells)
    next_grid = [[0 for _ in range(cols)] for _ in range(rows)]
    
    # Visit every cell, always reading from the original `grid` snapshot and
    # writing results into `next_grid` so this generation stays untouched.
    for r in range(rows):
        for c in range(cols):
            neighbors = count_neighbors(grid, r, c)
            is_alive = grid[r][c] == 1

            # The four rules collapse into two cases that produce a live cell:
            #   - exactly 3 neighbors: alive next gen no matter the current state
            #     (this is both "reproduction" and "survival with 3")
            #   - currently alive with exactly 2 neighbors: survives
            # Every other case stays dead, which next_grid already defaults to.
            if neighbors == 3 or (is_alive and neighbors == 2):
                next_grid[r][c] = 1

    return next_grid