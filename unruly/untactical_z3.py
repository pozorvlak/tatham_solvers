#!/usr/bin/env python


"""
Find Unruly boards which can't be solved using the four tactics using Z3.
"""

import sys

from z3 import Function, IntSort, Solver, sat, And, Implies, If, Or, Optimize

import unruly


def find_puzzle(n):
    size = 2 * n
    s = Optimize()
    puzzle = make_puzzle(n, size, s)
    solution = solution_for(puzzle, size, s)
    blank_count = sum(b2i(puzzle(i, j) == 2) for i in range(size) for j in range(size))
    s.add(blank_count > 10)
    # s.maximize(blank_count)
    iterations = 0
    # with open('board1') as f:
    #     board1 = unruly.read_board(f.readlines())
    #     print(board1)
    #     for i, row in enumerate(board1):
    #         for j, c in enumerate(row):
    #             s.add(puzzle(i, j) == c)
    # save_assertions(s)
    while True:
        iterations += 1
        if s.check() == sat:
            board = get_board(s, puzzle, size)
            # return board, board
            solution1 = get_board(s, solution, size)
            # return board, solution1
            s.push()
            s.add(yes_this(puzzle, board, size))
            s.add(not_this(solution, solution1, size))
            if s.check() == sat:
                # print("Alternative solution found!")
                solution2 = get_board(s, solution, size)
                # Solution is not unique
                if iterations % 100 == 0:
                    sys.stdout.write(".")
                    sys.stdout.flush()
                s.pop()
                s.add(not_this(puzzle, board, size))
            else:
                return board, solution1
        else:
            print()
            print("Can't find any suitable puzzles :-(")
            sys.exit(1)


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


def make_puzzle(n, size, s):
    puzzle = Function('puzzle', IntSort(), IntSort(), IntSort())
    transposed = Function('transposed', IntSort(), IntSort(), IntSort())
    # Squares must be black, white or empty
    for i in range(size):
        for j in range(size):
            # 0 = black, 1 = white, 2 = unknown
            s.add(puzzle(i, j) >= 0)
            s.add(puzzle(i, j) <= 2)
            # Transpose puzzle to reduce code duplication
            s.add(transposed(j, i) == puzzle(i, j))
    for board in (puzzle, transposed):
        # At most n squares of each colour in a given row
        limit_cells_per_row(board, n, s)
        # No more than two consecutive squares of the same colour
        limit_consecutive(board, size, s)
        # "gaps" and "endcaps" tactics can't be applied
        no_gaps_or_endcaps(board, size, s)
        pass
    return puzzle


def limit_cells_per_row(puzzle, n, s):
    size = 2 * n
    for i in range(size):
        black_count = sum(b2i(puzzle(i, j) == 0) for j in range(size))
        white_count = sum(b2i(puzzle(i, j) == 1) for j in range(size))
        s.add(black_count <= n)
        s.add(white_count <= n)
        # "n" tactic can't be applied
        s.add((black_count == n) == (white_count == n))


def limit_consecutive(puzzle, size, s):
    for colour in range(2):
        for i in range(size):
            for j in range(size - 2):
                row_sum = (
                    b2i(puzzle(i, j) == colour)
                    + b2i(puzzle(i, j + 1) == colour)
                    + b2i(puzzle(i, j + 2) == colour)
                )
                s.add(row_sum < 3)


def b2i(bool_expr):
    """Convert a Z3 boolean expression to an integer, so I can sum it"""
    return If(bool_expr, 1, 0)


def no_gaps_or_endcaps(puzzle, size, s):
    for i in range(size):
        for j in range(size - 2):
            a, b, c = puzzle(i, j), puzzle(i, j+1), puzzle(i, j+2)
            s.add(Implies(
                And(a < 2, a == c),
                b == (1 - a)
            ))
            s.add(Implies(
                And(a < 2, a == b),
                c == (1 - a)
            ))
            s.add(Implies(
                And(b < 2, b == c),
                a == (1 - b)
            ))


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
    n = int(sys.argv[1])
    board, solution = find_puzzle(n)
    print(unruly.board_to_str(board))
    print()
    print(unruly.board_to_str(solution))