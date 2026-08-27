# Primary-source audit: fixed power products in \(C_2*\mathbb Z\)

Date: 2026-07-29

## Bottom line

The published group-theoretic results justify one strong but narrow imported
lemma:

> For a fixed finitely generated group \(Q=C_2*\mathbb Z\), the parameter
> locus on which a fixed bounded product of powers is equal to another fixed
> bounded product of powers is effectively Presburger/semilinear.  Repeated
> exponent variables and additional Presburger constraints on the exponents
> are allowed by an effective reduction.

They do **not** provide a canonical reduced-word normalizer, a terminal-`c`
coset-section flag, exact shortlex-order predicates, or a disjoint exhaustive
table of canonical word chambers.  The power-word and power-compressed
subgroup results are decision algorithms for fully instantiated exponents;
they do not strengthen the parametric output.

Once the missing word predicates have actually been compiled to Presburger
formulas, a separate primary result of Woods does justify exact finite-fiber
parametric counting.  A particularly safe parity backend is an exact rational
generating function reduced modulo two.  This is a static symbolic backend,
not a finite weighted automaton on the synchronous unary convolution of
\((i,j)\).

Consequently the smallest bespoke theorem still needed by the **literal AST**
is an effective Presburger compiler for the **canonical `c_vertex` stream and
post-`c_vertex` shortlex comparison** of the finite collection of bounded
power-product schemas it generates.  The stream part is necessary because
the unary transport term literally reads
`qhat + r_v + inverse(qhat)`; a final comparison predicate alone would not
reconstruct the letters and prefixes of the moving canonical word `r_v`.
The theorem need not reprove group equality: equality is already imported.

## Scope of this audit

The local design under audit is
`.claude/worktrees/codex-proofs/.scratch/period_two_unary_defect_transducer.md`
and its hostile review.  Its moving labels have the form

\[
  a_0u_1^{L_1(p,z)}a_1\cdots u_k^{L_k(p,z)}a_k,
\]

where \(k\) is bounded, \(p=(h,d)\) are the two unbounded parameters, \(z\)
is a tuple of at most two bounded position variables, and the \(L_r\) are
affine on a Presburger domain.  Negative powers can be removed by the already
required finite sign split, replacing \(u^n\) by \((u^{-1})^{-n}\) on a
negative branch.

The five questions are deliberately separated below:

1. equality loci;
2. disjoint exhaustive canonical chambers;
3. terminal-`c` canonical coset normalization;
4. exact shortlex order; and
5. bounded-fiber parity counting.

## Primary sources read

1. Michael Figelius, Markus Lohrey, Georg Zetzsche, *Closure properties of
   knapsack semilinear groups*, arXiv:1911.12857v2, 26 Nov 2024:
   [version-pinned PDF](https://arxiv.org/pdf/1911.12857v2),
   [journal DOI](https://doi.org/10.1016/j.jalgebra.2021.08.016).
2. Markus Lohrey, *Knapsack in hyperbolic groups*, arXiv:1807.06774v2:
   [version-pinned PDF](https://arxiv.org/pdf/1807.06774v2),
   [journal DOI](https://doi.org/10.1016/j.jalgebra.2019.04.008).
3. Markus Lohrey, *Subgroup Membership in \(GL(2,\mathbb Z)\)*:
   [STACS 2021 primary paper and DOI](https://doi.org/10.4230/LIPIcs.STACS.2021.51),
   [final journal DOI](https://doi.org/10.1007/s00224-023-10122-2).
4. Markus Lohrey and Armin Weiß, *The Power Word Problem*:
   [arXiv PDF](https://arxiv.org/pdf/1904.08343),
   [MFCS 2019 primary paper and DOI](https://doi.org/10.4230/LIPIcs.MFCS.2019.43).
5. Kevin Woods, *Presburger arithmetic, rational generating functions, and
   quasi-polynomials*, arXiv:1211.0020:
   [primary PDF](https://arxiv.org/pdf/1211.0020),
   [JSL DOI](https://doi.org/10.1017/jsl.2015.4).

Only the primary papers above are used for substantive claims.  Search-result
snippets, surveys, theses, and later citations were not used as theorem
evidence.

## Imported group theorems

### 1. Lohrey, Theorem 8.1: every hyperbolic group is knapsack-tame

Theorem 8.1 (printed p. 10) states that every hyperbolic group is
knapsack-tame.  The definition immediately preceding the theorem (Section 5,
printed pp. 7--8) says that for every knapsack expression \(E\), a finite
semilinear representation of \(\operatorname{sol}(E)\) can be computed; tame
adds a polynomial bound on the **magnitude** of the vectors in a
representation.  The theorem is uniform in the depth of \(E\); the number of
powered factors is not assumed fixed.

Since \(C_2*\mathbb Z\) is virtually free, hence hyperbolic, this directly
gives an effective finite semilinear representation of

\[
 \{(n_1,\ldots,n_k)\in\mathbb N^k:
   g_1^{n_1}\cdots g_k^{n_k}=g\}.
\]

The paper expressly warns immediately after Theorem 8.1 that the total number
of vectors in a semilinear representation can be exponential, even for
\(\mathbb Z\).  The polynomial magnitude bound is not a polynomial total
output-size bound.

### 2. FLZ, Section 4.1: repeated variables remain effectively semilinear

Section 4 (printed pp. 5--6) distinguishes a knapsack expression, in which
each exponent variable occurs once, from an exponent expression, in which a
variable may recur.  Section 4.1 (printed p. 6) makes effectiveness part of
the definition of knapsack-semilinearity and gives the exact reduction for a
repeated-variable expression: replace occurrences by fresh variables,
intersect the resulting semilinear set with the linear equalities identifying
the fresh copies, and restrict back to the original coordinates.  The paper
states that intersection and restriction are effective.

This unnumbered Section 4.1 argument is the precise citation needed when the
same parameter appears in more than one powered factor.  Remark 4.1 stresses
that bare existence of a semilinear set is not enough; the representation must
be computable.

### 3. FLZ, Theorem 5.25 and Remark 5.27: a direct free-product route

Theorem 5.25 (printed pp. 23--24) states that if \(G_1,G_2\) are
knapsack-semilinear, then \(G_1*G_2\) is knapsack-semilinear.  With
\(K(n,m)=\max(K_{G_1}(n,m),K_{G_2}(n,m))\), it gives

\[
 K_{G_1*G_2}(n,m)
 \leq \max\{K(6mn,m),\ O(mn^4)\}.
\]

Taking \(G_1=C_2\) and \(G_2=\mathbb Z\) gives the same conclusion without
invoking hyperbolicity.  Remark 5.27 (printed pp. 24--25) records the
constructive finite-union decomposition into factor-group solution sets plus
an explicitly computable semilinear constraint.  Again, the degree \(m\) is
an input parameter, not a fixed constant.

Theorem 5.28 is only a nondeterministic polynomial-time **decision**
reduction for knapsack in a free product.  It is not the representation
theorem and should not be cited as one.

### 4. Safe affine-parameter corollary

The preceding results imply the following corollary, although none of the
papers states it in this packaging.

Let \(D(p,z)\) be a Presburger domain.  Let \(W_1(p,z),W_2(p,z)\) be fixed
bounded products of fixed group words whose power exponents are affine
integer functions of \((p,z)\), nonnegative on \(D\).  Then

\[
 \{(p,z):D(p,z)\land W_1(p,z)=_Q W_2(p,z)\}
\]

is effectively Presburger.

To derive it, introduce a fresh nonnegative exponent coordinate for each
powered occurrence, use Theorem 8.1 or Theorem 5.25 plus Section 4.1 for the
group equality, intersect with the Presburger graphs tying the fresh
coordinates to the affine forms, and project to \((p,z)\).  All these
operations are effective for semilinear/Presburger sets.  A finite sign split
handles signed affine exponents.

This also supplies equality of canonical \(Q/\langle c\rangle\) module
vertices without computing either canonical word:

\[
 \operatorname{cvert}(x)=\operatorname{cvert}(y)
 \iff x^{-1}y\in\{1,c\},
\]

a finite union of two imported power-product equality loci.

## What the group papers do not import

| Certificate obligation | Published result supplies it? | Exact reason |
|---|---:|---|
| Effective group-equality locus for a bounded power product | **Yes** | Lohrey Theorem 8.1; alternatively FLZ Theorem 5.25. |
| Repeated exponent variables | **Yes** | FLZ Section 4.1, p. 6. |
| Extra affine/congruence/domain constraints | **Yes, by closure** | Intersect the imported semilinear locus with the Presburger graph/domain and project. |
| Canonical-coset-label equality | **Yes, indirectly** | Reduce to \(x^{-1}y\in\{1,c\}\). |
| Pairwise-disjoint exhaustive chambers with a reduced-word template on every chamber | **No** | A semilinear representation is a finite union of linear sets and may overlap.  Neither theorem outputs reduced-word templates, phase/orientation data, or a canonical chamber partition. |
| Whether the reduced word ends in `c`, and the actual post-deletion `c_vertex` normal form | **No** | This is a normal-form/last-syllable predicate, not an equality to a fixed group element.  No cited theorem returns it. |
| Exact length of `c_vertex(W(p,z))` | **No** | Knapsack semilinearity concerns equality solutions, not normal-form length. |
| Exact shortlex order after `c_vertex` | **No** | Neither equality semilinearity nor power-word decision computes first mismatch or order between canonical words. |
| Bounded-fiber parametric parity count | **No, not from the group papers** | Their output is an equality solution set, not a count of auxiliary positions or a parity theorem. |
| Finite weighted automaton on synchronous unary convolution | **No** | None of the results makes arbitrary Presburger relations regular in that encoding; for example \(i=2j\) gives an \(a^jb^j\)-type convolution language. |

Two subtleties matter.

First, effective semilinearity permits Boolean refinement into a disjoint
Presburger partition **after the relevant predicate is known**.  It does not
manufacture a reduced-word predicate or a canonical word template.  Thus it
cannot be cited to discharge Normalizer Obligation 5.1 in the local design.

Second, the theorem's semilinear representation may have many components and
need not be practical.  “Effective” is the correct proof-level claim;
“small,” “polynomial total output,” and “certificate already emitted” are not.

## Power-word and virtually-free subgroup papers

These papers are relevant only as a boundary check.  Exact results are:

- Lohrey--Weiß, full arXiv **Theorem 3** (paper p. 23:6),
  **Theorem 7** and **Corollary 8** (paper p. 23:7); the corresponding MFCS
  numbering is **Theorem 2**, **Theorem 6**, and **Corollary 7** (paper
  p. 43:6).  Together they reduce the power-word problem for a finitely
  generated virtually free group to the word problem of \(F_2\).
- Lohrey, final journal **Theorem 1** (pp. 1100--1101), **Lemma 11**
  (pp. 1101--1102), and **Corollary 2** (p. 1102); the corresponding STACS
  numbering is **Theorem 12**, **Lemma 13**, and **Corollary 14** (paper
  pp. 51:13--51:14).  Together they give polynomial-time power-compressed
  subgroup membership for a fixed finitely generated virtually free group.

- A power word has **binary encoded, already instantiated integer
  exponents**.  Its power-word problem asks whether that one represented
  element is the identity.
- The virtually-free subgroup paper takes fully instantiated power words
  \(w_0,\ldots,w_n\) and decides whether the represented element of \(w_0\)
  belongs to the subgroup generated by the represented elements of the other
  words.

Their algorithms are valuable for evaluating one large parameter instance,
but they do not leave the exponents symbolic and do not output a semilinear
parameter locus.  They also do not output canonical reduced words, a
terminal-letter predicate, exact shortlex order, or a disjoint chamber table.
They therefore cannot repair the missing all-index normalizer.  The more
detailed version/numbering map is recorded in the companion audit
`.scratch/virtually_free_powerword_audit.md`.

## Primary counting theorem and its exact usable scope

Woods works with a Presburger formula \(F(c,p)\), counted variables \(c\),
and parameter variables \(p\).  Definition 1.6 (printed p. 2) assumes that
every fiber \(\{c:F(c,p)\}\) is finite.  Theorem 1.10 (printed p. 3) proves
that its counting function

\[
 g_F(p)=\#\{c\in\mathbb N^d:F(c,p)\}
\]

is a piecewise quasi-polynomial and that

\[
 \sum_{p\in\mathbb N^n}g_F(p)x^p
\]

is a rational generating function.  The number of parameter variables
\(n\) is arbitrary.  The proof of \(A\Rightarrow C\) in Section 4.1 (printed
p. 8) is constructive in the ordinary computability sense: apply effective
Presburger quantifier elimination (Theorem 3.2), disjointify the resulting
polyhedron/lattice pieces, construct their rational generating functions
(Theorem 3.3), and eliminate the counted variables by substitution
(Theorem 3.5).  Section 5.2 notes the algorithmic equivalence of the rational
and suitably represented piecewise forms; fixed-dimension hypotheses there
concern polynomial-time bounds, not existence/effectiveness.

This does justify the static counting backend **provided**:

1. every equality/order/domain condition has first been supplied as an exact
   Presburger formula;
2. finite fibers are proved on the complete admissible parameter domain; and
3. contribution multiplicities are expressed as counted Presburger tuples.

For parity, the safest exact representation is the rational generating
function.  Form the integer linear combination of the generating functions
for all constant-weight contribution types, put the difference from the
target over a common product of denominators \(1-x^a\), and require an
**integral** numerator.  The parity identity holds exactly when every
coefficient of that numerator is even; equivalently, the resulting rational
function is zero over \(\mathbb F_2\).  The standard denominators have
constant term one, so they are invertible as formal power series.  This
avoids trying to reduce an arbitrary rational scalar coefficient modulo two,
verifies every parameter simultaneously, and does not assert
unary-convolution regularity.

Arbitrary opaque variable polynomial weights are outside Theorem 1.10's
literal counting-function hypothesis.  The interface should instead expand
them into an explicit Presburger multiplicity relation.  Constant signed
weights are harmless; products such as ordered-pair or binomial
multiplicities should be represented by extra bounded counted variables and
an exact ordering/distinctness predicate.  If that expansion is not given,
a separate weighted-counting theorem is required.

## Smallest bespoke theorem still required

The imported equality and counting results allow the missing bespoke theorem
to be narrower than the proposed full normal-form theorem.

### Bounded power-product canonical-stream/comparison theorem

Fix the generator order and the canonical reduced-word section for
\(Q=C_2*\mathbb Z\).  There is an effective procedure which, from a fixed
bounded power-product schema \(W(p,z)\), affine exponent maps, and a
Presburger domain on which all displayed exponents are nonnegative, returns:

1. a Presburger formula for the terminal-`c` branch of the completely reduced
   product;
2. a finite Presburger-indexed stream for
   \(\operatorname{cvert}(W(p,z))\): its length, the letter at every bounded
   position, and a bounded-power-product description of the corresponding
   canonical prefix; and
3. for a pair \(W_1,W_2\), a Presburger formula equivalent to

\[
 \operatorname{key}(\operatorname{cvert}(W_1(p,z)))
 <_{\rm shortlex}
 \operatorname{key}(\operatorname{cvert}(W_2(p,z'))).
\]

The procedure must apply quotient reduction to the complete product before
the terminal-`c` deletion and must apply `c_vertex` again after every
inversion multiplier required by the AST.  The indexed-prefix output must be
strong enough to replay every `_KernelStream` prefix in the literal transport
terms; merely returning the final length and comparison truth value is not
enough.

This one theorem subsumes terminal-`c`, canonical transport streaming,
length, and first-mismatch handling.  It need not reprove equality.  If the
implementation chooses a chamber proof, then coverage and pairwise
disjointness of the chambers are verification obligations, not extra
mathematical assumptions.

No primary result audited here proves this theorem.  It is plausible for
fixed bounded products in a virtually free group, but plausibility is not an
imported certificate.

## Safe certificate interface

The proof artifact should expose the following records and nothing stronger.

### Input record

- `schema_id` and the fixed factor list
  \((a_0,u_1,a_1,\ldots,u_k,a_k)\);
- generator order and the exact `qred`/`c_vertex` convention;
- affine exponent maps, including the finite sign/residue branch;
- one Presburger admissibility formula in \((h,d,z)\);
- provenance identifying whether a requested predicate is imported equality
  or bespoke post-`c_vertex` shortlex order.

### Predicate output

- `eq_formula`: a quantifier-free Presburger formula or explicit semilinear
  representation for group/coset equality, with the exact instantiated
  exponent expression and the cited imported theorem;
- `stream_formula`: the bespoke length/letter/prefix relation for the
  post-`c_vertex` canonical word, with every position fiber proved bounded;
- `lt_formula`: the bespoke exact post-`c_vertex` shortlex formula;
- optionally `terminal_c_formula` and an affine length formula if those are
  useful intermediate witnesses, but the verifier must not trust them unless
  their equivalence is checked;
- if chambers are used: each chamber's formula and word-comparison witness,
  plus machine checks that the chamber union is the admissible domain and all
  pairwise intersections are empty.

### Counting output

- a finite list of contribution types with **constant integer weights**;
- for each type, an exact Presburger formula in parameter and counted
  position variables;
- a proof that every counted fiber is finite;
- the exact rational generating function produced from each formula;
- the combined numerator/denominator identity over \(\mathbb F_2\) against
  each of the eight target edge strata and the seed;
- root quotient/zero-integral-linear checks before invoking the commutator
  lemma and wedge projection.

### Fail-closed verifier rules

The verifier must reject if a formula is present without theorem provenance,
if a shortlex predicate is replaced by group equality, if any chamber cover
is sampled rather than proved exhaustive, if a fiber finiteness proof is
missing, if variable polynomial weights have not been expanded to counted
tuples, or if a unary-convolution automaton is offered as a substitute for
general Presburger counting.

## Status against the local design

- **Imported now:** effective equality/coset-equality loci for every fixed
  bounded power-product query, including repeated variables and affine
  parameter restrictions.
- **Published counting backend available:** exact finite-fiber Presburger
  counting via Woods, with a safe rational-generating-function parity check.
- **Still unsupported:** the design's claimed exhaustive canonical chamber
  lemma, terminal-`c` normal forms, and exact post-`c_vertex` shortlex
  predicates.
- **Bespoke theorem needed:** the bounded power-product canonical-stream/
  comparison theorem above.
- **Not established by any cited paper:** that the actual AST predicate
  tables have already been generated, that the coefficient DAG closes, or
  that the eight edge identities and seed hold.
