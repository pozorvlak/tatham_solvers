int: n;

set of int: COLUMN = 1..2*n;
array[COLUMN] of var bool: row;

constraint sum(row) = n;
constraint forall(c in 1..2*n-2)(
  let { var int: s = sum(i in 0..2)(row[c + i]); }
  in 0 < s /\ s < 3
);

solve satisfy;