% Looks for a (completed board, puzzle) pair such that
% - the completed board is a solution to the puzzle
% - none of the four standard tactics work on the puzzle

int: n; % number of cells of each colour in a unit

set of int: ROW = 1..2*n;
set of int: COLUMN = 1..2*n;

array[ROW, COLUMN] of var bool: board;

% must match the filled-in squares in the input
enum SPACE = { BLACK, WHITE, UNKNOWN };
array[SPACE] of SPACE: other = [WHITE, BLACK, UNKNOWN];
array[ROW, COLUMN] of var SPACE: puzzle;
constraint forall(r in ROW, c in COLUMN)(puzzle[r, c] = BLACK -> board[r, c] = false);
constraint forall(r in ROW, c in COLUMN)(puzzle[r, c] = WHITE -> board[r, c] = true);

% Exactly n blacks and n whites in each row and column
constraint forall(r in ROW)(sum(c in COLUMN)(board[r, c]) = n);
constraint forall(c in COLUMN)(sum(r in ROW)(board[r, c]) = n);

% no more than 2 consecutive black or white cells in a row
constraint forall(r in ROW)(
  forall(c in 1..2*n - 2)(
    let { var int: s = sum(i in 0..2)(board[r, c + i]); } in 0 < s /\ s < 3
  )
);

% no more than 2 consecutive black or white cells in a column
constraint forall(c in COLUMN)(
  forall(r in 1..2*n - 2)(
    let { var int: s = sum(i in 0..2)(board[r + i, c]); } in 0 < s /\ s < 3
  )
);

% "endcaps" tactic can't be applied
constraint forall(r in ROW, c in 2..2*n-2)(
  (puzzle[r, c] != UNKNOWN /\ puzzle[r, c] = puzzle[r, c+1]) -> (puzzle[r, c-1] = other[puzzle[r, c]])
);
constraint forall(r in ROW, c in 1..2*n-2)(
  (puzzle[r, c] != UNKNOWN /\ puzzle[r, c] = puzzle[r, c+1]) -> (puzzle[r, c+2] = other[puzzle[r, c]])
);
constraint forall(r in 2..2*n-1, c in COLUMN)(
  (puzzle[r, c] != UNKNOWN /\ puzzle[r, c] = puzzle[r+1, c]) -> (puzzle[r-1, c] = other[puzzle[r, c]])
);
constraint forall(r in 1..2*n-2, c in COLUMN)(
  (puzzle[r, c] != UNKNOWN /\ puzzle[r, c] = puzzle[r+1, c]) -> (puzzle[r+2, c] = other[puzzle[r, c]])
);

% "gaps" tactic can't be applied
constraint forall(r in ROW, c in 1..2*n-2)(
  (puzzle[r, c] != UNKNOWN /\ puzzle[r, c] = puzzle[r, c+2]) -> (puzzle[r, c+1] = other[puzzle[r, c]])
);
constraint forall(r in 1..2*n-2, c in COLUMN)(
  (puzzle[r, c] != UNKNOWN /\ puzzle[r, c] = puzzle[r+2, c]) -> (puzzle[r+1, c] = other[puzzle[r, c]])
);
% "n" tactic can't be applied
constraint forall(r in ROW, val in [BLACK, WHITE])(sum(c in COLUMN)(puzzle[r, c] = val) < n);
constraint forall(c in COLUMN, val in [BLACK, WHITE])(sum(r in ROW)(puzzle[r, c] = val) < n);

solve satisfy;

% function var string: cell_to_char(var bool: cell) = if cell then "#" else " " endif;

output [ show2d(board), show2d(puzzle) ];