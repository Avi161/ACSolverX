# MMS02 depth-three Nielsen/Alexander obstruction

## Result

The following named bridge mechanism is impossible.

> **Depth-three automorphism-assisted fixed-base ansatz.** Start with the exact
> two-relator base
>
> ```text
> A = xzYXyxZXYxyZ
> B = XyxZXYXyxzXYxy
> ```
>
> Apply an ambient automorphism of `F(x,y,z)` having elementary Nielsen
> length at most three in the frozen alphabet below. Require it to preserve
> the normal closure of `A,B`. Then attempt to change `zYX` to `Xyz`
> using the fixed base rows, conjugation, and inversion.

The complete depth-three Nielsen ball has 2,527 distinct automorphisms. The
`A5` representation variety rejects 2,523 immediately. Its only survivors
are the identity and three explicit involutions. The Alexander module rejects
all three nonidentity survivors. The identity is already rejected by the
existing fixed-base `A5` conjugacy obstruction.

This proves a finite, exact obstruction to the named ansatz. It is not an
obstruction to a general AC1--AC3 path in which the base rows move.

## Exact source and case roundtrip

The checker imports the misprinted three-generator descendant directly from
`.scratch/mms02_wirtinger_repair_checker.py` and obtains exactly

```text
xzYXyxZXYxyZ
XyxZXYXyxzXYxy
```

The inverse rename sends `x,y,z` back to the surviving MMS02 generators
`x5,x7,x12`, preserving the case of every letter. Both compositions are
checked word-for-word:

```text
raw -> rename_xyz -> inverse_rename_xyz = raw
word -> inverse_rename_xyz -> rename_xyz = word.
```

Among all 48 signed generator permutations, the identity is the only map
that preserves the unordered cyclic/inverse classes of the two literal base
relators.

## Frozen Nielsen ball

The elementary alphabet has 18 moves on the ordered free basis:

- three inversions `wi <- wi^-1`;
- three swaps `wi <-> wj`;
- twelve signed right transvections `wi <- wi wj^epsilon`, for
  `i != j` and `epsilon` equal to `+1` or `-1`.

Breadth-first enumeration, keyed by the exact freely reduced basis-image
triple, gives

| depth | distinct maps |
|---:|---:|
| 0 | 1 |
| 1 | 18 |
| 2 | 218 |
| 3 | 2,290 |
| total | 2,527 |

Every stored path is a composition of explicit elementary automorphisms.
For each surviving candidate, the checker replays the path and its reversed
inverse path back to `(x,y,z)`. It also substitutes the candidate into
itself; all three candidates are literal involutions.

## Complete A5 necessary gate

Let `H` be the exact set of triples `(X,Y,Z)` in `A5^3` that kill both
`A` and `B`. Exhaustive enumeration of all `60^3` triples gives

```text
|H| = 180 = 120 epimorphisms + 60 diagonal homomorphisms.
```

The 60 non-surjective solutions are exactly `(g,g,g)` for `g in A5`.
The number 180 is deliberately different from the separate count 272 in the
small-symmetric-group audit: 180 counts homomorphisms into the single fixed
codomain `A5`, whereas 272 aggregates homomorphisms into `S_n` for several
degrees.

If an ambient automorphism preserves the normal closure of `A,B`,
precomposition must permute `H`. Testing all 2,527 maps leaves exactly

```text
identity = (x, y, z)
psi      = (y, x, zyX)
eta_y    = (x, zYz, z)
eta_z    = (x, y, yZy).
```

The first nonidentity map is the attractive outer-`A5` candidate. Its exact
images are

```text
psi(A) = yzyXXYxyxYZYXyxxYZ
psi(B) = YxyxYZYXYxyzyXYXyx.
```

The other two finite-quotient survivors have exact images

```text
eta_y(A) = xyZXzYzxZXZyZxzY
eta_y(B) = XzYzxZXZyZXzYzxzXZyZxzYz

eta_z(A) = xyZXyxYzYXYxzY
eta_z(B) = XyxYzYXYXyxyZyXYxy.
```

Passing this gate is only necessary. The next section shows that all three
are finite-quotient mirages.

## Alexander-module gate

Let `Lambda = Z[t,t^-1]`, using the exact abelianization
`x,y,z -> t`. Put

```text
a = [yX]
b = [zX].
```

The abelianized Fox row of `A` gives

```text
(2 - t - t^-1) a - b = 0,
```

so `b = p a` with `p = 2-t-t^-1`. Substitution into the row of `B`
gives

```text
t^-3 Delta(t) a = 0,
Delta(t) = t^4 - 3t^3 + 5t^2 - 3t + 1.
```

For every exponent-zero word `w`, its module class is therefore

```text
[w] = Fox_y(w) + p Fox_z(w)  modulo Delta.
```

All candidate generator images have total exponent one, so the substituted
base relators have exponent zero and this test applies. Polynomial division
by the monic `Delta`, followed only by removal of a Laurent-unit power of
`t`, gives:

| map | remainder of image of A | remainder of image of B |
|---|---|---|
| `psi` | `2 - 3t + t^2` | `-1 + t - t^3` |
| `eta_y` | `-2` | `2 - 6t + 10t^2 - 4t^3` |
| `eta_z` | `-2 + 2t - 2t^2` | `2 - 4t + 6t^2 - 2t^3` |

Every displayed remainder is nonzero and has degree below four. Hence neither
substituted relator is trivial in the Alexander module for any of the three
maps. In particular,

```text
phi(A), phi(B) are not in normal_closure(A,B)
```

for `phi` equal to `psi`, `eta_y`, or `eta_z`. None descends even to
an endomorphism of the exact base group.

## Exact conclusion

Every nonidentity ambient automorphism in the frozen depth-three Nielsen ball
fails one of two necessary conditions:

1. it does not preserve the full 180-point `A5` solution set; or
2. it is one of the three survivors above and has a nonzero Alexander-module
   relator image.

The only remaining map is the identity. At the displayed `A5` epimorphism,
`zYX` lies in neither the conjugacy class of `Xyz` nor that of its inverse,
so the identity cannot complete the fixed-base exchange.

No knot-group identification is used or inferred from the Alexander
polynomial. The polynomial appears only as the order relation of the exact
Fox module computed from the displayed words.

## Scope

Proved:

- completeness for the exact 18-generator Nielsen ball through depth three;
- exact preservation of case and both rename roundtrips;
- completeness of all 180 `A5`-valued solutions;
- exact rejection of every nonidentity finite-quotient survivor.

Not proved:

- that a longer ambient automorphism cannot preserve the base;
- that an abstract automorphism of the quotient must lift to the ambient free
  group;
- that a path moving `A` and `B` is obstructed;
- any negative statement about AC or stable AC.

The unrestricted bridge

```text
(A,B,zYX) ~AC (A,B,Xyz)
```

remains open.

## Replay

```text
python3 .scratch/mms02_depth3_nielsen_alexander_obstruction.py
python3 .scratch/test_mms02_depth3_nielsen_alexander_obstruction.py
```

The main checker reconstructs the entire Nielsen ball and the complete
`A5^3` solution set; it does not load a stored candidate list or trace.
