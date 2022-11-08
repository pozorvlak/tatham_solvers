#!/usr/bin/env python


"""
Find Unruly boards which can't be solved using the four tactics using Z3.
"""

import fileinput

from z3 import Function, IntSort, Solver, sat, Or

import unruly
from unruly_z3 import solve_board


def minimize(board, expected_solution):
    size = len(board)
    clues = [
        (i, j)
        for i in range(size) for j in range(size)
        if board[i][j] != 2
    ]
    for (i, j) in clues:
        value = board[i][j]
        board[i][j] = 2
        if solve_board(board, exclusions=[expected_solution]) is not None:
            board[i][j] = value
    return board

def solve_board(board, exclusions=None):
    if exclusions is None:
        exclusions = []
    size = len(board[0])
    n = size // 2
    solution = Function('solution', IntSort(), IntSort(), IntSort())
    s = Solver()
    for i, row in enumerate(board):
        for j, c in enumerate(row):
            if c < 2:
                s.add(solution(i, j) == c)
            else:
                s.add(0 <= solution(i, j))
                s.add(solution(i, j) <= 1)
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
    for exclusion in exclusions:
        s.add(Or(*(
            solution(i, j) != exclusion[i][j]
            for i in range(size) for j in range(size)
        )))
    if s.check() == sat:
        m = s.model()
        board = [
            [ m.evaluate(solution(i, j)).as_long() for j in range(size) ]
            for i in range(size)
        ]
        return board
    else:
        return None


if __name__ == '__main__':
    board = unruly.read_board(fileinput.input())
    solution = solve_board(board)
    board = minimize(board, solution)
    blanks = sum(c == 2 for row in board for c in row)
    print(f"Found a subset with {blanks} empty squares")
    print(unruly.board_to_str(board))