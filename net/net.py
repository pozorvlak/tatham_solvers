#!/usr/bin/env python

import fileinput

import numpy as np


shapes = {
    'T': (True, False, True, True),
    'I': (True, False, True, False),
    'L': (False, True, True, False),
    'Q': (False, False, False, True),
}


def rotate(xs, i):
    return xs[i:] + xs[:i]


pics = {
    'T': "╦╣╩╠",
    'I': "═║═║",
    'L': "╚╔╗╝",
    'Q': "╥╡╨╞"
}


class Board:
    def __init__(self, lines, wrap=False):
        self.size = len(lines)
        self.pieces = [line.rstrip('\n') for line in lines]
        self.orientations = np.zeros((self.size, self.size), dtype=int)
        # If the board doesn't wrap, add an extra line at the edge which is always False
        exit_size = self.size + (not wrap)
        self.left = np.zeros((exit_size, exit_size))
        self.up = np.zeros((exit_size, exit_size))
        self.right = np.zeros((exit_size, exit_size))
        self.down = np.zeros((exit_size, exit_size))
        for i in range(self.size):
            for j in range(self.size):
                self.set_exits(i, j)

    def set_exits(self, i, j):
        shape = shapes[self.pieces[i][j]]
        orientation = self.orientations[i][j]
        (self.left[i, j], self.up[i, j], self.right[i, j], self.down[i, j]) = rotate(shape, orientation)

    def penalties(self):
        ret = np.zeros((self.size, self.size))
        # TODO vectorise this
        for i in range(self.size):
            for j in range(self.size):
                ret[i, j] = (
                        int(self.left[i, j] != self.right[i, j - 1]) +
                        int(self.up[i, j] != self.down[i - 1, j]) +
                        int(self.right[i, j] != self.left[i, j + 1]) +
                        int(self.down[i, j] != self.up[i + 1, j])
                )
        return ret

    def __str__(self):
        return "\n".join([
            ''.join([pics[self.pieces[i][j]][self.orientations[i, j]] for j in range(self.size)])
            for i in range(self.size)
        ])


if __name__ == '__main__':
    board = Board([line for line in fileinput.input()])
    print(board)
