int: n;

set of int: ROW = 1..2*n;
set of int: COLUMN = 1..2*n;

enum SPACE = { BLACK, WHITE, UNKNOWN };

int: num_fixpoints;
array[1..num_fixpoints, COLUMN] of SPACE: fixpoints;

array[ROW, COLUMN] of var SPACE: board;

include "table.mzn";

constraint forall(r in ROW)(table([board[r, c]| c in COLUMN], fixpoints));
constraint forall(c in COLUMN)(table([board[r, c]| r in ROW], fixpoints));

solve satisfy;

array[SPACE] of string: out = [ "B", "W", "_" ];

output [concat([out[fix(board[r, c])] | c in COLUMN]) ++ "\n" | r in ROW ];