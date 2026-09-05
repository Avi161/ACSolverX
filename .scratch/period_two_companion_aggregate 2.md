# Positive-chamber companion aggregate after the terminal crossing

Date: 2026-07-29

## 0. Status

**OPEN.**  On

\[
 i,j\geq0,\qquad d=i-j\geq1,
\]

the identity

\[
 \Omega_*(i,j)=1
 \tag{0.1}
\]

is neither proved nor refuted here.  No representative table, grid, census,
or rowwise-stabilization inference is used.

The maximal disjoint subaggregate closed here is the complete slot-zero
chronological load against the actual old terminal footprint.  Put

\[
 A_*:=\{(9,v^*_{ij}),(14,v^*_{ij})\},
 \qquad a_*:=1_{A_*},
 \tag{0.2}
\]

where the authoritative collision theorem gives

\[
 v^*_{ij}=\operatorname{cvert}
 \bigl(\texttt T\,\Gamma^{d-1}U^{i+1}\texttt{ct}\bigr),
 \tag{0.3}
\]

\[
 \Gamma=\texttt{ctcTTTctctcTTTctctcTTTct},\qquad
 U=\texttt{cTctttcTcTctttcTcTctttcT}.
 \tag{0.4}
\]

If \(g^{(0)}\) is the four-corner slot-zero curvature, this note proves

\[
 \boxed{\Theta_{*,0}(i,d):=\mathbb B(a_*,g^{(0)})=[d\geq2].}
 \tag{0.5}
\]

The certified terminal crossing \(\mathcal T_*=1\) is the occurrence pair
\((9,11)\) inside (0.5).  Hence all other slot-zero companions of that
crossing have xor

\[
 \boxed{\Theta_{*,0}+\mathcal T_*=[d=1].}
 \tag{0.6}
\]

Let

\[
 \mathfrak D
 =\sum g\rho+\mathbb B(a,g)+Q(g)
 +\mathbb B(b,f)+\mathbb B(b,g)+\mathbb B(f,g)
 \tag{0.7}
\]

be the full covariance defect, and remove the now-closed subaggregate by

\[
 \mathfrak D^\dagger:=\mathfrak D+\Theta_{*,0}.
 \tag{0.8}
\]

Since \(\Omega_*=\mathfrak D+\mathcal T_*\), (0.5) gives the exact reduced
identity

\[
 \boxed{
 \Omega_*(i,j)=[d=1]+\mathfrak D^\dagger(i,d),
 \qquad
 \Omega_*=1\iff \mathfrak D^\dagger=[d\ge2].
 }
 \tag{0.9}
\]

The smallest unresolved record family immediately adjacent to (0.5) is the
736-record inverse-\(Q\) path companion in Section 4.  It is fully
instantiated there with the corrected right-deck factor order, exact finite
domains, coefficient signs, chronology, collision interpretation, and
counting identity.  Its powered normal forms and all-power parity have not
been materialized, so no value is asserted for it.

Consequently positive-chamber augmented covariance, diagonal covariance of
the \(j\)-edge, both edge laws, and \(u_{ij}=\delta_{ij}\) remain open.
Nothing here proves or refutes Andrews--Curtis or stable Andrews--Curtis.

## 1. Audited semantics and parser typing

The following were read as one semantic package:

- `.scratch/period_two_complete_cochain_identity.md`;
- `.scratch/period_two_augmented_cut_covariance.md`;
- `.scratch/period_two_crossing_parity_induction.md`;
- `.scratch/period_two_raw_stream_manifest.md`, its generator, complete JSON,
  and approved review;
- `.scratch/period_two_anchored_ray_family.md`;
- the approved restricted powered-product normalizer and review; and
- the live lift, degree-two, phi4, source-flow, subgroup-rewrite,
  tree-flow, and literal-Hessian implementations cited by those files.

The canonical JSON contains 69,674 scalar leaves.  A complete scalar-path
traversal has SHA-256

```text
e67556aa69e4598612a4788210dddbe0e00cf8154130c5e3e74805da405280c0
```

and the package hashes are

```text
manifest   824d17adc0bc9b553d722eb627ee60f363451673237e366f6eb869acc6e058dd
generator  edd1f21fda1665b092447143b30d25e65f8c9a9cf2753a56ceb5da16db150bb1
```

All raw actions below use raw letter parsing followed by quotient reduction.
In particular

\[
 p=\texttt{tc},\qquad p^{-1}=\texttt{cT}.
 \tag{1.1}
\]

`lift.parse_quotient` is used only for module vertices.  It is never used for
\(p\), \(p^{-1}\), an occurrence prefix, or a transport action.  Forest
paths use the live anti-homomorphic `eval_path`.  Every occurrence action is
followed by `c_vertex`.  Same-occurrence chronology is increasing
module-vertex shortlex at a positive occurrence and decreasing shortlex at a
negative occurrence.

The following are fixed proved inputs, not replay inferences:

1. the complete slot-zero raw contribution to \(\sum g\rho\) is zero;
2. \(\mathcal T_*=1\) for every \(d\geq1\);
3. the actual merged old activity at \(v^*\) is one; and
4. the local slot-three raw identity at \(v^*\) and
   \(\operatorname{cvert}(p_1v^*)\) is zero.  This fixed local identity is
   not used below: \(\operatorname{cvert}(p_1v^*)\) is an ordinary left
   translate and is not identified with the right-deck shifted terminal
   coordinate in (4.2).

## 2. Collision-safe provenance expansion

For a current-coordinate parity vector \(x\), occurrence expansion is the
linear map

\[
 x_s(v)\longmapsto1_{A(s,v)},
 \qquad A(s,v)=\{(o,v):s_o=s\}.
 \tag{2.1}
\]

The current is first aggregated integrally:

\[
 K_s(v)=\sum_Rc_R[\,v_R=v\,],
 \qquad x_s(v)=K_s(v)\bmod2.
 \tag{2.2}
\]

Because \(\mathbb B(a_*,\cdot)\) is linear over \(\mathbb F_2\), substituting
(2.2) gives

\[
 \mathbb B(a_*,x)
 =\sum_R(c_R\bmod2)\,
  \mathbb B\bigl(a_*,1_{A(s_R,v_R)}\bigr).
 \tag{2.3}
\]

Equation (2.3) is an algebraic expansion of the already aggregated current;
it does not assign activity to virtual rows.  Equal provenance rows cancel
twice exactly as they do in (2.2).  This permits the linear terminal-leg
calculation below without weakening the mandatory aggregation rule.

Split

\[
 g=g^{(0)}+g^{(Q)},
 \tag{2.4}
\]

where \(g^{(0)}\) is the four slot-zero corners and

\[
 g^{(Q)}_s
 =\sum_{\nu=1}^6\epsilon_\nu(p_\nu-1)a_{\nu,ij}
   \mathsf E_s(Q_\nu^{-1}),\qquad s=2,3,4.
 \tag{2.5}
\]

The two partner-token provenance sets in (2.4) are disjoint.  Section 3
closes the first.  Section 4 gives the exact finite schema, but not an
all-power evaluation, for the second.

## 3. Complete slot-zero terminal companion

Put \(S=\Gamma^{-1}\).  For a corner \((\epsilon,\eta)\), put

\[
 e=d+\epsilon-\eta,
 \qquad n=i+\epsilon+1,
 \qquad Y(e,n)=p^{-1}\Gamma^ecS^nt.
 \tag{3.1}
\]

The four corners are

\[
 (0,0),(0,1),(1,1),(1,2).
 \tag{3.2}
\]

The two terminal labels are exactly

\[
\begin{aligned}
 X_9(i,d)&=\texttt{ctcTTct}\,\Gamma^{d-1}U^{i+1}\texttt{ct},
 &|X_9|&=24(i+d)+9,\\
 X_{14}(i,d)&=\Gamma^{d-1}U^{i+1}\texttt{ct},
 &|X_{14}|&=24(i+d)+2.
\end{aligned}
 \tag{3.3}
\]

For the six slot-zero occurrences define

\[
 Z_o(e,n)=\operatorname{cvert}(q_oY(e,n)).
 \tag{3.4}
\]

Write \(g_0=\texttt{ctcTTTct}\), so \(\Gamma=g_0^3\).  Direct maximal
boundary reduction gives the following complete disjoint normal forms.  In
the \(e\geq1\) column the displayed power is \(\Gamma^{e-1}\), so the
formula includes \(e=1\).

| \(o\) | \(q_op^{-1}\) | \(e=0\): \(Z_o\) | \(e\ge1\): \(Z_o\) | \(C_0,C_+\) |
|---:|---|---|---|---:|
| 3 | `eps` | `c` \(S^nt\) | \(\Gamma^e\)`c` \(S^nt\) | \(2,2\) |
| 4 | `ctcTTTct` | `ctcTTTctc` \(S^nt\) | \(g_0\Gamma^e\)`c` \(S^nt\) | \(10,10\) |
| 7 | `ctcTcTc` | `ctcTcT` \(S^nt\) | `ctcTTTTct` \(\Gamma^{e-1}\) `ctcTTTctctcTTTctc` \(S^nt\) | \(7,3\) |
| 8 | `ctcTTTTct` | `ctcTTTTctc` \(S^nt\) | `ctcTTTTct` \(\Gamma^{e-1}\) `ctcTTTctctcTTTctctcTTTctc` \(S^nt\) | \(11,11\) |
| 11 | `ctcTc` | `ctcT` \(S^nt\) | `cTTct` \(\Gamma^{e-1}\) `ctcTTTctctcTTTctc` \(S^nt\) | \(5,-1\) |
| 12 | `cTTct` | `cTTctc` \(S^nt\) | `cTTct` \(\Gamma^{e-1}\) `ctcTTTctctcTTTctctcTTTctc` \(S^nt\) | \(7,7\) |

Here

\[
 |Z_o(e,n)|=
 \begin{cases}
 24n+C_0(o),&e=0,\\
 24(e+n)+C_+(o),&e\ge1.
 \end{cases}
 \tag{3.5}
\]

Every displayed boundary is reduced.  These are literal all-power words,
not values at selected exponents.

The corners \((0,0),(1,1),(1,2)\) are longer than both terminal labels.
Only \((0,1)\) has the same \(24(i+d)\) slope.  Its constant decides every
comparison except

\[
 Z_3(d-1,i+1)=X_{14}(i,d),
 \tag{3.6}
\]

which is literal equality.  Equation (3.6) follows from

\[
 cS^nt=U^nct
 \tag{3.7}
\]

after the common prefix \(\Gamma^{d-1}\).

Using actual occurrence order gives the complete four-corner xor table:

| terminal occurrence | partner occurrence | \(d=1\) | \(d\ge2\) |
|---:|---:|:---:|:---:|
| 9 | 3 | 1 | 1 |
| 9 | 4 | 0 | 0 |
| 9 | 7 | 1 | 1 |
| 9 | 8 | 0 | 0 |
| 9 | 11 | 1 | 1 |
| 9 | 12 | 1 | 1 |
| 14 | 3 | 0 | 0 |
| 14 | 4 | 0 | 0 |
| 14 | 7 | 0 | 0 |
| 14 | 8 | 0 | 0 |
| 14 | 11 | 0 | 1 |
| 14 | 12 | 0 | 0 |

Occurrences 4, 8, and 12 remain negative occurrences.  Their atom blocks
are decreasing internally; their positions relative to terminal occurrences
9 and 14 are their literal AST positions.  Therefore

\[
 \boxed{\Theta_{*,0}=[d\ge2].}
 \tag{3.8}
\]

The row \((9,11)\) is \(\mathcal T_*=1\), proving (0.6).

## 4. Corrected inverse-\(Q\) path companion schema

The first draft incorrectly treated a right-deck translate as ordinary left
multiplication.  That formula is withdrawn completely.  The correct rows
are the terminal **positive** \(Q_\nu\)-copy and its diagonal shift.

For zero-based \(0\leq k<|Q_\nu|\), let \(e_{\nu k}\) be the stored letter,
\(m_{\nu k}\) its live incidence multiplier, and

\[
 E_{\nu k}=E(Q_{\nu,<k}).
 \tag{4.1}
\]

For \(\delta\in\{0,1\}\), define

\[
 w_{\nu k\delta}(i,d)=\operatorname{cvert}\bigl(
 m_{\nu k}E_{\nu k}q_\nu^{d-1}c_\nu
 p_\nu^{i+\delta}r_\nu\bigr).
 \tag{4.2}
\]

This factor order is the manifest's positive-\(Q\) row with \(h=d-1\).
It is not
\(\operatorname{cvert}(p_\nu^\delta mE(Q^{-1}_{<k})q_\nu^d\cdots)\).

The exact current identity is obtained before parity.  Appending
\(Q_\nu^{-1}\) retraces the terminal positive \(Q_\nu\)-copy, so

\[
 a_{\nu,ij}\mathsf E_s(Q_\nu^{-1})
 =-\sum_{k:s(e_{\nu k})=s}
   \iota_{\nu k}e_{w_{\nu k0}}.
 \tag{4.3}
\]

After diagonal translation and subtraction,

\[
 g^{(Q)}_s
 =\sum_{\nu,k:s(e_{\nu k})=s}
 \epsilon_\nu\iota_{\nu k}
 \bigl(e_{w_{\nu k0}}-e_{w_{\nu k1}}\bigr).
 \tag{4.4}
\]

Here \(\iota_{\nu k}\in\{\pm1\}\) is the live incidence sign.  Thus both
provenance copies have parity one, while their integral signs remain printed
in (4.4).  Equation (4.4) follows from the right-deck cocycle and holds for
all \(i\ge d\ge1\); an independent live-current guard is recorded in
Section 5.

For partner occurrence \(o'\), put

\[
 Z_{o',\nu k\delta}(i,d)=\operatorname{cvert}\bigl(
 q_{o'}m_{\nu k}E_{\nu k}q_\nu^{d-1}c_\nu
 p_\nu^{i+\delta}r_\nu\bigr).
 \tag{4.5}
\]

The action \(q_{o'}\) is raw quotient data.  It is parsed raw and only then
quotient-reduced as part of the complete product in (4.5).

For terminal occurrence \(o\in\{9,14\}\), define

\[
 \operatorname{pol}(o)\in\{+1,-1\}
 \tag{4.6a}
\]

to be its literal occurrence polarity, and define

\[
 \chi_{o,o'}(v,w)=
 \begin{cases}
 [\tau_o(v)<_{\rm sl}\tau_{o'}(w)],&o<o',\\
 [\tau_{o'}(w)<_{\rm sl}\tau_o(v)],&o'<o,\\
 [\tau_o(v)<_{\rm sl}\tau_o(w)],&o=o',\ \operatorname{pol}(o)=+1,\ v<_{\rm sl}w,\\
 [\tau_o(w)<_{\rm sl}\tau_o(v)],&o=o',\ \operatorname{pol}(o)=+1,\ w<_{\rm sl}v,\\
 [\tau_o(v)<_{\rm sl}\tau_o(w)],&o=o',\ \operatorname{pol}(o)=-1,\ v>_{\rm sl}w,\\
 [\tau_o(w)<_{\rm sl}\tau_o(v)],&o=o',\ \operatorname{pol}(o)=-1,\ w>_{\rm sl}v,\\
 0,&o=o',\ v=w.
 \end{cases}
 \tag{4.6}
\]

The first two lines use different occurrences, so their literal AST order
is fixed.  The next four lines explicitly encode increasing positive and
decreasing negative same-occurrence chronology.  Every label in (4.6) is
post-action `c_vertex` data.

The complete unresolved inverse-\(Q\) terminal companion is now the exact
finite xor

\[
 \boxed{
 \Theta_{*,Q}(i,d)=
 \sum_{\nu=1}^6\sum_{0\le k<|Q_\nu|}
 \sum_{\delta=0}^1\sum_{o\in\{9,14\}}
 \sum_{o'\in\mathcal O_{s(e_{\nu k})}}
 \chi_{o,o'}(v^*_{ij},w_{\nu k\delta}(i,d))
 \pmod2.
 }
 \tag{4.7}
\]

There are two occurrences in each of slots 2, 3, and 4.  Since

\[
 (|Q_1|,\ldots,|Q_6|)=(14,14,14,18,14,18),
 \tag{4.8}
\]

(4.7) has exactly

\[
 2\cdot2\cdot2\sum_\nu|Q_\nu|=736
 \tag{4.9}
\]

records.  This is a fixed finite family; there is no row-position variable
besides the bounded selector \(k\in\{0,\ldots,17\}\).

The exact all-power normal-form/counting problem for this smallest remaining
family is:

\[
 \boxed{
 \text{normalize every word in (4.5), including terminal `c`, and evaluate
 the 736 strict-order bits in (4.7) for all }i\ge d\ge1.
 }
 \tag{4.10}
\]

Equivalently, a Presburger certificate must emit disjoint cells \(C\) and
constants \(\varepsilon_{C,\nu k\delta oo'}\in\{0,1\}\) such that

\[
 \Theta_{*,Q}(i,d)
 =\sum_{\nu,k,\delta,o,o'}
   \varepsilon_{C,\nu k\delta oo'}\pmod2
 \qquad((i,d)\in C),
 \tag{4.11}
\]

with a reduced fixed-block word, affine length, exact first mismatch,
same-occurrence module order, coverage, and pairwise-empty-overlap record for
every \(\varepsilon\).  No such materialized table is claimed here.  In
particular, neither

\[
 \Theta_{*,Q}=[d\ge2]
 \tag{4.12}
\]

nor \(\mathbb B(a_*,g)=0\) is asserted.  Equation (4.12) is merely the value
that would cancel the proved slot-zero subaggregate on the whole old-terminal
leg; covariance could also involve nonterminal cancellations.

## 5. Fresh semantic guards

### 5.1 Correct path-current factor order

At \((i,j)=(1,0)\), the integral current reconstructed from (4.2)--(4.4)
was compared coefficientwise with

\[
 D_{2,2}-D_{2,1}-D_{1,1}+D_{1,0}.
 \tag{5.1}
\]

The three path slots returned

```text
slot 2: equal, support sizes 26 and 26
slot 3: equal, support sizes 40 and 40
slot 4: equal, support sizes 40 and 40
```

This is a bounded semantic guard on the factor order, not the proof of
(4.4); the all-power proof is the terminal-copy retracing identity (4.3)
and the right-deck recurrence.

### 5.2 One permitted full cell

Raw parsing printed `tc` and `cT`.  At the minimal positive cell
\((i,j)=(1,0)\), the four endpoint \(\Phi\)-bits at

\[
 (1,0),(1,1),(2,1),(2,2)
\]

were

\[
 (1,0,1,0).
 \tag{5.2}
\]

Hence \(\mathfrak D(1,0)=0\) and \(\Omega_*(1,0)=1\).  This zero defect is
not used to infer (0.1), periodicity, or a chamber value.

## 6. Exact remaining boundary after the closed subaggregate

The closed slot-zero terminal family has only the 48 comparisons in Section
3.  Removing it gives \(\mathfrak D^\dagger\), for which the exact target is
(0.9):

\[
 \mathfrak D^\dagger(i,d)=[d\ge2].
 \tag{6.1}
\]

The first disjoint part of \(\mathfrak D^\dagger\) is the explicit
736-record family (4.7).  The remaining source families are still the old
positive `P/C/Q` rows, the fixed inverse-\(Q\) rows in \(b,g\), the diagonal
increment rows in \(f\), the seventy fixed literal tokens, and the odd fixed
base rows.  A useful syntactic reduction survives hostile audit: because
\(b\) and \(g\) contain only fixed one-copy inverse-\(Q\) positions, every
provenance monomial in

\[
 \mathbb B(a,g),\quad Q(g),\quad
 \mathbb B(b,f),\quad\mathbb B(b,g),\quad\mathbb B(f,g)
 \tag{6.2}
\]

has at most one unbounded old repetition variable.  This is only an arity
bound.  The corresponding record index sets, collision polynomials, raw
events, and bounded-fiber counts have not been materialized and are not
called an explicit certificate here.

## 7. Exact theorem consequences

### Proved

1. The complete slot-zero old-terminal chronological subaggregate is
   \([d\ge2]\), (0.5)/(3.8), with all six occurrences and negative
   chronology retained.
2. The other slot-zero companions of the certified crossing have xor
   \([d=1]\), (0.6).
3. The full target is reduced exactly to (0.9)/(6.1).
4. The adjacent inverse-\(Q\) path problem is the corrected finite family
   (4.2)--(4.11), with 736 exact records and no unbounded row-position
   variable.
5. The broader remaining provenance algebra has at most one unbounded old
   repetition variable per monomial; no evaluation is inferred from that
   arity statement.

### Open

1. The all-power value of \(\Theta_{*,Q}\).
2. The value of \(\mathfrak D^\dagger\), hence \(\Omega_*=1\), on the
   positive chamber.
3. Positive-chamber augmented covariance and diagonal covariance of the
   \(j\)-edge.
4. The other \(d\le0\) covariance chambers, all edge-law boundary values,
   both edge laws, and \(u_{ij}=\delta_{ij}\).

An exact cell with \(\Omega_*\ne1\), equivalently a complete covariance
defect \(\mathfrak D\ne0\), would refute augmented covariance and therefore
the unary delta identity.  It would not refute Andrews--Curtis or stable
Andrews--Curtis.  No such cell is produced here.

## 8. Hostile referee: initial verdict and repairs

### Initial verdict: REJECT, repairable

The hostile referee accepted raw parser typing, the definition and actual
activity of \(A_*\), the collision-safe linear expansion, the split
\(g=g^{(0)}+g^{(Q)}\), and the slot-zero normal forms/table.  The referee
therefore accepted exactly (0.5), and no larger aggregate theorem.

The referee rejected three load-bearing claims in the first draft.

1. The draft asserted 736 all-power path normal forms while printing only
   cyclic-core lengths and grouped counts.  It emitted no per-row reduced
   words, terminal-`c` branches, first mismatches, coverage, or disjointness
   records.
2. Five zero-offset rows and grouped `N/Z/P/T` totals were aggregate bounded
   evidence, not the other 731 row certificates.  Same-occurrence module
   order and diagonal exclusion were not materialized.
3. The draft called implicit index sets \(\Lambda_0,\Lambda_1\) an exact
   remainder table.  It did not enumerate the \(Q(g)\) unary/pair records,
   collision terms, chronology, or coefficients.

A fresh independent check made during review found an even earlier error:
the first draft's path vertex prepended \(p_\nu^\delta\) as an ordinary left
action and used an inverse-\(Q\) prefix.  This contradicted the live
right-deck current in every path slot.

All claims depending on that formula and on the unmaterialized table are
withdrawn.  Section 4 now derives the correct row from the terminal positive
\(Q\)-copy, keeps \(p_\nu^{i+\delta}\) in the right-deck factor position,
prints the integral signs, gives the exact 736-record xor, and labels its
normal forms and all-power parity open.  Section 6 retains only the accepted
one-variable syntactic arity bound and no longer calls implicit Cartesian
products an explicit certificate.

### Focused rereview: APPROVE

**APPROVE — zero remaining load-bearing findings.**  The same hostile
referee checked the corrected draft (pre-append SHA-256
`439f16f671f761430e81486cb344e34f782c6795f85dfc4a90fef6381af045f6`)
against the live implementation.  In particular, the referee confirmed the
rowwise equivalence of the terminal-positive-\(Q\) and reversed-inverse-\(Q\)
parameterizations with opposite incidence sign, the integral signs in
(4.3)--(4.4), the total chronology in (4.6), the 736-record count, the
slot-zero all-power theorem, the reduced-defect algebra, and the restricted
one-variable syntactic arity claim in Section 6.

The approved theorem boundary is exactly: (i)
\(\Theta_{*,0}=[d\ge2]\); (ii) the other slot-zero companions xor to
\([d=1]\); (iii) \(\Omega_*=[d=1]+\mathfrak D^\dagger\); (iv) the
correct 736-record schema is an exact remaining obligation; and (v) each
remaining provenance monomial has at most one unbounded old repetition
index.  The values of \(\Theta_{*,Q}\), \(B(a_*,g)\),
\(\mathfrak D^\dagger\), and \(\Omega_*\), together with covariance,
the edge laws, and unary \(\delta\), remain open.
