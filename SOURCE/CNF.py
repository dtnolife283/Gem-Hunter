from pysat.formula import CNF
from pysat.solvers import Minisat22
from itertools import combinations

def read_file(filename):
    with open(filename, 'r') as f:
        matrix = []
        for line in f:
            matrix.append(line.strip().split(','))
    return matrix

def map_convert_CNF(matrix):
    rows, cols = len(matrix), len(matrix[0])
    cnf = CNF()

    # Define variables for each cell
    variables = [[(i * cols + j + 1) for j in range(cols)] for i in range(rows)]

    # Add constraints for each cell
    for r in range(rows):
        for c in range(cols):
            num_adjacent_traps = matrix[r][c]

            # If the cell is known (not '_')
            if num_adjacent_traps != '_':
                cnf.append([-variables[r][c]])
                num_adjacent_traps = int(num_adjacent_traps)
                adjacent_vars = []

                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols:
                            if matrix[nr][nc] == '_':
                                adjacent_vars.append(variables[nr][nc])

                if num_adjacent_traps == len(adjacent_vars):
                    tmp = CNF()
                    for var in adjacent_vars:
                        tmp.append([var])
                    cnf.extend(tmp.clauses)
                    continue
                else:
                    cnf.append(adjacent_vars)
                    cnf.append([-x for x in adjacent_vars])
                    for i in range(1, len(adjacent_vars) + 1):
                        if i == num_adjacent_traps:
                            continue
                        else:
                            for combination in combinations(adjacent_vars, i):
                                clause = [x if x not in combination else -x for x in adjacent_vars]
                                cnf.append(clause)  
    return cnf

# Example matrix
matrix = [
    [3, '_', 2, '_'],
    ['_', '_', 2, '_'],
    ['_', 3, 1, '_']
]

# Convert matrix to CNF
cnf = map_convert_CNF(matrix)

# Use SAT solver to find satisfying assignment
with Minisat22(bootstrap_with=cnf.clauses) as solver:
    rows, cols = len(matrix), len(matrix[0])
    # Define variables for each cell
    variables = [[(i * cols + j + 1) for j in range(cols)] for i in range(rows)]
    if solver.solve():
        # Get the satisfying assignment
        satisfying_assignment = solver.get_model()

        # Print out the results
        rows, cols = len(matrix), len(matrix[0])
        for r in range(rows):
            for c in range(cols):
                cell_var = (r * cols) + c + 1
                if satisfying_assignment[cell_var - 1] > 0:
                    print(f'Cell ({variables[r][c]}) is a trap.')
    else:
        print("No solution found.")


