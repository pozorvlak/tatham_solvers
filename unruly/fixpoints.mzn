int: n;

set of int: COLUMN = 1..2*n;
enum SPACE = { BLACK, WHITE, UNKNOWN };

array[SPACE] of SPACE: other = [WHITE, BLACK, UNKNOWN];

array[COLUMN] of var SPACE: row;

constraint forall(c in 1..2*n-2)((row[c] != UNKNOWN /\ row[c] = row[c+1]) -> row[c+2] = other[row[c]]);
constraint forall(c in 2..2*n-1)((row[c] != UNKNOWN /\ row[c] = row[c+1]) -> row[c-1] = other[row[c]]);
constraint forall(c in 1..2*n-2)((row[c] != UNKNOWN /\ row[c] = row[c+2]) -> row[c+1] = other[row[c]]);
var int: n_blacks = sum(c in COLUMN)(row[c] = BLACK);
var int: n_whites = sum(c in COLUMN)(row[c] = WHITE);
constraint n_whites < n;
constraint n_blacks < n;

% TODO this is too strict - we want "rule has already been applied", not "rule cannot be applied"
% constraint n_blacks = n - 1 -> forall(c in 1..2*n-2)(row[c] = BLACK \/ row[c+1] = BLACK \/ row[c+2] = BLACK);
% constraint n_whites = n - 1 -> forall(c in 1..2*n-2)(row[c] = WHITE \/ row[c+1] = WHITE \/ row[c+2] = WHITE);

solve satisfy;

array[SPACE] of string: out = [ "B", "W", "_" ];

output [concat([out[fix(row[c])] | c in COLUMN])];