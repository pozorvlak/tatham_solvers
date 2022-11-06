% Searches for Unruly boards whose rows and columns all come from a specified list.
% The idea is that these should be fixpoints for a set of tactics, so the board
% as a whole is a fixpoint for those tactics.

int: n;

set of int: ROW = 1..2*n;
set of int: COLUMN = 1..2*n;

enum SPACE = { BLACK, WHITE, UNKNOWN };

int: num_fixpoints;
set of int: MASK = 1..num_fixpoints;
array[MASK, COLUMN] of SPACE: fixpoints;
% array[MASK] of set of int: solutions;

array[ROW, COLUMN] of var SPACE: board;
array[COLUMN] of var MASK: column;
array[ROW] of var MASK: row;

constraint forall(r in ROW, c in COLUMN)(board[r, c] = fixpoints[row[r], c]);
constraint forall(r in ROW, c in COLUMN)(board[r, c] = fixpoints[column[c], r]);

solve satisfy;

array[SPACE] of string: out = [ "B", "W", "_" ];

output [concat([out[fix(board[r, c])] | c in COLUMN]) ++ "\n" | r in ROW ];