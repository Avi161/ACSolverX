# Exact crossing contraction and source-tree cut induction

Date: 2026-07-29

## 0. Verdict

The two all-index edge identities

\[
 I_{ij}=[i-j\in\{-1,0\}],\qquad
 J_{ij}=[i-j\in\{0,1\}]
\tag{0.1}
\]

are **not proved or refuted here**.  What is proved is an exact reduction
which removes the two bookkeeping obstructions left by
`period_two_linear_event_involution.md`:

1. all noncentral raw events of a transported correction atom contract to
   one explicit linear weight \(\rho_o(v)\); and
2. alternating-path surgery through the merged section contributes no
   separate crossing or survivor-permutation term.

After this contraction, an endpoint residual is represented by a core stream
containing the fixed literal events and one event for each correction atom.
Its full-wedge bit is an explicit quadratic cut form on the parity of the
*actual merged coefficients* \(B_s+D_s\).  Equations (4.8) and (6.9) below
are literal leaf-removal formulas.  They retain the shortlex merge, every
negative occurrence, every raw quotient-prefix defect, and endpoint
reversal.

The remaining all-index theorem is the pair of completely specified cut
identities (7.3).  Equivalently, it is the \(j\)-edge identity plus the zero
diagonal-step identity (7.6).  There is no undefined potential in either
form: every summand is a raw palindrome weight, a chronological comparison,
or a source-tree edge prescribed by the live incidence rules.

One exact local example proves that the raw weight cannot be discarded or
made a function only of the central source-tree label.  Thus a pure
label-preserving path telescope is false in that stronger form.

No index grid, census, broad search, or representative-class inference is
used.  One three-event structural replay in Section 5 only checks the local
raw formula which was derived first.

## 1. Conventions

Let \(C=(C_0,\ldots,C_4)\) be the complete integral correction current
supplied to the literal residual AST.  For the unary ray,

\[
 C_{ij}=B+D_{ij}.
\tag{1.1}
\]

Let \(\mathcal E(C)\) be the literal chronological Schreier-event stream of
the residual \(\mathcal R(C)\), with no optional adjacent free
cancellation.  The approved event involution proves that every event label
has even multiplicity.

The sixteen correction occurrences are denoted by \(o\).  Their slot,
polarity, and **raw quotient prefix** are \((s_o,p_o,q_o)\).  The word
\(q_o\) is not passed through `c_vertex`; in particular prefixes such as
`tc` retain their terminal `c`.  For a canonical module vertex \(v\), put

\[
 \tau_o(v)=\operatorname{cvert}(q_ov).
\tag{1.2}
\]

The exact occurrence table is the one proved by the typed AST:

| \(o\) | \(s_o\) | \(p_o\) | \(q_o\) |
|---:|---:|---:|---|
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

Write \(<_{\rm sl}\) for the certificate's shortlex order on canonical
module vertices and also on event labels.  At a positive occurrence the
atom blocks are in increasing shortlex order.  At a negative occurrence the
whole canonical section is reversed and inverted, so the atom blocks are in
decreasing shortlex order.  The sign of a coefficient changes the raw atom
orientation but not its place in this vertex order.

## 2. Contracting one raw transported atom

Fix \(o,v\).  The approved raw bridge gives a word \(z=z(q_o,v)\) such that

\[
 \operatorname{red}(q_ovccv^{-1}q_o^{-1})=zccz^{-1}.
\tag{2.1}
\]

The terminal-`c` branch and its `tau` deletion are part of the definition of
\(z\).  Scan \(z\) by the literal `_KernelStream` rule.  Relative to the
canonical quotient section, write its chronological kernel-event word as

\[
 a_1a_2\cdots a_m.
\tag{2.2}
\]

If \(\alpha_h\) is the post-`c_vertex` label of \(a_h\), the complete event
label word of the positive transported atom is

\[
 (\alpha_1,\ldots,\alpha_m,
   \tau_o(v),
   \alpha_m,\ldots,\alpha_1).
\tag{2.3}
\]

For a negative atom the event word is reversed and sign-inverted, but its
label palindrome is the same.  Define the **raw mirror weight**

\[
 \boxed{
 \rho_o(v)=\sum_{h=1}^m[\alpha_h\ne\tau_o(v)]\pmod2.
 }
\tag{2.4}
\]

This is an explicit raw-word formula: \(z\) is supplied by the disjoint
maximal-overlap branches in the approved raw manifest, and each
\(\alpha_h\) is obtained from the displayed `_KernelStream` emission rule.
If \(\mu_o(v)\) is the integral linear Schreier coordinate of the prefix
word \(a_1\cdots a_m\), then the same formula has the cochain form

\[
 \rho_o(v)
 =\left\langle {\bf 1}+e_{\tau_o(v)}^*,
   \mu_o(v)\right\rangle\pmod2.
\tag{2.5}
\]

Indeed, modulo two a signed coefficient is the unsigned occurrence count,
and the covector in (2.5) counts every label except the central one.  This
identifies the raw term as a concrete section-defect cochain; it does not
assert that this cochain is a source-tree coboundary.

### Lemma 2.1 (raw-mirror contraction)

Use the local mirror matching of (2.3).  Every local mirror chord is nested
inside its atom block.  It crosses exactly one nonlocal chord: the chord
incident to that atom's unique central event.  The crossing is
heterochromatic precisely when the mirror label differs from
\(\tau_o(v)\).  Hence all local mirror chords in the atom contribute
\(\rho_o(v)\).

#### Proof

The mirror pairs in (2.3) are nested, so they do not cross one another.  Atom
blocks are disjoint intervals, so a mirror chord does not cross a mirror
chord from another atom.  No fixed literal event lies inside an atom block.
After local pairing there is exactly one unpaired event in the block, its
central event.  The mate of that event lies outside the block because the
global involution is fixed-point-free and there is no second central event
inside the same atom.  Therefore each mirror chord has exactly one endpoint
of that global chord in its interior and crosses it.  The
heterochromatic restriction gives (2.4).  \(\square\)

This proof also handles all signs.  Reversal of the palindrome preserves
nesting, labels, and (2.4).

## 3. The core stream and the exact endpoint formula

Form the **core stream** \(\mathcal K(C)\) from \(\mathcal E(C)\) as
follows.

* Retain every fixed-literal Schreier event, in its actual AST chronology.
  There are seventy before optional adjacent cancellation.
* Replace every correction atom at occurrence \(o\), vertex \(v\), and
  coefficient copy by its one central event labelled \(\tau_o(v)\).

All raw mirror endpoints have been removed in same-label pairs.  Therefore
every label still has even multiplicity in \(\mathcal K(C)\).  The
matching-independent heterochromatic chord theorem applies to this core
stream.

For each correction token \((o,v)\), define its activity

\[
 a_C(o,v)=C_{s_o}(v)\pmod2.
\tag{3.1}
\]

The absolute value and the sign give the same parity.  Two identical copies
have twice every interaction with the rest of the stream, and their mutual
pair is monochromatic, so only (3.1) survives.  Every fixed token has
activity one.

### Theorem 3.1 (exact endpoint contraction)

For every integral full correction current \(C\) whose residual has zero
linear Schreier coordinate,

\[
 \boxed{
 \phi_\infty(\mathcal R(C))
 =\operatorname{sort}\mathcal K(C)
  +\sum_{o,v}a_C(o,v)\rho_o(v).
 }
\tag{3.2}
\]

Here

\[
 \operatorname{sort}\mathcal K(C)
 =\sum_{p\triangleleft q}a_C(p)a_C(q)
   [\ell(p)<_{\rm sl}\ell(q)]
\tag{3.3}
\]

where \(p,q\) range over fixed and active correction tokens,
\(\triangleleft\) is literal chronology, and \(\ell\) is the exact final
event label.

#### Proof

Apply Lemma 2.1 simultaneously to every atom.  The local mirror chords give
the second term of (3.2) and cross no other local or fixed chord.  What
remains is a same-label perfect matching of the even-label core stream.
The matching-independent chord theorem identifies its heterochromatic
crossing parity with (3.3).  Reducing coefficient copies modulo two is valid
by the paragraph preceding the theorem.  \(\square\)

The seventy fixed events include the six pairs which become adjacent only
when correction leaves are empty.  They need not be removed or treated as
special cut chords.  Keeping them in \(\mathcal K(C)\) is what makes (3.2)
independent of that optional stack reduction.

## 4. Literal leaf-removal and simultaneous-cut formulas

It is useful to put all possible tokens in one ordered universe
\(\mathscr P\).  Only a finite subset is active in any calculation.

* A fixed token is one of the seventy fixed-literal events.  Its chronology
  and label are fixed and its activity is one.
* A correction token is \((o,v)\).  Its label is \(\tau_o(v)\).  Within
  occurrence \(o\),

  \[
  v\triangleleft_o w
  \iff
  \begin{cases}
  v<_{\rm sl}w,&p_o=+1,\\
  w<_{\rm sl}v,&p_o=-1.
  \end{cases}
  \tag{4.1}
  \]

The expanded-AST leaf order puts different occurrences and fixed tokens in
their literal positions.  Thus (4.1) includes the complete negative-
occurrence chronology; there is no later survivor permutation.

For distinct tokens define the symmetric chronological kernel

\[
 \xi(p,q)=
 \begin{cases}
 [\ell(p)<_{\rm sl}\ell(q)],&p\triangleleft q,\\
 [\ell(q)<_{\rm sl}\ell(p)],&q\triangleleft p.
 \end{cases}
\tag{4.2}
\]

Put \(r(p)=\rho_o(v)\) for \(p=(o,v)\) and \(r(p)=0\) for a fixed token.
Then (3.2) is the explicit quadratic form

\[
 \Phi(a)=
 \sum_pa(p)r(p)
 +\sum_{\{p,q\}}a(p)a(q)\xi(p,q).
\tag{4.3}
\]

The second sum is finite because only active tokens are used.

### 4.1 One current-coordinate leaf

Changing one current coefficient \(C_s(v)\) by an odd integer toggles the
whole occurrence footprint

\[
 A(s,v)=\{(o,v):s_o=s\}.
\tag{4.4}
\]

This footprint has respectively \(6,4,2,2,2\) tokens for
\(s=0,1,2,3,4\).  Define

\[
\boxed{
\begin{aligned}
 \lambda_a(s,v)
 ={}&\sum_{p\in A(s,v)}r(p)
 +\sum_{\{p,q\}\subset A(s,v)}\xi(p,q)\\
 &+\sum_{p\in A(s,v)}
   \sum_{q\notin A(s,v)}a(q)\xi(p,q).
\end{aligned}}
\tag{4.5}
\]

Every sum in (4.5) is a literal raw-label or chronological comparison.
Direct expansion of (4.3) gives the leaf-removal identity

\[
 \boxed{
 \Phi(a+1_{A(s,v)})+\Phi(a)=\lambda_a(s,v).
 }
\tag{4.6}
\]

The value (4.5) is independent of the current activity on the footprint
itself.  In particular, toggling the same coordinate twice in succession
gives the same \(\lambda\) twice and contributes zero.  This is the cut-level
reason that

* an integral coefficient change by two is invisible;
* two elementary tokens canceled in the merged section are invisible; and
* an adjacent inverse pair in a forest path gives zero.

No virtual base/flow chronology is used.  The initial activity in (4.5) is
always that of the actual merged current \(B+F\).

### 4.2 An arbitrary finite increment

Let \(C'=C+L\), and put

\[
 d(o,v)=L_{s_o}(v)\pmod2,\qquad d(p)=0
 \quad\hbox{for fixed }p.
\tag{4.7}
\]

Expanding (4.3) once, without choosing a toggle order, gives

\[
\boxed{
\begin{aligned}
 \mathscr C(a_C,d)
 :={}&\sum_p d(p)r(p)\\
 &+\sum_{\{p,q\}}\xi(p,q)
 \bigl(a_C(p)d(q)+d(p)a_C(q)+d(p)d(q)\bigr)\\
 ={}&\phi_\infty(\mathcal R(C'))
   +\phi_\infty(\mathcal R(C)).
\end{aligned}}
\tag{4.8}
\]

Equivalently, for any deterministic list of the changed current
coordinates, (4.8) is the sum of (4.5) evaluated after the preceding
toggles.  Because (4.8) is symmetric in the changed set, the answer is
independent of that list.

### 4.3 Why alternating merge surgery disappears

The alternating-path graph in `period_two_linear_event_involution.md` is
needed to prove that the actual merged event labels admit a perfect
same-label matching.  Once that fact is known, heterochromatic crossing
parity is matching-independent.  Formula (4.8) therefore uses the actual
coefficient parity

\[
 (B_s+F_s)(v)\pmod2
\tag{4.9}
\]

directly.  Insertion or deletion of a vertex from a canonical support does
not reorder any common vertex: common vertices keep their shortlex order,
with the whole order reversed exactly at negative occurrences.  Hence there
is no extra `pi_L`, alternating-component, or survivor-order term.

This does **not** identify the virtual base and flow streams.  It avoids
that false identification by never assigning them a chronology separately.

## 5. The raw weight is a genuine obstruction to a label-only telescope

The weight (2.4) need not vanish and is not determined by the central label.
Take the actual raw occurrence prefix

\[
 q=\texttt{tc},\qquad v=\texttt{cT}.
\tag{5.1}
\]

It is essential here that `tc` is the raw quotient prefix, not its
post-`c_vertex` representative.  Literal reduction and `_KernelStream`
scanning give

\[
 \operatorname{red}(qvccv^{-1}q^{-1})
 =\texttt{tccTcctCCT}
\tag{5.2}
\]

and the three events

\[
 (\texttt{t}^{+},\ \texttt{eps}^{+},\ \texttt{t}^{-}).
\tag{5.3}
\]

Thus the central label is `eps` and

\[
 \rho_{\texttt{tc}}(\texttt{cT})=1.
\tag{5.4}
\]

By contrast \(q=v=\texttt{eps}\) gives the raw word `cc`, the sole central
event `eps`, and

\[
 \rho_{\texttt{eps}}(\texttt{eps})=0.
\tag{5.5}
\]

The two atoms have the same central label and different raw weights.
Consequently neither the source-tree vertex label nor the alternating path
component can pair away the \(\rho\)-term.  Any valid source-tree induction
must carry

\[
 R_s(v)=\sum_{o:s_o=s}\rho_o(v)
\tag{5.6}
\]

through its leaf cuts.  The constant-size replay of (5.2)--(5.5) is only a
check of the already derived local formula, not evidence about an index
stratum.

## 6. Exact source-tree telescoping for an adjacent ray step

Put

\[
 p=tc,\qquad \gamma=(ctcTTTct)^3,
\qquad
 y_{ij}=p^{-1}\gamma^{i-j}c\gamma^{-(i+1)}t.
\tag{6.1}
\]

Let \(H(y)\) be the exact anchored direction.  Since
`source_scalar(y)=-2`,

\[
 H(y)_0=e_y+2e_T,\qquad H(y)_1=0.
\tag{6.2}
\]

For two adjacent ray vertices \(y,y'\), the anchor cancels integrally and

\[
 \Delta(y,y'):=H(y')-H(y)
\tag{6.3}
\]

has

\[
 \Delta_0=e_{y'}-e_y,\qquad \Delta_1=0.
\tag{6.4}
\]

Let

\[
 \mathcal O_0=\{3,4,7,8,11,12\}.
\tag{6.5}
\]

Applying the slot-zero occurrence operator to (6.4) gives, modulo two, the
twelve boundary vertices

\[
 \tau_o(y),\ \tau_o(y')\qquad(o\in\mathcal O_0).
\tag{6.6}
\]

For each of the three adjacent steps below, the approved complete-cover
factorization proves that each displayed old/new pair lies in one
source-tree component.  Let

\[
 \pi_o(y,y')=\operatorname{path\_between}
   (\tau_o(y),\tau_o(y'))
\tag{6.7}
\]

be its unique reduced forest path.  The finite-tree-flow uniqueness theorem
then gives the exact parity currents

\[
\boxed{
 \overline\Delta_s(y,y')
 =\sum_{o\in\mathcal O_0}\mathsf E_s(\pi_o(y,y')),
 \qquad s=2,3,4.
}
\tag{6.8}
\]

Overlaps among the six paths cancel coefficientwise.  Equation (6.8) does
not depend on using these six pairs in the canonical boundary sort: any
pairing with the same boundary produces the same finite flow in a tree.

To obtain a literal leaf induction, process first the two slot-zero
coordinates in (6.4), then process the six paths in increasing occurrence
order, and within each path process its forest letters chronologically.
The live `A/a`, `B/b`, and `G/g` incidence rule turns each forest letter
into one coordinate \((s,v)\).  Sum (4.5), updating the actual activity
after each toggle.  An adjacent forest inverse pair toggles the same
coordinate twice and contributes zero by (4.6).  Hence the sum is unchanged
by free reduction and telescopes exactly to

\[
 \boxed{
 \sum_{\text{source leaves in }\Delta(y,y')}
   \lambda_{a_{\rm current}}(s,v)
 =\mathscr C(a_{B+H(y)},\overline\Delta(y,y')).
 }
\tag{6.9}
\]

This is the requested literal leaf-removal/cut formula over each canonical
source-tree path.  Local raw mirrors enter only through \(r=\rho\) in
(4.5); merged-section cancellation is already in the current activity;
negative occurrence chronology is in (4.1).

For reference, the three old/new source vertices have fixed left ratios

\[
\begin{aligned}
 y_{i,j+1}&=h^j y_{ij},&
 h^j&=p^{-1}\gamma^{-1}p,\\
 y_{i+1,j}&=h^i_d y_{ij},&
 h^i_d&=p^{-1}\gamma^{d+1}c\gamma^{-1}c\gamma^{-d}p,\\
 y_{i+1,j+1}&=h^{\rm diag}_d y_{ij},&
 h^{\rm diag}_d&=p^{-1}\gamma^dc\gamma^{-1}c\gamma^{-d}p,
\end{aligned}
\qquad d=i-j.
\tag{6.10}
\]

These identities follow by multiplying each new word by
\(y_{ij}^{-1}\) on the right and freely canceling the common tail.  Thus,
after conjugation by each fixed occurrence prefix, the six source-tree
increment paths have fixed translation words depending only on \(d\)
(and in the \(j\)-case independent of \(d\)).  Their basepoints still move
with \(i\).  Formula (4.5) also contains the whole old core activity, so
(6.10) alone does not prove that the weighted cut sum depends only on
\(d\).

## 7. The smallest remaining all-index identities

Write

\[
 a_{ij}=a_{B+D_{ij}},
\tag{7.1}
\]

and let \(d^i_{ij},d^j_{ij}\) be the occurrence-expanded parity toggles
obtained from

\[
 D_{i+1,j}-D_{ij},\qquad D_{i,j+1}-D_{ij}
\tag{7.2}
\]

by (4.7), or equivalently by the six paths (6.7)--(6.9).  The exact
difference-word and endpoint-reversal lemmas give

\[
\boxed{
\begin{aligned}
 I_{ij}=\mathscr C(a_{ij},d^i_{ij}),\qquad
 J_{ij}=\mathscr C(a_{ij},d^j_{ij}).
\end{aligned}}
\tag{7.3}
\]

Indeed, choose the disjoint union of the two endpoint involutions on
\(\mathcal R(C')\mathcal R(C)^{-1}\).  Every chord lies wholly in one
endpoint block, so there is no cross-block crossing.  Reversal of an
endpoint preserves chord crossings and \(\rho\).  Equivalently, for the
core stable-sort count,

\[
 \operatorname{sort}(\operatorname{rev}\mathcal K)
 +\operatorname{sort}(\mathcal K)
 =\sum_{x<y}m_xm_y=0,
\tag{7.4}
\]

because every core-label multiplicity \(m_x\) is even.

Substituting (4.8) into (7.3), the two and only two remaining edge
identities are

\[
\boxed{
\begin{aligned}
 \mathscr C(a_{ij},d^i_{ij})
   &=[i-j=-1]+[i-j=0],\\
 \mathscr C(a_{ij},d^j_{ij})
   &=[i-j=0]+[i-j=1].
\end{aligned}}
\tag{7.5}
\]

Every term of the left sides is explicitly defined in (1.2), (2.1)--(2.4),
(4.1)--(4.2), and (6.4)--(6.8).  In particular, (7.5) contains no final
wedge comparison, arbitrary matching, undefined boundary potential, or
bounded normal-form table.

There is a slightly better equivalent proof target.  Put

\[
 d^{\rm diag}_{ij}
 =a_{B+D_{i+1,j+1}}+a_{B+D_{ij}}.
\]

Then (7.5) is equivalent to

\[
\boxed{
\begin{aligned}
 \mathscr C(a_{ij},d^j_{ij})&=[i-j=0]+[i-j=1],\\
 \mathscr C(a_{ij},d^{\rm diag}_{ij})&=0.
\end{aligned}}
\tag{7.6}
\]

The implication back to the \(i\)-edge uses the exact path identity

\[
 I_{ij}
 =\bigl(u_{i+1,j}+u_{i+1,j+1}\bigr)
  +\bigl(u_{i+1,j+1}+u_{ij}\bigr)
 =J_{i+1,j}+\mathcal D_{ij}.
\tag{7.7}
\]

The right side of the first line of (7.6), evaluated at \((i+1,j)\), is
one exactly for \(i-j\in\{-1,0\}\), as required.  Conversely the two
edge targets (7.5) make (7.7)'s diagonal term zero, so the formulations are
equivalent.

The \(j\)-step in (7.6) is the cleaner first target: its six path shapes are
the fixed \(Q_\nu^{-1}\) blocks from the approved factorization.  The
diagonal step uses the fixed left ratios \(h^{\rm diag}_d\) in (6.10).

## 8. Exact proof boundary

### Proved here

1. the raw-mirror contraction (2.4)/(3.2), including negative atoms and
   negative occurrences;
2. the actual-merged core-stream quadratic form (4.3);
3. the simultaneous leaf cut (4.8), with no survivor-permutation term;
4. endpoint reversal and the difference-word identities (7.3);
5. source-tree leaf telescoping (6.8)--(6.9); and
6. the exact adjacent-source ratios (6.10).

### Refuted here

The raw correction term is not a function only of the central
post-`c_vertex` label: (5.4)--(5.5) give an exact counterexample.  Therefore
a proof which erases local raw mirrors after constructing only a
label-preserving source-tree matching is invalid.

### Still open

The two explicit weighted cut identities (7.5), equivalently (7.6), remain
unproved.  Their load-bearing terms are

* the occurrence-wise raw weights \(\rho_o(v)\);
* the cut load against the complete old merged activity \(a_{ij}\); and
* the new--new quadratic comparisons among the six increment paths.

The fact that the source translation words in (6.10) depend only on
\(d=i-j\) does not make the cut load a function of \(d\): the moving
basepoints and the old anchored flow remain in (4.5).  Proving that their
sum collapses to the two boundary indicators is precisely the remaining
theorem.  No period-two lift, stable Andrews--Curtis conclusion, or
Andrews--Curtis conclusion follows at this stage.

## 9. Smallest non-grid continuation

The optimized pair (7.6) avoids a separate attack on the more complicated
\(i\)-edge.  The next proof should use the following order.

1. **Augmented diagonal covariance.**  Translate simultaneously the old
   anchored flow, the six \(j\)-increment paths, and every token in (4.5)
   under \((i,j)\mapsto(i+1,j+1)\).  Prove directly from the raw section
   cocycle (2.5) and the chronological kernel (4.2) that the *sum* of the
   six path loads is invariant.  The claim must include \(\rho\); covariance
   of central labels alone is false by Section 5.  This would prove that
   the \(j\)-cut is constant along each fixed-\(d\) ray.
2. **Three axis chambers, not index cells.**  At the initial point of a
   fixed-\(d\) ray, compare the explicit cyclic normal forms in (6.10).
   Prove one same-side cut theorem for \(d<0\), one for \(d>1\), and compute
   the two boundary words \(d=0,1\).  The desired values are respectively
   \(0,0,1,1\).  This is an all-power normal-form proof of the same kind as
   the retained primitive \(P_{ij}=\delta_{ij}\) proof, not a representative
   table.
3. **Diagonal step.**  Apply the same augmented covariance to
   \(h_d^{\rm diag}\).  The required statement is that the six complete
   path loads cancel for every \(d\), giving the second line of (7.6).

Each proposed lemma is falsifiable using the already defined
\(\lambda_a(s,v)\); none introduces a new potential.  If augmented
covariance fails, the failing raw prefix, occurrence, and forest edge give
an exact counterexample to this continuation without calling the target
identity false.

## Hostile review

**APPROVE — zero load-bearing findings.**  An independent referee checked
Lemma 2.1, core evenness and copy parity, (4.5)/(4.8), negative-occurrence
chronology, disappearance of alternating merge surgery, the raw `tc` pin,
the six-path flow identity (6.8), the ratios (6.10), endpoint reversal, and
the equivalence of (7.5) and (7.6) against the authoritative notes and live
source semantics.
