# Residual augmented defect after the complete old-terminal cancellation

Date: 2026-07-29

## 0. Status and exact advance

Work throughout on the positive chamber

\[
 i,j\in\mathbb N,\qquad d=i-j\geq1,
 \qquad a=d-1,\qquad n=i-d=j.
 \tag{0.1}
\]

The complete augmented-covariance defect is

\[
 \mathfrak D
 =L(g)+\mathbb B(a_{ij},g)+Q(g)
  +\mathbb B(b,f)+\mathbb B(b,g)+\mathbb B(f,g),
 \tag{0.2}
\]

where \(L(x)=\sum_p x(p)r(p)\), and every vector is an activity
vector formed only **after integral current aggregation** and occurrence
expansion.  The notation \(a_{ij}\) in (0.2) is the old endpoint activity;
it is not the exponent \(a=d-1\).

The approved inverse-\(Q\) certificate now proves

\[
 \Theta_{*,Q}(i,d)=[d\geq2].
 \tag{0.3}
\]

Together with the previously approved

\[
 \Theta_{*,0}(i,d)=[d\geq2],
 \tag{0.4}
\]

this closes the complete old-terminal leg:

\[
 \boxed{\mathbb B(a_*,g)
 =\Theta_{*,0}+\Theta_{*,Q}=0.}
 \tag{0.5}
\]

This note derives the exact provenance-excised remainder and proves one
additional all-power cancellation:

\[
 \boxed{L(g^{(Q)})=0\qquad(i\geq d\geq1).}
 \tag{0.6}
\]

The already approved slot-zero theorem gives \(L(g^{(0)})=0\), so **all raw
mirror terms disappear from the residual**.  The final exact remainder is
the purely chronological quadratic expression (6.2).

The identity

\[
 \mathfrak D^\ddagger=0
 \tag{0.7}
\]

is still open.  This note produces neither an all-index zero proof nor an
exact nonzero chamber for the complete remainder.  The old-terminal
cancellation and (0.6) do not imply (0.7) by formal quadratic algebra; the
exact algebra checker in Section 7 proves that limitation.

Consequently positive-chamber augmented covariance, diagonal covariance of
the \(j\)-edge, both edge laws, and \(u_{ij}=\delta_{ij}\) remain open.
Even a future failure of (0.7) would refute this unary-delta continuation,
not Andrews--Curtis or stable Andrews--Curtis.

## 1. Token cochain and raw typing

Use the fixed token universe \(\mathscr P\) from the approved crossing
contraction.  For a correction token \(p=(o,v)\),

\[
 \ell(o,v)=\tau_o(v)=\operatorname{cvert}(q_ov),
 \qquad r(o,v)=\rho_o(v).
 \tag{1.1}
\]

For fixed tokens, \(r=0\).  Literal AST order is used between occurrences;
within a positive occurrence the module vertices are increasing shortlex,
and within a negative occurrence they are decreasing shortlex.  For two
distinct tokens the resulting symmetric chronological kernel is \(\xi\).
Put

\[
\begin{aligned}
 \mathbb B(u,v)
 &=\sum_{\{p,q\}}\xi(p,q)
   \bigl(u(p)v(q)+v(p)u(q)\bigr),\\
 Q(v)&=\sum_{\{p,q\}}v(p)v(q)\xi(p,q),\\
 \mathscr C(u,v)&=L(v)+\mathbb B(u,v)+Q(v).
\end{aligned}
\tag{1.2}
\]

All expressions take values in \(\mathbb F_2\).

Raw quotient data remain raw.  In particular,

\[
 p=\texttt{tc},\qquad p^{-1}=\texttt{cT}.
 \tag{1.3}
\]

Neither \(p\), an occurrence action \(q_o\), nor a transport factor is
passed through the module-vertex parser.  The product is quotient-reduced
first and `c_vertex` is applied only at the specified module interface.  The
six forest paths continue to use the live anti-homomorphic `eval_path`.

For every current vector, all signed provenance rows at a coordinate
\((s,v)\) are first summed in \(\mathbb Z\); the coefficient is reduced
modulo two only afterward.  Linear forms such as \(L\) and
\(\mathbb B(a_*,\cdot)\) may then be expanded over signed provenance rows,
because equal rows cancel in exactly the same way before and after that
linear expansion.  No such rowwise replacement is made inside \(Q\).

## 2. Exact four-corner variables

Let \(A_{rs}\) be the actual merged activity at the indicated endpoint,
with

\[
 A_{00}=a_{B+D_{ij}},\quad
 A_{01}=a_{B+D_{i,j+1}},\quad
 A_{11}=a_{B+D_{i+1,j+1}},\quad
 A_{12}=a_{B+D_{i+1,j+2}}.
 \tag{2.1}
\]

Define

\[
 a_{ij}=A_{00},\qquad
 b=A_{01}+A_{00},\qquad
 f=A_{11}+A_{00},\qquad
 g=A_{12}+A_{11}+A_{01}+A_{00}.
 \tag{2.2}
\]

Before parity the curvature splits as

\[
 \widetilde g=\widetilde g^{(0)}+\widetilde g^{(Q)},
 \tag{2.3}
\]

where

\[
 \widetilde g^{(0)}_0
 =e_{y_{i+1,j+2}}-e_{y_{i+1,j+1}}
  -e_{y_{i,j+1}}+e_{y_{ij}},
 \qquad \widetilde g^{(0)}_s=0\ (s\ne0),
 \tag{2.4}
\]

and, for \(s=2,3,4\),

\[
 \widetilde g^{(Q)}_s
 =\sum_{\nu=1}^6\epsilon_\nu(p_\nu-1)a_{\nu,ij}
   \mathsf E_s(Q_\nu^{-1}),
 \qquad \widetilde g^{(Q)}_0=\widetilde g^{(Q)}_1=0.
 \tag{2.5}
\]

Let \(g^{(0)}\) and \(g^{(Q)}\) be the activity parities of these two
integrally aggregated subcurrents.  Parity is linear after aggregation, so

\[
 g=g^{(0)}+g^{(Q)}.
 \tag{2.6}
\]

Here the slot-zero and path occurrence footprints are disjoint.  The cross
term \(\mathbb B(g^{(0)},g^{(Q)})\) in the polarization of \(Q(g)\)
retains every chronological interaction between those two distinct token
families.

## 3. The complete old-terminal footprint

Put

\[
 \Gamma=\texttt{ctcTTTctctcTTTctctcTTTct},\qquad
 U=\texttt{cTctttcTcTctttcTcTctttcT},
 \tag{3.1}
\]

and

\[
 v^*_{ij}=\operatorname{cvert}
 \bigl(\texttt T\,\Gamma^{d-1}U^{i+1}\texttt{ct}\bigr).
 \tag{3.2}
\]

The approved collision theorem gives actual activity one at this slot-three
coordinate.  Its two occurrence tokens are

\[
 A_*:=\{(9,v^*_{ij}),(14,v^*_{ij})\},
 \qquad a_*:=1_{A_*}.
 \tag{3.3}
\]

The two disjoint partner-current families are exactly \(g^{(0)}\) and
\(g^{(Q)}\), and the approved all-power results are

\[
 \mathbb B(a_*,g^{(0)})=[d\ge2],\qquad
 \mathbb B(a_*,g^{(Q)})=[d\ge2].
 \tag{3.4}
\]

Thus (0.5) follows by bilinearity.

The boundary arithmetic is explicit:

| chamber | \(\Theta_{*,0}\) | \(\Theta_{*,Q}\) | complete leg |
|---|:---:|:---:|:---:|
| \(d=1\) | 0 | 0 | 0 |
| \(d\ge2\) | 1 | 1 | 0 |

There is no exceptional value at \(i=d\); the inverse-\(Q\) certificate
covers every \(n=i-d\ge0\).

## 4. Definition and scalar boundary of \(\mathfrak D^\ddagger\)

The earlier reduced defect was

\[
 \mathfrak D^\dagger=\mathfrak D+\Theta_{*,0}.
 \tag{4.1}
\]

Define

\[
 \boxed{
 \mathfrak D^\ddagger
 :=\mathfrak D^\dagger+\Theta_{*,Q}
 =\mathfrak D+\Theta_{*,0}+\Theta_{*,Q}.
 }
 \tag{4.2}
\]

Then

\[
 \mathfrak D^\dagger=[d\ge2]+\mathfrak D^\ddagger,
 \qquad
 \boxed{\Omega_*=1+\mathfrak D^\ddagger.}
 \tag{4.3}
\]

For both boundary chambers,

\[
 \boxed{\mathfrak D^\ddagger=\mathfrak D\quad\text{as a scalar function}.}
 \tag{4.4}
\]

Equation (4.4) is not a vacuous renaming.  Formula (4.2) records a disjoint
provenance subaggregate that has been evaluated and removed.  To exhibit the
remaining provenance exactly, define the terminal-excised old activity

\[
 a^\circ:=a_{ij}+a_*.
 \tag{4.5}
\]

The two tokens in \(A_*\) are active in \(a_{ij}\), so (4.5) deletes them.
Using (0.5),

\[
 \mathbb B(a_{ij},g)
 +\Theta_{*,0}+\Theta_{*,Q}
 =\mathbb B(a^\circ,g).
 \tag{4.6}
\]

Substitution into (0.2) gives the exact provenance-excised identity

\[
 \boxed{
 \mathfrak D^\ddagger
 =L(g)+\mathbb B(a^\circ,g)+Q(g)
  +\mathbb B(b,f)+\mathbb B(b,g)+\mathbb B(f,g).
 }
 \tag{4.7}
\]

Every fixed literal token remains in \(a^\circ\); only the two actual
terminal tokens (3.3) are removed.

## 5. All-power vanishing of the inverse-\(Q\) raw load

### 5.1 Exact 184-row family

For a positive-\(Q\) stored letter \(e_{\nu k}\), let
\(m_{\nu k}\) be its incidence multiplier and put

\[
 w_{\nu k\delta}(i,d)=\operatorname{cvert}\bigl(
 m_{\nu k}E(Q_{\nu,<k})q_\nu^{d-1}c_\nu
 p_\nu^{i+\delta}r_\nu\bigr),
 \qquad \delta\in\{0,1\}.
 \tag{5.1}
\]

This is the corrected right-deck factor order.  There are 92 values of
\((\nu,k)\), hence 184 provenance copies.  If

\[
 R_s(v)=\sum_{o:s_o=s}\rho_o(v),
 \tag{5.2}
\]

linearity after integral aggregation gives

\[
 L(g^{(Q)})
 =\sum_{\nu,k,\delta}R_{s(e_{\nu k})}
   \bigl(w_{\nu k\delta}(i,d)\bigr).
 \tag{5.3}
\]

The integral signs are retained in the provenance certificate; modulo two
each is one.  If two rows collide, their equal \(R_s\)-values cancel in
(5.3), exactly as their integral coefficients cancel before activity.

### 5.2 Raw boundary-locality lemma

Let \(q\) be one fixed raw occurrence action and let \(v\) be a canonical
module word.  In the product \(qv\), every quotient cancellation involving
the moving word consumes one letter of the finite action side.  Therefore at
most \(|q|\) initial letters of \(v\) participate in the boundary cascade.
After that cascade the unconsumed suffix of \(v\) appends to a reduced
canonical prefix and creates no additional first-half raw event.

Consequently the ordered list of noncentral first-half event labels in

\[
 qvccv^{-1}q^{-1}=zccz^{-1}
 \tag{5.4}
\]

depends only on the finite action and the boundary prefix of \(v\).  Suppose
a cyclically reduced core \(R\) occurs as

\[
 v=A R^m B,
 \tag{5.5}
\]

with both displayed boundaries reduced, the next copies of \(R\) are
inserted after the existing \(m\) copies, and

\[
 |A|+m|R|>|q|+1.
 \tag{5.6}
\]

Then replacing \(m\) by \(m+t\), \(t\ge0\), cannot change the noncentral
event list.  If the central label is already strictly longer than every
label in that list, and its certified affine length increases with \(t\),
the equalities remain false.  Thus \(\rho_q(v)\) is constant for all
\(t\ge0\).

This is a finite-prefix theorem, not a finite-index or representative-value
assumption.  It uses the raw `tc`/`cT` action before canonicalization.

### 5.3 Sixteen disjoint cells and certificate

Use the exact partition

\[
 a\in\{0,1,2,\ge3\},\qquad
 n\in\{0,1,2,\ge3\}.
 \tag{5.7}
\]

The powered schemas imported from the approved inverse-\(Q\) certificate
use the common primitive cyclic cores of length eight.  On an unbounded
cell, the base value three already contains at least three primitive copies
before any future insertion.  The checker verifies (5.6) for the first
changing block of every row, occurrence slot, unbounded coordinate, and
cell: 1,472 primitive-core shield checks.

It also compares the **complete** noncentral event-label list, every
central-label equality bit, and \(\rho\) across the first pump transition.
At every pump base, the central label is strictly longer than every
noncentral label, and the imported affine template has positive length
coefficient in the pumped coordinate.  There are zero
observable-transition failures and zero central-length/equality failures.
The locality lemma then extends each base record to its whole unbounded
cell.

The exact counts among the 184 paired slot footprints are

| cell | one records | xor |
|---|---:|:---:|
| \(a=0\), every \(n\) cell | 84 | 0 |
| \(a=1\), every \(n\) cell | 80 | 0 |
| \(a=2\), every \(n\) cell | 80 | 0 |
| \(a\ge3\), every \(n\) cell | 80 | 0 |

All 184 selectors, both diagonal copies, and both raw occurrences of the
selected slot are present.  This proves (0.6).

Together with the approved \(L(g^{(0)})=0\), linearity gives

\[
 \boxed{L(g)=L(g^{(0)})+L(g^{(Q)})=0.}
 \tag{5.8}
\]

## 6. Exact remaining chronological quadratic term

Polarization gives

\[
 Q(g)=Q(g^{(0)})
 +\mathbb B(g^{(0)},g^{(Q)})+Q(g^{(Q)}).
 \tag{6.1}
\]

Using (2.6), (4.7), and (5.8), the complete remaining term is

\[
\boxed{
\begin{aligned}
 \mathfrak D^\ddagger={}&
 \mathbb B(a^\circ,g^{(0)})
 +\mathbb B(a^\circ,g^{(Q)})\\
 &+Q(g^{(0)})
 +\mathbb B(g^{(0)},g^{(Q)})
 +Q(g^{(Q)})\\
 &+\mathbb B(b,f)
 +\mathbb B(b,g^{(0)})
 +\mathbb B(b,g^{(Q)})\\
 &+\mathbb B(f,g^{(0)})
 +\mathbb B(f,g^{(Q)}).
\end{aligned}}
\tag{6.2}
\]

This is an exact ten-family ledger.  It contains no raw cochain term and no
comparison contributed by \(A_*\) as the old \(a_{ij}\)-factor.  The same
token coordinates can remain active in \(b\), \(f\), or \(g^{(Q)}\), and
therefore in their quadratic and bilinear terms.  The ledger retains:

1. all fixed-literal and nonterminal old activity in \(a^\circ\);
2. every slot-zero/path and path/path new--new comparison;
3. the complete inverse-\(Q\) \(j\)-increment in \(b\);
4. the complete diagonal increment, including its fixed \(P\)-rows and
   translated old rows, in \(f\); and
5. collision aggregation before every quadratic activity.

The known syntactic arity bound survives: after provenance expansion, every
monomial in (6.2) has at most one unbounded old repetition selector.  That
bound does not evaluate any family in (6.2).

## 7. Why the closed legs do not formally imply zero

The independent algebra checker represents polynomials over \(\mathbb F_2\)
as exact sets of squarefree monomials.  With six abstract tokens, two fixed
terminal tokens, independent raw weights, and independent chronological
kernels, it verifies byte-for-byte that

\[
 \mathfrak D
 +\mathbb B(a_*,g^{(0)})
 +\mathbb B(a_*,g^{(Q)})
 \tag{7.1}
\]

is exactly (4.7), and that splitting \(g=g^{(0)}+g^{(Q)}\) gives the
pre-(5.8) expansion of (6.2).  The respective abstract polynomial sizes are

\[
 282,\qquad20,\qquad262
 \tag{7.2}
\]

monomials for the original defect, terminal leg, and provenance-excised
remainder.

In particular the 262-monomial formal remainder is nonzero.  This is only a
no-go statement: the concrete ray may impose additional word identities
which cancel it.  A formal valuation of independent kernels is not an exact
ray chamber and is not a counterexample to covariance.

## 8. Exact proof boundary

### Proved

1. The two approved terminal values agree on both boundary chambers and
   cancel the complete old-terminal leg, (3.4).
2. The exact provenance-excised identity (4.7), including the distinction
   between scalar equality and removal of a certified record family.
3. The all-power raw inverse-\(Q\) cancellation \(L(g^{(Q)})=0\), using
   184 collision-safe rows, sixteen disjoint cells, primitive-core pumping,
   and raw boundary locality.
4. The disappearance of every raw term, (5.8).
5. The exact ten-family chronological quadratic remainder (6.2).
6. Formal quadratic algebra alone cannot make (6.2) zero.

### Not proved or refuted

1. \(\mathfrak D^\ddagger=0\) for all \(i\ge d\ge1\).
2. Any exact nonzero all-power chamber of the **complete**
   \(\mathfrak D^\ddagger\).
3. Positive-chamber augmented covariance.
4. The other covariance chambers \(d\le0\), the \(j\)-edge boundary values,
   diagonal cancellation, either edge law, or \(u_{ij}=\delta_{ij}\).

The earlier exact cell \((i,d)=(1,1)\) has \(\mathfrak D=0\).  It is a
semantic pin only and is not used in any all-power inference here.

### Next exact target

The raw part is now closed.  The next certificate should aggregate (6.2)
by actual collision fibers and exploit the one-old-selector arity bound.
The smallest structurally isolated quadratic family is

\[
 Q(g^{(0)})
 +\mathbb B(g^{(0)},g^{(Q)})+Q(g^{(Q)}),
 \tag{8.1}
\]

the complete new--new curvature term.  It should be normalized as one
aggregate; proving its constituents separately zero is neither expected nor
required.  Any nonzero result from (8.1) alone is still not a covariance
counterexample until the other seven chronological families in (6.2) are
included.

## 9. Reproduction and hashes

Artifacts:

```text
.scratch/period_two_residual_augmented_defect.md
.scratch/period_two_residual_augmented_defect_checker.py
.scratch/period_two_residual_augmented_defect_raw_checker.py
```

Commands, each bounded below 30 seconds:

```text
python3 .scratch/period_two_residual_augmented_defect_checker.py
python3 .scratch/period_two_residual_augmented_defect_raw_checker.py
```

The algebra checker prints

```text
PASS: exact GF(2) residual identities
original polynomial monomials: 282
terminal-leg polynomial monomials: 20
provenance-excised monomials: 262
```

The raw checker prints sixteen even record counts, zero observable-transition
failures, zero central-stability failures, and 1,472 primitive-core shield
checks.  Final byte hashes and the hostile-referee verdict are recorded after
the review below.

## 10. Hostile referee

### Initial verdict: REVISE

The independent referee found no critical issue and accepted the complete
all-power raw theorem.  One important wording defect remained: the draft
said that no remaining comparison was incident to either terminal token.
That was too broad.  The inverse-\(Q\) curvature can reactivate the same
token coordinates, so only the contribution of \(A_*\) as the **old**
\(a_{ij}\)-factor had been removed.  Section 6 now states that exact scope.

The referee also requested that the raw checker distinguish the combined
central-length/equality guard from an equality-only diagnostic.  The checker
now names and prints `central_stability_failures`.

The referee independently confirmed:

1. raw `tc`/`cT` typing and the live bridge semantics;
2. fiber-first recomputation on all sixteen cells, with 106 fibers, 72 odd
   fibers, and row xor equal to fiber xor equal to zero;
3. 9,200 independent raw-word/event-stream replays with no mismatch;
4. 1,472 primitive-core shields, with minimum strict shield margin 22;
5. 2,944 pump-base observables, with minimum central-length margin 117;
6. the all-power coverage of the sixteen-cell locality argument;
7. the counts 184/368/1,472 and all ten families in (6.2); and
8. the exact algebraic monomial counts 282/20/262.

### Focused rereview: APPROVE

**APPROVE — zero Critical, Important, or Minor findings remain.**  The
same referee verified both repairs and reran the bounded algebra and raw
checkers.  The load-bearing bytes approved before this review text was
appended had SHA-256 values

```text
memo             554a29d3892549ddd04e7247dba447a97f482dfb130d21c3113ff7e3161d5a25
algebra checker  aea2efdf31e2252956333c1c17a12004a80f100ab5ae180a24aabf44c895c413
raw checker      64b2477e7b9e63f121c04da7681291df7443f619c3ed3ba5e0442ca361cb5403
```

No Andrews--Curtis, stable Andrews--Curtis, covariance, edge-law, or unary
delta conclusion is added by the review.

### Controller mechanical gate and byte rereview

The controller removed two non-executable shebangs, unquoted postponed
`Poly` annotations, and sorted one standard-library import block.  No formula,
branch, record, or assertion changed.  Fresh replay retained the counts
282/20/262, all sixteen raw cells, zero failures, and 1,472 shields; Ruff
0.16.0 passed.  The same hostile referee reread the exact final checker bytes
and returned **APPROVE**, confirming that the changes are purely mechanical.
The approved post-repair hashes are

```text
memo before this controller append  7e11523c07612f021c4fa7073a802f6db3d51a14462112f81883c58fcd29dec2
algebra checker                     3b1160445902dd8f4455d10bd0c4d9d023294e36a0a6d4c6bc1244a49728d6a5
raw checker                         52412bf13d03b87cda8d041c0a1fa13fb1185e23d182aa5b7e850172d08ae8ef
```
