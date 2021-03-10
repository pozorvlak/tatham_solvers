#!/usr/bin/env python

from collections import Counter
from itertools import product
import sys

from minizinc import Instance, Model, Solver

import unruly


# 0 = black, 1 = white, 2 = unknown
def mask_to_str(mask):
    return "".join(["BW_"[i] for i in mask])


def get_all_solutions(n):
    solver = Solver.lookup("chuffed")
    model = Model("unruly_row.mzn")
    instance = Instance(solver, model)
    instance['n'] = n
    all_solutions = instance.solve(all_solutions=True)
    return all_solutions


def filter_by_bit(all_solutions):
    all_indices = set(range(len(all_solutions)))
    by_bit = [(set(), set(), all_indices)  for i in range(2 * n)]
    for i, solution in enumerate(all_solutions):
        for j in range(2 * n):
            by_bit[j][solution.row[j]].add(i)
    return by_bit


def solve_masks(n, by_bit):
    all_indices = set(by_bit[0][2])
    solutions = {}
    for mask in product(*([0, 1, 2] for i in range(2 * n))):
        matches = set(all_indices)
        for b in range(2 * n):
            matches &= by_bit[b][mask[b]]
        solutions[mask_to_str(mask)] = matches
    return solutions


def get_counts(solutions):
    counts = Counter()
    for (mask, matches) in solutions.items():
        counts[len(matches)] += 1
    return counts


def get_solvable(solutions):
    solvable = []
    for (mask, matches) in solutions.items():
        if len(matches) == 1:
            solvable.append(mask)
    return solvable


def solvable_with_rules(mask):
    board = unruly.read_board([mask])
    solved = unruly.board_to_str(unruly.propagate(board))
    return "_" not in solved


def main(n):
    all_solutions = get_all_solutions(n)
    by_bit = filter_by_bit(all_solutions)
    solutions = solve_masks(n, by_bit)
    print(get_counts(solutions))
    solvable = get_solvable(solutions)
    for mask in solvable:
        if not solvable_with_rules(mask):
            solution = all_solutions[list(solutions[mask])[0]].row
            print(f"{mask} -> {mask_to_str(solution)}")


if __name__ == '__main__':
    n = int(sys.argv[1])
    main(n)
