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

function var int: wrap(var int: i, var int: n) = ((i - 1) mod n) + 1;

constraint forall(i in 1..height-1, j in 1..width)(d[i, j] = u[i + 1, j]);
constraint forall(i in 1..height, j in 1..width-1)(r[i, j] = l[i, j + 1]);

constraint wrap -> forall(i in 1..height)(r[i, width] = l[i, 1]);
constraint wrap -> forall(j in 1..width)(d[height, j] = u[1, j]);

solve satisfy;

array[SHAPE, DIRECTION] of string: pic =
[|"╦", "╠", "╩", "╣",
 |"═", "║", "═", "║",
 |"╚", "╝", "╗", "╔",
 |"╥", "╞", "╨", "╡",
 |" ", " ", " ", " "|];

output ( [concat([pic[shape[i, j], fix(orientation[i, j])] | j in COLUMN]) ++ "\n" | i in ROW] );
