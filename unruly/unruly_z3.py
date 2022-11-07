#!/usr/bin/env python


"""
Solve partial Unruly boards using the Z3 SMT solver from Microsoft Research
"""
import fileinput

from z3 import Function, IntSort, Solver, sat

import unruly


def solve_board(board):
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
    if s.check() == sat:
        m = s.model()
        board = [
            [ m.evaluate(solution(i, j)).as_long() for j in range(size) ]
            for i in range(size)
        ]
    return board


def test_solutions_():
    for infile in ['board1', 'board2', 'board3', 'board4', 'board5']:
        with open(infile) as f:
            board = unruly.read_board(f.readlines())
            solution = solve_board(board)
        with open(infile + '.soln') as f:
            expected = unruly.read_board(f.readlines())
        assert solution == expected, infile


if __name__ == '__main__':
    board = unruly.read_board(fileinput.input())
    board = solve_board(board)
    print(unruly.board_to_str(board))