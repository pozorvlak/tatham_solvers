#!/usr/bin/env python

import fileinput


UNKNOWN = 0
BLACK = 1
WHITE = 2


def char_to_enum(c):
    return {
            '_': UNKNOWN,
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


def char(e):
    return '_BW'[e]


def board_to_str(board):
    return "\n".join(["".join([char(e) for e in row]) for row in board])


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


def counts(line):
    whites, blacks = 0, 0
    for space in line:
        whites += (space == WHITE)
        blacks += (space == BLACK)
    return whites, blacks


def space_for_three(line, c):
    """Is there space for three adjacent squares of colour c?

    Returns the first index of every such triple."""
    o = other(c)
    starts = []
    for i in range(len(line) - 2):
        if o not in line[i:i+3]:
            starts.append(i)
    return starts


def intersect_threes(starts, unknowns):
    """Given start indices for triples, find spaces common to them all"""
    indices = set(unknowns)
    for j in starts:
        indices &= set([j, j + 1, j + 2])
    return indices


def possible_remaining(line, c, unknowns):
    possible_threes = space_for_three(line, other(c))
    others = intersect_threes(possible_threes, unknowns)
    return others


def complete_line(line, i):
    n = len(line) // 2
    whites, blacks = counts(line)
    unknowns = [j for j, s in enumerate(line) if s == UNKNOWN]
    if whites == n:
        return [(BLACK, j) for j in unknowns]
    if blacks == n:
        return [(WHITE, j) for j in unknowns]
    if whites == n - 1:
        possible_whites = possible_remaining(line, WHITE, unknowns)
        updates = [(BLACK, j) for j in set(unknowns) - possible_whites]
        return updates
    if blacks == n - 1:
        possible_blacks = possible_remaining(line, BLACK, unknowns)
        updates = [(WHITE, j) for j in set(unknowns) - possible_blacks]
        return updates
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
                raise ValueError(f"""
Conflict at {(ii, jj)}!

Update from {(i, j)} implies should be {char(c)}, but is already {char(board[ii][jj])}.

Full board:
{board_to_str(board)}""")
    return board


def test_complete_line():
    line = [char_to_enum(c) for c in 'BWWBWB__BWWB_W']
    assert complete_line(line, 0) == [(BLACK, 12)]


if __name__ == '__main__':
    board = read_board(fileinput.input())
    board = propagate(board)
    print(board_to_str(board))
