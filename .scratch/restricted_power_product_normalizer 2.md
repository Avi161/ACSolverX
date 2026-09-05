# Restricted quotient powered-product normalizer

Date: 2026-07-29

## Status and exact scope

**The generic quotient normalizer is proved; its application to the literal
period-two AST is not proved.**  Given an explicitly supplied finite list of
bounded power-product schemas over the pinned quotient alphabet, the argument
constructs finite Presburger records.  It does not show that the 305 raw
forest positions have been converted to such schemas, compile the signed raw
word consumed by `_KernelStream`, establish the variable arity of the typed
AST trace, or emit the instantiated chamber tables.

The construction is deliberately not a cancellation-case search.  It first
computes a finite bounded-language cover of every possible completely reduced
output.  Effective equality semilinearity is then used only to select a
candidate that is already certified to be a canonical reduced word.  Exact
length, terminal-`c` deletion, the indexed canonical stream, prefixes, and
shortlex first mismatch are read from that selected word by separate regular
and Presburger predicates.  In particular, shortlex is not inferred from
group equality.

This proves only the safe quotient theorem in Section 7.  Sections 1 and 8
separate the raw source facts from the four application obligations that must
be discharged before any exact-AST normalizer theorem can be restored.  No
grid, broad computation, or finite-state unary-transducer claim is used.

## 1. Pinned quotient conventions and the missing application input

Put
\[
 Q=\langle c,t\mid c^2=1\rangle=C_2*\mathbb Z.
\]
Use the certificate alphabet
\[
 \Sigma=\{T,c,t\}=\{-2,1,2\},
 \qquad T^{-1}=t,\qquad c^{-1}=c,
\tag{1.1}
\]
with the integer order
\[
 T<c<t.
\tag{1.2}
\]
A canonical quotient word contains none of
\(Tt,tT,cc\).  The length-reducing rules
\(Tt,tT,cc\to\epsilon\), after replacing both signs of the original
`C` generator by `c`, are terminating and confluent by the free-product
normal-form theorem.  Their unique output is the code's `quotient_reduce`.
For a reduced word \(w\),
\[
 \operatorname{cvert}(w)=
 \begin{cases}
 w'&w=w'c,\\
 w&\text{otherwise}.
 \end{cases}
\tag{1.3}
\]
The code's shortlex key is exactly
\((|\operatorname{cvert}(w)|,\operatorname{cvert}(w))\), with the tuple
order (1.2).

The intended application starts from the six approved **raw forest-word**
block triples

| \(\nu\) | \(P_\nu\) | \(C_\nu\) | \(Q_\nu\) |
|---:|---|---|---|
| 1 | `aBgAgAggABBgAb` | `aBgAgAggABBgAb` | `GaGaGbABaGbbaG` |
| 2 | `AgABBgAbaBgAgAga` | `AgABBgAbaBgAgAgBaGb` | `baGGaGaGbABaGb` |
| 3 | `aGbAAGaGbAAGaGbAAG` | `aGbAAGaGbAAGaGbAAG` | `baGGaGaGbABaGb` |
| 4 | `aGbAAGaGbAAGaGbAAG` | `aGbAAGaGbAAGaGbAAGaG` | `gAbaGGaGaGbABaGbaG` |
| 5 | `aGbAAGaGbAAGaGbAAG` | `aGbAAGaGbAAGaGbAAGbaG` | `GaGaGbABaGbbaG` |
| 6 | `AgABBgAbaBgAgAga` | `AgABBgAbaBgAgAgBaGbaG` | `gAbaGGaGaGbABaGbaG` |

and the factorization
\[
 W^w_{\nu,i,j}=\operatorname{red}
 \bigl(P_\nu^iC_\nu Q_\nu^{i-j}\bigr).
\tag{1.4}
\]
The approved fixed count is \(100+113+92=305\) raw letter positions before
slot and orientation decoration.  It does **not** enumerate their module
vertices or supply quotient schemas.  A positive power uses a forward raw
position; a negative \(Q\)-power uses the same raw positions in reverse
order.

The generic compiler instead takes an explicitly supplied parameter tuple
\(x\) of arbitrary fixed finite arity, an exact Presburger domain \(D(x)\),
and a quotient schema
\[
 W(x)=a_0u_1^{L_1(x)}a_1\cdots u_k^{L_k(x)}a_k,
\tag{1.5}
\]
where \(k\) is fixed, the \(a_r,u_r\) are fixed quotient words, and the
\(L_r\) are affine integer functions.  Split each sign by the disjoint
conditions \(L_r\ge0\) and \(L_r<0\); on the latter branch replace
\(u_r^{L_r}\) by \((u_r^{-1})^{-L_r}\).  Thus all displayed powers below
have nonnegative exponents.

No row-by-row construction from (1.4) to (1.5) is supplied here.  In
particular, the right-deck-to-module-vertex map, raw prefixes, signs, domains,
orientations, slot-zero singleton, fixed base atoms, and anchors have not
been assembled into a source-schema manifest.  Likewise, the literal AST
query set has not been materialized.  These are Application Obligations A
and C in Section 8, not hypotheses verified by the raw count 305.

## 2. Effective bounded covers of all reduced outputs

Call a language *bounded* if it is contained in an expression
\[
 b_0v_1^*b_1\cdots v_m^*b_m
\tag{2.1}
\]
with fixed finite words.  A finite union of such expressions is a finite
bounded cover.  The cover is allowed to contain words that are not reduced;
canonicality will be imposed exactly in Section 3.

### Lemma 2.1 (powered factor)

For every fixed word \(u\), the set
\(\{\operatorname{qred}(u^n):n\ge0\}\) has an effectively computable finite
bounded cover with explicit primitive-core, orientation, and phase tags.

### Proof

Compute \(\operatorname{qred}(u)=xrx^{-1}\) by repeatedly removing inverse
first/last letters until \(r\) is cyclically reduced.  This process is finite
because \(u\) is fixed and each step shortens it.

If \(r=\epsilon\), every power is trivial.  If \(r=c\), the two parity
branches give \(1\) and \(xcx^{-1}\).  Otherwise \(r^n\) is reduced for all
\(n\ge0\), and
\[
 \operatorname{qred}(u^0)=\epsilon,
 \qquad
 \operatorname{qred}(u^n)=xr^nx^{-1}\quad(n>0).
\tag{2.2}
\]
The expression \(\{\epsilon\}\cup xr^*x^{-1}\) is a finite bounded cover.

Because \(r\) is a fixed word, test its finitely many divisors and write
\(r=\rho^e\) with \(\rho\) primitive and \(e\) maximal.  Record \(\rho\),
the orientation \(+\), and phase zero.  An inverse-power sign branch records
\(\rho^{-1}\), orientation \(-\), and the corresponding fixed endpoint
phases.  Proper prefixes and suffixes used below have one of the finitely
many phases \(0,\ldots,|\rho|-1\).  These are computations on a fixed word,
not parameter searches.  \(\square\)

### Lemma 2.2 (prefixes and suffixes)

From a finite bounded cover \(\mathcal B\), one can effectively compute
finite bounded covers of \(\operatorname{Pref}(\mathcal B)\) and
\(\operatorname{Suff}(\mathcal B)\), including the empty word.

### Proof

For one expression (2.1), choose the fixed factor or starred factor in which
the cut occurs.  All earlier starred exponents remain arbitrary; all later
ones disappear.  Inside a starred factor \(v^n\), the cut is after some
number of complete copies and one of the finitely many proper prefixes of
\(v\).  This gives finitely many bounded prefix expressions.  The suffix
construction is the reverse statement.  The cut records the primitive-core
orientation and its residue phase.  Taking the union over the finite cover
is effective.  \(\square\)

### Lemma 2.3 (product cover, including vanished blocks)

If the reduced outputs of expressions \(E\) and \(F\) have finite bounded
covers, then so do the reduced outputs of \(EF\).  Write
\(\mathcal C(E)\) and \(\mathcal C(F)\) for the two cover families.  An
effective cover is
\[
 \bigcup_{K\in\mathcal C(E),\ L\in\mathcal C(F)}
 \operatorname{Pref}(K)\operatorname{Suff}(L).
\tag{2.3}
\]

### Proof

Let \(U=\operatorname{qred}(E)\) and
\(V=\operatorname{qred}(F)\).  There are cover languages
\(K\in\mathcal C(E)\), \(L\in\mathcal C(F)\) with \(U\in K\), \(V\in L\),
and there is a unique longest word \(X\) such
that
\[
 U=PX,\qquad V=X^{-1}Q,
\tag{2.4}
\]
and \(PQ\) is reduced.  Thus
\(\operatorname{qred}(EF)=PQ\), with \(P\) a prefix of \(U\) and \(Q\) a
suffix of \(V\).  Since \(P\in\operatorname{Pref}(K)\) and
\(Q\in\operatorname{Suff}(L)\), formula (2.3) contains the output even when
the cover languages themselves contain noncanonical words.

This one maximal-overlap statement also covers complete disappearance of
either side.  In a longer product, left-associative induction first reduces
the whole accumulated left expression.  If one or several intervening fixed
or powered blocks vanish, the newly exposed nonadjacent blocks occur on the
two sides of the next instance of (2.4).  No assumption that a separator
survives is made.  \(\square\)

### Proposition 2.4 (finite output-cover compiler)

For every fixed schema (1.5), there is an effective finite bounded cover
\[
 \mathcal C(W)=\{V_s(q):1\le s\le N,\ q\in\mathbb N^{m_s}\}
\tag{2.5}
\]
of all words \(\operatorname{qred}(W(x))\) on its domain.

### Proof

Use Lemma 2.1 at every powered leaf, singleton covers at fixed leaves, and
Lemma 2.3 at product nodes.  Lemma 2.2 supplies each product step.  The
schema has finitely many leaves and product nodes, so the resulting union is
finite.  \(\square\)

The construction explicitly includes inverse and commensurable cores.  It
does not have to guess how much of two periodic cores cancels: all surviving
prefix/suffix phases are in (2.5), and Section 3 selects the one whose whole
expansion is reduced and represents the input.  If two same-orientation
commensurable cores can merge, or opposite orientations can cancel, their
possibly redundant output codes are resolved by the unique-code rule below.
Torsion boundaries are already separated by the \(r=c\) parity branch.

## 3. Selecting the unique canonical output

Write a cover template in the fixed form
\[
 V_s(q)=b_{s,0}v_{s,1}^{q_1}b_{s,1}\cdots
 v_{s,m_s}^{q_{m_s}}b_{s,m_s}.
\tag{3.1}
\]
All words here are fixed quotient words and \(q\ge0\).

Let \(\mathsf{Red}_s(q)\) mean that the literal expansion (3.1) is in the
canonical language, i.e. it has no `Tt`, `tT`, or `cc`.  This is effectively
Presburger.  Indeed, the canonical language is recognized by a four-state
DFA remembering the last letter (plus a dead state).  For each fixed block
\(v\), the DFA transformation induced by \(v^q\) is eventually periodic in
\(q\), since it is a power in a finite transformation monoid.  Enumerating
the finitely many intermediate DFA states gives a finite disjunction of
threshold and congruence conditions on \(q\).  Zero exponents are explicit
branches, so blocks that vanish and expose new boundaries are checked by the
same DFA run.

Let \(D(x)\) be the Presburger domain of the query.  Define
\[
 \mathsf A_s(x,q):=D(x)\wedge(q\ge0)\wedge
 \mathsf{Red}_s(q)\wedge[W(x)=_Q V_s(q)].
\tag{3.2}
\]
The last predicate is effectively Presburger by the imported equality
semilinearity theorem: apply Lohrey's hyperbolic-group theorem, or the
Figelius--Lohrey--Zetzsche free-product theorem, and their repeated-variable
reduction; then intersect with the affine exponent graphs and the domain.
This is exactly a use for which the published output suffices.  Both sides of
the equality are bounded products of fixed powers, and all signed exponents
have already been split.

For every \(x\in D\), at least one \(\mathsf A_s(x,q)\) holds by
Proposition 2.4.  Conversely, every word satisfying \(\mathsf A_s\) is a
canonical reduced representative of the same group element as \(W(x)\).
Uniqueness of free-product normal form implies that all such candidates spell
the same literal word.

To make the representation itself functional, order codes first by template
number and then lexicographically in \(\mathbb N^{m_s}\).  Every nonempty set
of codes has a least element.  Put
\[
\begin{aligned}
 \mathsf G_s(x,q):={}&\mathsf A_s(x,q)\\
 &\wedge\bigwedge_{r<s}\neg\exists q'\,\mathsf A_r(x,q')\\
 &\wedge\neg\exists q'\,[q'<_{\rm lex}q\wedge\mathsf A_s(x,q')].
\end{aligned}
\tag{3.3}
\]
This is Presburger, total on \(D\), and functional: exactly one pair
\((s,q)\) satisfies it for each \(x\).

### Lemma 3.1 (effective affine output on Presburger cells)

The graph (3.3) can be converted effectively into a finite, pairwise-disjoint
partition of \(D\) by exact Presburger cells.  On each cell \(s\) is fixed
and every coordinate of \(q\) is affine.  No claim is made that a cell is a
single polyhedron with only a fixed residue tag; its full Presburger formula
is retained.

### Proof

Effective Presburger elimination converts (3.3) to a finite semilinear
union.  Consider one linear component of its functional graph,
\[
 (x,q)=(x_0,q_0)+\sum_i n_i(a_i,b_i).
\tag{3.4}
\]
If \(\sum_i n_i a_i=\sum_i n'_i a_i\), functionality forces
\(\sum_i n_i b_i=\sum_i n'_i b_i\).  Hence the assignment
\(a_i\mapsto b_i\) is a well-defined homomorphism on the period lattice.
It follows that \(q\) is an affine function of \(x\) on this component's
projected domain.  The affine formula is integral on the actual projected
linear monoid.  A period with \(a_i=0\) must have \(b_i=0\), again by
functionality.  The projected domain may require an arbitrary semilinear or
Presburger description, which the output record keeps verbatim.

Order the finitely many resulting domain cells and replace the \(j\)-th by
itself minus the earlier cells.  Presburger sets are effectively closed under
difference.  The affine formula remains valid on the subset.  This gives a
disjoint cover, and the Presburger sentences
\[
 D=\bigcup_j C_j,
 \qquad C_j\cap C_k=\varnothing\ (j\ne k)
\tag{3.5}
\]
are decidable symbolic coverage and overlap checks.  \(\square\)

Thus each exact Presburger cell record contains a literal reduced template,
nonnegative affine surviving exponents, primitive core, phase and orientation tags, and
an exact domain.  Small exponents, zero powers, inverse cores,
commensurability, and torsion residues are not exceptional unproved cases;
they are branches of (3.2)--(3.3) and the DFA predicate.

## 4. Terminal `c`, exact length, and the indexed prefix stream

Fix an exact Presburger cell from Lemma 3.1.  Since \(V_s(q(x))\) is already
completely reduced, its quotient length is the affine function
\[
 L_s(x)=\sum_{r=0}^{m_s}|b_{s,r}|+
         \sum_{r=1}^{m_s}|v_{s,r}|q_r(x).
\tag{4.1}
\]
The predicate that its final letter is `c` is Presburger: run the same finite
DFA with output of the last nonempty block, or equivalently split on the
finitely many conditions saying which final fixed or powered block is the
last nonempty one.  Refine the Presburger cell by its truth value
\(\tau_s(x)\in\{0,1\}\).  Then
\[
 \ell_s(x)=L_s(x)-\tau_s(x)
\tag{4.2}
\]
is the exact length of \(\operatorname{cvert}(W(x))\), and the canonical
word is the first \(\ell_s(x)\) letters of \(V_s(q(x))\).  This applies
terminal deletion only after reduction of the complete product.

For each \(a\in\Sigma\), define
\(\mathsf{Letter}_{s,a}(x,r)\) by splitting on the fixed block or powered
block containing position \(r\).  In a powered block \(v^q\), the condition
is
\[
 B(x)\le r<B(x)+|v|q(x),
 \qquad r-B(x)\equiv j\pmod {|v|},
\tag{4.3}
\]
where the \(j\)-th letter of \(v\) is \(a\).  Here \(B(x)\) is the affine
length of preceding blocks.  Fixed blocks give finitely many affine equality
cases.  Restrict to \(0\le r<\ell_s(x)\).  The formulas are Presburger and,
for every such \(r\), exactly one letter predicate holds.

The same split gives an exact quotient-prefix record.  Let \(\ell\) be the
letter position and let \(\beta\) be the index of the powered block containing
it.  If \(\ell\) lies after \(k\) complete copies of that block and at phase
\(j\), the prefix before position \(\ell\) is
\[
 b_{s,0}v_{s,1}^{q_1(x)}b_{s,1}\cdots
 v_{s,\beta-1}^{q_{\beta-1}(x)}b_{s,\beta-1}
 v_{s,\beta}^{k}p_{\beta,j},
\tag{4.4}
\]
where \(p_{\beta,j}\) is one of the finitely many fixed prefixes of
\(v_{s,\beta}\), and \(k\) is tied to \(\ell\) by the corresponding affine
offset equality and congruence from (4.3).  Thus every indexed **quotient**
prefix is again a bounded product of fixed words with nonnegative affine
exponents and a finite phase selector.

If a supplied quotient schema prepends a fixed word \(a\), the generic
compiler applies to \(aW(x)\).  Likewise, after terminal deletion, its finite
template split can be supplied to a second generic quotient normalization.
If the deleted `c` lies inside the last positive copy of a powered block,
replace that final power by one fewer copy followed by the fixed proper
prefix.  This is the final-position case of (4.4), so `c_vertex` is not
treated as a homomorphism.

These statements concern only canonical quotient words.  They do **not**
construct the freely reduced signed word
\(\widehat q\,vCCv^{-1}\widehat q^{-1}\), distinguish positive from
negative `C` events, handle free cancellation at its boundaries, or prove
that `_KernelStream` accumulates each event at the stated vertex.  That
missing raw-stream lifting is Application Obligation B in Section 8.

## 5. Equality and exact shortlex first mismatch

### 5.1 Module-label equality

For arbitrary quotient words \(X,Y\),
\[
 \operatorname{cvert}(X)=\operatorname{cvert}(Y)
 \iff X^{-1}Y\in\{1,c\}.
\tag{5.1}
\]
Both implications follow from uniqueness of the reduced representative of a
right \(\langle c\rangle\)-coset.  Therefore equality of any pair of
explicitly supplied quotient schemas is the union of two effective
power-product equality loci.  This is another use for which published
equality semilinearity supplies exactly the needed output.  Refining each
generic quotient cell by (5.1) makes the equality truth value constant.

### 5.2 First mismatch and shortlex

Let \(X(x),Y(y)\) be two post-`c_vertex` streams supplied by Section 4, with
lengths \(\ell_X,\ell_Y\).  For fixed distinct letters \(a,b\in\Sigma\),
define \(\mathsf{Mis}_{a,b}(x,y,r)\) by
\[
\begin{aligned}
 0\le r<\ell_X=\ell_Y,
 \quad &\mathsf{Letter}_{X,a}(x,r),
       \mathsf{Letter}_{Y,b}(y,r),\\
 &\forall u\,[0\le u<r\Rightarrow
       \bigvee_{e\in\Sigma}
       (\mathsf{Letter}_{X,e}(x,u)\wedge
        \mathsf{Letter}_{Y,e}(y,u))].
\end{aligned}
\tag{5.2}
\]
Formula (5.2) is Presburger; its bounded universal quantifier is eliminated
effectively.  The disjunction over the six ordered pairs \(a\ne b\) has
exactly one pair and one \(r\) when the equal-length words differ, and no
witness when they are equal.  Its functional semilinear graph can be refined
by Lemma 3.1, so a cell record contains either `no mismatch` or the exact
affine formula on its full Presburger cell for the first mismatch position
and its two letters.

The exact code order is then
\[
 X<_{\rm shortlex}Y
 \iff
 \ell_X<\ell_Y
 \ \vee\ 
 \bigl[\ell_X=\ell_Y\ \wedge\
        \bigvee_{a<b}\exists r\,
        \mathsf{Mis}_{a,b}(x,y,r)\bigr],
\tag{5.3}
\]
where \(a<b\) uses \(T<c<t\).  Length comparison and the three possible
ordered mismatch-letter pairs are Presburger branches.  Refining by (5.3)
makes every requested shortlex result constant while retaining the exact
first-mismatch witness.

No equality theorem is used to infer (5.2) or (5.3).  Equality is used only
in (3.2) to select an already reduced representative and in (5.1) for the
separate equality predicate.  The lexicographic comparison is performed
letter by letter on the explicit post-`c_vertex` stream.

## 6. Well-foundedness and coverage of the generic quotient compiler

For one explicitly supplied schema, Proposition 2.4 recurses on its product
syntax with the measure
\[
 \mu(E)=\text{number of unprocessed product nodes of }E.
\tag{6.1}
\]
Powered and fixed leaves have measure zero.  At a product node both recursive
calls have strictly smaller syntax; prefix/suffix enumeration is a finite
nonrecursive loop over fixed words and phases.  There is no cancellation
recursion, so newly exposed or commensurable cores cannot create a loop.

DFA transformation powers range over a finite monoid.  Presburger
elimination and semilinear decomposition are terminating effective
procedures.  Disjointification processes a finite ordered list of exact
Presburger cells.  For each supplied schema the invariant is:

- the sign split is exhaustive and disjoint;
- Proposition 2.4 covers its canonical quotient output;
- formula (3.3) selects exactly one reduced code;
- Lemma 3.1 partitions the complete supplied domain by (3.5); and
- terminal, equality, length, first-mismatch, phase, orientation, and letter
  predicates are finite Presburger refinements.

A finite explicitly supplied list is handled one schema and one requested
pair at a time.  This proves termination, coverage, and disjointness of the
generic quotient compiler.  It does not provide a well-founded trace of the
literal AST, because the source-to-schema map, raw-stream constructor, typed
constructor manifest, and actual query list are not supplied.

## 7. Safe theorem boundary

### Theorem 7.1 (generic quotient powered-product normalizer)

Let \(Q=C_2*\mathbb Z\) use the pinned quotient alphabet and canonical
reduced-word section (1.1)--(1.3).  Given an explicitly supplied finite list
of bounded power-product schemas (1.5), with fixed quotient factor words,
affine integer exponent maps, exact Presburger domains, and an arbitrary
fixed finite tuple of parameters, there is an effective procedure returning
a finite disjoint partition by exact Presburger cells.  On each cell the
selected quotient normal form is represented by fixed blocks and affine
powers.  The procedure also returns:

1. the post-terminal-`c` word and exact length;
2. indexed quotient-letter and quotient-prefix predicates;
3. group and right-coset equality for each explicitly supplied pair; and
4. exact shortlex order and its first-mismatch predicate.

Repeated variables, affine exponents, and signed exponents are allowed after
the finite sign split.  The output exponent maps are affine on their full
Presburger cells; no simpler polyhedron-plus-residue representation is
claimed.

### Proof

Lemmas 2.1--2.3 and Proposition 2.4 construct a finite bounded cover of each
completely reduced quotient output, including vanished separators and newly
exposed blocks.  Formula (3.2) uses imported equality semilinearity only to
select candidates already accepted by the canonical-language predicate.
Uniqueness of quotient normal form and the least-code formula (3.3) make the
selection total and functional.  Lemma 3.1 gives affine outputs on exact
disjoint Presburger cells.  Sections 4--5 give terminal deletion, quotient
length, indexed quotient letters and prefixes, right-coset equality, and
first-mismatch shortlex.  The measure (6.1) and the finite-cell invariant in
Section 6 prove termination, coverage, and disjointness.  \(\square\)

This theorem is only a quotient compiler.  It does not identify the raw 305
positions with its input schemas, reproduce the signed raw `_KernelStream`,
bound the literal AST's variable arity, trace the literal AST, or materialize
that application's records.

## 8. Period-two application obligations

The exact literal-AST normalizer theorem and the former statement that no
normalizer query class remains are withdrawn.  The intended application is
open until all four obligations below are emitted and verified.

### Application Obligation A: source-schema manifest

Emit a finite table indexed by
\[
 (\nu,\mathsf{block},\mathsf{letter\ position},
   \mathsf{orientation},\mathsf{slot})
\tag{8.1}
\]
for all 305 raw forest positions, plus the moving slot-zero singleton and
every fixed base and anchor atom.  Each row must contain:

- the exact raw forest prefix and letter;
- its coefficient, sign, and complete Presburger domain;
- the right-deck/module-vertex construction;
- the resulting quotient bounded-power schema with all fixed factors and
  affine exponents; and
- a symbolic equality proving that the row contributes exactly the approved
  signed current.

Coverage must show that every raw position/orientation/slot is present once
with the correct multiplicity.  The count 305 alone is not this manifest.

### Application Obligation B: signed raw `_KernelStream` lifting

For every selected canonical quotient template \(v\) and every fixed AST
transport word \(\widehat q\), construct finite bounded templates for the
freely reduced **signed** word
\[
 \operatorname{multiply}
 (\widehat q,\operatorname{relation\_generator}(v),\widehat q^{-1})
 =\operatorname{red}(\widehat q\,vCCv^{-1}\widehat q^{-1}).
\tag{8.2}
\]
The lifting record must:

- branch exactly over free cancellation at both outer boundaries and the
  boundaries adjacent to the two raw `C` letters;
- state and verify the finite cancellation bound used by those branches;
- preserve the sign of every raw `C`/`C^{-1}` letter;
- give the exact positive-event predicate and negative-event predicate used
  by `append_literal`; and
- identify the running quotient prefix and post-prefix `c_vertex` attached
  to every emitted event, including events on the inverse half.

Quotient orientation tags and the central letters `cc` do not by themselves
discharge this lifting obligation.

### Application Obligation C: typed AST and variable-arity manifest

Emit the literal two-endpoint constructor trace.  For every correction,
product, inverse, conjugation, transport, section, equality, and order node,
record its input query types, output query types, retained parameter
variables, newly introduced selector/position variables, and exact output
domain.  Then prove by induction over this concrete manifest that every
derived query is a bounded quotient schema after applying Obligations A and
B.

The fixed AST implies that some finite maximum arity exists once this trace
and its constructors are proved finite, but no bound is established here.
In particular, the former bound two is withdrawn: a source position may
survive while a degree-two raw stream introduces an ordered pair of event
positions, so arity three is not excluded.  Every downstream bounded-fiber
claim must use the maximum actually proved by the manifest.

### Application Obligation D: materialized query and chamber tables

From A--C, emit the complete machine-readable query manifest for both
endpoints and run Theorem 7.1 on every quotient schema and requested pair.
The output must include the selected normal-form records, imported equality
records, raw-stream event records, exact shortlex first mismatches, and the
full Presburger formula of every cell.  It must also include symbolic checks
that each query's cells cover its admissible domain and that every pairwise
cell intersection is empty.  A generic effective procedure without these
application records is not a completed fixed-AST certificate.

### Remaining normalizer application class

The remaining class is the entire unmaterialized literal-AST trace: all
source atoms from A, all signed transport-event prefixes from B, all derived
action/inversion/product/tensor equality and order queries from C, and all
instantiated tables and checks from D.  Finiteness is expected from the fixed
source and AST, but its exact manifest and application-dependent variable
arity remain unproved.

After A--D, the separate endpoint coefficient DAG, root quotient/zero-linear
typing, commutator/wedge check, bounded-fiber counting, eight edge strata,
and seed would still remain.

The only imported group result in the generic theorem is effective equality
semilinearity, precisely where its output is a yes/no equality locus between
fixed bounded quotient power products.  The quotient stream and shortlex
comparison are separate consequences of the bounded-output cover,
canonical-language DFA, and Presburger first-mismatch formula.

## 9. Bounded evidence and provenance

No grid, index replay, source census, or broad computation was run for this
memo.  The bounded source facts used are the already approved six block
triples, the fixed count \(100+113+92=305\), and the fixed
sixteen-occurrence AST with slot counts \((6,4,2,2,2)\).  The quotient and
ordering conventions were read directly from
`depth4_period_two_lift_certificate.py` and
`depth4_period_two_phi_infinity_hessian_certificate.py`.

The supporting proof boundary and source reviews are:

- `period_two_unary_defect_transducer.md` and its approved re-review;
- `virtually_free_power_product_literature.md`;
- `period_two_companion_identity.md` and its approved review; and
- `period_two_unary_ray_recurrence.md` and its approved review.

## Fix round 1

Review status: all eight findings in
`restricted_power_product_normalizer_review.md` are addressed at the safe
theorem boundary.  No computation, replay, grid, census, or tracked edit was
performed.

1. **Operand/cover names — addressed.**  Lemma 2.3 now uses \(U,V\) for the
   actual reduced operands and \(K,L\) for their cover languages.  Its proof
   explicitly uses \(U\in K\), \(V\in L\), so noncanonical words elsewhere
   in the covers cause no ambiguity.
2. **Canonical selection — retained.**  `Red_s`, imported equality
   semilinearity, and the least-code selector remain unchanged in substance.
   Equality still selects an already reduced candidate and is not used to
   infer shortlex.
3. **Presburger cells — qualified.**  Lemma 3.1 now claims affine outputs on
   full exact Presburger cells only.  It makes no simple polyhedron-plus-
   residue claim, and the verifier-facing record retains the entire cell
   formula.
4. **Quotient prefix index — addressed.**  Formula (4.4) uses \(\ell\) for
   the letter position and \(\beta\) for the powered-block index.  Section 4
   is explicitly limited to quotient letters and quotient prefixes.
5. **Raw 305 positions — withdrawn and isolated.**  The raw triples and
   count are no longer asserted to supply schemas (1.5).  Application
   Obligation A requires a row for every raw position/orientation/slot and
   every fixed atom, including its right-deck/module-vertex proof.
6. **Literal `_KernelStream` — withdrawn and isolated.**  The former claim
   that quotient prefixes already reproduce the literal stream is removed.
   Application Obligation B requires signed raw free reduction, boundary
   branches and their bound, positive/negative `C` events, inverse-half
   events, and the exact event vertex.
7. **Variable arity — corrected.**  The bound two is withdrawn.  Application
   Obligation C requires a typed constructor/variable manifest and an
   inductive proof of the actual finite maximum; no numerical maximum is
   claimed here.
8. **AST theorem and emitted tables — withdrawn.**  Theorem 7.1 is now only
   the generic quotient compiler.  The statement that no normalizer query
   remains is deleted.  Application Obligation D requires the materialized
   query, cell, equality, raw-event, coverage, and overlap records before a
   fixed-AST certificate can be claimed.

**Exact next deliverable.**  Emit Application Obligation A as a
machine-readable source-schema manifest with exactly one provenance row for
each of the 305 raw forest positions under every required orientation and
slot decoration, plus explicit rows for the moving slot-zero singleton,
fixed bases, and anchors.  Each row must contain the five fields listed in
Section 8 and a symbolic check against the approved signed right-deck current.
This manifest is the first input needed before raw-stream lifting or the
typed AST trace can be audited.
