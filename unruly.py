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


def space_contains(board, i, j, c):
    if i < 0 or i >= len(board):
        return False
    if j < 0 or j >= len(board[i]):
        return False
    return board[i][j] == c


def two_in_a_row(board, i, j):
    """If (i, j) is part of any pairs, return a list of end-caps"""
    # print(f"two_in_a_row on {i, j}")
    c = board[i][j]
    o = other(c)
    if c == UNKNOWN:
        return []
    updates = []
    if space_contains(board, i, j + 1, c):
        updates.extend([(o, i, j + 2), (o, i, j - 1)])
    if space_contains(board, i, j - 1, c):
        updates.extend([(o, i, j - 2), (o, i, j + 1)])
    if space_contains(board, i + 1, j, c):
        updates.extend([(o, i + 2, j), (o, i - 1, j)])
    if space_contains(board, i - 1, j, c):
        updates.extend([(o, i - 2, j), (o, i + 1, j)])
    return updates


def fill_in_holes(board, i, j):
    c = board[i][j]
    o = other(c)
    if c == UNKNOWN:
        return []
    updates = []
    if space_contains(board, i, j + 2, c):
        updates.append((o, i, j + 1))
    if space_contains(board, i, j - 2, c):
        updates.append((o, i, j - 1))
    if space_contains(board, i + 2, j, c):
        updates.append((o, i + 1, j))
    if space_contains(board, i - 2, j, c):
        updates.append((o, i - 1, j))
    return updates


def all_updates(board, i, j):
    return two_in_a_row(board, i, j) + fill_in_holes(board, i, j)


def propagate(board):
    frontier = [(i, j)
            for i in range(len(board)) for j in range(len(board[i]))
            if board[i][j] != UNKNOWN]
    while len(frontier) > 0:
        (i, j) = frontier.pop(0)
        for (c, ii, jj) in all_updates(board, i, j):
            if ii < 0 or ii > len(board):
                continue
            elif jj < 0 or jj > len(board[ii]):
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
