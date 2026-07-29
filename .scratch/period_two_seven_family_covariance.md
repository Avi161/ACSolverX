# Seven-family covariance: exact reduction and the closed (Q(b)) leg

Date: 2026-07-29

## 0. Status and theorem boundary

Work on the positive chamber

\[
 i\ge d\ge1,\qquad n=i-d\ge0,\qquad a=d-1\ge0.
 \tag{0.1}
\]

Let (A_{n,d}) be the complete endpoint activity of
(B+D_{i,j}), including all seventy fixed literal tokens, where
(j=n) and (i=n+d).  Put

\[
\begin{aligned}
 b_{n,d}&=A_{n,d-1}+A_{n,d},\\
 f_{n,d}&=A_{n+1,d}+A_{n,d},\\
 g_{n,d}&=b_{n+1,d}+b_{n,d}
          =f_{n,d-1}+f_{n,d}.
\end{aligned}
\tag{0.2}
\]

The approved new--new theorem gives (Q(g_{n,d})=0).  The certificate
accompanying this note proves the additional all-power identity

\[
 \boxed{Q(b_{n+1,d})=Q(b_{n,d})=1}
 \qquad(n\ge0, d\ge1),
 \tag{0.3}
\]

and, independently from the complete cross-pair ledger,

\[
 \boxed{\mathbb B(b_{n,d},b_{n+1,d})=0.}
 \tag{0.4}
\]

Consequently

\[
 \boxed{\mathbb B(b_{n,d},g_{n,d})=0.}
 \tag{0.5}
\]

This closes exactly the two displayed seven-family constituents

\[
 \mathbb B(b,g^{(0)})+\mathbb B(b,g^{(Q)})=0.
 \tag{0.6}
\]

The complete seven-family xor is still open.  No all-power zero proof and no
nonzero positive-chamber cell is asserted here.  In particular, the finite
seven-tuples replayed in Section 6 are semantic guards only.

## 1. Exact seven-family reduction

The approved residual and new--new theorems give

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
\tag{1.1}
\]

Here (a^\circ=A_{n,d}+a_*), and the approved old-terminal theorem is

\[
 \mathbb B(a_*,g)=0.
 \tag{1.2}
\]

Regrouping (1.1), with no term deleted, gives

\[
 \mathfrak D^\ddagger
 =\mathbb B(a^\circ,g)+\mathbb B(b,f)
  +\mathbb B(b,g)+\mathbb B(f,g).
 \tag{1.3}
\]

Let the complete endpoint cochain be

\[
 \Phi(x)=L(x)+Q(x),
 \tag{1.4}
\]

with the fixed-token activity implicit.  The four corners are

\[
 A_{n,d},\quad A_{n,d-1}=A_{n,d}+b,
 \quad A_{n+1,d}=A_{n,d}+f,
 \quad A_{n+1,d-1}=A_{n,d}+b+f+g.
 \tag{1.5}
\]

Polarization of (1.4), followed only by the approved identities

\[
 L(g)=0,\qquad Q(g)=0,\qquad \mathbb B(a_*,g)=0,
 \tag{1.6}
\]

proves

\[
\boxed{
 \mathfrak D^\ddagger
 =J_{n+1,d}+J_{n,d},
 \qquad
 J_{n,d}:=\Phi(A_{n,d-1})+\Phi(A_{n,d}).
}
\tag{1.7}
\]

Thus the complete target is exactly diagonal invariance of the (j)-edge
bit.  Equation (1.7) is an equivalence, not a covariance proof.

## 2. Why the (Q(b)) theorem is the correct closed subproblem

For every (n,d), polarization and (g=b_{n+1,d}+b_{n,d}) give

\[
 Q(g)=Q(b_{n+1,d})+Q(b_{n,d})
      +\mathbb B(b_{n,d},b_{n+1,d}).
 \tag{2.1}
\]

The all-power values (0.3), together with the independently evaluated cross
ledger (0.4), replay (2.1) as (0=1+1+0) on every symbolic cell.  Also

\[
 \mathbb B(b_{n,d},g)
 =\mathbb B(b_{n,d},b_{n+1,d}),
 \tag{2.2}
\]

because the chronological polarization is alternating.  This proves
(0.5) directly, without inferring it from a finite grid.

Expanding (J) instead gives

\[
 J_{n,d}
 =L(b_{n,d})+\mathbb B(A_{n,d},b_{n,d})+Q(b_{n,d}).
 \tag{2.3}
\]

The approved (L(g)=0) makes the first term invariant under
(n\mapsto n+1), and (0.3) makes the third term invariant.  Therefore the
complete seven-family target is now exactly equivalent to the single
old--new chronology lemma

\[
\boxed{
 \mathbb B(A_{n+1,d},b_{n+1,d})
 =\mathbb B(A_{n,d},b_{n,d})
 \qquad(n\ge0, d\ge1).
}
\tag{2.4}
\]

This is the smallest remaining exact lemma.  It includes collision-first
old activity, all fixed tokens, all six path components, literal occurrence
order, and decreasing chronology at negative occurrences.  The six
component paths undergo different powered right-deck normal forms, so the
current recurrence alone does not establish (2.4).

## 3. Symbolic certificate for (0.3)--(0.5)

Use the disjoint exhaustive partition

\[
 a\in\{0,1,2,\ge3\},\qquad
 n\in\{0,1,2,\ge3\}.
 \tag{3.1}
\]

The certificate imports the approved shared primitive phases for every
slot-zero corner and every inverse-(Q) path row.  On each of the sixteen
cells it separately constructs the unshifted edge (b_{n,d}) and shifted
edge (b_{n+1,d}).

For each edge and cell:

1. all 92 signed inverse-(Q) provenance rows are grouped by exact powered
   module-word equality;
2. integral coefficients are summed before parity;
3. the result is 53 collision fibers, 36 of them active;
4. the two slot-zero vertices contribute twelve tokens, while the 36 active
   path fibers contribute 72 tokens, for 84 total;
5. all \(\binom{84}{2}=3,486\) chronological pairs are evaluated, including
   increasing positive and decreasing negative same-occurrence order; and
6. every equality, strict order, first mismatch, chronology type, and pair
   bit is stored in deterministic digests.

Across both edges and all cells this is 111,552 complete quadratic pair
records.  The separate cross ledger evaluates all (84^2) comparisons per
cell, 112,896 in total.  It has no equal-coordinate exclusions and gives
(\mathbb B(b_{n,d},b_{n+1,d})=0) on every cell.

The powered templates prove that each comparison is constant on its whole
cell.  Representative evaluation is not used for that extension.  Sixteen
independent direct current replays at the cell bases reconstruct both edges
through the live anchored flow and match the symbolic (Q)-values.

## 4. (Q(b))-invariance does not formally imply the seven-family target

The distinction is algebraic, not a question of missing samples.  Let
(V=\mathbb F_2^4) and

\[
 Q(x)=x_1x_2+x_3x_4,
 \qquad
 \mathbb B(x,y)=x_1y_2+x_2y_1+x_3y_4+x_4y_3.
 \tag{4.1}
\]

Choose four formal corners by

\[
 A_{00}=e_2,\qquad b=0,\qquad f=0,\qquad g=e_1.
 \tag{4.2}
\]

Then (A_{01}=A_{11}=e_2) and (A_{12}=e_1+e_2).  The shifted edge is
(b'=b+g=e_1).  Hence

\[
 Q(g)=0,\qquad Q(b')=Q(b)=0,
 \qquad \mathbb B(b,g)=0,
 \tag{4.3}
\]

while

\[
 \mathbb B(A_{00},g)=1.
 \tag{4.4}
\]

Taking (L=0) and (a_*=0), all formal closed-leg hypotheses in (1.6)
hold, but the complete four-corner/seven-family xor is one.  Thus neither
polarization nor (Q(b))-invariance can replace the ray-specific
old--new lemma (2.4).

## 5. Exact proof boundary

### Proved

1. The exact regrouping of the approved seven families, (1.3).
2. The exact equivalence between the seven-family xor and
   (J_{n+1,d}+J_{n,d}), (1.7).
3. The all-power theorem (Q(b_{n,d})=Q(b_{n+1,d})=1), (0.3).
4. The independent all-pairs theorem
   \(\mathbb B(b_{n,d},b_{n+1,d})=0\), hence (0.5).
5. The reduction of the complete remaining target to (2.4).

### Open

1. The old--new chronology identity (2.4).
2. The complete seven-family xor and positive-chamber augmented covariance.
3. The other covariance chambers, boundary edge values, diagonal
   cancellation, both edge laws, and the unary delta identity.

A failure of (2.4) would refute this covariance/invariant route.  It would
not refute Andrews--Curtis or stable Andrews--Curtis.  No such failure is
produced here.  Conversely covariance alone would not prove the unary delta
identity without the separate boundary data.

## 6. Semantic guards only

The direct checker reproduces the approved first rectangle, including

\[
 (\mathscr C(a,g),\mathbb B(b,f),\mathbb B(b,g),\mathbb B(f,g))
 =(0,1,0,1).
 \tag{6.1}
\]

It also replays the ordered seven values

\[
 (0,0,1,0,0,1,0)\quad(d=1),
 \tag{6.2}
\]

and

\[
 (0,1,1,0,0,0,0)\quad(d\ge2)
 \tag{6.3}
\]

at the bounded cells exercised by the test.  Equations (6.2)--(6.3) are not
promoted to all-power constituent values.  Only (0.3)--(0.5) have the
complete powered proof in the manifest.

## 7. Reproduction and hashes

Artifacts:

```text
.scratch/period_two_seven_family_covariance.md
.scratch/period_two_seven_family_covariance_checker.py
.scratch/period_two_seven_family_covariance_manifest.json
.scratch/test_period_two_seven_family_covariance_checker.py
```

Commands:

```text
PYTHONDONTWRITEBYTECODE=1 python3 .scratch/period_two_seven_family_covariance_checker.py --check
PYTHONDONTWRITEBYTECODE=1 python3 .scratch/test_period_two_seven_family_covariance_checker.py
```

Expected final lines:

```text
"status": "PASS"
PASS: period-two seven-family covariance checker tests
```

SHA-256:

```text
checker   740d6c46cbbbeefdc466bcffdb3fd85fc376737cf5627bace1a958d3389b4aa1
manifest  f6f851841f49606ae32fde4e94d4c3be3eedaac881f359ae64237d3ca02a9b9a
test      43e2b939db1fe2c64eff4dc72aeb678b07409d78d060f3d681627bd8d46889f4
```
