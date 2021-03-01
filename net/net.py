#!/usr/bin/env python

import numpy as np


shapes = {
    'T': (True, False, True, True),
    'I': (True, False, True, False),
    'L': (False, True, True, False),
    'Q': (False, False, False, True),
}


def rotate(xs, i):
    return xs[i:] + xs[:i]


class Board:
    def __init__(self, lines):
        self.size = len(lines)
        self.pieces = [line.rstrip('\n') for line in lines]
        self.orientations = np.zeros((self.size, self.size))
        self.exits = np.zeros((self.size, self.size, 4))
        for i in range(self.size):
            for j in range(self.size):
                self.set_exits(i, j)

    def set_exits(self, i, j):
        piece = self.pieces[i][j]
        orientation = self.orientations[i][j]
        self.exits[i, j, :] = rotate(piece, orientation)

