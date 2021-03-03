enum SHAPE = { T, I, L, Q, B };
enum DIRECTION = { left, up, right, down };
array[SHAPE, 1..4] of bool: exit =
[|true, false, true, true,
 |true, false, true, false,
 |false, true, true, false,
 |false, false, false, true,
 |false, false, false, false|];

int: width;
int: height;
bool: wrap;
set of int: ROW = 1..height;
set of int: COLUMN = 1..width;
array[ROW, COLUMN] of SHAPE: shape;
array[ROW, COLUMN] of var DIRECTION: orientation;

array[ROW, COLUMN] of var bool: l;
array[ROW, COLUMN] of var bool: u;
array[ROW, COLUMN] of var bool: r;
array[ROW, COLUMN] of var bool: d;

constraint forall(i in ROW, j in COLUMN)(
  l[i, j] = exit[shape[i, j], orientation[i, j]] /\
  u[i, j] = exit[shape[i, j], wrap(orientation[i, j] + 1, 4)] /\
  r[i, j] = exit[shape[i, j], wrap(orientation[i, j] + 2, 4)] /\
  d[i, j] = exit[shape[i, j], wrap(orientation[i, j] + 3, 4)]
);

function var int: wrap(var int: i, var int: n) = if i > n then i - n elseif i < 1 then i + n else i endif;

% all junctions must match up
constraint forall(i in 1..height-1, j in 1..width)(d[i, j] = u[i + 1, j]);
constraint forall(i in 1..height, j in 1..width-1)(r[i, j] = l[i, j + 1]);

constraint wrap -> forall(i in 1..height)(r[i, width] = l[i, 1]);
constraint wrap -> forall(j in 1..width)(d[height, j] = u[1, j]);

% every square must be reachable in exactly one way
array[ROW, COLUMN] of var int: path_count;
array[ROW, COLUMN] of var DIRECTION: upstream;
int: mid_row = ceil(height / 2);
int: mid_col = ceil(width / 2);
constraint forall(i in ROW, j in COLUMN)(
  (i != mid_row \/ j != mid_col) -> [l[i, j], u[i, j], r[i, j], d[i, j]][upstream[i, j]]
);
constraint forall(i in ROW, j in COLUMN)(
  (i != mid_row \/ j != mid_col) ->
  % for every direction in which there is an exit, the cell on the other side is downstream iff it's not upstream
%   (l[i, j] -> (upstream[i, j] = left) xor upstream[i, wrap(j - 1, width)] = right) /\
%   (u[i, j] -> (upstream[i, j] = up) xor (upstream[wrap(i - 1, height), j] = down)) /\
  (r[i, j] -> (upstream[i, j] = right) xor upstream[i, wrap(j + 1, width)] = left) /\
  (d[i, j] -> (upstream[i, j] = down) xor upstream[wrap(i + 1, height), j] = up)
);
constraint path_count[mid_row, mid_col] = 1;
constraint forall(i in ROW, j in COLUMN)(
  (upstream[i, j] = left ->  path_count[i, j] = path_count[i, wrap(j - 1, width)]) /\
  (upstream[i, j] = up -> path_count[i, j] = path_count[wrap(i - 1, height), j]) /\
  (upstream[i, j] = right -> path_count[i, j] = path_count[i, wrap(j + 1, width)]) /\
  (upstream[i, j] = down -> path_count[i, j] = path_count[wrap(i + 1, height), j])
);
constraint forall(i in ROW, j in COLUMN)(path_count[i, j] = 1);

solve satisfy;

array[SHAPE, DIRECTION] of string: pic =
[|"╦", "╠", "╩", "╣",
 |"═", "║", "═", "║",
 |"╚", "╝", "╗", "╔",
 |"╥", "╞", "╨", "╡",
 |" ", " ", " ", " "|];

output (
  [concat([pic[shape[i, j], fix(orientation[i, j])] | j in COLUMN]) ++ "\n" | i in ROW]
  ++ ["\n", show2d(path_count)]
  ++ ["\n", show2d(upstream)]
);
