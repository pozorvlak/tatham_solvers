#!/usr/bin/env python

"""
Tries to find Unruly boards in which
 - Every row and column has a unique solution
 - None of the standard four tactics are applicable

This is a very strict condition, which doesn't seem to be achievable in
practice. It's much stronger than we actually need, but also greatly reduces
the size of the search space.
"""

from collections import defaultdict, Counter
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


def get_fixpoints(n):
    solver = Solver.lookup("chuffed")
    model = Model("fixpoints.mzn")
    instance = Instance(solver, model)
    instance['n'] = n
    fixpoints = instance.solve(all_solutions=True)
    indices = {'BLACK': 0, 'WHITE': 1, 'UNKNOWN': 2}
    masks = [[indices[c] for c in f.row] for f in fixpoints]
    fixed = [unruly.propagate([mask]) for mask in masks]
    deduped = {unruly.board_to_str(f): f[0] for f in fixed if unruly.UNKNOWN in f[0]}
    return list(deduped.values())


def filter_by_bit(all_solutions):
    all_indices = set(range(len(all_solutions)))
    by_bit = [(set(), set(), all_indices)  for i in range(2 * n)]
    for i, solution in enumerate(all_solutions):
        for j in range(2 * n):
            by_bit[j][solution.row[j]].add(i)
    return by_bit


def solve_masks(masks, all_solutions):
    all_indices = set(range(len(all_solutions)))
    by_bit = filter_by_bit(all_solutions)
    solutions = {}
    for mask in masks:
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


def get_boards(n, fixpoints):
    solver = Solver.lookup("chuffed")
    model = Model("unsolvable.mzn")
    instance = Instance(solver, model)
    instance['n'] = n
    instance['num_fixpoints'] = len(fixpoints)
    ix = {'B': 'BLACK', 'W': 'WHITE', '_': 'UNKNOWN'}
    instance['fixpoints'] = [[ix[n] for n in mask] for mask in fixpoints]
    board = instance.solve()
    return board


def output_as_minizinc(n, fixpoints):
    print(f"n = {n};")
    print(f"num_fixpoints = {len(fixpoints)};")
    print("fixpoints = ")
    print(unruly.board_to_minizinc(fixpoints))


def main(n):
    all_solutions = get_all_solutions(n)
    print(f"% Total number of solutions: {len(all_solutions)}")
    fixpoints = get_fixpoints(n)
    print(f"% Total number of fixpoints: {len(fixpoints)}")
    solutions = solve_masks(fixpoints, all_solutions)
    print("% ", get_counts(solutions))
    solvable = get_solvable(solutions)
    print(f"% Total number of uniquely-solvable fixpoints: {len(solvable)}")
    output_as_minizinc(n, solvable)
    # board = get_boards(n, solvable)
    # print(board)


if __name__ == '__main__':
    n = int(sys.argv[1])
    main(n)
