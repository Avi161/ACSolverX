# Complete new--new curvature aggregate on the positive chamber

Date: 2026-07-29

## 0. Theorem and scope

Put

\[
 i\ge d\ge1,\qquad a=d-1\ge0,\qquad n=i-d\ge0.
 \tag{0.1}
\]

Let \(g=g^{(0)}+g^{(Q)}\) be the exact four-corner activity curvature from
the approved residual memo, formed only after integral current aggregation
and occurrence expansion.  Define the **complete new--new aggregate**

\[
\begin{aligned}
 N(i,d)
 &:=Q(g)\\
 &=Q(g^{(0)})
  +\mathbb B(g^{(0)},g^{(Q)})+Q(g^{(Q)}).
\end{aligned}
\tag{0.2}
\]

The certificate accompanying this memo proves

\[
 \boxed{N(i,d)=0\qquad(i\ge d\ge1).}
 \tag{0.3}
\]

This is a joint theorem.  Its three displayed constituents are not assumed
to vanish separately.  Indeed, on \(d\ge2\) the slot-zero and path/path
pieces are both one and cancel each other, while the cross piece is zero.
That cancellation is why the aggregate, rather than its terms in isolation,
is the correct proof object.

The result removes the complete three-term new--new line from the exact
ten-family residual.  It leaves

\[
\boxed{
\begin{aligned}
 \mathfrak D^\ddagger={}&
 \mathbb B(a^\circ,g^{(0)})
 +\mathbb B(a^\circ,g^{(Q)})
 +\mathbb B(b,f)\\
 &+\mathbb B(b,g^{(0)})+\mathbb B(b,g^{(Q)})
 +\mathbb B(f,g^{(0)})+\mathbb B(f,g^{(Q)}).
\end{aligned}}
\tag{0.4}
\]

Thus positive-chamber covariance and \(\mathfrak D^\ddagger=0\) remain
open.  A value of one in any constituent of (0.2) is not a counterexample;
only their certified aggregate matters.  Nothing here proves or refutes
Andrews--Curtis or stable Andrews--Curtis.

## 1. Exact token cochain and chronology

For a correction token \((o,v)\), retain the literal raw occurrence action
\(q_o\) and put

\[
 \tau_o(v)=\operatorname{cvert}(q_ov).
 \tag{1.1}
\]

Raw actions are parsed and quotient-reduced before the final module
canonicalization.  In particular,

\[
 \operatorname{raw}(\texttt{tc})=\texttt{tc},\qquad
 \operatorname{raw}(\texttt{tc})^{-1}=\texttt{cT}.
 \tag{1.2}
\]

The module parser, which would send literal `tc` to `t`, is not used for an
action, prefix, or transport factor.

For distinct tokens define the symmetric chronological kernel

\[
 \xi(p,q)=
 \begin{cases}
 [\ell(p)<_{\rm sl}\ell(q)],&p\triangleleft q,\\
 [\ell(q)<_{\rm sl}\ell(p)],&q\triangleleft p.
 \end{cases}
 \tag{1.3}
\]

Different occurrences use literal AST order.  Within one positive
occurrence, module vertices are increasing shortlex; within one negative
occurrence, they are decreasing shortlex.  Every action label is compared
only after `c_vertex`.  For a finite activity \(x\),

\[
 Q(x)=\sum_{\{p,q\}}x(p)x(q)\xi(p,q).
 \tag{1.4}
\]

No raw mirror term occurs in (0.2); both raw curvature loads were closed in
the preceding residual certificate.  Negative chronology and all
new--new comparisons remain load-bearing here.

## 2. The two curvature currents

### 2.1 Four slot-zero corners

Put

\[
 \Gamma=\texttt{ctcTTTctctcTTTctctcTTTct},
 \qquad S_\Gamma=\Gamma^{-1},
 \tag{2.1}
\]

and

\[
 Y(e,m)=p^{-1}\Gamma^e cS_\Gamma^m t.
 \tag{2.2}
\]

The four pairwise distinct current coordinates of \(g^{(0)}\) are

\[
\begin{array}{c|c|c}
\text{corner}&e&m\\ \hline
00&a+1&a+n+2\\
01&a&a+n+2\\
11&a+1&a+n+3\\
12&a&a+n+3.
\end{array}
\tag{2.3}
\]

Every corner has parity one.  Each expands through the six slot-zero
occurrences \(3,4,7,8,11,12\), giving exactly

\[
 4\cdot6=24
 \tag{2.4}
\]

active tokens.

### 2.2 Inverse-\(Q\) path curvature

For a stored positive-\(Q_\nu\) letter at position \(k\), use the corrected
right-deck vertex

\[
 w_{\nu k\delta}(i,d)=\operatorname{cvert}\bigl(
 m_{\nu k}E(Q_{\nu,<k})q_\nu^{d-1}c_\nu
 p_\nu^{i+\delta}r_\nu\bigr),
 \qquad\delta\in\{0,1\}.
 \tag{2.5}
\]

Its integral provenance coefficient is

\[
 c_{\nu k\delta}
 =\epsilon_\nu\iota_{\nu k}(-1)^\delta.
 \tag{2.6}
\]

There are 92 values of \((\nu,k)\), hence 184 signed provenance rows.  For
each slot and canonical module word, the certificate first forms the
integer fiber

\[
 K_s(v)=\sum_{\nu,k,\delta}
 c_{\nu k\delta}[w_{\nu k\delta}=v],
 \tag{2.7}
\]

and only then uses \(K_s(v)\bmod2\) as activity.  On every all-power cell,
the 184 rows form exactly 106 fibers:

| fiber size | fibers |
|---:|---:|
| 1 | 50 |
| 2 | 34 |
| 3 | 22 |

Their integral sums are 17 fibers of each of \(-2,+2\) and 36 fibers of
each of \(-1,+1\).  Therefore exactly 72 current fibers are odd.  Each odd
fiber expands through the two occurrences of its slot, giving

\[
 72\cdot2=144
 \tag{2.8}
\]

active \(g^{(Q)}\)-tokens.

The complete activity used in (0.2) consequently has

\[
 24+144=168
 \tag{2.9}
\]

tokens on every cell.  Virtual provenance rows are never assigned separate
quadratic activity.

## 3. Common primitive-core normal forms

The exact normalizer uses the common primitive length-eight cores

\[
 R=\texttt{ctcTTTct},\qquad
 S=\texttt{cTctttcT}.
 \tag{3.1}
\]

Every path factor from (2.5) is a conjugate of \(R^3\) or \(S^3\), as
proved by the approved inverse-\(Q\) certificate.  Each slot-zero module or
action schema has the form

\[
 A\Gamma^{a+\alpha}c\Gamma^{-(a+n+\kappa)}t,
 \qquad \alpha\in\{0,1\},\quad\kappa\in\{2,3\},
 \tag{3.2}
\]

with the fixed raw occurrence action included in \(A\).  The four module
schemas and their six action schemas give 28 slot-zero schemas.

It is essential to normalize \(\Gamma^{-1}\) against the same reference
core \(S\) used by the path schemas.  Its native primitive word
`TctttcTc` is a cyclic rotation of \(S\).  A draft which used the native
phase assigned different keys to literally equal powered functions; for
example

```text
g0:00:action:o11
partner:action:nu3:k13:delta0:o1
```

is equal throughout the relevant \(a=0\) family.  Re-expressing both
families in the common \(R/S\) phase makes functional equality equivalent to
canonical primitive-core equality.

The 28 slot-zero schemas produce 448 templates on the sixteen cells below.
Together with the imported path schemas, every word retains:

1. the fixed blocks and affine primitive-core exponents;
2. terminal-`c` status after complete reduction;
3. affine post-`c_vertex` length;
4. surviving adjacent primitive copies for every unbounded pump; and
5. exact fixed or affine first-mismatch data.

No terminal deletion is moved inside a product.

## 4. Exact Presburger partition

The combined schema family requires the disjoint partition

\[
 a\in\{0,1,2,\ge3\},
 \qquad n\in\{0,1,2,\ge3\}.
 \tag{4.1}
\]

These sixteen cells cover \(\mathbb N^2\), and any two disagree in a
mutually exclusive equality or lower-bound atom.  The bounded cells are
reduced literally.  On an unbounded coordinate the base exponent is three;
future copies are inserted between surviving adjacent copies of the
cyclically reduced primitive core.  Thus each base cancellation trace and
terminal branch remains valid for the whole cell.

The refinement is not a powered grid.  The values 0, 1, and 2 are exact
boundary chambers, while \(\ge3\) is discharged by one pumping theorem.

## 5. Collision and comparison certificate

### 5.1 Collision equivalence

For every cell, all 5,684 unordered same-slot pairs among the 184 path
module schemas are compared.  Across sixteen cells this gives 90,944 exact
pair/cell checks.  The branches are:

| equality branch | checks |
|---|---:|
| strict affine length | 88,736 |
| identical canonical primitive-core key | 1,600 |
| fixed-prefix first mismatch | 568 |
| affine pumped first mismatch | 40 |

The checker requires

\[
 \text{module functions equal on a cell}
 \iff
 \text{their canonical primitive-core keys agree}.
 \tag{5.1}
\]

This reconstructs the 106 integer fibers and 72 odd activities before any
token pair is formed.  Equal members of a fiber are also checked to have
equal action labels at both occurrences of their slot.

### 5.2 Complete quadratic pair set

The 168 active tokens give

\[
 \binom{168}{2}=14{,}028
 \tag{5.2}
\]

unordered chronological comparisons per cell, hence 224,448 across all
sixteen cells.  Their provenance partition is

| pair source | pairs per cell |
|---|---:|
| \(g^{(0)},g^{(0)}\) | 276 |
| \(g^{(0)},g^{(Q)}\) | 3,456 |
| \(g^{(Q)},g^{(Q)}\) | 10,296 |

Literal distinct-occurrence order accounts for 12,240 pairs per cell.
Same-occurrence increasing and decreasing chronology account for 894 each.
Thus every negative-occurrence pair is retained rather than evaluated in an
increasing surrogate order.

The 224,448 action-label decisions use:

| shortlex branch | checks |
|---|---:|
| strict affine length | 220,304 |
| canonical pumped-word equality | 1,472 |
| fixed-prefix first mismatch | 2,528 |
| affine pumped first mismatch | 144 |

The 28,608 same-occurrence module decisions use 28,240 strict lengths, 312
fixed-prefix mismatches, and 56 affine pumped mismatches.  Equality is
excluded for two distinct active tokens in one occurrence.

Every unordered pair record is serialized with its endpoints in deterministic
token-ID order and hashed.  The manifest retains both its proof-record digest
and a semantic digest which omits the proof-method labels and can be replayed
directly from raw products.

## 6. Exact aggregate count

The complete counts are independent of \(n\) but this is a consequence of
the sixteen certified cells, not an extrapolation:

| chamber | one pair records | \(N\) |
|---|---:|:---:|
| \(a=0\) (\(d=1\)) | 6,790 | 0 |
| \(a=1\) | 6,772 | 0 |
| \(a=2\) | 6,772 | 0 |
| \(a\ge3\) | 6,772 | 0 |

The component xors expose the nontermwise cancellation:

| chamber | \(Q(g^{(0)})\) | \(\mathbb B(g^{(0)},g^{(Q)})\) | \(Q(g^{(Q)})\) | total |
|---|:---:|:---:|:---:|:---:|
| \(d=1\) | 0 | 0 | 0 | 0 |
| \(d\ge2\) | 1 | 0 | 1 | 0 |

Reducing the exact counts modulo two proves (0.3).  The second row also
shows why the earlier slot-zero observation could not be promoted in
isolation: its nonzero value is canceled by the path/path curvature.

## 7. Independent direct replay

Only after the symbolic records and pair digests were derived, six points
were reconstructed without using the pumped templates to form their words:

| \((i,d)\) | \((a,n)\) | cell | one records | \(N\) |
|---:|---:|---|---:|:---:|
| \((1,1)\) | \((0,0)\) | `a0_n0` | 6,790 | 0 |
| \((5,1)\) | \((0,4)\) | `a0_nge3` | 6,790 | 0 |
| \((2,2)\) | \((1,0)\) | `a1_n0` | 6,772 | 0 |
| \((5,3)\) | \((2,2)\) | `a2_n2` | 6,772 | 0 |
| \((5,5)\) | \((4,0)\) | `age3_n0` | 6,772 | 0 |
| \((9,5)\) | \((4,4)\) | `age3_nge3` | 6,772 | 0 |

For each point the replay:

1. forms all 184 path vertices in the corrected raw right-deck order;
2. groups exact \((s,v)\) words and sums integer coefficients;
3. obtains 106 fibers and 72 odd fibers;
4. forms all four slot-zero words directly from (2.2)--(2.3);
5. applies each occurrence action raw, then `c_vertex`;
6. evaluates all 14,028 chronological pairs; and
7. matches the symbolic semantic-pair digest byte-for-byte.

These replays are semantic guards, not the source of the all-power theorem.

## 8. Consequence for the residual proof

The approved residual theorem gave

\[
\begin{aligned}
 \mathfrak D^\ddagger={}&
 \mathbb B(a^\circ,g^{(0)})
 +\mathbb B(a^\circ,g^{(Q)})\\
 &+N(i,d)+\mathbb B(b,f)
 +\mathbb B(b,g^{(0)})+\mathbb B(b,g^{(Q)})\\
 &+\mathbb B(f,g^{(0)})+\mathbb B(f,g^{(Q)}).
\end{aligned}
\tag{8.1}
\]

Substitution of (0.3) gives exactly (0.4).  The remaining seven families
contain old/new and increment/increment interactions involving \(a^\circ\),
\(b\), and \(f\).  This note proves no identity among those families.

A future nonzero result for one remaining family would still not refute
covariance unless its complete seven-family xor were certified nonzero.

## 9. Proof boundary

### Proved

1. Collision-first activity for all 184 inverse-\(Q\) provenance rows on
   every positive-chamber cell.
2. Common primitive-phase normalization of every slot-zero and path schema,
   including terminal-`c` handling.
3. Exact coverage of all 168 active tokens and 14,028 pair records per cell.
4. Literal positive and decreasing-negative same-occurrence chronology.
5. The all-power identity \(N(i,d)=0\), with the nontermwise cancellation
   on \(d\ge2\).
6. The exact seven-family residual (0.4).

### Still open

1. The seven-family xor in (0.4), hence \(\mathfrak D^\ddagger=0\).
2. Positive-chamber augmented covariance and diagonal covariance of the
   \(j\)-edge.
3. The other covariance chambers, edge boundary values, diagonal
   cancellation, both edge laws, and \(u_{ij}=\delta_{ij}\).
4. Any Andrews--Curtis or stable Andrews--Curtis conclusion.

The next exact target should preserve the aggregate principle.  A natural
grouping is the complete \(g\)-load against the remaining old/increment
activity,

\[
 \mathbb B(a^\circ+b+f,g),
 \tag{9.1}
\]

together with \(\mathbb B(b,f)\).  Neither summand is asserted to vanish.

## 10. Reproduction and artifacts

Artifacts:

```text
.scratch/period_two_new_new_aggregate.md
.scratch/period_two_new_new_aggregate_manifest.json
.scratch/period_two_new_new_aggregate_checker.py
.scratch/test_period_two_new_new_aggregate_checker.py
```

Commands, each bounded below 30 seconds:

```text
PYTHONDONTWRITEBYTECODE=1 python3 \
  .scratch/period_two_new_new_aggregate_checker.py --check

PYTHONDONTWRITEBYTECODE=1 python3 \
  .scratch/test_period_two_new_new_aggregate_checker.py
```

Final hashes and the hostile-referee verdict are recorded after review.

## 11. Hostile referee

### Initial verdict: APPROVE with one Minor wording repair

The independent referee found zero Critical or Important findings.  The
only Minor finding was that a draft called the records "ordered pairs."
Section 5 now correctly says that each pair is unordered and its two
endpoints are merely serialized in deterministic token-ID order.

The referee independently confirmed:

1. the definition \(N=Q(g^{(0)}+g^{(Q)})\), all four slot-zero corners,
   raw `tc`/`cT` typing, corrected path factor order, and integral signs;
2. all 184 provenance rows, 106 collision fibers, the 50/34/22 size
   distribution, the signed fiber sums, and 72 odd fibers on every cell;
3. common primitive \(R/S\) phasing, including the formerly under-refined
   cross-family equality;
4. 357,420 independent direct order/equality checks over all 28 slot-zero
   and 555 imported schemas, sixteen cells, and selected pump interiors,
   with 1,449 equalities and no mismatch;
5. all terminal-`c` branches, 168 tokens, 14,028 pairs per cell, source
   counts/xors, and positive/decreasing-negative chronology;
6. five additional direct interior replays at
   \((a,n)=(1,11),(2,13),(3,1),(8,2),(8,9)\), all matching the fiber
   membership, component xors, chronology counts, one-count, and semantic
   digest; and
7. the exact reduction from ten residual families to seven.

### Focused rereview: APPROVE

**APPROVE — zero Critical, Important, or Minor findings remain.**  The same
referee verified the terminology repair and reran the checker and test.  The
load-bearing bytes approved before this review text was appended had hashes

```text
memo      31c070943d51980d7cde89638f207a248d843906a63456130e1415965648fad0
manifest  39183f77a56915b6f1e135b23b26d1067c1b56f0a4af8b6c09057d9fc477d640
checker   e1f8b9f748ca5a6cfeed9f7db7243892bc888a92ab0e096e754fb0d06b9ec650
test      462ac8f1b02277d6e479c612bcd84a01241ad393ee08aeb46011b5864f1abac3
```

The review adds no covariance, unary-delta, Andrews--Curtis, or stable
Andrews--Curtis conclusion.
