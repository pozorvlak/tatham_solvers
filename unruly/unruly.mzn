% Find solutions to the provided Unruly board.
% Inputs for this solver are generated by board_to_dzn.py.

int: n; % number of cells of each colour in a unit

set of int: ROW = 1..2*n;
set of int: COLUMN = 1..2*n;

array[ROW, COLUMN] of var bool: board;

% must match the filled-in squares in the input
enum SPACE = { BLACK, WHITE, UNKNOWN };
array[ROW, COLUMN] of SPACE: puzzle;
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

solve satisfy;

% function var string: cell_to_char(var bool: cell) = if cell then "#" else " " endif;

output [ show2d(board) ];