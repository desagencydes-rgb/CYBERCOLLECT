import time

class SudokuSolver:
    def __init__(self, grid):
        self.grid = grid
        self.n = len(grid)
        self.sub_n = int(self.n ** 0.5)
        self.solutions = []

    def is_valid(self, row, col, num):
        """Vérifie si num peut être placé à (row, col)."""
        # Ligne
        for x in range(self.n):
            if self.grid[row][x] == num:
                return False
        # Colonne
        for x in range(self.n):
            if self.grid[x][col] == num:
                return False
        # Sous-carré
        start_row = row - row % self.sub_n
        start_col = col - col % self.sub_n
        for i in range(self.sub_n):
            for j in range(self.sub_n):
                if self.grid[i + start_row][j + start_col] == num:
                    return False
        return True

    def find_empty_location(self):
        """Trouve une case vide avec l'heuristique MRV."""
        min_options = self.n + 1
        best_pos = None
        for i in range(self.n):
            for j in range(self.n):
                if self.grid[i][j] == 0:
                    options = 0
                    for num in range(1, self.n + 1):
                        if self.is_valid(i, j, num):
                            options += 1
                    if options < min_options:
                        min_options = options
                        best_pos = (i, j)
        return best_pos

    def solve(self):
        """Backtracking simple avec MRV."""
        pos = self.find_empty_location()
        if not pos:
            return True # Terminé
        
        row, col = pos
        for num in range(1, self.n + 1):
            if self.is_valid(row, col, num):
                self.grid[row][col] = num
                if self.solve():
                    return True
                self.grid[row][col] = 0 # Backtrack
        return False

    def print_grid(self):
        for row in self.grid:
            print(" ".join(map(str, row)))

def solve_demonstration():
    grid = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]

    solver = SudokuSolver(grid)
    print("Grille initiale :")
    solver.print_grid()
    
    start = time.time()
    if solver.solve():
        print("\nSolution trouvée en {:.4f}s :".format(time.time() - start))
        solver.print_grid()
    else:
        print("\nPas de solution.")

if __name__ == "__main__":
    solve_demonstration()
