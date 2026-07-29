# Period-two raw-stream and typed-AST bridge

Date: 2026-07-29

## Corrected status

**Bridge Obligations A--C are proved by the deterministic generator/replay
`period_two_raw_stream_manifest_generator.py`.  Application Obligation D is
still open.**  This supersedes the refuted v1 branch cover.

## 1. Reproducible finite source and AST data

The generator derives all quotient images and incidence rows through the live
`phi4_escape`, `degree_two_escape`, source-flow, subgroup-rewrite, lift,
tree-flow, and literal-Hessian objects.  The approved path-factor words are
explicit semantic pins.  Domains and equalities in JSON are predicate/expression
ASTs, not prose-only booleans.

Replay proves 305 unique W base positions,
397 oriented W rows, 167 V rows,
21 anchor rows, 585
source-current equality records, 6 anchor endpoint
equalities, 16 occurrences, and 62
quotient/product gates per endpoint.  There are 17
distinct transport actions and the actual maximum arity is 3.

The row proof is uniform.  For a literal raw prefix U, the live forest images
give E(UV)=E(V)E(U); applying the exact live A/a, B/b, G/g incidence rule gives
the printed coefficient and module vertex.  Removing an adjacent forest inverse
pair removes the same stored edge twice with opposite incidence signs.  Hence
the row sum equals the approved freely reduced current for all indices, not
only the replayed fixtures.

## 2. Correct terminal maximal-overlap partition

Let b(q) be the length of the trailing T/t run of the fixed canonical action
q.  Since q and a canonical post-c_vertex v contain only positive raw C,
free cancellation cannot cross the last c of q, so the maximal outer overlap
k satisfies 0 <= k <= b(q).

For 0 <= k < b(q), branch B_k requires:

1. len(v) >= k;
2. prefix(v,k) = inverse(suffix(q,k)); and
3. either len(v)=k or the next letters do not cancel.

The corrected terminal branch B_b requires only:

1. len(v) >= b(q); and
2. prefix(v,b(q)) = inverse(suffix(q,b(q))).

It has **no next-letter or len(v)=b(q) maximality requirement**.  Further
cancellation is impossible because q is exhausted or its preceding letter is
positive c while v has no negative C.

For every canonical v, let m be the actual maximal overlap.  If m<b(q), the
next-letter mismatch puts v in B_m; all smaller branches fail their maximality
test and all larger branches fail prefix matching.  If m=b(q), v lies in B_b,
and every smaller branch fails maximality.  This proves all-word coverage and
pairwise disjointness independently of the bounded replay.

Put x=q[:-k]v[k:].  Tau has two terminal subcases:

- if q[:-b(q)] is nonempty and ends in positive c, tau=1 exactly when
  len(v)=b(q);
- if q is exhausted (including q='', q='T', and q='t'), tau=0 even when
  len(v)=b(q).

For nonterminal branches tau=0.  Deleting the terminal positive C exactly
when tau=1 gives z and

    red(q v C C v^-1 q^-1) = z C C z^-1.

The positive event is `raw[r]=+C` with a quotient prefix ending c; the negative
event is `raw[r]=-C` with a prefix not ending c.  In both cases the emitted
label is `c_vertex(quotient_prefix_through_r)`, including the inverse half.

## 3. Bounded hostile replay and arity

As a guard, not as the all-word proof, replay covered all 17 actions
times all 31 canonical non-terminal-c
words of length at most 4 (527 pairs):

- uncovered: 0;
- multiply covered: 0;
- wrong overlap key: 0;
- raw-word identity failures: 0;
- tau failures: 0;
- event failures: 0.

Arity three is attained by the live W row `W:nu1:P:9:o+1` at
`(i,j,h)=(1,0,0)` and gate 30: the source position rho survives while the
transported-generator tensor introduces ordered event positions r1,r2.

## 4. Determinism, provenance, and remaining gap

Run:

    python3 .scratch/period_two_raw_stream_manifest_generator.py --check

The command regenerates canonical JSON and this memo in memory, verifies all
structured checks and the bounded hostile replay, and requires byte-for-byte
equality with both files.  `--write` deterministically regenerates them.

Generator SHA-256: `edd1f21fda1665b092447143b30d25e65f8c9a9cf2753a56ceb5da16db150bb1`

JSON SHA-256: `824d17adc0bc9b553d722eb627ee60f363451673237e366f6eb869acc6e058dd`

Section SHA-256 values:

- source_schema_manifest: `4333c121e0783d1bd19a31d2b0990169f4ac7b5366fb7d0da9ab7217d4c7b31a`
- raw_stream_lifting_manifest: `2e4153c35257aa1f88abd5bf9c950b507ad9b57465da9d4ec77faf9ad8b56b95`
- typed_ast_query_manifest: `180f037ae872deeec754053da869ba05872282d92bbca6a9604cf6cb4c120da1`
- checks: `08a58efe6705948bc95b7f705476082e5d3dc044a3d7cad9b0149f30de17c35d`
- provenance: `f8f04ed6b03a624b14b27a769600d7b5cb59ac4d1f3c6076e5fc5600f1d6ae8c`


The provenance list is the recursive project-local import closure of the
generator's semantic modules, plus the pinned proof/review inputs; it includes
the generator, phi4 escape, degree-two escape, and tree-flow factorization.

The exact remaining normalizer gap is Application Obligation D: materialize
the normal-form, equality, raw-event, shortlex, complete Presburger-cell,
coverage, and pairwise-empty-overlap records.  No tracked files are changed.
