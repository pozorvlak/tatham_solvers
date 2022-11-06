#!/usr/bin/env python

import fileinput
import unruly

board = [row.strip() for row in fileinput.input()]
print(f"n = {len(board[0]) // 2};")
print(f"puzzle = ")
print(unruly.board_to_minizinc(board))