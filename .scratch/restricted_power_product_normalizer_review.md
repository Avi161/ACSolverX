# Hostile review: restricted powered-product normalizer

Date: 2026-07-29

## Verdict

**REFUTED as written.**  The quotient-only core is substantially stronger than
the former overlap sketch and is credible: Lemmas 2.1--2.3 give a valid finite
bounded cover, canonical-language recognition and imported equality
semilinearity select the unique reduced word, and the resulting quotient word
supports exact terminal-`c`, indexed-letter, prefix, and first-mismatch
Presburger predicates.

The stated theorem nevertheless claims the exact literal-AST normalizer, and
that application is not proved.  The memo never constructs the map from the
305 raw forest-path positions to the asserted quotient schemas, does not lift
the quotient stream to the signed raw free-group word actually consumed by
`_KernelStream`, and does not establish its claimed bound of two bounded
position variables.  In fact, its own description can retain a source path
position and add two stream positions in a degree-two term.  The fixed-AST
measure therefore proves termination only for an assumed quotient-schema
trace, not coverage of the actual trace.  No instantiated chamber system or
machine-checkable trace is emitted.

## Numbered findings

### 1. Lemmas 2.1--2.3 and vanished blocks — APPROVE

For a fixed quotient word, cyclic conjugation gives
`qred(u^n)=x r^n x^{-1}` away from the trivial and order-two cases.  This is a
bounded language, and the parity split for a core conjugate to `c` is exact.
Finite bounded languages are effectively closed under taking prefixes and
suffixes by choosing the cut factor and its finite phase.

The use of

\[
  \operatorname{Pref}(K)\operatorname{Suff}(L)
\]

in Lemma 2.3 remains valid when the cover languages contain noncanonical
words.  The actual reduced operands (A,B) are members of some cover
languages (K,L); maximal boundary cancellation writes the output as a
literal prefix of (A) followed by a literal suffix of (B), hence as a
member of the displayed superset.  Empty prefixes and suffixes cover complete
disappearance of either operand.  Left-associated induction also covers the
later meeting of blocks exposed when all intervening blocks vanish.  The
cover may be extremely redundant, but it is finite and effective.

Smallest repair: use distinct names for reduced operands and cover languages
in Lemma 2.3.  The present reuse of `B` obscures, but does not invalidate, the
argument.

### 2. `Red_s`, equality semilinearity, and least-code selection — APPROVE

`Red_s(q)` is effectively Presburger.  A DFA for the forbidden adjacent
pairs composes the transformations induced by the fixed blocks; powers of a
finite transformation have threshold-periodic behavior.  Explicit zero-power
branches make newly exposed boundaries visible to the same run.

The imported equality theorem is used within its approved boundary.  After
introducing one nonnegative coordinate for each power occurrence, FLZ's
repeated-variable reduction and effective Presburger intersection/projection
handle repeated parameters, affine exponent graphs, congruence domains, and
auxiliary bounded position variables.  The split `L>=0` versus `L<0` handles
signed affine exponents without losing `L=0`.

The template-first, tuple-lexicographic minimum in (3.3) exists because every
nonempty subset of a finite product of `N` has a lexicographic least element.
Its definition is Presburger.  Cover existence, `Red_s`, and uniqueness of
free-product normal form make the selected code total and functional.  This
does not use equality semilinearity to infer shortlex.

No repair is required.

### 3. Functional semilinear graph versus affine chambers — APPROVE the conclusion; REVISE the advertised cell form

A linear component contained in a functional graph really does determine an
affine output on its projected domain.  Any integral relation among projected
periods can be separated into its positive and negative parts; functionality
then forces the corresponding relation among output periods.  Thus the period
map extends to a homomorphism on the generated lattice and to a rational
linear map on the ambient rational span.  It is integral on the component's
actual projected domain.  Projecting finitely many semilinear components and
subtracting earlier domains gives a finite disjoint Presburger cover on which
the output formula remains valid.

What is not proved by the two sentences in Lemma 3.1 is the stronger informal
picture that every domain cell is merely one polyhedron plus a fixed list of
residue classes.  A projected linear monoid may require an arbitrary
semilinear/Presburger description.  The theorem's formal use of exact
Presburger domains is safe; the phrase “affine/residue chambers” is safe only
if it means affine outputs on Presburger cells.

Smallest repair: either make that wording explicit, or add an effective
Smith/Hermite-normal-form and patterned-polyhedron decomposition proving the
stronger representation.  A verifier must retain the full Presburger cell
formula, not only a residue tag.

### 4. Quotient terminal deletion, indexed streams, and shortlex — APPROVE conditionally

Once a selected literal template is certified reduced, (4.1)--(4.3) give its
exact length, terminal letter, and indexed letter relation.  If terminal `c`
lies in the last positive copy of a powered block, the split `q>0` followed by
`v^(q-1)` and the fixed proper prefix is exact; deletion is performed after
complete reduction and is not treated as a homomorphism.  The same phase
split gives the quotient prefix before each indexed letter.

The bounded universal quantifier in (5.2) is a legitimate Presburger
quantifier.  It requires equality at every earlier bounded position and a
distinct pair at the witness, so it returns exactly the first mismatch.
Together with exact lengths and the order `T<c<t`, (5.3) is the code's exact
shortlex order.

This finding approves predicates on an already obtained canonical **quotient
word**.  It does not approve the later claim that these predicates already
describe the raw forest word consumed by `_KernelStream`; that is Finding 6.

Smallest repair: fix the overloaded index in (4.4), where `r` denotes both a
letter position and a powered-block number.  The intended prefix-before-letter
formula is otherwise correct.

### 5. The 305 forest positions are not instantiated quotient schemas — REJECTED

Section 1 displays six triples in the raw complete-cover alphabet
`a,A,b,B,g,G` and the raw factorization

\[
  \operatorname{red}(P_\nu^i C_\nu Q_\nu^{i-j}).
\]

It then asserts, without a construction, that every path-position atom has a
quotient label of form (1.6).  The count `100+113+92=305` counts raw letter
positions; it is not an enumeration of their forest-generator images or of
their quotient labels.  The memo gives neither the right-deck-to-module-vertex
map for a position nor the fixed prefix/suffix words and affine exponents
produced by that map.  Consequently the hypotheses of the quotient compiler
have not been checked for the actual source atoms.

This is exactly the free-product/forest-path mismatch that an “exact query
set” must close.  Referring to an approved count and to source code does not
define the compiler input or let a verifier check that every position,
orientation, slot-zero singleton, base atom, and anchor is included.

Smallest repair: emit a finite source-schema table indexed by
`(nu, block, letter-position, orientation, slot)` plus every fixed atom.  Each
row must give its raw forest prefix, coefficient/sign/domain, exact quotient
image as a bounded power product, and a symbolic equality to the approved
right-deck current.  Then derive (1.6) row by row.

### 6. Quotient prefixes do not yet compile the literal `_KernelStream` — REJECTED

The literal implementation does not stream only the word represented in
`Sigma={T,c,t}`.  It forms the raw free-group word

\[
  \widehat q\,v C C v^{-1}\widehat q^{-1}
\]

using free reduction, and `append_literal` distinguishes `C` from `C^{-1}`
when deciding whether to emit a positive or negative kernel letter.  Only the
running prefix is quotient-reduced.  By contrast, Section 4 constructs
prefixes of the canonical quotient template, says that fixed outer portions
are appended, and merely states that the central `cc` letters are retained.
It gives no finite branch construction for raw free cancellation at the
outer boundaries, no signed-`C` event predicate on the inverse half, and no
proof that the `c_vertex` attached to each emitted event is the one returned
by the actual stream.

Collapsing both signs of `C` to `c` is harmless for quotient normalization
but not for `_KernelStream` emission.  Primitive-core orientation tags do not
by themselves prove that the lost raw sign and free-reduction history have
been reconstructed.

Smallest repair: prove a raw-stream lifting lemma.  From each canonical
quotient template for (v) and each fixed (q), it must construct finite
bounded templates for the freely reduced signed word
`multiply(q, relation_generator(v), inverse(q))`; give exact predicates for
every positive/negative `C` event; and identify the post-prefix `c_vertex`.
The proof may exploit that (q) is fixed and boundary free cancellation is
bounded, but it must state and verify that bound.

### 7. The two-position invariant and derived-query closure — REJECTED

The claimed grammar permits `z` to contain at most two bounded position
variables.  Its own transport description does not preserve that invariant.
A source atom can already depend on one path-position variable.  Section 4
then adds an additional stream-position variable for a prefix, while a
degree-two internal stream term can require an ordered pair of stream
positions.  Unless one proves that a selector replaces the source variable,
or that all kernel-event positions are a fixed finite set independent of the
moving word, such a term depends on the source position plus two stream
positions: three bounded variables.

The sentence “degree two uses at most a pair” is not an induction.  Nor does
the prose syntax trace enumerate which variables survive products,
inversions, correction aggregation, transports, and tensor pairs.  A fixed
AST guarantees some finite maximum arity and a finite number of constructor
applications; it does not imply the asserted maximum arity two.

Smallest repair: provide a typed constructor table with, for every literal
AST gate, its input query types, output query types, retained variables, new
variables, and maximum arity.  Prove the arity invariant inductively.  If the
raw-stream lifting lemma shows that event positions are only finite selectors,
say so and remove the spurious stream counters.  Otherwise widen the theorem
to the actual finite arity and re-audit every downstream bounded-fiber query.

### 8. Well-foundedness and “effective compiler” versus emitted tables — REJECTED for the stated AST theorem

The product-syntax measure (6.1) is sound for an explicitly supplied quotient
schema.  Given a formal constructor-to-schema transformation, finite
branching at each level of a finite AST would also make the chamber induction
well founded; post-`c_vertex` canonicalization is not intrinsically circular.

The memo has not supplied that formal trace.  Its AST-height measure assumes
that every actual constructor output has already been converted to one of the
schemas and arities disputed in Findings 5--7.  Therefore the final invariant
proves coverage and disjointness only for whatever quotient schemas the
abstract compiler is handed, not for every source, raw-stream, equality, and
order query used by the literal AST.  The assertions that the AST has no
remaining normalizer query class and that a verifier can check all records do
not follow.

Not printing a huge table is not, by itself, a defect in a theorem asserting
the existence of an effective procedure.  It is a defect in the stronger
certificate claim that this fixed query set has been traced and its records
returned.  No query manifest, chamber records, imported equality records,
coverage formulas, or pairwise-overlap formulas are emitted here.

Smallest repair: split Theorem 7.1 into (i) the generic quotient compiler at
the safe boundary below and (ii) an application theorem conditional on a
machine-readable source/AST query manifest and the raw-stream lifting lemma.
Materialize the tables before claiming a completed certificate; until then
say only that the generic algorithm can be instantiated after those inputs
are supplied.

## Safe theorem boundary

The following is the strongest theorem established by the memo's present
argument, with the wording qualification in Finding 3.

> Let (Q=C_2*\mathbb Z) use the pinned quotient alphabet and canonical
> reduced-word section.  Given an explicitly supplied finite list of bounded
> power-product schemas over that quotient alphabet, with fixed factor words,
> affine integer exponent maps, and exact Presburger domains, there is an
> effective procedure that returns a finite disjoint Presburger partition on
> which the selected quotient normal form is represented by fixed blocks and
> affine powers.  It also returns the post-terminal-`c` length, indexed
> quotient letters and prefixes, group/right-coset equality, and exact
> shortlex first-mismatch predicates.  Repeated, affine, and signed exponents
> are allowed after finite sign splitting.

This theorem does **not** establish that the 305 raw forest-path positions
have been converted to such schemas, that the raw signed `_KernelStream` has
been compiled, that all derived queries use at most two bounded variables,
or that the fixed AST's query manifest and chamber tables have been emitted.
Those are application obligations, not consequences of quotient equality
semilinearity.

## Accepted and rejected claims

### Accepted

- Effective bounded covers for powers and products, including noncanonical
  cover words, vanished powers/separators, and newly exposed blocks.
- Effective canonical-language predicates for bounded templates.
- Effective equality loci with repeated, affine, and signed exponents after
  the stated Presburger reductions and sign split.
- Presburger least-code selection and uniqueness of the selected literal
  quotient normal form.
- Affine outputs on finite exact Presburger cells of a functional semilinear
  graph; not the stronger unstated claim that every cell is only one simple
  residue chamber.
- Terminal-`c` deletion, length, quotient letter/prefix streams, and exact
  first-mismatch shortlex for an already supplied quotient schema.
- Termination and coverage/disjointness of the generic quotient compiler.

### Rejected or not established

- That the approved raw count `305` supplies, or even enumerates, the required
  quotient compiler inputs.
- That raw forest-generator paths and right-deck position atoms have been
  identified with the free-product schemas in (1.6).
- That quotient prefix templates alone reproduce the signed, freely reduced
  words and emission events of the literal `_KernelStream`.
- That every derived AST query has at most two bounded position variables.
- That Sections 1, 4, and 6 give an independently checkable complete query
  trace rather than assuming the disputed source and transport interfaces.
- Theorem 7.1 for the exact literal-AST query set, the statement that no
  normalizer query class remains, and any claim that the instantiated chamber
  tables or verifier records have already been produced.

## Re-review round 1

**Verdict: APPROVE.**  All eight original findings are addressed at the safe
generic-quotient boundary.  This was a scoped textual re-review of the revised
memo and the recorded findings; no computation, replay, grid, census, source
trace, or table materialization was performed.  No new breakage was found.

1. **Finding 1 — ADDRESSED.**  Lemma 2.3 now distinguishes the actual reduced
   operands (U,V) from their cover languages (K,L), explicitly uses
   (U\in K) and (V\in L), and retains empty-prefix/suffix and
   left-associated coverage of vanished separators.  Noncanonical words in a
   cover no longer create a notational ambiguity.
2. **Finding 2 — ADDRESSED.**  The effective `Red_s` predicate, repeated and
   affine exponent reduction, exhaustive signed split, and Presburger
   least-code selector are retained within the approved equality-semilinearity
   boundary.  Equality selects an already reduced quotient candidate and is
   still not used to infer shortlex.
3. **Finding 3 — ADDRESSED.**  Lemma 3.1 is retitled and limited to affine
   outputs on full exact Presburger cells.  It expressly disclaims a single
   polyhedron-plus-residue representation and keeps the complete projected
   Presburger domain in each output record.
4. **Finding 4 — ADDRESSED.**  Formula (4.4) now uses ℓ for the letter
   position and β for the powered-block index.  Section 4 consistently calls
   its products quotient letters and quotient prefixes, retains terminal-`c`
   deletion after full quotient reduction, and sends raw-stream semantics to
   an explicit application obligation.
5. **Finding 5 — ADDRESSED.**  Section 1 identifies the six triples and 305
   positions as raw forest data only, states that the count supplies no
   quotient schemas, and withdraws the row-by-row source-to-schema claim.
   Application Obligation A now requires the exact source manifest, including
   raw prefixes, signs/domains, right-deck/module vertices, quotient schemas,
   fixed atoms, and symbolic coverage.
6. **Finding 6 — ADDRESSED.**  The claim that quotient prefixes already
   compile `_KernelStream` is withdrawn.  Application Obligation B requires
   the freely reduced signed raw word, an explicit finite boundary-cancellation
   bound, positive and negative `C` event predicates, inverse-half events,
   running quotient prefixes, and the exact post-prefix `c_vertex`.
7. **Finding 7 — ADDRESSED.**  The maximum arity two is withdrawn.  The generic
   compiler accepts an arbitrary fixed finite parameter tuple, while
   Application Obligation C requires the concrete two-endpoint typed
   constructor trace and an induction proving the actual finite arity.  The
   memo explicitly notes that arity three is not excluded.
8. **Finding 8 — ADDRESSED.**  Section 6 proves well-foundedness, coverage,
   and disjointness only for explicitly supplied generic quotient schemas.
   Theorem 7.1 is now the generic quotient powered-product normalizer; the
   exact literal-AST theorem and the statement that no query class remains are
   expressly withdrawn.  Application Obligation D requires the query
   manifest, instantiated normal-form/equality/raw-event/shortlex records, and
   symbolic coverage and overlap checks before a fixed-AST certificate may be
   claimed.

**Open findings: none.**  The source manifest, signed raw-stream lifting,
typed AST/arity trace, and instantiated query/chamber tables remain unresolved
application obligations exactly as stated.  The endpoint DAG, root typing,
counting backend, edge identities, and seed remain separate later obligations;
none is promoted by the revised generic theorem.
