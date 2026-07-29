# Complete cochain identity for the first period-two unary ray

Date: 2026-07-29

## 0. Theorem status

**OPEN.**  The exact augmented-covariance identity

\[
 \boxed{
 \mathscr C(a,g)
 =\mathbb B(b,f)+\mathbb B(b,g)+\mathbb B(f,g)
 }
 \tag{0.1}
\]

is neither proved nor refuted here.  The symbols \(a,b,f,g\) are exactly
the four actual-merged activity increments in (3.1) below.  All sixteen
correction occurrences, integral coefficient collisions before parity,
negative-occurrence chronology, raw occurrence prefixes, raw mirror weights,
fixed events, and new--new terms remain present.

This note advances the exact boundary in four ways.

1. It pulls the complete cochain back to the six \(P/C/Q\) all-power path
   families and distinguishes the tautological potential \(\Phi\) on the
   **full activity state** from the desired reduced augmented-state
   coboundary.  The latter has not been constructed.
2. It proves the complete slot-zero raw-mirror contribution of the
   four-source curvature \(g_0\) is zero for every \(i,j\), by a finite
   all-power prefix argument.
3. It gives one exact all-power normal-form chamber for a real source row,
   `W:nu1:Q:0:o+1`, and proves that its four-corner chronological load is a
   single terminal crossing \([h=i-j-1]\).
4. It proves that the terminal row has actual merged activity one, then
   isolates the first genuinely missing instantiated datum: the complete
   raw/new companion aggregate which would have to cancel that certified
   crossing.  The generic powered-product normalizer proves that the
   relevant equality and order loci are effectively Presburger, but it does
   not emit this aggregate or an all-power stabilization certificate.

One corrected constant-size rectangle is zero.  It is a semantic pin only
and supplies no all-index evidence.

Consequently the \(d<0,d=0,d=1,d>1\) values of the \(j\)-edge, the diagonal
boundary, both edge laws, and \(u_{ij}=\delta_{ij}\) remain open.  Nothing in
this note implies Andrews--Curtis or stable Andrews--Curtis.

## 1. Authoritative conventions and the raw-prefix typing trap

The semantics are those of the following files, read together:

- `experiments/stable_ac/depth4_period_two_phi_infinity_hessian_certificate.py`;
- `experiments/stable_ac/depth4_period_two_subgroup_rewrite_certificate.py`;
- `experiments/stable_ac/depth4_period_two_source_flow_certificate.py`;
- `experiments/stable_ac/depth4_period_two_tree_flow_factorization_certificate.py`;
- `.scratch/period_two_raw_stream_manifest_generator.py` and its approved
  manifest/review; and
- the primitive all-power proof in Section 5 of
  `.scratch/period_two_anchored_ray_family.md`.

Put

\[
 p=\texttt{tc},\qquad
 g_*=\texttt{ctcTTTct},\qquad
 \Gamma=g_*^3,\qquad S=\Gamma^{-1},
 \tag{1.1}
\]

and

\[
 y_{ij}=p^{-1}\Gamma^{i-j}c\Gamma^{-(i+1)}t,
 \qquad D_{ij}=H(y_{ij}).
 \tag{1.2}
\]

Here \(p\) and every \(q_o\) below are **raw quotient group elements**.
Their terminal `c` must be retained.  In particular,

\[
 p^{-1}=\texttt{cT}.
 \tag{1.3}
\]

The helper `lift.parse_quotient` is a module-vertex parser: it applies
`c_vertex` and therefore sends the literal `tc` to `t`.  It is inadmissible
for parsing \(p\), a transport action, or an occurrence prefix.  The correct
path is raw letter parsing followed by `quotient_reduce`, exactly as in
`period_two_raw_stream_manifest_generator.parse_raw` and
`phi_infinity_hessian_certificate._parse_quotient_word`.

This distinction was audited at every interface used here:

- \(p\) and the sixteen \(q_o\) use raw parsing and quotient reduction;
- the forest strings \(P_\nu,C_\nu,Q_\nu\) use the live anti-homomorphic
  endpoint evaluation `eval_path`, never `parse_quotient`;
- roots, source endpoints, and current support labels are module vertices
  and correctly use `c_vertex`; and
- the raw bridge receives the unreplaced \(q_o\), then applies `c_vertex`
  only to emitted event labels.

The literal occurrence table is

| \(o\) | slot \(s_o\) | polarity | raw \(q_o\) |
|---:|---:|:---:|---|
| 1 | 2 | + | `eps` |
| 2 | 1 | + | `tc` |
| 3 | 0 | + | `tc` |
| 4 | 0 | - | `ctcTTTcttc` |
| 5 | 1 | - | `ctcTctt` |
| 6 | 2 | - | `ctcTcTctc` |
| 7 | 0 | + | `ctcTcTctc` |
| 8 | 0 | - | `ctcTTTTcttc` |
| 9 | 3 | + | `ctcTTctt` |
| 10 | 1 | + | `ctcTctc` |
| 11 | 0 | + | `ctcTctc` |
| 12 | 0 | - | `cTTcttc` |
| 13 | 1 | - | `tt` |
| 14 | 3 | - | `t` |
| 15 | 4 | + | `t` |
| 16 | 4 | - | `eps` |

The six path triples are

| \(\nu\) | \(P_\nu\) | \(C_\nu\) | \(Q_\nu\) |
|---:|---|---|---|
| 1 | `aBgAgAggABBgAb` | `aBgAgAggABBgAb` | `GaGaGbABaGbbaG` |
| 2 | `AgABBgAbaBgAgAga` | `AgABBgAbaBgAgAgBaGb` | `baGGaGaGbABaGb` |
| 3 | `aGbAAGaGbAAGaGbAAG` | `aGbAAGaGbAAGaGbAAG` | `baGGaGaGbABaGb` |
| 4 | `aGbAAGaGbAAGaGbAAG` | `aGbAAGaGbAAGaGbAAGaG` | `gAbaGGaGaGbABaGbaG` |
| 5 | `aGbAAGaGbAAGaGbAAG` | `aGbAAGaGbAAGaGbAAGbaG` | `GaGaGbABaGbbaG` |
| 6 | `AgABBgAbaBgAgAga` | `AgABBgAbaBgAgAgBaGbaG` | `gAbaGGaGaGbABaGbaG` |

Writing \(E\) for the live anti-homomorphic forest endpoint map, the old
paths are

\[
 W_{\nu,ij}=\operatorname{red}(P_\nu^iC_\nu Q_\nu^{i-j}),
 \qquad
 a_{\nu,ij}=[W_{\nu,ij}],
 \tag{1.4}
\]

with right-deck composition acting on the rightmost current first.

For later formulas put

\[
 p_\nu=E(P_\nu),\qquad c_\nu=E(C_\nu),
 \qquad q_\nu=E(Q_\nu),
 \tag{1.5}
\]

and use the component roots

\[
 (r_1,\ldots,r_6)
 =(\texttt{ct},\mathrm{eps},\texttt{ct},\texttt{ct},
   \texttt{ct},\mathrm{eps}).
 \tag{1.6}
\]

The live incidence data for a forest letter \(e\) are

| \(e\) | slot \(s(e)\) | incidence | multiplier \(m_e\) |
|:---:|---:|---:|---|
| `A` | 4 | \(-1\) | \(1\) |
| `a` | 4 | \(+1\) | \(E(\texttt a)\) |
| `B` | 2 | \(+1\) | \(1\) |
| `b` | 2 | \(-1\) | \(E(\texttt b)\) |
| `G` | 3 | \(-1\) | \(\texttt T\) |
| `g` | 3 | \(+1\) | \(\texttt T\,E(\texttt g)\) |

Products in the last column are quotient products in the displayed order.

## 2. The complete endpoint cochain

Let \(\mathscr P\) be the fixed token universe from the approved crossing
contraction.  It contains every fixed raw Schreier event and every
correction token \((o,v)\).  For a correction token put

\[
 \ell(o,v)=\tau_o(v)=\operatorname{cvert}(q_ov),
 \qquad r(o,v)=\rho_o(v),
 \tag{2.1}
\]

where the all-word raw bridge gives

\[
 \operatorname{red}(q_ovccv^{-1}q_o^{-1})=zccz^{-1}
 \tag{2.2}
\]

and, if \(\alpha_1,\ldots,\alpha_m\) are the chronological first-half
Schreier labels of \(z\),

\[
 \rho_o(v)=\sum_{r=1}^m[\alpha_r\ne\tau_o(v)]\pmod2.
 \tag{2.3}
\]

Fixed tokens have \(r=0\).  The chronology is literal AST order, increasing
shortlex within a positive correction occurrence, and decreasing shortlex
within a negative occurrence.  For distinct tokens define

\[
 \xi(p,q)=
 \begin{cases}
 [\ell(p)<_{\rm sl}\ell(q)],&p\triangleleft q,\\
 [\ell(q)<_{\rm sl}\ell(p)],&q\triangleleft p.
 \end{cases}
 \tag{2.4}
\]

For a complete integral current \(C=B+D\), aggregate every coefficient at
\((s,v)\) integrally and only then put

\[
 a_C(o,v)=C_{s_o}(v)\pmod2.
 \tag{2.5}
\]

Every fixed token has activity one.  On the zero-linear residual domain the
complete endpoint bit is the quadratic form

\[
 \Phi(a)=\sum_pa(p)r(p)
 +\sum_{\{p,q\}}a(p)a(q)\xi(p,q).
 \tag{2.6}
\]

Set

\[
\begin{aligned}
 \mathbb B(u,v)
 &=\sum_{\{p,q\}}\xi(p,q)
   \bigl(u(p)v(q)+v(p)u(q)\bigr),\\
 Q(d)&=\sum_{\{p,q\}}d(p)d(q)\xi(p,q),\\
 \mathscr C(a,d)
 &=\Phi(a+d)+\Phi(a)
  =\sum_pd(p)r(p)+\mathbb B(a,d)+Q(d).
\end{aligned}
 \tag{2.7}
\]

This retains fixed--new, old--new, and new--new comparisons, as well as the
raw mirror term.

## 3. Exact four-corner variables and identity

After integral aggregation and occurrence expansion, define

\[
\begin{aligned}
 a&=a_{B+D_{ij}},\\
 b&=a_{B+D_{i,j+1}}+a_{B+D_{ij}},\\
 f&=a_{B+D_{i+1,j+1}}+a_{B+D_{ij}},\\
 g&=a_{B+D_{i+1,j+2}}+a_{B+D_{i+1,j+1}}
   +a_{B+D_{i,j+1}}+a_{B+D_{ij}}.
\end{aligned}
 \tag{3.1}
\]

The underlying integral currents are

\[
\begin{aligned}
 \widetilde b_0&=e_{y_{i,j+1}}-e_{y_{ij}},
 &\widetilde b_1&=0,\\
 \widetilde b_s
 &=\sum_\nu\epsilon_\nu a_{\nu,ij}
      \mathsf E_s(Q_\nu^{-1}),\\[1mm]
 \widetilde f_0&=e_{y_{i+1,j+1}}-e_{y_{ij}},
 &\widetilde f_1&=0,\\
 \widetilde f_s
 &=\sum_\nu\epsilon_\nu\bigl(
      \mathsf E_s(P_\nu)+(p_\nu-1)x^s_{\nu,ij}\bigr),\\[1mm]
 \widetilde g_0
 &=e_{y_{i+1,j+2}}-e_{y_{i+1,j+1}}
   -e_{y_{i,j+1}}+e_{y_{ij}},
 &\widetilde g_1&=0,\\
 \widetilde g_s
 &=\sum_\nu\epsilon_\nu(p_\nu-1)a_{\nu,ij}
      \mathsf E_s(Q_\nu^{-1}),\qquad s=2,3,4.
\end{aligned}
 \tag{3.2}
\]

The signs are \((1,-1,1,1,-1,-1)\), and
\(p_\nu=[P_\nu]\).  The doubled anchors are retained integrally in each
endpoint and disappear only after aggregation and parity.

Endpoint reversal and quadratic expansion give

\[
\begin{aligned}
 J_{ij}&=\mathscr C(a,b),\\
 J_{i+1,j+1}&=\mathscr C(a+f,b+g),\\
 J_{i+1,j+1}+J_{ij}
 &=\mathscr C(a,g)+\mathbb B(b,f)
   +\mathbb B(b,g)+\mathbb B(f,g).
\end{aligned}
 \tag{3.3}
\]

Thus (0.1) is exactly equivalent to diagonal covariance of \(J\).

## 4. Pullback to the six path families

The manifest makes the cochain pullback explicit.  For a stored forest
letter \(e\), let \(m_e\) be its live incidence multiplier and let
\(s(e)\in\{2,3,4\}\) be its slot.  For a \(P\)-row at position \(k\),

\[
 v^P_{\nu,k}(i,h)
 =\operatorname{cvert}\bigl(
   m_eE(P_{\nu,<k})p_\nu^h r_\nu\bigr),
 \qquad 0\le h<i.
 \tag{4.1}
\]

For a \(C\)-row,

\[
 v^C_{\nu,k}(i)
 =\operatorname{cvert}\bigl(
   m_eE(C_{\nu,<k})p_\nu^i r_\nu\bigr).
 \tag{4.2}
\]

For a positive \(Q\)-row,

\[
 v^{Q,+}_{\nu,k}(i,j,h)
 =\operatorname{cvert}\bigl(
  m_eE(Q_{\nu,<k})q_\nu^h c_\nu p_\nu^i r_\nu\bigr),
 \quad 0\le h<i-j,
 \tag{4.3}
\]

and, with \(\bar Q_\nu=Q_\nu^{-1}\) and the literal reversed position
\(\bar k\),

\[
 v^{Q,-}_{\nu,k}(i,j,h)
 =\operatorname{cvert}\bigl(
  m_{\bar e}E(\bar Q_{\nu,<\bar k})q_\nu^{-h}
  c_\nu p_\nu^i r_\nu\bigr),
 \quad 0\le h<j-i.
 \tag{4.4}
\]

These are the generator's exact factor orders.  Every row also carries its
integral source sign and incidence sign.  For \(s\in\{2,3,4\}\) and a
module vertex \(v\), the actual coefficient is not one row but the collision
fiber

\[
 K_s(i,j;v)
 =B_s(v)+2A_s(v)
  +\sum_{R\in\mathcal M_s}
    \sum_{z\in D_R(i,j)}c_R[\,v_R(i,j,z)=v\,],
 \tag{4.5}
\]

where \(\mathcal M_s\) is the finite manifest row set in slot \(s\),
\(D_R\) is the exact row domain, and \(c_R\) is the integral row
coefficient.  Only

\[
 \kappa_s(i,j;v)=K_s(i,j;v)\pmod2
 \tag{4.6}
\]

is inserted into the activity (2.5).  Formula (4.5), not a virtual
row-by-row activity, is the coefficient used in every \(\rho\) and \(\xi\)
term.  Slot zero instead has \(D_{ij,0}=e_{y_{ij}}+2e_T\), and slot one is
zero.

### 4.1 What potential exists

On the full activity cube, \(\Phi\) is already the exact potential.  For a
current-coordinate footprint

\[
 A(s,v)=\{(o,v):s_o=s\},
 \tag{4.7}
\]

its coboundary is

\[
\begin{aligned}
 \lambda_a(s,v)
 ={}&\sum_{p\in A(s,v)}r(p)
 +\sum_{\{p,q\}\subset A(s,v)}\xi(p,q)\\
 &+\sum_{p\in A(s,v)}
   \sum_{q\notin A(s,v)}a(q)\xi(p,q),
\end{aligned}
 \qquad
 \Phi(a+1_{A(s,v)})+\Phi(a)=\lambda_a(s,v).
 \tag{4.8}
\]

Processing the six source paths leaf by leaf therefore integrates the
complete \(\rho+\xi\) load exactly.

This is not the desired covariance potential.  It lives on the full state
\((a,\text{raw chronology})\).  A proposed reduced state

\[
 (\text{raw prefix},\ \text{canonical vertex},\
   \text{first-half kernel coordinate},\ \text{chronology cut})
 \tag{4.9}
\]

does not yet have a proved transition map that determines the collision
fiber (4.5), the old activity in the last line of (4.8), and every later
negative-occurrence comparison.  Adding \(a\) to (4.9) makes (4.8) true but
returns to the tautological full-state potential.  No reduced-state
identification between the initial and terminal states of the diagonal
translation has been proved.

### 4.2 Why quadratic polarization does not close the square

The third polarization of a quadratic form vanishes for three independent
additive increments.  Here the activity map itself has curvature \(g\):

\[
 a_{i+1,j+2}+a_{i+1,j+1}+a_{i,j+1}+a_{ij}=g\ne0.
 \tag{4.10}
\]

Already \(\widetilde g_0\) has four pairwise distinct ray vertices.  Hence
the four-corner defect is not a third polarization of \(\Phi\); its unary
curvature term is \(\mathscr C(a,g)\).  Equation (3.3), rather than generic
quadraticity, is the exact polarization statement.

## 5. A closed all-power subcalculation: the slot-zero raw term

This section uses only the six slot-zero occurrence prefixes

\[
 \texttt{tc},\ \texttt{ctcTTTcttc},\
 \texttt{ctcTcTctc},\ \texttt{ctcTTTTcttc},\
 \texttt{ctcTctc},\ \texttt{cTTcttc}.
 \tag{5.1}
\]

For

\[
 Y(e,n)=p^{-1}\Gamma^e cS^nt,
 \qquad n\ge1,
 \tag{5.2}
\]

the canonical word begins `cTT` when \(e<0\), and `cTc` when
\(e\ge0\).  Every prefix in (5.1) ends in `c`.  The maximal-overlap branch
therefore reduces to a finite boundary cascade.  Scanning that cascade by
the literal `_KernelStream` rule gives the following all-power values:

| raw prefix \(q_o\) | \(e<0\) | \(e=0\) | \(e>0\) |
|---|:---:|:---:|:---:|
| `tc` | 1 | 1 | 1 |
| `ctcTTTcttc` | 0 | 1 | 1 |
| `ctcTcTctc` | 1 | 0 | 1 |
| `ctcTTTTcttc` | 0 | 1 | 1 |
| `ctcTctc` | 1 | 0 | 1 |
| `cTTcttc` | 0 | 1 | 1 |

The proof is finite but not sampled.  The complete first-half event-label
lists in the three chambers are:

| raw prefix | \(e<0\) | \(e=0\) | \(e>0\) |
|---|---|---|---|
| `tc` | `t` | `t` | `t` |
| `ctcTTTcttc` | `ctcTTTctt`, `ctcTTT`, `ct`, `eps` | `ctcTTTctt` | `ctcTTTctt` |
| `ctcTcTctc` | `ctcTcTct` | `ctcTcTct`, `ctcTcT` | `ctcTcTct`, `ctcTcT`, `ctcT` |
| `ctcTTTTcttc` | `ctcTTTTctt`, `ctcTTTT` | `ctcTTTTctt` | `ctcTTTTctt` |
| `ctcTctc` | `ctcTct` | `ctcTct`, `ctcT` | `ctcTct`, `ctcT`, `ct` |
| `cTTcttc` | `cTTctt`, `cTT` | `cTTctt` | `cTTctt` |

To derive the lists, cancel the maximal terminal `t`/`T` overlap between
the fixed prefix and the initial `cTT` or `cTc` segment of \(Y(e,n)\), then
apply the positive-`c` emission rule at each exposed `cc` boundary.  The
fixed prefix is exhausted before the remaining power tail is reached.  That
remainder is a canonical quotient tail and creates no further first-half
event.  The central label contains at least one full \(S\)-tail and is
strictly longer than every fixed label in the table, so every listed event
is noncentral.  Taking the parity of each displayed list gives the preceding
\(\rho\)-table and proves (5.3)--(5.5).

Thus the entire slot-zero occurrence footprint satisfies

\[
 R_0(Y(e,n)):=\sum_{o:s_o=0}\rho_o(Y(e,n))=[e<0].
 \tag{5.3}
\]

The four vertices in \(g_0\) have exponents

\[
 d,\quad d-1,\quad d,\quad d-1,
 \qquad d=i-j.
 \tag{5.4}
\]

Therefore

\[
 \boxed{
 \sum_{p\in\operatorname{supp}(g_0)}g_0(p)r(p)
 =2[d<0]+2[d-1<0]=0.
 }
 \tag{5.5}
\]

This closes only the slot-zero part of \(\sum g\rho\).  The translated
slot-two, slot-three, and slot-four path loads remain, as do all \(\xi\)
terms.

## 6. One exact all-power crossing chamber

Consider the manifest row

```text
W:nu1:Q:0:o+1
```

It is the first `G` position of a positive \(Q_1\)-copy.  Its exact domain
and data are

\[
 i,j\ge0,\qquad d=i-j\ge1,\qquad 0\le h<d,
 \tag{6.1}
\]

slot three, integral coefficient \(-1\), and incidence multiplier `T`.
The live endpoint words are

\[
 \Gamma=\texttt{ctcTTTctctcTTTctctcTTTct},
 \qquad
 U=\texttt{cTctttcTcTctttcTcTctttcT},
 \tag{6.2}
\]

both cyclically reduced of length 24.  Since \(P_1=C_1\), the row's module
vertex is

\[
 v_{i,h}=\operatorname{cvert}
 \bigl(\texttt{T}\,\Gamma^hU^{i+1}\texttt{ct}\bigr).
 \tag{6.3}
\]

At occurrence 9, whose raw action is `ctcTTctt`, the central label is the
already reduced word

\[
 X_{i,h}
 =\texttt{ctcTTct}\,\Gamma^hU^{i+1}\texttt{ct},
 \qquad |X_{i,h}|=24(i+h)+33.
 \tag{6.4}
\]

Now pair it with each slot-zero corner of \(g_0\) at occurrence 11, whose
raw action is `ctcTctc`.  For a corner \((\epsilon,\eta)\) put

\[
 e=d+\epsilon-\eta,qquad n=i+\epsilon+1,
 \qquad
 Z_{\epsilon\eta}
 =\operatorname{cvert}(\texttt{ctcTctc}\,y_{i+\epsilon,j+\eta}).
 \tag{6.5}
\]

The four corners are
\((0,0),(0,1),(1,1),(1,2)\).  Put

\[
\begin{aligned}
 A&=\texttt{cTTctctcTTTctctcTTTctc},\\
 R&=\texttt{tcTTTctctcTTTctctcTTTctc},\\
 S&=\texttt{TctttcTcTctttcTcTctttcTc}.
\end{aligned}
 \tag{6.6}
\]

The complete reduced outputs are

\[
 Z_{\epsilon\eta}=
 \begin{cases}
  \texttt{ctcT}\,S^n\texttt{t},&e=0,\\
  A R^{e-1}S^n\texttt{t},&e\ge1.
 \end{cases}
 \tag{6.7}
\]

There is no hidden terminal-`c` deletion in (6.7); both words end in `t`.
All displayed boundaries are reduced.  Their lengths are

\[
 |Z_{\epsilon\eta}|=
 \begin{cases}
  24n+5,&e=0,\\
  24(e+n)-1,&e\ge1.
 \end{cases}
 \tag{6.8}
\]

Occurrence 9 precedes occurrence 11, so the relevant chronological kernel
is \([X_{i,h}<_{\rm sl}Z_{\epsilon\eta}]\).  Length comparison alone gives

| corner | \(e\) | exact comparison |
|---|---:|:---:|
| \((0,0)\) | \(d\) | 1 |
| \((0,1)\) | \(d-1\) | \([h\le d-2]\) |
| \((1,1)\) | \(d\) | 1 |
| \((1,2)\) | \(d-1\) | 1 |

The formula for \((0,1)\) includes \(d=1\): then \(e=0\), the only row
index is \(h=0\), and the comparison is false.  Hence the four-corner xor
from this old row against these four new slot-zero tokens is

\[
 \boxed{
 \sum_{(\epsilon,\eta)}
 [X_{i,h}<_{\rm sl}Z_{\epsilon\eta}]
 =[h=d-1].
 }
 \tag{6.9}
\]

This is a genuine all-power chamber proof, of the same kind as the primitive
\(P_{ij}=\delta_{ij}\) proof.  It also shows why representative values do
not close (0.1): one literal source row has a persistent terminal crossing
on every positive diagonal.

## 7. The certified terminal token and the smallest remaining datum

Equation (6.9) is initially a row statement.  Let

\[
 v^*_{ij}:=v_{i,d-1}
 =\operatorname{cvert}
 \bigl(\texttt{T}\,\Gamma^{d-1}U^{i+1}\texttt{ct}\bigr),
 \qquad d=i-j\ge1.
 \tag{7.1}
\]

Its actual merged activity can be determined without a generic equality
table.

### 7.1 The collision fiber is one

The target is the `G`-edge based at the prefix

\[
 P_1^iC_1Q_1^{d-1}
 \tag{7.2}
\]

of the reduced geodesic \(P_1^iC_1Q_1^d\).  Every boundary in that word is
freely reduced, so the path traverses no edge twice.  The only other path
families with root `ct` are \(\nu=3,4,5\).  Their reduced geodesics begin
`aG`, whereas the \(\nu=1\) geodesic begins `aB`.  After the second edge
the paths lie in different branches of a tree and cannot reconverge.
Families \(\nu=2,6\) start in the other tree component.

The target module word has

\[
 |v^*_{ij}|=24(i+d)+3\ge51,
 \tag{7.3}
\]

so it is neither fixed slot-three base vertex `eps` nor `TTct`.  The anchor
current \(2A_3\) is even.  Consequently the sole odd integral contribution
at \(v^*_{ij}\) is the displayed row, of coefficient \(-1\), and

\[
 \boxed{
 \kappa_*(i,j)
 =(B_3+D_{ij,3})(v^*_{ij})\bmod2=1.
 }
 \tag{7.4}
\]

Thus (6.9) is an actual token contribution, not merely a virtual row
contribution:

\[
 \boxed{\mathcal T_*(i,j)=1\qquad(d\ge1).}
 \tag{7.5}
\]

It refutes termwise stabilization of the old/new cut load.  It does not
refute the complete covariance identity, whose other terms may cancel it.

### 7.2 The local slot-three raw companion vanishes

For slot three put

\[
 R_3(v)=\rho_9(v)+\rho_{14}(v),
 \tag{7.6}
\]

with raw actions `ctcTTctt` and `t`.  The word \(v^*_{ij}\) begins `Tc`.
The first action has exactly one terminal `t`/`T` overlap and the second is
exhausted by the same overlap; in both cases the remaining first half is a
canonical quotient word and emits no event.  Since \(p_1=U\), the translated
word \(\operatorname{cvert}(p_1v^*_{ij})\) begins `cT`.  Neither action has
a boundary overlap there, and again the concatenation is canonical.  Hence

\[
 \boxed{
 R_3(v^*_{ij})
 =R_3(\operatorname{cvert}(p_1v^*_{ij}))=0.
 }
 \tag{7.7}
\]

The certified crossing (7.5) must therefore be canceled, if covariance is
true, by the remaining chronological and new--new terms rather than by this
local raw footprint.

### 7.3 Companion-aggregate schema \(\mathfrak G_*\)

There is no proved provenance-local pairing for the remaining scalar terms:
collision aggregation and the bilinear kernels can cancel contributions
from different source leaves.  The smallest honest missing datum after
(7.5)--(7.7) is therefore one finite aggregate bit on the positive chamber.

Define the complete defect

\[
 \mathfrak D(i,j)
 =\sum g\rho+\mathbb B(a,g)+Q(g)
  +\mathbb B(b,f)+\mathbb B(b,g)+\mathbb B(f,g),
 \tag{7.8}
\]

and remove the certified term by

\[
 \Omega_*(i,j)=\mathfrak D(i,j)+\mathcal T_*(i,j).
 \tag{7.9}
\]

The missing instantiated schema for \(\Omega_*\) has the following exact
finite form.

**Variables and inequalities.**  Its free variables are
\(i,j\in\mathbb N\) with \(d=i-j\ge1\).  Each source token has the bounded
row variables \(z\) and domain \(D_R(i,j,z)\) from (4.1)--(4.4); a token
pair has \((z,z')\); and a raw event has positions
\(0\le r_1<r_2<|Z_{o,R}|\).  These are the manifest's exact inequalities,
not a sampled bounding box.

**Normal-form outputs.**  On each disjoint Presburger cell, every source
row must emit

\[
 N_R(i,j,z)
 =A_{R,0}V_{R,1}^{L_{R,1}(i,j,z)}A_{R,1}
  \cdots V_{R,m}^{L_{R,m}(i,j,z)}A_{R,m},
 \tag{7.10}
\]

with terminal-`c` status.  For every occurrence it must also emit

\[
 T_{o,R}=\operatorname{cvert}(q_oN_R),
 \qquad
 \operatorname{red}(q_oN_RccN_R^{-1}q_o^{-1})
   =Z_{o,R}ccZ_{o,R}^{-1}.
 \tag{7.11}
\]

**Integral aggregation and \(\rho/\xi\) outputs.**  Equality loci among all
\(N_R\) first produce the integral coefficients (4.5) and their activity
parities.  Each active token then contributes

\[
 \rho_{o,R}
 =\sum_{r\in\operatorname{Ev}(Z_{o,R})}
   [\operatorname{cvert}(Z_{o,R,\le r})\ne T_{o,R}],
 \tag{7.12}
\]

and every active token pair contributes its exact chronology-selected
shortlex bit (2.4), including decreasing order at negative occurrences.
The finite weighted xor of these records is \(\Omega_*\); the four records
already summed in \(\mathcal T_*\) are omitted once.

**All-power proof obligation.**  Positive-chamber covariance is equivalent
to

\[
 \boxed{\Omega_*(i,j)=1\qquad(i-j\ge1).}
 \tag{7.13}
\]

The output must include exact modulo-two counts of every bounded Presburger
fiber and a finite-state or Presburger certificate for (7.13).  A nonzero
value of one remaining row does not decide (7.13); a certified failure of
(7.13) at one exact symbolic cell would refute covariance.  The other
chambers \(d\le0\) still require their analogous complete aggregates.

## 8. Why the generic normalizer does not certify stabilization

The approved generic powered-product theorem proves the following
existence statement: once a finite bounded-power schema is supplied, its
normal form, equality, raw-letter, prefix, and shortlex predicates admit a
finite disjoint Presburger refinement.  The raw manifest proves source,
raw-bridge, and typed-AST obligations A--C.

Those theorems do not prove (0.1), for four exact reasons.

1. No instantiated record (7.10)--(7.12) exists for the companion aggregate
   \(\mathfrak G_*\).  Effective existence is not an aggregate certificate.
2. Pointwise equality/order cells do not evaluate the unbounded
   bounded-variable fiber counts in \(\Omega_*\) modulo two.  A transfer
   matrix or Presburger-counting recurrence and its all-power proof are
   additionally required.
3. Stabilization is an aggregate statement.  It must combine equality
   collisions before parity, the signed raw bridge, first mismatches,
   negative chronology, fixed-token loads, and all new--new terms.  None is
   implied by a normal form for one virtual row.
4. The generic theorem gives no state identification under
   \((i,j)\mapsto(i+1,j+1)\).  Therefore it cannot turn the full-state
   potential \(\Phi\) into a reduced-state diagonal coboundary.

The explicit terminal crossing (6.9) is a symbolic obstruction to any
argument that claims all old/new comparisons stabilize termwise.  It is not
a counterexample to the complete identity, because the companion aggregate
\(\Omega_*\) can cancel it.

## 9. One corrected constant-size semantic pin

After deriving (3.3), the single rectangle

\[
 (2,0),\ (2,1),\ (3,1),\ (3,2)
 \tag{9.1}
\]

was replayed through the live anchored directions and symbolic residual
coordinate.  Raw parsing retained \(p=\texttt{tc}\) and
\(p^{-1}=\texttt{cT}\).  The four endpoint \(\Phi\)-bits were

\[
 (1,1,1,1),
 \qquad
 1+1+1+1=0.
 \tag{9.2}
\]

An earlier local probe that used `lift.parse_quotient("tc")` was discarded
completely: it had changed \(p\) to `t` by terminal-`c` deletion and was not
an evaluation of the theorem.  Equation (9.2) is the corrected replay.

The zero in (9.2) proves nothing beyond consistency at that rectangle.  It
is not used to infer covariance, a chamber value, or periodicity.

## 10. Consequences and exact proof boundary

### Proved here

1. The exact pullback (4.1)--(4.6) of the complete token cochain to the six
   all-power path families.
2. The distinction between the tautological full-state potential \(\Phi\)
   and the unconstructed reduced augmented-state potential.
3. The failure of a generic third-polarization argument because \(g\ne0\).
4. The all-power slot-zero raw cancellation (5.5).
5. The all-power normal forms and unique terminal crossing (6.7)--(6.9).
6. The actual merged terminal activity \(\kappa_*=1\), (7.4), and the
   vanishing local raw companion (7.7).
7. The concrete missing companion-aggregate schema \(\mathfrak G_*\),
   including its variables, inequalities, normal-form outputs,
   \(\rho/\xi\) loads, and all-power counting obligation.
8. The corrected semantic pin (9.2), with no universal inference.

### Not proved or refuted

1. The complete identity (0.1), equivalently
   \(J_{i+1,j+1}=J_{ij}\).
2. The \(j\)-edge chamber values

   \[
   J(d)=0\ (d<0),\qquad J(0)=J(1)=1,\qquad J(d)=0\ (d>1).
   \tag{10.1}
   \]

3. The diagonal boundary \(\mathcal D_{i,0}=0\), or the full diagonal
   identity \(\mathcal D_{ij}=0\).
4. The two edge laws

   \[
   I_{ij}=[i-j\in\{-1,0\}],
   \qquad
   J_{ij}=[i-j\in\{0,1\}].
   \tag{10.2}
   \]

5. The unary identity \(u_{ij}=\delta_{ij}\).

If (0.1) is later proved, (10.1) still requires three genuine all-power
boundary chambers, and diagonal cancellation reduces only to the
one-parameter family \(\mathcal D_{i,0}=0\).  If (0.1) is refuted by a
certified nonzero **complete** aggregate, then the unary identity
\(u_{ij}=\delta_{ij}\) is also false, because that identity implies the
diagonally covariant \(j\)-edge law (10.2).  Such a refutation would not
refute Andrews--Curtis or stable Andrews--Curtis.

## 11. Hostile referee

### Initial verdict: REJECT, repairable

The independent referee reported six findings.

1. The proposed missing collision fiber was actually computable:
   source-tree geodesic uniqueness, the `aB`/`aG` divergence, component
   separation, and the base-length check prove \(\kappa_*=1\).
2. Formula (4.5) needed the scope \(s\in\{2,3,4\}\), and the draft needed
   explicit definitions of \(p_\nu,c_\nu,q_\nu,r_\nu\) and the incidence
   multipliers.
3. The slot-zero raw table had the right parities but did not print the
   fixed first-half event-label cascades needed for an auditable all-power
   proof.
4. The final consequence was misstated: a nonzero complete covariance
   defect would also refute \(u_{ij}=\delta_{ij}\), although it would imply
   no Andrews--Curtis conclusion.
5. The referee independently confirmed the row data, normal forms, lengths,
   comparison table, and terminal crossing (6.9).
6. Raw typing, the generator package, and the absence of carriage-return
   bytes were confirmed.  The referee independently replayed the first two
   endpoints of (9.1) as \(1,1\); a cold third endpoint reached the enforced
   25-second limit and was stopped, with no inference drawn from that timeout.

All statement and proof defects in findings 1--4 are repaired in Sections
1, 4, 5, 7, 8, and 10.  The same referee's focused rereview follows below.

### Focused rereview: APPROVE

**APPROVE -- zero remaining load-bearing findings.**  The same referee
confirmed that every initial finding is repaired, (7.7) is valid,
\(\mathfrak G_*\) is scoped only as an open all-power proof obligation, raw
\(p=\texttt{tc}\) typing is preserved, and the artifact contains no carriage
returns.

For the one permitted rectangle, the referee independently obtained

\[
 \Phi_{3,1}=1,\qquad \Phi_{3,2}=1
 \tag{11.1}
\]

in separate bounded runs below 25 seconds.  Together with the independently
checked first two values \(1,1\), this verifies the corrected tuple (9.2) as
\((1,1,1,1)\).  No other rectangle was sampled, and no all-index inference
is drawn from this zero rectangle.
