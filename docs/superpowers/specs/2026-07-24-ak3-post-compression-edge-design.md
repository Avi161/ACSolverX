# AK(3) post-compression AC-edge design

Date: 2026-07-24

Status: candidate identified; disposable one-step audit completed; theorem and
certificate not yet built. Numerical observations are **[unverified]**.

## Objective

The proven one-edge second-stage corridor has 20 canonical rank-two endpoints.
Every endpoint is stably AC-equivalent to AK(3), and their minimum Whitehead
floor is 14.

Append one ordinary rank-two Definition-2.1 multiplication:

\[
 (R,S)\longmapsto
 \operatorname{canon}(
   \operatorname{rot}(R_i)
   \operatorname{rot}(R_j^\delta),
   R_j),
 \qquad i\ne j,\quad\delta\in\{\pm1\}.
\]

Enumerate all rotations, not only cancelling seams.

The candidate is:

> **Post-compression floor-12 lemma [unverified].** Some full one-edge child
> of the 20 canonical compression endpoints has complete Aut-floor at most
> 12.

## Stable implication

Each root has an explicit two-stabilization, first removal, cyclic
multiplication, and second-removal witness in
`ak3_one_edge.json`. Relator order, inversion, and rotation carry its raw
output to the stored canonical root by AC1--AC3.

One further Definition-2.1 multiplication is classical AC. If its child has
Aut-floor at most 12, the complete Whitehead witness supplies an ambient
automorphism to a length-at-most-12 presentation. The repository's classical
length theorem then supplies an AC trivialization. The ambient automorphism is
realized stably, so the composite proves stable AC-triviality of AK(3).

## Exact finite decision

For each canonical output in `ak3_one_edge.json`:

1. choose either target relator;
2. choose the other relator's sign;
3. enumerate every target and other cyclic rotation;
4. freely and cyclically reduce the product;
5. retain the unchanged other relator and canonicalize the pair;
6. deduplicate root-child edges while keeping the first literal move;
7. compute and certify every distinct child's complete Whitehead floor.

The trace binds the upstream certificate trace, root, literal move, reduced
target, canonical child, and duplicate/new gate.

The verifier must validate the upstream certificate, replay every stored edge
with an independent word layer, verify every Aut witness, rerun the full
finite census, and compare the complete payload.

## Disposable observation

The preflight over the 20 roots reported:

| quantity | observed value |
|---|---:|
| deduplicated root-child edges | 4,368 |
| globally distinct children | 4,368 |
| minimum child floor | 15 |
| children at the observed minimum | 80 |

If confirmed, the floor-12 lemma is refuted and every full one-edge neighbor
of the corridor endpoints lies above the floor-14 minimum.

## Theoretical consequence of a null

A verified minimum 15 proves a local ridge statement for this finite corridor:
after compression, no single AC multiplication maintains or lowers the best
Whitehead floor.

It does not prove that every stable path must cross floor 15, because the
corridor samples only a finite stable family. It does prove that continuing
this particular route needs at least two nontrivial classical moves after
removal.

The next proof question would be structural:

> Which cancellation pattern can cross the floor-15 ridge in two moves
> without enumerating a graph larger than the local 1,000-node cap?

Candidate mechanisms include a symbolic two-product identity, a different
rank-3 multiplication before removal, or a nontriangular dependency. A blind
second-neighborhood enumeration is excluded.

## Artifacts

- `literature/proofs/AK3_POST_COMPRESSION_EDGE.md`
- `experiments/stable_ac/rank3_compression/post_compression_edge.py`
- `experiments/stable_ac/rank3_compression/post_compression_edge_certificate.py`
- `tests/stable_ac/test_post_compression_edge.py`
- `results/stable_ac/theory/ak3_post_compression_edge.json`
- `results/stable_ac/theory/AK3_POST_COMPRESSION_EDGE.md`

## Constraints

- New task files only.
- No AC graph traversal; this is a complete one-edge image.
- CPU only; `.venv/bin/python3`.
- Bind and independently verify the upstream one-edge certificate.
- Commit and push `codex/proofs` at least every twenty minutes.
- Do not touch unrelated untracked files.
- No pull request or merge.
