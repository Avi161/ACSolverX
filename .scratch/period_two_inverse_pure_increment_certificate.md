# All-power inverse pure-increment certificate

## Status and theorem

Let

\[
 e=j-i\geq0,\qquad n=i\geq0,
 \qquad
 b^-_{n,e}=A^-_{n,e}+A^-_{n,e+1}.
 \tag{0.1}
\]

The guarded v4 certificate proves, for every such \((n,e)\),

\[
\boxed{
 L((b^-_{n,e})^{(0)})=[e=0],\qquad
 L_{\ne0}(b^-_{n,e})=[e=0],\qquad
 L(b^-_{n,e})=0,
}
\tag{0.2}
\]

and

\[
\boxed{
 Q(b^-_{n,e})=1,
 \qquad
 \Phi(b^-_{n,e})=L(b^-_{n,e})+Q(b^-_{n,e})=1.}
\tag{0.3}
\]

Together with the independently proved inverse old--new value
\(\mathbb B(A^-_{n,e},b^-_{n,e})=[e\geq1]\), this gives only the
nonpositive/inverse \(j\)-edge law

\[
\boxed{J^-_{n,e}=[e=0].}
\tag{0.4}
\]

The proof interface and reduction to 36 nonzero-slot raw bits and the
84-token quadratic stream are in
`literature/proofs/AK3_OLD_NEW_INVERSE_Q_CONNECTORS.md`, Section 7.  The
machine certificate is:

- `.scratch/period_two_inverse_pure_increment_checker.py`;
- `.scratch/test_period_two_inverse_pure_increment_checker.py`; and
- `.scratch/period_two_inverse_pure_increment_manifest.json`.

## 1. Exhaustive all-power cells

The parameter quadrant is partitioned into the twelve disjoint cells

\[
 \{e=0,e=1,e\geq2\}
 \times
 \{n=0,n=1,n=2,n\geq3\}.
 \tag{1.1}
\]

The base point of an unbounded cell is its least point: \(e=2\) for
\(e\geq2\) and \(n=3\) for \(n\geq3\).  The manifest records the following
values on every point of the indicated symbolic cell:

| \(e\)-cell | \(n\)-cells | \(L_{0}\) | \(L_{\ne0}\) | \(L\) | \(Q\) | \(\Phi\) | \(L_{\ne0}+Q\) |
|:---|:---|---:|---:|---:|---:|---:|---:|
| \(e=0\) | \(0,1,2,\geq3\) | 1 | 1 | 0 | 1 | 1 | 0 |
| \(e=1\) | \(0,1,2,\geq3\) | 0 | 0 | 0 | 1 | 1 | 1 |
| \(e\geq2\) | \(0,1,2,\geq3\) | 0 | 0 | 0 | 1 | 1 | 1 |

Thus the last column is \([e\geq1]\), exactly the remaining scalar in the
proof reduction.  These are symbolic pumped cells, not twelve sampled
parameter pairs.

## 2. Collision and token census

The negative-oriented \(Q\)-increment source contributes 92 integral
provenance rows.  In each cell the exact all-power canonical-word comparison
partitions them into 53 collision fibers.  Integral coefficients are summed
inside each fiber before reduction modulo two.  Exactly 36 fibers are active,
with slot profile

\[
 (|S_2|,|S_3|,|S_4|)=(8,14,14).
 \tag{2.1}
\]

Adding the two slot-zero coordinates gives 38 collision-aggregated module
coordinates.  Each active edge coordinate has its two slot occurrences and
each slot-zero coordinate has its six occurrences, so the decorated stream
has

\[
 36\cdot2+2\cdot6=84
 \tag{2.2}
\]

tokens.  The manifest records 72 nonzero-slot raw rows and every unordered
decorated-token pair,

\[
 \binom{84}{2}=3486,
 \tag{2.3}
\]

in every cell.  The 210 same-slot module-order predicates isolated in the
theory note are included in those exact pair records; none is replaced by a
topological guess.

## 3. Common primitive phase repair

The initial hostile audit blocked promotion because commensurable powered
schemas could use cyclically rotated primitive cores.  Equal all-power words
could then agree at a cell base while receiving different pumped canonical
block keys.  Refining the numerical threshold did not repair that defect.

The v4 construction passes one common primitive reference through every
commensurable path and slot-zero schema.  Phase rotations are absorbed into
the fixed conjugating pieces before canonical powered blocks are compared.
The primitive cores have length eight; each full 24-letter powered block is
represented by affine primitive increment three.  Collision equality,
label order, and module order are therefore comparisons of common-phase
all-power normal forms throughout each cell.

## 4. Raw one-increment saturation lemma

For a raw observable with a pumped normal form \(A R^{kt}B\), suppose one
affine increment places the inserted right boundary strictly beyond the
finite action horizon, the exact raw signatures at the cell base and the
next point agree, and the central-label length has positive slope.  Every
later insertion is then beyond the same finite prefix, so the raw bit is
constant along that unbounded cell direction.

Each free raw pump records the fields

`insertion_split`, `affine_increment`, `core_length`, `action_horizon`,
`saturated_boundary`, `base_next_raw_signature_equal`, and
`central_length_slope`, together with the derived boolean
`horizon_saturated`.  Verification recomputes

\[
 \texttt{saturated_boundary}
 =\texttt{insertion_split}
  +\texttt{affine_increment}\cdot\texttt{core_length}
 >\texttt{action_horizon},
 \tag{4.1}
\]

requires the base/next signature equality and positive central-length slope,
and fails closed if any condition is altered.  Across the twelve cells there
are \(7\cdot72=504\) certified free-direction pump records.  The independent
direct semantic replay at every cell base checks all 84 tokens, coordinates,
labels, raw bits, 3,486 pair bits, and the three totals \(L,Q,\Phi\).

## 5. Verification, hashes, and review

The approved commands are

```sh
python3 .scratch/test_period_two_inverse_pure_increment_checker.py
python3 .scratch/period_two_inverse_pure_increment_checker.py --write
python3 .scratch/period_two_inverse_pure_increment_checker.py --check
```

The frozen SHA-256 bindings are:

| artifact | SHA-256 |
|:---|:---|
| checker | `0f4675e4e0dab936e32fa9cc7d1ec093bbd806363d2e92f82e36d4ca4e203d48` |
| tests | `c1e5c2d9a7c45c46ba8dadcc2c392c793a40adb88d049a21b31ebbb67ae1a7fe` |
| manifest | `4e821f1cc9b721281178341b458669de3ac7191314a8e613fb7a37866e40b0cd` |

The test suite checks the exclusive command-line modes, exact cell catalog,
92-row provenance uniqueness, collision partition and coefficient parity,
53/36 fiber counts, slot profile, 38 coordinates, 84 distinct token IDs, 72
raw rows, all 3,486 pair IDs and recomputed pair bits, raw saturation fields,
direct replay totals, and rejection after hostile mutations of guards,
fibers, tokens, raw records, pair records, saturation witnesses, and the
claimed value of \(\Phi\).  `--check` rebuilds the certificate and requires
byte-for-byte equality with the frozen manifest.

After the common-primitive phase repair and raw-saturation hardening, the
focused hostile final review returned **APPROVED**, with no remaining
load-bearing finding for (0.2)--(0.4).

## 6. Strict boundary

This certificate itself proves only the inverse/nonpositive chamber
\(e=j-i\geq0\).  The separate theorem
`literature/proofs/AK3_POSITIVE_J_EDGE_RAW_LOAD.md` proves
\(L(b_{n,d})=0\) and \(J_{n,d}=[d=1]\) for \(d\geq1\).  Thus the two notes
together close the \(j\)-edge law in every chamber, but the positive theorem
is not a consequence of this inverse certificate.

Neither note proves the diagonal defect, the \(i\)-edge law, unary delta
identity, period-two lift, AK(3), stable Andrews--Curtis, or
Andrews--Curtis.
