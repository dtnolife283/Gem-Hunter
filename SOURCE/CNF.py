from pysat.formula import CNF
from pysat.solvers import Minisat22
from itertools import combinations
from itertools import product
import os
import time

def write_file(filename, matrix):
    with open(filename, 'w') as f:
        for row in matrix:
            f.write(', '.join(row) + '\n')

def read_file(filename):
    with open(filename, 'r') as f:
        matrix = []
        for line in f:
            matrix.append(line.strip().split(', '))
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
            if num_adjacent_traps != "_":
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
                elif num_adjacent_traps == 0:
                    tmp = CNF()
                    for var in adjacent_vars:
                        tmp.append([-var])
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

# Use SAT solver to find satisfying assignment
def solveWithSAT(matrix, cnf):
    print("Solving with SAT library:")
    RunTime = time.time_ns()
    res = matrix.copy()
    with Minisat22(bootstrap_with=cnf.clauses) as solver:
        rows, cols = len(matrix), len(matrix[0])
        if solver.solve():
            # Get the satisfying assignment
            satisfying_assignment = solver.get_model()

            RunTime = time.time_ns() - RunTime

            # Print out the results
            rows, cols = len(matrix), len(matrix[0])
            for r in range(rows):
                for c in range(cols):
                    cell_var = (r * cols) + c + 1
                    if satisfying_assignment[cell_var - 1] > 0:
                        print('T', end=' ')
                        res[r][c] = 'T'
                    else:
                        if matrix[r][c] == '_':
                            print('G', end=' ')
                            res[r][c] = 'G'
                        else:
                            print(matrix[r][c], end=' ')
                            res[r][c] = matrix[r][c]
                print()
            print()
            current_dir = os.path.dirname(os.path.abspath(__file__))
            current_dir = os.path.join(current_dir, "testcases")
            filename = "output_" + str(len(matrix)) + "x" + str(len(matrix[0])) + ".txt"
            write_file(os.path.join(current_dir, filename), res)
        else:
            print("No solution found.")
    return RunTime

# Optimal solution
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

visitedValue = set()

def applySingleResolution(cnfList):
    i = 0
    length = len(cnfList)
    flag = False
    while (i < length):
        if len(cnfList[i]) != 1:
            i += 1
            continue
        val = cnfList[i][0]

        if val in visitedValue:
            i += 1
            continue
        else:
            visitedValue.add(val)

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

def first_truth_values(cnf):
    literals = set(abs(literal) for clause in cnf for literal in clause)
    possible_truth_values = list(product([0, 1], repeat=len(literals)))
    for values in possible_truth_values:
        truth_values_dict = {literal: value for literal, value in zip(literals, values)}
        truth_values_list = [[lit] if truth_values_dict[lit] == 1 else [-lit] for lit in literals]
        if evaluate_cnf(cnf, truth_values_dict):
            return truth_values_list
    return []

def checkForTrap(val, cnfList):
    for i in cnfList:
        if len(i) == 0:
            continue
        if val == i[0]:
            return True
    return False

def checkNoSolution(cnfList):
    for i in cnfList:
        if len(i) != 1:
            continue
        for j in cnfList:
            if len(j) != 1:
                continue
            if i[0] + j[0] == 0:
                return True
    return False



def solveOptimal(matrix, cnfList):
    RunTime = time.time_ns()
    print("Solving with Optimal solution:")
    while(applySingleResolution(cnfList)):
        pass

    cnfList = remove_duplicate_lists(cnfList)
    if checkNoSolution(cnfList):
        print ("No Solution!")
        RunTime = time.time_ns() - RunTime
        return RunTime

    newList = []
    for i in range (len(cnfList) - 1, -1, -1):
        if len(cnfList[i]) > 1:
            newList.append(cnfList[i])
            cnfList.remove(cnfList[i])
    

    newList = first_truth_values(newList)
    
    
    
    resultList = cnfList[:]
    for j in newList:
        resultList.append(j)
    
    RunTime = time.time_ns() - RunTime

    resultMatrix = [row[:] for row in matrix]
    for i in range (len(resultMatrix)):
        for j in range (len(resultMatrix)):
            if resultMatrix[i][j] == '_':
                val = i * len(resultMatrix) + j + 1
                if checkForTrap(val, resultList):
                    resultMatrix[i][j] = "T"
                else:
                    resultMatrix[i][j] = "G"
    for i in range (len(resultMatrix)):
        for j in range (len(resultMatrix)):
            print(resultMatrix[i][j], end = ' ')
        print()
    print()
    return RunTime

# Backtracking
def is_satisfiable(cnf_formula, assignment):
    num_vars = cnf_formula.nv
    for clause in cnf_formula.clauses:
        clause_satisfied = False
        for literal in clause:
            variable, negated = abs(literal), literal < 0
            if variable <= num_vars:
                if (negated and not assignment[variable-1]) or (not negated and assignment[variable-1]):
                    clause_satisfied = True
                    break
        if not clause_satisfied:
            return False
    return True

def solve_with_backtracking(cnf_formula):
    num_vars = cnf_formula.nv

    def backtrack(assignment, var_index):
        if var_index == num_vars:
            return assignment if is_satisfiable(cnf_formula, assignment) else None

        assignment[var_index] = True
        result = backtrack(assignment, var_index + 1)
        if result:
            return result

        assignment[var_index] = False
        result = backtrack(assignment, var_index + 1)
        if result:
            return result

    assignment = [None] * num_vars
    return backtrack(assignment, 0)

def solveBacktracking(matrix, cnf):
    RunTime = time.time_ns()
    solution = solve_with_backtracking(cnf)
    RunTime = time.time_ns() - RunTime
    if solution:
        print("Solving with BackTracking:")
        for var, value in enumerate(solution):
            if value:
                print('T', end=' ')
            else:
                if matrix[var // len(matrix[0])][var % len(matrix[0])] == '_':
                    print('G', end=' ')
                else:
                    print(matrix[var // len(matrix[0])][var % len(matrix[0])], end=' ')
            if (var + 1) % len(matrix[0]) == 0:
                print()
        print()
    else:
        print("No satisfying assignment exists.")
    return RunTime

#Brute Force
def solveBruteForce(cnf, initialMatrix: list[list]):
    start_time = time.time_ns()
    num_vars = max([abs(lit) for clause in cnf for lit in clause])
    result = []
    for assignment in product([False, True], repeat=num_vars):
        if all(any(lit > 0 and assignment[abs(lit) - 1] or lit < 0 and not assignment[abs(lit) - 1] for lit in clause) for clause in cnf):
            end_time = time.time_ns()
            countTime = end_time - start_time
            result = assignment
            break
    print("Brute Force: ")
    length = len(initialMatrix)
    for i in range (length):
        for j in range (length):
            if initialMatrix[i][j] != '_':
                print(initialMatrix[i][j], end = ' ')
            else:
                if result[(i * length) + j] == True:
                    print("T ", end = "")
                else:
                    print("G ", end = "")
        print()
    return countTime




def main():
    # Welcome message
    print()
    print("Welcome to the Gem Hunter solver")
    print()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    current_dir = os.path.join(current_dir, "testcases")

    loop = True

    while loop:
        # Choose a map file to solve
        opt = 0
        print("Choose a map file to solve:")
        for filename in os.listdir(current_dir):
            if filename.endswith(".txt"):
                if filename.startswith("output_"):
                    continue
                print(f"{opt}. {filename}")
                opt += 1
        map_choice = int(input("Enter the number of the map file to solve: "))

        while map_choice < 0 or map_choice >= opt:
            map_choice = int(input("Invalid choice. Enter the number of the map file to solve: "))
        print()
        map_filename = os.path.join(current_dir, os.listdir(current_dir)[map_choice])

        # Read the map file
        matrix = read_file(map_filename)

        # Convert the map to CNF
        cnf = map_convert_CNF(matrix)

        # Choose the solving method
        print("Choose the solving method:")
        print("1. SAT Solver")
        print("2. Backtracking")
        print("3. Optimal")
        print("4. Brute Force")
        print("5. All")

        solving_method = int(input("Enter the number of the solving method: "))
        while solving_method < 1 or solving_method > 5:
            solving_method = int(input("Invalid choice. Enter the number of the solving method: "))
        print()

        print("The map is:")
        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                print(matrix[i][j], end = ' ')
            print()
        print()

        # Solve the map
        if solving_method == 1:
            SATTime = solveWithSAT(matrix, cnf)
            print("Time taken by SAT solver: ", SATTime)
        elif solving_method == 2:
            BackTrackTime = solveBacktracking(matrix, cnf)
            print("Time taken by Backtracking: ", BackTrackTime)
        elif solving_method == 3:
            visitedValue.clear()
            OptimalTime = solveOptimal(matrix, cnf.clauses)
            print("Time taken by Optimal solution: ", OptimalTime)
        elif solving_method == 4:
            BruteForceTime = solveBruteForce(cnf, matrix)
            print("Time taken by Brute Force solution: ", BruteForceTime)
        elif solving_method == 5:


            SATTime = solveWithSAT(matrix, cnf)
            visitedValue.clear()
            OptimalTime = solveOptimal(matrix, cnf.clauses)
            BackTrackTime = solveBacktracking(matrix, cnf)
            BruteForceTime = solveBruteForce(cnf, matrix)

            print("Time taken by SAT solver: ", SATTime)
            print("Time taken by Optimal solution: ", OptimalTime)
            print("Time taken by Backtracking: ", BackTrackTime)
            print("Time taken by Brute Force solution: ", BruteForceTime)
    
        # Ask if the user wants to solve another map
        print()
        print("Do you want to solve another map?")
        print("1. Yes")
        print("2. No")
        choice = int(input("Enter your choice: "))
        while choice < 1 or choice > 2:
            choice = int(input("Invalid choice. Enter your choice: "))
        print()

        if choice == 2:
            loop = False

if __name__ == "__main__":
    main()