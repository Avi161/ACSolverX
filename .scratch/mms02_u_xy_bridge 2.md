# MMS02 `U=xy`: exact descendants and the remaining bridge equation

## Result

Use `x=x5`, `y=x7`, and `z=x12` in the repaired MMS02 corridor.  The exact
three-generator descendants are

```text
corrected:
  C1 = yZXzYXyZxz
  C2 = YxyZxzYXyZxZXz

misprinted:
  A = xzYXyxZXYxyZ
  B = XyxZXYXyxzXYxy
```

For `U=xy`, the extra relation is `zYX=1`, so `z=xy`.  Direct substitution
and free reduction give

```text
corrected U=xy:   (Xy,      YxYXy)
misprinted U=xy: (xyxYXXY, XyxYXXYXyxxyXYxy).
```

Both pairs are ordinarily AC-trivial.  No stabilization is used:

```text
corrected:  1 Definition-2.1 macro  = 14 primitive AC1--AC3 moves
misprinted: 5 Definition-2.1 macros = 39 primitive AC1--AC3 moves
```

The same misprinted three-generator base with the published `U=Yx` relation
has kill word `Xyz` and specializes to

```text
(xYxYXyyXYxyXy, XyyXYXyxYYxy),
```

the raw spelling normalized in the earlier checker to the published pair and
then carried by the 53 published `h_i` moves to AK(3).  The present calculation
does **not** bridge the two kill words.  It reduces that bridge to one exact
rank-three AC equation and proves a fixed-base obstruction to the simplest
attempt.

## Exact ordinary AC replays

For compactness, write

```text
M(i,j,e,k,l): ri <- rot_k(ri) rot_l(rj^e),
```

where indices in the displayed five-tuples below are zero-based.  After each
move, freely/cyclically reduce, choose the least rotation-or-inverse of every
row, and sort the rows.  These normalizations are only shorthand: the checker
expands every rotation, inversion, cyclic cancellation, and row swap into
literal AC1, AC2, and AC3 moves, then independently replays the resulting
before/after transcript.

For the corrected raw pair, normalization followed by

```text
(1,0,-1,1,0)
```

gives the canonical path

```text
(Y, Yx) -> (Y, X).
```

Including normalization of `(Xy,YxYXy)`, this is 14 primitive moves: 4 AC1,
7 AC2, and 3 AC3.

For the misprinted raw pair, the five macros are

```text
(1,0, 1,5,1)
(1,0,-1,1,1)
(1,0, 1,4,0)
(1,0, 1,1,0)
(1,0,-1,1,0)
```

and the canonical states are

```text
YXyxxyX | YXyxYXXYxyxxyXYx
YXyxxyX | YXyxxyXYx
Yx       | YXyxxyX
Yx       | YXXyx
Y        | Yx
Y        | X.
```

Including normalization of the raw pair, this is 39 primitive moves: 11 AC1,
14 AC2, and 14 AC3.

## Common rank-three coordinates

The common misprinted base is `(A,B)` above.  The two relevant balanced triples
are therefore

```text
Txy  = (A, B, zYX)
Tpub = (A, B, Xyz).
```

The first is ordinarily AC-trivial.  Its exact macro path is

```text
(2,1,-1,3,0)
(2,0,-1,0,0)
(2,0,-1,1,0)
(2,1,-1,0,0)
(1,0, 1,2,1)
(0,1,-1,1,2)
(2,0,-1,2,0)
(2,0, 1,1,0)
(2,0,-1,0,0)
(2,0, 1,0,0)
(2,1, 1,0,0)
```

with canonical states

```text
Zxy | ZXzYXyxzXYxy | ZXYXyxzXYxyXyx
Zxy | ZXZxzXyx     | ZXzYXyxzXYxy
Zxy | ZXZxzXyx     | ZXYxyZxyx
Zxy | ZXYxyx       | ZXZxzXyx
Zxy | ZXzYxx       | ZXYxyx
Zxy | Zxx           | ZXYxyx
Yx  | Zxx           | ZXYxyx
Yx  | Zxx           | ZXyx
Zx  | Yx            | Zxx
X   | Zx            | Yx
Y   | X             | Zx
Z   | Y             | X.
```

The checker expands this path to 134 primitive moves: 50 AC1, 59 AC2, and 25
AC3.

At the original fourteen-generator level, delete `r12` as in the MMS02
corridor and retain the same thirteen misprinted Wirtinger rows.  The two extra
rows are, in the surviving coordinates,

```text
Kxy  = x12 X7 X5 = zYX,
Kpub = X5 x7 x12 = Xyz.
```

Thus the existing Tietze eliminations place both questions over exactly the
same `(A,B)` base.  This is a common coordinate system, not an elementary
AC4--AC5 bridge: the fourteen-generator substitution-and-removal history has
not been expanded into primitive AC4/AC5 moves here.

## A rigorous fixed-base no-go

The exact misprinted group `<x,y,z | A,B>` has the following quotient onto
`A5` (permutations act on `0,...,4`):

```text
x = (0,1,3,4,2)
y = (0,2,3,1,4)
z = (2,0,1,3,4).
```

Both `A` and `B` evaluate to the identity, and these three images generate all
60 even permutations.  The kill words evaluate to

```text
zYX -> (2,3,4,0,1)
Xyz -> (2,0,4,1,3).
```

The first is in neither the `A5` conjugacy class of the second nor the class of
its inverse.  Consequently there is no bridge that keeps `A` and `B` fixed as
words and changes only the third row using multiplication by `A` or `B`,
inversion, and conjugation.  This is only a fixed-base obstruction.  It says
nothing about a general AC path in which `A` or `B` moves.

## Smallest exact remaining equation

Because `Txy` is AC-trivial, a general bridge is equivalent to trivializing
`Tpub`.  The unresolved word equation is exactly

```text
find a literal AC1--AC3 sequence in F(x,y,z)

  (xzYXyxZXYxyZ,
   XyxZXYXyxzXYxy,
   zYX)

       ~AC

  (xzYXyxZXYxyZ,
   XyxZXYXyxzXYxy,
   Xyz),

allowing all three rows to move.
```

Equivalently, trivialize `(A,B,Xyz)` at rank three.  Such a sequence, combined
with the existing published reduction to AK(3), would prove stable
AC-triviality of AK(3).  No such sequence is supplied here.  A 50,000-node,
per-row-cap-40 greedy search did not solve `Tpub`; its minimum total length was
14 at `(ZYx,ZxyX,ZZZyyyy)`.  That bounded null result is a search lead only, not
an obstruction.

## Replay

Run

```text
python3 .scratch/mms02_u_xy_bridge_checker.py
```

to check the descendants, all three primitive replays, and the `A5` witness.
Add `--verbose` to print every primitive move with its exact before and after
words.
