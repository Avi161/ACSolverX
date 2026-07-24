# AK(3) one-edge second-stage compression design

Date: 2026-07-24

Status: theorem opportunity identified; disposable seam census completed;
certificate not yet built. Numerical observations are **[unverified]** until
the committed certificate replays.

## Objective

The immediate two-stabilization certificate found 3,224 distinct rank-3
tuples after the first generator removal. Immediate second removal produced
no endpoint below floor 13.

This attempt allows exactly one AC multiplication before testing for the
second isolator:

\[
 R_i\longmapsto
 \overline{\operatorname{rot}(R_i)\,
 \operatorname{rot}(R_j^\delta)},
 \qquad i\ne j,\quad\delta\in\{\pm1\}.
\]

If the resulting triple has a relator with one \(x^{\pm1}\), Lemma 11 removes
\(x\), producing a rank-two endpoint.

The candidate is:

> **One-edge second-stage lemma [unverified].** Within the already-certified
> defining-word/template bounds, one AC edge after the \(y\)-removal produces
> a rank-two endpoint of Aut-floor at most 12.

## One-edge stable theorem

The first two stabilizations, braid-template compression, and \(y\)-removal
are covered by `AK3_TWO_STABILIZATION.md`.

On the resulting rank-3 tuple, relator inversion, cyclic rotation, conjugation,
and multiplication of one relator by another are AC1--AC3 composites.
Therefore every displayed one-edge product is a valid AC move. If the child
has one \(x^{\pm1}\), the second substitution-and-removal is legal. The final
rank-two output remains stably AC-equivalent to AK(3).

## Seam-completeness theorem to prove

The implementation should enumerate only products with a cancelling
concatenation seam:

```text
last(rot(R_i)) == inverse(first(rot(R_j^delta))).
```

This is complete for creating a new one-letter isolator, provided the
following lemma is proved.

> **Cyclic seam lemma [unverified].** Let \(U,V\) be cyclically reduced cyclic
> words, each containing at least two occurrences of \(x^{\pm1}\). If a
> cyclically reduced product of conjugates of \(U\) and \(V^{\pm1}\) contains
> exactly one \(x^{\pm1}\), then the same cyclic relator has a representative
> \(\operatorname{rot}(U)\operatorname{rot}(V^{\pm1})\) whose concatenation
> seam cancels.

Proof route:

1. The unreduced concatenation contains at least four \(x^{\pm1}\)-letters,
   while the result contains one, so free/cyclic cancellation occurs.
2. In a product of two cyclic factors, every cross-factor cancellation occurs
   at one of the two cyclic seams.
3. If cancellation occurs at the displayed seam, the claim is immediate.
4. If it occurs at the cyclic wrap seam, cyclically rotate the product across
   that seam. The cyclic word is unchanged and the two factors become
   rotations in the reversed displayed order.
5. Reversing the displayed order is a cyclic rotation of the two-factor
   product, hence the same relator up to conjugation.

The proof must address cancellation cascades explicitly: choose the first
cross-factor cancellation in the cyclic reduction annulus, then cut the
annulus at that seam. Internal cancellations are absent because both factors
are cyclically reduced.

Existing immediate-isolator triples are handled before this lemma; for the
non-immediate tuples every factor has at least two \(x\)-occurrences.

## Exact finite decision

Regenerate the immediate certificate's rank-3 tuples, freely and cyclically
reduce every relator, and quotient only relator order/rotation/inversion.
Do not apply generator automorphisms because \(x\) is the distinguished
generator to remove.

For every distinct triple:

1. choose ordered target/other indices \(i\ne j\);
2. choose \(\delta=\pm1\);
3. enumerate all rotations of both factors satisfying the seam condition;
4. freely and cyclically reduce their product;
5. replace the target relator;
6. test all three relators for exactly one \(x^{\pm1}\);
7. perform the second Lemma-11 removal;
8. relabel \(z,t\) and compute the complete rank-two Aut-floor.

The trace must bind the source rank-3 tuple, move
`(target, other, sign, k1, k2)`, child relator, isolator index, expression,
and output.

## Preflight observations

The disposable preflight reported:

| quantity | value |
|---|---:|
| cyclically reduced distinct rank-3 tuples | 3,160 |
| seam-cancelling AC products | 531,936 |
| one-\(x\) isolator incidences | 190,736 |
| distinct raw rank-two outputs | 47,610 |
| minimum output floor | 13 |
| raw outputs at floor 13 | 1,042 |

The complete preflight floor distribution was:

```text
13:1042, 14:3462, 15:1620, 16:1020, 17:2852, 18:1616,
19:4980, 20:872, 21:4248, 22:1536, 23:3904, 24:2090,
25:1456, 26:1160, 27:1648, 28:612, 29:1104, 30:900,
31:1472, 32:112, 33:1296, 34:112, 35:632, 36:224,
37:172, 38:192, 39:160, 40:208, 41:844, 42:208,
43:992, 44:124, 45:496, 46:284, 47:352, 48:760,
49:1104, 50:352, 51:496, 52:48, 53:64, 55:192,
56:104, 59:28, 60:64, 63:92, 67:32, 70:32,
71:48, 79:64, 81:128
```

Sample minimum outputs had AK(3)'s Aut representative
`YXYxyx | YYYYxxx`. The certificate must verify all 1,042 before making the
universal minimum-orbit statement.

## Implementation architecture

Create:

- `literature/proofs/AK3_ONE_EDGE_COMPRESSION.md`;
- `experiments/stable_ac/rank3_compression/one_edge.py`;
- `experiments/stable_ac/rank3_compression/one_edge_certificate.py`;
- `tests/stable_ac/test_one_edge.py`;
- `results/stable_ac/theory/ak3_one_edge.json`;
- `results/stable_ac/theory/AK3_ONE_EDGE.md`.

The enumerator should reuse only the committed immediate two-stabilization
census as its source of rank-3 tuples. The one-edge move generator and replay
must be new and independently tested.

To avoid repeating the slow preflight mistake, deduplicate raw outputs by the
existing pair canonicalizer before calling `aut_canon`. Store one exact
one-edge witness per raw output, complete aggregate counts, the full trace,
all canonical Aut witnesses, and every minimum-output witness.

The verifier must:

1. rebuild the immediate rank-3 source set;
2. replay every stored seam move from its exact source;
3. recheck the one-\(x\) gate and second removal;
4. verify all Aut witnesses;
5. rerun the complete seam census and compare counts, trace, output
   partition, floor distribution, minima, and verdict.

## Expected adjudication

The preflight predicts minimum 13 and `REFUTED`; this is not yet a result.

If the seam lemma and certificate both hold, the null decides the complete
one-edge candidate, not merely a heuristic seam subset.

If a floor-at-most-12 output appears, expand its two stabilizations,
template compression, first removal, one AC edge, second removal, and
classical endpoint chain into an independently replayed stable proof.

If minimum 13 is confirmed, the next theory target is not a second AC edge
immediately. First attempt to prove a **floor-13 return theorem** for these
corridors: every one-edge endpoint with \(\mu=13\) lies in AK(3)'s Aut orbit.
Understanding why the wall is rigid may reveal either a normal form or the
specific mechanism needed to escape it.

## Constraints

- New task files only.
- No AC graph search; this is an exhaustive one-edge decision.
- CPU only; `.venv/bin/python3`.
- Commit and push `codex/proofs` at least every twenty minutes.
- Do not touch the unrelated untracked `hsearch-hyper.bundle`, `prompts/`, or
  `tmp/`.
- No pull request or merge.
