#!/usr/bin/env python

import fileinput
from random import random

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
        orientation = self.orientations[i, j]
        (self.left[i, j], self.up[i, j], self.right[i, j], self.down[i, j]) = self.exits(i, j, orientation)

    def exits(self, i, j, orientation):
        shape = shapes[self.pieces[i][j]]
        return rotate(shape, orientation)


    def penalty(self, i, j, orientation):
        left, up, right, down = self.exits(i, j, orientation)
        return (
            int(left != self.right[i, j - 1]) +
            int(up != self.down[i - 1, j]) +
            int(right != self.left[i, j + 1]) +
            int(down != self.up[i + 1, j])
        )

    def penalties(self):
        ret = np.zeros((self.size, self.size))
        # TODO vectorise this
        for i in range(self.size):
            for j in range(self.size):
                ret[i, j] = self.penalty(i, j, self.orientations[i, j])
        return ret

    def __str__(self):
        return "\n".join([
            ''.join([pics[self.pieces[i][j]][self.orientations[i, j]] for j in range(self.size)])
            for i in range(self.size)
        ])

    def solve(self, steps=None):
        count = 0
        while True:
            if count >= steps:
                break
            count += 1
            penalties = np.reshape(self.penalties(), self.size ** 2)
            error = np.sum(penalties)
            if error == 0:
                # Finished!
                break
            index = np.random.choice(np.arange(self.size ** 2), p=(penalties / error))
            i, j = divmod(index, self.size)
            current = self.orientations[i, j]
            self.orientations[i, j] = (current + 1) % 4
            self.set_exits(i, j)
            # if not an improvement, reject with probability new / (new + old)
            # TODO we don't need to recalculate all penalties for this
            old_penalty = penalties[index]
            new_penalty = self.penalties()[i, j]
            if new_penalty > old_penalty and random() < new_penalty / (new_penalty + old_penalty):
                self.orientations[i, j] = current
                self.set_exits(i, j)
        return count


if __name__ == '__main__':
    board = Board([line for line in fileinput.input()])
    print(board)
    print(board.penalties())
    print(np.sum(board.penalties()))
    print()
    count = board.solve(steps=500)
    print(f"After {count} steps:")
    print(board)
    print(board.penalties())
    print(np.sum(board.penalties()))
