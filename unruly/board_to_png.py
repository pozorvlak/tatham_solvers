#!/usr/bin/env python

import sys

import matplotlib.pyplot as plt
import matplotlib.patches as patches

import unruly


def plot_board(board, outfile):
    rows = len(board)
    cols = len(board[0])
    print(f"{rows} rows, {cols} columns")
    fig = plt.figure(figsize=(5, 5 * (rows / cols)))
    plt.axis("off")
    ax = fig.gca()

    for i in range(cols + 1):
        ax.plot([i] * (rows + 1), range(rows + 1), color="grey", linewidth=1)
    for i in range(rows + 1):
        ax.plot(range(cols + 1), [i] * (cols + 1), color="grey", linewidth=1)

    colours = ["black", "white", "lightgrey"]
    for i in range(rows):
        for j in range(cols):
            rect = patches.Rectangle((j, i), 1, 1, linewidth=0, facecolor=colours[board[rows - i - 1][j]])
            ax.add_patch(rect)
    plt.savefig(outfile)


if __name__ == '__main__':
    for infile in sys.argv[1:]:
        with open(infile) as f:
            board = unruly.read_board(f.readlines())
        plot_board(board, infile + ".png")