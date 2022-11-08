#!/usr/bin/env python


"""
Find Unruly boards which can't be solved using the four tactics using Z3.
"""

import fileinput
import sys

from z3 import Function, IntSort, Solver, sat, And, Implies, If, Or

import unruly
from unruly_z3 import solve_board


def minimize(board, expected_solution):
    size = len(board)
    s = Solver()
    puzzle = make_puzzle(size, s)
    for i, row in enumerate(board):
        for j, c in enumerate(row):
            s.add(Or(puzzle(i, j) == c, puzzle(i, j) == 2))
    solution = solution_for(puzzle, size, s)
    lo_blanks = sum(c == 2 for row in board for c in row)
    hi_blanks = size * size
    blank_count = sum(b2i(puzzle(i, j) == 2) for i in range(size) for j in range(size))
    while (hi_blanks - lo_blanks) > 1:
        goal = (lo_blanks + hi_blanks) // 2
        print(f"Can achieve {lo_blanks}, can't achieve {hi_blanks}, goal is {goal}")
        s.add(blank_count > goal)
        iterations = 0
        while True:
            iterations += 1
            if s.check() == sat:
                board = get_board(s, puzzle, size)
                blanks = s.model().evaluate(blank_count).as_long()
                s.push()
                s.add(yes_this(puzzle, board, size))
                s.add(not_this(solution, expected_solution, size))
                if s.check() == sat:
                    # Solution is not unique
                    if iterations % 10 == 0:
                        sys.stdout.write(".")
                        sys.stdout.flush()
                    s.pop()
                    s.add(not_this(puzzle, board, size))
                else:
                    s.pop()
                    print(f"\nFound a subset with {blanks} blanks")
                    print(unruly.board_to_str(board))
                    lo_blanks = blanks
                    break
            else:
                print(f"Can't find any solutions with {goal} blanks")
                hi_blanks = goal
                break
    return board


def save_assertions(s):
    with open("assertions", "w") as f:
        for a in s.assertions():
            f.write(str(a) + "\n")
                

def yes_this(variable, board, size):
    return And(*(
        variable(i, j) == board[i][j]
        for i in range(size) for j in range(size)
    ))


def not_this(variable, board, size):
    return Or(*(
        variable(i, j) != board[i][j]
        for i in range(size) for j in range(size)
    ))


def make_puzzle(size, s):
    puzzle = Function('puzzle', IntSort(), IntSort(), IntSort())
    # Squares must be black, white or empty
    for i in range(size):
        for j in range(size):
            # 0 = black, 1 = white, 2 = unknown
            s.add(puzzle(i, j) >= 0)
            s.add(puzzle(i, j) <= 2)
    return puzzle


def b2i(bool_expr):
    """Convert a Z3 boolean expression to an integer, so I can sum it"""
    return If(bool_expr, 1, 0)


def solution_for(puzzle, size, s):
    solution = Function('solution', IntSort(), IntSort(), IntSort())
    n = size // 2
    for i in range(size):
        for j in range(size):
            c = puzzle(i, j)
            s.add(0 <= solution(i, j))
            s.add(solution(i, j) <= 1)
            s.add(Implies(c < 2, solution(i, j) == c))
    for i in range(size):
        s.add(sum(solution(i, j) for j in range(size)) == n)
        s.add(sum(solution(j, i) for j in range(size)) == n)
    for i in range(size):
        for j in range(size - 2):
            row_sum = solution(i, j) + solution(i, j + 1) + solution(i, j + 2)
            col_sum = solution(j, i) + solution(j + 1, i) + solution(j + 2, i)
            s.add(0 < row_sum)
            s.add(row_sum < 3)
            s.add(0 < col_sum)
            s.add(col_sum < 3)
    return solution


def get_board(s, solution, size):
    m = s.model()
    board = [
        [ m.evaluate(solution(i, j)).as_long() for j in range(size) ]
        for i in range(size)
    ]
    return board


if __name__ == '__main__':
    board = unruly.read_board(fileinput.input())
    solution = solve_board(board)
    board = minimize(board, solution)
    print(unruly.board_to_str(board))