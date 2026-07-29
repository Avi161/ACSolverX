# Exact all-power inverse-Q terminal companion

Date: 2026-07-29

## 0. Status and theorem

The finite certificate accompanying this memo closes the 736-record family
in (4.2)--(4.11) of `.scratch/period_two_companion_aggregate.md`.  On

\[
 i\ge d\ge1
\]

it proves

\[
 \boxed{\Theta_{*,Q}(i,d)=[d\ge2].}
 \tag{0.1}
\]

This is an all-power calculation, not an inference from a grid.  The proof
uses the nine disjoint Presburger cells obtained from

\[
 a=d-1\in\{0,1,\ge2\},\qquad
 n=i-d\in\{0,1,\ge2\}.
 \tag{0.2}
\]

The machine-readable certificate contains all 736 record IDs, 555 powered
word schemas, 4,995 cellwise reduced normal forms, all shortlex and
same-occurrence module comparisons, integral collision fibers, and the nine
modulo-two totals.  A deterministic checker reconstructs all of these from
the reviewed raw manifest generator and the live quotient implementation.

The hostile review required by the task is recorded in Section 9.

## 1. Authoritative input and raw typing

The inputs are:

- `.scratch/period_two_companion_aggregate.md`;
- `.scratch/period_two_complete_cochain_identity.md`;
- the raw-stream manifest generator, complete JSON, memo, and approved
  review;
- the restricted powered-product normalizer and approved scoped review; and
- the cited live lift, source-flow, subgroup-rewrite, tree-flow, and literal
  Hessian implementations.

The raw manifest package replayed byte-for-byte with

```text
generator  edd1f21fda1665b092447143b30d25e65f8c9a9cf2753a56ceb5da16db150bb1
JSON       824d17adc0bc9b553d722eb627ee60f363451673237e366f6eb869acc6e058dd
status     PASS
```

The checker performs the raw parser guard before every independent boundary
pin:

\[
 \operatorname{raw}(\texttt{tc})=\texttt{tc},\qquad
 \operatorname{raw}(\texttt{tc})^{-1}=\texttt{cT}.
 \tag{1.1}
\]

For comparison, the module-vertex parser sends the same literal `tc` to
`t`; that parser is never used for an action, prefix, or transport factor.

For a stored positive-Q letter at position \(k\), every certified partner
vertex is built in the corrected order

\[
 \boxed{
 m_{\nu k}E(Q_{\nu,<k})q_\nu^{d-1}c_\nu
 p_\nu^{i+\delta}r_\nu .
 }
 \tag{1.2}
\]

No row prepends \(p_\nu^\delta\), and no row substitutes an inverse-Q
prefix.  The integral coefficient retained on the provenance copy is

\[
 c_{\nu k\delta}
 =\epsilon_\nu\iota_{\nu k}(-1)^\delta.
 \tag{1.3}
\]

There are 92 bounded Q positions.  Multiplying by two diagonal copies, two
terminal occurrences, and the two partner occurrences of the selected slot
gives

\[
 92\cdot2\cdot2\cdot2=736
 \tag{1.4}
\]

unique record IDs.

## 2. Finite cyclic normal-form refinement

### 2.1 The 555 schemas

Put \(a=d-1\) and \(n=i-d\).  Each needed module or action label has the
form

\[
 W(a,n)=Aq^aBp^{a+n+\kappa}C,
 \qquad a,n\ge0,quad \kappa\ge1,
 \tag{2.1}
\]

where \(A,B,C,q,p\) are fixed quotient words.  The 555 schemas are:

\[
 3\text{ terminal schemas}
 +92\cdot2\text{ partner-module schemas}
 +92\cdot2\cdot2\text{ partner-action schemas}.
 \tag{2.2}
\]

The three terminal schemas are the module word and its actions at
occurrences 9 and 14.  The partner action is always the raw occurrence
action applied before final `c_vertex`.

Put the two common primitive cores

\[
 R=\texttt{ctcTTTct},\qquad
 S=\texttt{cTctttcT}.
 \tag{2.3}
\]

They are cyclically reduced, primitive, and have length 8.  Every powered
factor is a conjugate of the third power of the corresponding primitive
core:

\[
 q_\nu=x_\nu R^3x_\nu^{-1},\qquad
 p_\nu=y_\nu S^3y_\nu^{-1}.
 \tag{2.4}
\]

The exact conjugators are:

| \(\nu\) | \(x_\nu\) | \(y_\nu\) |
|---:|---|---|
| 1 | `eps` | `eps` |
| 2 | `ctcTc` | `Tc` |
| 3 | `ctcTc` | `ctcTc` |
| 4 | `ctcTcTc` | `ctcTc` |
| 5 | `eps` | `ctcTc` |
| 6 | `ctcTcTc` | `Tc` |

Substitution in (2.1) gives

\[
 (Ax_\nu)R^{3a}
 (x_\nu^{-1}By_\nu)S^{3(a+n+\kappa)}
 (y_\nu^{-1}C).
 \tag{2.5}
\]

The certificate stores the exact fixed words in (2.5), not only their
lengths.

### 2.2 The nine Presburger cells

The refinement is the Cartesian product

\[
 \mathcal A_0:\ a=0,\quad
 \mathcal A_1:\ a=1,\quad
 \mathcal A_+:\ a\ge2
 \tag{2.6}
\]

and

\[
 \mathcal N_0:\ n=0,\quad
 \mathcal N_1:\ n=1,\quad
 \mathcal N_+:\ n\ge2.
 \tag{2.7}
\]

In the original variables these are respectively

\[
 d=1,\ d=2,\ d\ge3,
 \qquad
 i=d,\ i=d+1,\ i\ge d+2.
 \tag{2.8}
\]

Equations (2.6)--(2.7) cover every \(a,n\in\mathbb N\).  Two distinct
cells disagree in at least one of the mutually exclusive atoms
`=0`, `=1`, `>=2`; hence every pairwise intersection is empty.  The JSON
retains each cell as a predicate AST and records zero coverage and overlap
failures.

### 2.3 Exact all-power reduction on each cell

For a bounded cell, the checker freely reduces (2.5) exactly.  For an
unbounded coordinate it uses the base exponent 2 and retains, on every
letter, its source block, copy number, and phase in the 8-letter primitive
core.  After complete quotient reduction and terminal-`c` handling, it
requires a surviving adjacent boundary

\[
 (\text{copy }j,\text{ phase }7)
 (\text{copy }j+1,\text{ phase }0).
 \tag{2.9}
\]

An arbitrary number of additional copies is inserted at (2.9).  Since the
core is cyclically reduced, neither the internal word nor either insertion
boundary cancels.  The original power identity permits the new identical
copies to be placed between any two consecutive surviving copies.  Thus the
base cancellation trace remains valid for every nonnegative extra exponent.

This gives the following fixed-block power forms:

- on \(a\in\{0,1\}, n\ge2\), insert
  \(S^{3(n-2)}\);
- on \(a\ge2, n\in\{0,1\}\), insert
  \(R^{3(a-2)}\) and \(S^{3(a-2)}\);
- on \(a,n\ge2\), insert
  \(R^{3(a-2)}\) and \(S^{3(a+n-4)}\).

The checker verifies all required surviving boundaries: 8 structural
pumping checks for each of 555 schemas, hence 4,440 checks.  It then emits
all 555 by 9 reduced fixed-block power words.  Every record contains:

1. its exact fixed and cyclic blocks;
2. the affine exponent of every power;
3. the complete Presburger cell;
4. the terminal-`c` truth value after full reduction;
5. the affine pre- and post-`c_vertex` lengths; and
6. the two adjacent surviving copy numbers supporting each pump.

The 4,995 terminal branches split as 2,484 terminal-`c` and 2,511
nonterminal-`c` branches.  Terminal deletion is never moved inside a product
and is never treated as a homomorphism.

## 3. Exact order bits and chronology

All words use shortlex key

\[
 (|w|,w),\qquad \texttt T<\texttt c<\texttt t.
 \tag{3.1}
\]

For every requested pair on every cell, the two affine length functions
have the same \(a,n\) coefficients.  Consequently their difference is a
constant on that cell.  The materialized comparisons split as follows:

| comparison branch | label comparisons | same-occurrence module comparisons |
|---|---:|---:|
| strict affine length | 6,579 | 1,206 |
| identical canonical pumped words | 27 | 18 |
| equal length, fixed-prefix first mismatch | 18 | 0 |

In all 18 record-pair mismatch branches, the first mismatch occurs before
every pump insertion.  Its exact position and the two letters are printed in
JSON.  Identical words are certified after absorbing adjacent fixed copies
of the same primitive core into the affine exponent.  The only
transformations are

\[
 AU\,U^eB=A\,U^{e+1}B,
 \qquad
 AU^e\,UB=A\,U^{e+1}B.
 \tag{3.2}
\]

Collision equality requires more pairs than the terminal record table.  The
checker compares all 5,684 unordered same-slot pairs of the 184 module
schemas on each of nine cells, for 51,156 symbolic pair/cell checks:

| all-pairs equality branch | checks |
|---|---:|
| strict affine length | 49,917 |
| identical canonical primitive-core key | 900 |
| constant-position fixed-letter mismatch | 309 |
| affine pumped fixed-letter mismatch | 30 |

For every equal-length unequal-key pair, the checker cuts both templates
immediately before the first unequal fixed letters.  The two complete
powered prefixes normalize to the same literal block expression and have
the same affine length; the next two fixed letters differ.  This proves the
first mismatch at that affine length for every point of the cell.  In the 30
pumped branches the positions are \(24a+C\), with
\(C\in\{-1,0,5,6,7,8\}\).  For example,
`partner:module:nu3:k0:delta1` versus
`partner:module:nu5:k11:delta0` on `age2_n0` first differs at
\(24a+5\).  No value of \(a\) or \(n\) is sampled to infer these formulas.
The exhaustive result is

\[
 \text{module functions equal on a cell}
 \iff
 \text{their canonical primitive-core keys agree}.
 \tag{3.3}
\]

For distinct occurrences, the earlier literal AST occurrence supplies the
left chronological token.  For the same occurrence, let

\[
 \mu=\operatorname{ord}_{\rm sl}(v^*,w)\in\{-1,0,1\},
 \qquad
 \lambda=\operatorname{ord}_{\rm sl}
 (\tau_o(v^*),\tau_o(w)).
 \tag{3.4}
\]

The exact bit used by the checker is

\[
 \chi_{o,o}(v^*,w)
 =[\mu\ne0]\,[\lambda=\operatorname{pol}(o)\mu].
 \tag{3.5}
\]

Thus occurrence 9 uses increasing module order and occurrence 14 uses
decreasing module order.  Equality contributes zero.  Equation (3.5) is
exactly the six same-occurrence lines of (4.6) in the companion memo.

## 4. Integral collisions before parity

There are 184 current-provenance copies \((\nu,k,\delta)\).  Each retains
the integral coefficient (1.3).  On every cell, module-word equality is
computed from the canonical pumped normal form before reducing coefficients
modulo two.

On every one of the nine cells, the 184 copies form exactly 106 collision
fibers:

| fiber size | number of fibers |
|---:|---:|
| 1 | 50 |
| 2 | 34 |
| 3 | 22 |

Their integral sums are

| integral sum | fibers |
|---:|---:|
| \(-2\) | 17 |
| \(-1\) | 36 |
| \(+1\) | 36 |
| \(+2\) | 17 |

Hence exactly 72 fibers are odd on every cell.  The exhaustive all-pairs
equivalence (3.3), rather than a hash collision key alone, proves that no
same-slot equality is omitted and no unequal functions are merged.

For every one of the nine cells, the checker evaluates the terminal pairing
both ways:

1. xor all 736 provenance-expanded bits; and
2. first sum the integral coefficients in each collision fiber, reduce the
   fiber coefficient modulo two, and then xor its terminal bits.

The two results agree on every cell.  This is the collision-safe linear
expansion of (4.3)--(4.7), not an assignment of activity to virtual rows.

## 5. Modulo-two bounded-fiber count

The exact nine-cell totals are:

| \(a=d-1\) | \(n=i-d\) | one bits among 736 | \(\Theta_{*,Q}\) |
|---:|---:|---:|:---:|
| 0 | 0 | 398 | 0 |
| 0 | 1 | 398 | 0 |
| 0 | \(\ge2\) | 398 | 0 |
| 1 | 0 | 399 | 1 |
| 1 | 1 | 399 | 1 |
| 1 | \(\ge2\) | 399 | 1 |
| \(\ge2\) | 0 | 399 | 1 |
| \(\ge2\) | 1 | 399 | 1 |
| \(\ge2\) | \(\ge2\) | 399 | 1 |

Every selector \(k\), both values of \(\delta\), both terminal
occurrences, and both slot-partner occurrences are present once.  Reducing
the displayed exact counts modulo two gives

\[
 \Theta_{*,Q}(i,d)
 =\begin{cases}
 0,&d=1,\\
 1,&d\ge2,
 \end{cases}
 \tag{5.1}
\]

which is (0.1).  No value was extrapolated from representative indices.

## 6. Independent formula-selected boundary replay

Only after deriving and writing the nine-cell certificate, four points were
replayed directly through the live right-deck products and occurrence
actions.  The replay does not use the reduced templates to construct its
words.

| \((i,d)\) | cell | direct one count | direct xor |
|---:|---|---:|:---:|
| \((1,1)\) | `a0_n0` | 398 | 0 |
| \((3,1)\) | `a0_nge2` | 398 | 0 |
| \((2,2)\) | `a1_n0` | 399 | 1 |
| \((5,3)\) | `age2_nge2` | 399 | 1 |

All 736 record bits matched the already-derived cell records at each point.
The raw parser guard (1.1) ran before these pins.

## 7. Exact effect on the remaining defect

The reviewed companion memo proved

\[
 \Theta_{*,0}=[d\ge2].
 \tag{7.1}
\]

Together with (0.1), the complete old-terminal footprint against \(g\)
therefore cancels:

\[
 \boxed{
 \mathbb B(a_*,g)
 =\Theta_{*,0}+\Theta_{*,Q}=0.
 }
 \tag{7.2}
\]

Recall

\[
 \mathfrak D^\dagger=\mathfrak D+\Theta_{*,0},
 \qquad
 \Omega_*=[d=1]+\mathfrak D^\dagger.
 \tag{7.3}
\]

Remove the now-complete old-terminal leg by defining

\[
 \mathfrak D^\ddagger
 :=\mathfrak D^\dagger+\Theta_{*,Q}
 =\mathfrak D+\Theta_{*,0}+\Theta_{*,Q}.
 \tag{7.4}
\]

Then

\[
 \mathfrak D^\dagger=[d\ge2]+\mathfrak D^\ddagger,
 \qquad
 \boxed{\Omega_*=1+\mathfrak D^\ddagger.}
 \tag{7.5}
\]

Because (7.2) is zero, \(\mathfrak D^\ddagger=\mathfrak D\) as a scalar
function; the notation records that the complete old-terminal subaggregate
has been removed from its provenance expansion.  The remaining theorem is
exactly

\[
 \Omega_*=1
 \iff
 \mathfrak D^\ddagger=0.
 \tag{7.6}
\]

The old positive `P/C/Q` rows, fixed inverse-Q terms in the other bilinear
loads, diagonal increment rows, fixed literal tokens, odd base rows, and
new--new terms have not all been closed.  Therefore this memo does **not**
prove full covariance, either edge law, or the unary delta identity.

## 8. Reproduction and artifacts

Artifacts:

```text
.scratch/period_two_inverse_q_companion.md
.scratch/period_two_inverse_q_companion_manifest.json
.scratch/period_two_inverse_q_companion_checker.py
.scratch/test_period_two_inverse_q_companion_checker.py
```

Current repaired pre-rereview hashes:

```text
manifest  616c7eaa570f0be87a42c1dae17d0301cbe0b0280f52777f926c6504172225d3
checker   37bfcd326951848f2a721e3dabbaa6d65220b5b1109fafb21e4aa403db94d980
```

Replay commands, each bounded below 30 seconds:

```text
PYTHONDONTWRITEBYTECODE=1 python3 \
  .scratch/period_two_raw_stream_manifest_generator.py --check

python3 .scratch/test_period_two_inverse_q_companion_checker.py

python3 .scratch/period_two_inverse_q_companion_checker.py --check

python3 .scratch/period_two_inverse_q_companion_checker.py \
  --replay-boundaries
```

## 9. Hostile referee

### Initial verdict

**REJECT, repairable.**  The referee accepted raw `tc`/`cT` typing, the
correct positive-Q factor order, all 736 IDs and coefficients, the 555
schema count, nine-cell coverage and disjointness, threshold-two pumping,
terminal-`c` handling, record order bits, negative chronology, the 398/399
raw xor, the post-derivation pins, and the conditional defect algebra.

The rejected load-bearing claim was the first draft's collision partition.
It grouped by a nonprimitive 24-letter-core key and checked equality only
inside a key.  At `age2_n0`, the smallest missed equality was

```text
partner:module:nu2:k0:delta0
partner:module:nu6:k2:delta0
```

at \((a,n)=(2,0)\), equivalently \((i,d)=(3,3)\).  Both coefficient
\(+1\) rows are the same slot-two module word, so their true fiber has
coefficient \(+2\) and even activity.  The draft incorrectly printed two
active singletons.  Its zero aggregation-failure count was vacuous across
distinct keys.  The referee therefore withheld aggregate approval while
not finding a counterexample to the raw 398/399 xor.

### Repairs and focused rereview

The repair replaces every rotated 24-letter core by the common primitive
8-letter core in (2.3), with exponent multiplier three.  Adjacent primitive
copies are absorbed into exponent constants by the literal identities
(3.2).  Every one of the 51,156 same-slot pair/cell comparisons is then
proved by strict affine length, identical canonical keys, or an exact
constant/affine first mismatch.  This repairs the referee's smallest pair
and produces the same 106 integral fibers, size distribution, signed sums,
and 72 odd fibers on all nine cells.

The manifest, its hash, and the four direct pins are regenerated only after
this repair.  Focused rereview of those repaired bytes follows below.

### Focused rereview

**APPROVE -- zero remaining load-bearing findings.**  The same hostile
referee checked the repaired manifest and checker hashes and independently
confirmed:

1. the primitive, cyclically reduced length-eight cores \(R,S\), exponent
   multiplier three, and all six printed conjugator pairs reconstruct the
   live \(q_\nu,p_\nu\);
2. all 4,995 normalized templates preserve their base words and affine
   lengths;
3. the exhaustive 51,156 all-pairs classification has exactly 49,917
   strict-length, 900 equality, 309 constant-mismatch, and 30 affine-pumped
   mismatch certificates;
4. the former `nu2:k0:delta0` / `nu6:k2:delta0` counterexample is now one
   coefficient-\(+2\), even fiber on every cell;
5. every cell has exactly 106 fibers with the printed sizes, signed sums,
   and 72 odd fibers, and independent raw xor equals fiber-first aggregation;
6. the 398/399 counts, raw typing, corrected factor order, terminal-`c`
   handling, positive/decreasing-negative chronology, and four
   post-derivation pins all pass; and
7. (0.1), (7.2), and (7.5) are correct while covariance, the edge laws,
   and unary delta remain open.

The focused reviewer found no counterexample and approved the final theorem
boundary exactly as stated in Sections 0 and 7.
