#!/usr/bin/env python

import fileinput


UNKNOWN = 0
BLACK = 1
WHITE = 2


def char_to_enum(c):
    return {
            ' ': UNKNOWN,
            'B': BLACK,
            'W': WHITE
            }[c]


def other(c):
    if c == BLACK:
        return WHITE
    elif c == WHITE:
        return BLACK
    else:
        raise ValueError(f"Tried to invert colour {c}")


def read_board(lines):
    return [[char_to_enum(c) for c in line.rstrip("\n")] for line in lines]


def enum_to_char(e):
    return ' BW'[e]


def board_to_str(board):
    return "\n".join(["".join([' BW'[e] for e in row]) for row in board])


def space_contains(line, i, c):
    if i < 0 or i >= len(line):
        return False
    return line[i] == c


def two_in_a_row(line, i):
    """If line[i] is part of any pairs, return a list of end-caps"""
    # print(f"two_in_a_row on {i, j}")
    c = line[i]
    o = other(c)
    if c == UNKNOWN:
        return []
    updates = []
    if space_contains(line, i + 1, c):
        updates.extend([(o, i + 2), (o, i - 1)])
    if space_contains(line, i - 1, c):
        updates.extend([(o, i - 2), (o, i + 1)])
    return updates


def fill_in_holes(line, i):
    """If line[i] is part of an 'X X' pattern, fill in the hole"""
    c = line[i]
    o = other(c)
    if c == UNKNOWN:
        return []
    updates = []
    if space_contains(line, i + 2, c):
        updates.append((o, i + 1))
    if space_contains(line, i - 2, c):
        updates.append((o, i - 1))
    return updates


def counts(unit):
    whites, blacks = 0, 0
    for space in unit:
        whites += (space == WHITE)
        blacks += (space == BLACK)
    return whites, blacks


def complete_line(line, i):
    n = len(line) // 2
    whites, blacks = counts(line)
    if whites == n:
        return [(BLACK, j) for j in range(2 * n) if line[j] == UNKNOWN]
    if blacks == n:
        return [(WHITE, j) for j in range(2 * n) if line[j] == UNKNOWN]
    return []


def all_updates(board, i, j):
    propagators = [
            two_in_a_row,
            fill_in_holes,
            complete_line,
        ]
    updates = []
    row = board[i]
    col = [r[j] for r in board]
    for p in propagators:
        updates.extend([(c, i, jj) for (c, jj) in p(row, j)])
        updates.extend([(c, ii, j) for (c, ii) in p(col, i)])
    return updates


def propagate(board):
    frontier = [(i, j)
            for i in range(len(board)) for j in range(len(board[i]))
            if board[i][j] != UNKNOWN]
    while len(frontier) > 0:
        (i, j) = frontier.pop(0)
        for (c, ii, jj) in all_updates(board, i, j):
            if ii < 0 or ii >= len(board):
                continue
            elif jj < 0 or jj >= len(board[ii]):
                continue
            elif board[ii][jj] == c:
                continue
            elif board[ii][jj] == UNKNOWN:
                board[ii][jj] = c
                frontier.append((ii, jj))
            else:
                raise Error(f"""
Conflict at {(ii, jj)}!

Update from {(i, j)} implies should be {c}, but is already {board[ii][jj]}.

Full board:
{board_to_str(board)}""")
    return board


if __name__ == '__main__':
    board = read_board(fileinput.input())
    board = propagate(board)
    print(board_to_str(board))
