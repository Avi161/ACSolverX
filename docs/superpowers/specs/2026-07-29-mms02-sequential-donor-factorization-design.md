# MMS02 Sequential Donor Factorization Design

## Objective and scope

This checkpoint records three exact, independently replayable free-group proof
objects for the misprinted MMS02 presentation:

1. the approved nine-action triangular path from `(r,q,v)` to `(x,y,z)`;
2. the eight donor macros of the S1 branch from `(r,q,v)` to `(A,q,v)`; and
3. the two donor macros of the S2 branch from `(r,q,v)` to `(r,B,v)`.

The two donor branches have the same start and are separate. They are not
concatenated. The certificate also records the two rank-two quotient gates that
remain after setting `v=1`, but it does not attempt to decide either gate.

No existing solver, runner, notebook, proof guard, or proof checker is changed.
All new proof code, focused tests, and the canonical JSON certificate live under
`.scratch/`.

## Literal convention and pinned words

Lowercase letters are generators and uppercase letters are their inverses.
For a word `w`, `w^-1` means reverse `w` and swap case. Products are freely
reduced by cancelling adjacent opposite-case copies of the same letter. There
is no implicit cyclic rotation or cyclic reduction. The commutator convention
is `[s,t]=s t s^-1 t^-1`.

The pinned literal words are

```text
A = xzYXyxZXYxyZ
B = XyxZXYXyxzXYxy
u = zYX
c = yxZXY
C = c^-1 = yxzXY
r = xyxZXY
q = Xy
v = Xyz
h = YX
K = [u,C] = u C u^-1 C^-1
D = h [X,r] h^-1 = h X r x r^-1 h^-1
```

The generator and independent verifier must check the literal identities

```text
A = free_reduce(r K^-1)
B = free_reduce(q D^-1)
```

before accepting any certificate. A failure is terminal: the implementation
must report `BLOCKED` rather than changing a pinned word or convention.

## Primitive actions and typed current-row ledger

Rows are numbered 1, 2, 3. Every action reads the current tuple, not the tuple
at the start of a branch.

- `invert(i)` replaces current row `i` by its inverse.
- `multiply(i,j)` replaces current row `i` by the freely reduced product of
  current row `i` followed on the right by current row `j`; row `j` is unchanged.
- `conjugate(w,i)` replaces current row `i` by
  `free_reduce(w row_i w^-1)`.

Each serialized primitive action contains its exact before and after 3-tuples,
kind, 1-based target row, and the literal donor row or conjugator when relevant.
The verifier rejects zero-based, swapped, or out-of-range indices.

## Nine-action triangular transcript

The triangular transcript is independent of S1 and S2. It starts at
`(r,q,v)` and uses exactly the following nine actions:

```text
I3, M32, I3, C_yx(3), M13, C_XY(3), C_Yx(1), M21, C_Xy(1)
```

Here `Ii` is `invert(i)`, `Mij` is `multiply(i,j)`, and `C_w(i)` is
`conjugate(w,i)`. Its exact current-row ledger is:

| Step | Action | Current rows after the action |
|---:|---|---|
| 0 | start | `(xyxZXY, Xy, Xyz)` |
| 1 | `I3` | `(xyxZXY, Xy, ZYx)` |
| 2 | `M32` | `(xyxZXY, Xy, Z)` |
| 3 | `I3` | `(xyxZXY, Xy, z)` |
| 4 | `C_yx(3)` | `(xyxZXY, Xy, yxzXY)` |
| 5 | `M13` | `(x, Xy, yxzXY)` |
| 6 | `C_XY(3)` | `(x, Xy, z)` |
| 7 | `C_Yx(1)` | `(Yxy, Xy, z)` |
| 8 | `M21` | `(Yxy, y, z)` |
| 9 | `C_Xy(1)` | `(x, y, z)` |

The certificate and verifier bind the literal case, action order, indices,
every intermediate tuple, and the final `(x,y,z)` endpoint. A regression test
must reject a certificate that replaces this transcript by either donor branch.

## S1 donor obligation

In the current rows `(r,q,v)`, define four conjugates of the current donor
rows:

```text
f1 = (x q x^-1)
f2 = (x^2 q^-1 x^-2)
f3 = (x^2 v x^-2)
f4 = (x q^-1 x^-1)
C  = f1 f2 f3 f4
```

The generator and verifier must check this literal free-group factorization.
Since `K^-1=C u C^-1 u^-1`, the ordered S1 macro factors are

| Macro | Target | Donor | Conjugator | Sign |
|---:|---:|---:|---|---:|
| 1 | 1 | 2 | `x` | `+1` |
| 2 | 1 | 2 | `xx` | `-1` |
| 3 | 1 | 3 | `xx` | `+1` |
| 4 | 1 | 2 | `x` | `-1` |
| 5 | 1 | 2 | `zY` | `+1` |
| 6 | 1 | 3 | `zYx` | `-1` |
| 7 | 1 | 2 | `zYx` | `+1` |
| 8 | 1 | 2 | `zY` | `-1` |

These are respectively
`f1,f2,f3,f4,u f4^-1 u^-1,u f3^-1 u^-1,
u f2^-1 u^-1,u f1^-1 u^-1`, after freely reducing each conjugator.
Right multiplication of current row 1 by the eight factors must give the exact
endpoint `(A,q,v)`.

For a positive macro with conjugator `w`, target `i`, and donor `j`, the exact
primitive expansion is:

```text
conjugate(w,j); multiply(i,j); conjugate(w^-1,j)
```

For a negative macro it is:

```text
invert(j); conjugate(w,j); multiply(i,j); conjugate(w^-1,j); invert(j)
```

Every macro contains its before and after tuple, its primitive expansion, the
donor word before and after, and `donor_restored=true`. The verifier must replay
the primitives and prove that the donor after the macro equals the donor before
the macro. Thus S1 has 8 macros and 32 primitive actions: 8 multiplications,
16 conjugations, and 8 inversions.

## S2 donor obligation

The exact second factorization is

```text
D^-1 = h r h^-1 (hX) r^-1 (hX)^-1.
```

Starting again from `(r,q,v)`, not from the S1 endpoint, S2 uses:

| Macro | Target | Donor | Conjugator | Sign |
|---:|---:|---:|---|---:|
| 1 | 2 | 1 | `YX` | `+1` |
| 2 | 2 | 1 | `YXX` | `-1` |

The same primitive-expansion and restoration rules apply. Right multiplication
of current row 2 by these factors must give `(r,B,v)`. S2 has 2 macros and 8
primitive actions: 2 multiplications, 4 conjugations, and 2 inversions.

Across the independent transcript and both branches, the certificate contains
49 primitive actions: 13 multiplications, 24 conjugations, and 12 inversions.

## Remaining rank-two quotient gates

Setting `v=Xyz=1` gives the named substitution `z=Yx` and `Z=Xy`. Literal
substitution followed only by free reduction gives:

```text
A_bar = xYxYXyyXYxyXy
D_bar = YXyyXYxyxY
B_bar = XyyXYXyxYYxy
K_bar = YxYXyxYYxyXyyyXY
```

The two named quotient presentations and defect words are therefore

```text
Q_A = <x,y | xYxYXyyXYxyXy>,  defect delta_D = YXyyXYxyxY
Q_B = <x,y | XyyXYXyxYYxy>,    defect delta_K = YxYXyxYYxyXyyyXY
```

The first gate asks whether `delta_D` is trivial in `Q_A`, equivalently whether
`D` lies in the normal closure of `A` and `v`. The second asks whether
`delta_K` is trivial in `Q_B`, equivalently whether `K` lies in the normal
closure of `B` and `v`. The certificate checks only the substitutions, free
reductions, and exact presentation/defect strings.

## Certificate boundary and independent verification

The generator produces one canonical JSON object only after its in-memory
replay validates all pinned identities, all three ledgers, endpoints,
restorations, action counts, and quotient words. Every macro serializes:

- exact before and after row tuples;
- 1-based target and donor indices;
- literal conjugator and donor sign;
- donor before, donor after, and restoration boolean; and
- the complete primitive action expansion with per-action before/after tuples.

The independent verifier reads literal JSON and implements inversion, free
reduction, multiplication, conjugation, branch replay, and quotient substitution
itself. It does not import the generator. It rejects wrong schema/version,
wrong letter case, altered words, extra or missing actions, reordered macros,
wrong indices, donor drift, wrong endpoints, wrong quotient words, and a
conflated triangular transcript.

## Explicit nonclaims

- The separate S1 and S2 branches do not concatenate to a path from
  `(r,q,v)` to `(A,B,v)`.
- The full sequential donor factorization needed to combine the branches is
  equivalent to the still-open MMS02 bridge; this checkpoint does not supply
  that factorization and does not solve the bridge.
- The nine-action path `(r,q,v)->(x,y,z)` is a separate triangular witness and
  is not evidence that either donor branch can use the other branch's endpoint.
- No factorization of `delta_D` by conjugates of `A_bar` is claimed.
- No factorization of `delta_K` by conjugates of `B_bar` is claimed.
- No membership or nonmembership in either named quotient is claimed without
  an explicit normal-closure factorization or homomorphism.
- No finite quotient, finite-group enumeration, heuristic search, or bounded
  search result is part of this checkpoint.
- No claim is made beyond the exact free reductions and replayed actions stored
  in the certificate.
