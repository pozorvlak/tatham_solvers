#!/usr/bin/env python

"""
Solve Net puzzles using Tabu search
"""

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
    def __init__(self, lines, wrap=False, tabu_length=20):
        self.size = len(lines)
        self.wrap = wrap
        self.pieces = [line.rstrip('\n') for line in lines]
        self.orientations = np.zeros((self.size, self.size), dtype=int)
        # If the board doesn't wrap, add an extra line at the edge which is always False
        self.exit_size = self.size + (not wrap)
        self.left = np.zeros((self.exit_size, self.exit_size))
        self.up = np.zeros((self.exit_size, self.exit_size))
        self.right = np.zeros((self.exit_size, self.exit_size))
        self.down = np.zeros((self.exit_size, self.exit_size))
        for i in range(self.size):
            for j in range(self.size):
                self.set_exits(i, j)
        self.tabu_list = []
        self.tabu_length = tabu_length

    def set_exits(self, i, j):
        if self.wrap:
            i = i % self.size
            j = j % self.size
        elif not (0 <= i < self.size and 0 <= j < self.size):
            return
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
            int(right != self.left[i, (j + 1) % self.exit_size]) +
            int(down != self.up[(i + 1) % self.exit_size, j])
        )

    def penalties(self):
        ret = np.zeros((self.size, self.size))
        # TODO vectorise this
        for i in range(self.size):
            for j in range(self.size):
                ret[i, j] = self.penalty(i, j, self.orientations[i, j])
        return ret

    def __str__(self, orientations=None):
        if orientations is None:
            orientations = self.orientations
        return "\n".join([
            ''.join([pics[self.pieces[i][j]][orientations[i, j]] for j in range(self.size)])
            for i in range(self.size)
        ])

    def update(self, i, j, new_orientation):
        old_orientation = self.orientations[i, j]
        self.orientations[i, j] = new_orientation
        new_orientations = self.orientations.tolist()
        if new_orientations in self.tabu_list:
            self.orientations[i, j] = old_orientation
            return
        self.tabu_list.append(new_orientations)
        if len(self.tabu_list) > self.tabu_length:
            self.tabu_list.pop(0)
        self.set_exits(i, j)
        self.set_exits(i - 1, j)
        self.set_exits(i + 1, j)
        self.set_exits(i, j - 1)
        self.set_exits(i, j + 1)


    def solve(self, steps=None):
        count = 0
        min_penalty, best_iteration = np.inf, 0
        while True:
            if count >= steps:
                break
            count += 1
            penalties = np.reshape(self.penalties(), self.size ** 2)
            error = np.sum(penalties)
            if error < min_penalty:
                min_penalty = error
                best_iteration = count - 1
                best_orientations = np.copy(self.orientations)
            if error == 0:
                # Finished!
                break
            index = np.random.choice(np.arange(self.size ** 2), p=(penalties / error))
            i, j = divmod(index, self.size)
            weights = np.array([1 / (1 + self.penalty(i, j, o)) for o in range(4)])
            weights = weights / np.sum(weights)
            new_orientation = np.random.choice(np.arange(4), p=weights)
            self.update(i, j, new_orientation)
        return count, min_penalty, best_iteration, best_orientations


if __name__ == '__main__':
    board = Board([line for line in fileinput.input()], wrap=True)
    print(board)
    print(board.penalties())
    print(np.sum(board.penalties()))
    print()
    count, best_score, best_iteration, best_board = board.solve(steps=50000)
    print(f"After {count} steps:")
    print(board)
    print(board.penalties())
    print(np.sum(board.penalties()))
    print()
    print(f"Best configuration, after {best_iteration} steps:")
    print(best_score)
    print(board.__str__(orientations=best_board))
