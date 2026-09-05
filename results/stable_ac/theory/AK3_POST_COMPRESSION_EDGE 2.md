# AK(3) post-compression AC-edge result

Date: 2026-07-24

## Verdict

The stable implication is **PROVEN**. The bounded post-compression floor-12
lemma is **REFUTED**.

Starting from all 20 canonical outputs of the certified one-edge compression,
the exact census enumerated every full Definition-2.1 multiplication: both
targets, both signs, and all cyclic rotations. The minimum child Aut-floor is
15.

The best compression roots have floor 14. Thus they form a certified strict
one-edge local minimum inside this finite stable corridor: every nontrivial
classical multiplication from any stored canonical root has floor at least
15.

This is not an obstruction to stable AC-triviality. AK(3) remains open.

## Exact census

| quantity | value |
|---|---:|
| canonical compression roots | 20 |
| root floors | 16 at 14; 4 at 28 |
| literal signed rotation products | 8,736 |
| distinct root-child edges | 4,368 |
| globally distinct children | 4,368 |
| child Aut-orbits | 464 |
| minimum child floor | 15 |
| minimum children | 80 |
| strict local minimum | yes |
| trace SHA-256 | `925532ca88d917931f577cc1b4e14ad1e4204b8064c92b1a590345d236e4fd14` |

The complete distinct-child floor distribution is:

```text
15:80, 16:16, 17:192, 18:16, 19:496, 20:40, 21:472,
22:96, 23:672, 24:32, 25:208, 26:384, 31:120, 33:224,
35:128, 37:352, 41:16, 48:36, 49:96, 50:64, 51:212,
52:64, 54:352
```

The 80 floor-15 children occupy exactly five complete Whitehead orbits:

```text
YXXYx  | YYYXYxyyyX
YXXYx  | YYYYXXyyyx
YXXYx  | YYYYXYxyyX
YXXYx  | YYYYYXXyyx
YYXXyx | YXXXyxxxx
```

## The theorem

The proof is in:

```text
literature/proofs/AK3_POST_COMPRESSION_EDGE.md
```

Every canonical root is stably AC-equivalent to AK(3). A signed product of
cyclic rotations is an AC1--AC3 composite. If a child had complete Whitehead
floor at most 12, the stable ambient automorphism theorem followed by MM03
Theorem 1.1 would make AK(3) stably AC-trivial.

The certificate finds no such child.

## Certificate and replay

Certificate:

```text
results/stable_ac/theory/ak3_post_compression_edge.json
```

Replay:

```bash
PYTHONHASHSEED=0 .venv/bin/python3 -m \
  experiments.stable_ac.rank3_compression.post_compression_edge_certificate \
  --verify
```

Verified output:

```text
CERTIFICATE VERIFIES: 20 roots, 4368 children,
minimum 15, lemma REFUTED
```

The verifier first rebuilds and independently checks the entire upstream
11,083,776-case one-edge-compression certificate. It then:

1. reconstructs the 20 canonical roots;
2. independently replays every stored rotation product;
3. checks every canonical root-child edge;
4. verifies every Whitehead witness;
5. reruns the full 8,736-move image;
6. requires complete payload equality.

## Ridge-crossing diagnosis

The 80 minimum children have only five Whitehead representatives, so the next
theory-guided test does not need a blind second neighborhood. Enumerating one
full edge from those five representatives gives 540 root-child edges and 536
globally distinct children, below the 1,000-node local cap.

The disposable result is:

```text
minimum floor: 13
unique minimum child: YYXXyx | YYxyXXX
Whitehead representative: YYXXyx | YYYxyXX
```

This is **[unverified]** until a chained certificate is built.

The representative `YYXXyx | YYYxyXX` is orbit-2. It is already known,
with an independently replayed classical path, to be AC-equivalent to AK(3).
Therefore the observed two-edge ridge crossing is not an escape: it returns
to the same classical wall in a better-connected coordinate system.

## Next proof attempt

Certify the five-orbit ridge image exactly. The expected theorem is:

> Every floor-minimizing two-edge continuation through the certified
> post-compression wall has floor at least 13, and the unique floor-13
> endpoint is orbit-2.

If verified, this closes the tempting “one more downhill edge” mechanism and
identifies the algebraic return map of the corridor. The next genuinely new
route must then alter the compression before removal—most plausibly a second
rank-3 product with a symbolic cancellation identity or a nontriangular
two-generator dependency—rather than spend more classical moves after
returning to AK(3)'s own AC class.

The proof loop remains active.
