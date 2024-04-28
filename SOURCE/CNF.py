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

# # Example matrix
# matrix = [
#     ['_', '_',  2, '_'],
#     ['_', '_',  4,  '_'],
#     ['_', '_', '_', 2],
#     ['_',  4,   3, '_']
# ]

matrix = [
    [2, '_', '_', 1, '_'],
    ['_', 5, 4, 2, '_'],
    [3, '_', '_', 2, 1],
    [3, '_', '_', '_', 1],
    ['_', '_', '_', 2, 1],
]

# Convert matrix to CNF
cnf = map_convert_CNF(matrix)





# Use SAT solver to find satisfying assignment
def solveWithSAT(matrix, cnd):
    print("Solving with SAT library")
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
                        print('T', end=' ')
                    else:
                        if matrix[r][c] == '_':
                            print('G', end=' ')
                        else:
                            print(matrix[r][c], end=' ')
                print()
        else:
            print("No solution found.")

solveWithSAT(matrix, cnf)


def remove_duplicate_lists(matrix):
    unique_lists = set()
    result = []

    for sublist in matrix:
        # Convert the sublist to a tuple so it can be hashed and compared
        sublist_tuple = tuple(sublist)
        if sublist_tuple not in unique_lists:
            result.append(sublist)
            unique_lists.add(sublist_tuple)

    return result



def applySingleResolution(cnfList):
    i = 0
    length = len(cnfList)
    flag = False
    while (i < length):
        if len(cnfList[i]) != 1:
            i += 1
            continue
        val = cnfList[i][0]

        j = 0
        while (j < length):
            if len(cnfList[j]) == 1:
                j += 1
                continue

            k = 0
            while (k < len(cnfList[j])):
                literal = cnfList[j][k]
                if val == literal:
                    cnfList.remove(cnfList[j])
                    flag = True
                    j -= 1
                    i -= 1
                    length -= 1
                    break
                if val == -literal:
                    cnfList[j].remove(-val)
                    flag = True
                    k -= 1
                
                k += 1
            j += 1
        i += 1
    return flag



from itertools import product

def evaluate_clause(clause, truth_values):
    for literal in clause:
        if (literal > 0 and truth_values[abs(literal)] == 1) or (literal < 0 and truth_values[abs(literal)] == 0):
            return True
    return False

def evaluate_cnf(cnf, truth_values):
    for clause in cnf:
        if not evaluate_clause(clause, truth_values):
            return False
    return True

def all_possible_truth_values(cnf):
    literals = set(abs(literal) for clause in cnf for literal in clause)
    possible_truth_values = list(product([0, 1], repeat=len(literals)))
    satisfiable_values = []
    for values in possible_truth_values:
        truth_values_dict = {literal: value for literal, value in zip(literals, values)}
        truth_values_list = [[lit] if truth_values_dict[lit] == 1 else [-lit] for lit in literals]
        if evaluate_cnf(cnf, truth_values_dict):
            satisfiable_values.append(truth_values_list)
    return satisfiable_values



def checkForTrap(val, cnfList):
    for i in cnfList:
        if len(i) == 0:
            continue
        if val == i[0]:
            return True
    return False



def solveOptimal(cnfList):
    print("\noptinal solution")
    while(applySingleResolution(cnfList)):
        pass

    cnfList = remove_duplicate_lists(cnfList)
    newList = []
    for i in range (len(cnfList) - 1, -1, -1):
        if len(cnfList[i]) > 1:
            newList.append(cnfList[i])
            cnfList.remove(cnfList[i])
    
    newList = all_possible_truth_values(newList)

    result = []

    for i in newList:
        resultList = cnfList[:]
        for j in i:
            resultList.append(j)
        result.append(resultList)
    
    for subList in result:
        resultMatrix = [row[:] for row in matrix]
        for i in range (len(resultMatrix)):
            for j in range (len(resultMatrix)):
                if resultMatrix[i][j] == '_':
                    val = i * len(resultMatrix) + j + 1
                    if checkForTrap(val, subList):
                        resultMatrix[i][j] = "T"
                    else:
                        resultMatrix[i][j] = "G"
        for i in range (len(resultMatrix)):
            for j in range (len(resultMatrix)):
                print(resultMatrix[i][j], end = ' ')
            print()
        print('\n')
    




cnfMatrix = [row[:] for row in cnf.clauses]
cnfMatrix = remove_duplicate_lists(cnfMatrix)

solveOptimal(cnfMatrix)
