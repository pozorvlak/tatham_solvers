Hi! This is my code for finding "untactical" Unruly puzzles, i.e. those with unique solutions which can't be found using only the tactics used by the generator in [Simon Tatham's implementation](https://www.chiark.greenend.org.uk/~sgtatham/puzzles/js/unruly.html). It's pretty messy and has a lot of duplicated code, I'm afraid.

The first step was to write my own implementation of a tactical solver: you can find this in `unruly.py`, together with some utilities for reading puzzles from files and so on which are imported elsewhere. There's also a [MiniZinc](https://minizinc.org/) solver in `unruly.mzn`, and a Z3-based solver in `unruly_z3.py`: both of these should find a solution if one exists, regardless of whether it can be found tactically. You can convert a puzzle in plain text format into a format suitable for MiniZinc using `board_to_dzn.py`.

I then tried looking for untactical solutions to the 1-dimensional problem, using the [MiniZinc](https://www.minizinc.org/) constraint solver, and then tried to build a two-dimensional puzzle using only untactical rows/columns. The first bit worked fine, but the second bit didn't: I found no solutions for small n, and the solver ran for a long time without producing any solutions for n = 7 and above. You can find the Python driver for this search in `find_solvable_rows.py`, and the MiniZinc code in `fixpoints.mzn` and `unsolvable.mzn`.

I tried to use MiniZinc to search for (puzzle, solution) pairs where no tactics applied to the puzzle: this code is in `untactical.mzn`. Unfortunately most puzzles it finds will not have unique solutions.

I then switched to using the [Z3 Theorem Prover](https://github.com/Z3Prover/z3) instead of MiniZinc, with the following plan:
 - Look for a (puzzle, completed solution) pair such that no tactics can be applied to the puzzle and the completed solution is a solution for the puzzle
 - Check that no other solution exists for the puzzle
 - If not, disallow that puzzle and start again.

You can find the code for doing this in `untactical_z3.py`. Once you've found some solutions, you can use `minimize_z3.py` to reduce the number of clues provided while preserving the uniqueness of the solution. The puzzles I found this way can be found under `found/`.

The images I used in the talk were generated from textual board descriptions that you can find under `gates/`; the code to turn them into images is in `board_to_png.py`. You can see [my slides here](https://docs.google.com/presentation/d/1sKVxpxUiWvyh6OOCqEk4slcyN0_3X2VQzIORVEKRzcU/edit?usp=sharing).