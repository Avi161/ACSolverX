# AK(3) one-edge second-stage result

Date: 2026-07-24

## Verdict

The cyclic one-edge stable-compression theorem is **PROVEN**. Its bounded
AK(3) floor-12 candidate is **REFUTED**.

The candidate starts only from first-stage two-stabilization corridors that
do not already contain an \(x\)-isolator. It then permits one signed
Definition-2.1 product of cyclic relator rotations. If that move creates an
\(x\)-isolator, Lemma 11 removes \(x\) and produces a rank-two endpoint.

The cancelling-seam theorem proves that the seam enumeration is complete for
this exact new-isolator class. The complete certificate found minimum
Aut-floor 14. No endpoint reaches the classical length-at-most-12 region.

This is a bounded negative, not a stable-AC obstruction. AK(3) remains open.

## Exact census

| quantity | value |
|---|---:|
| defining words | 16 |
| ordered defining-word pairs | 256 |
| structural templates | 43,296 |
| literal word/template cases | 11,083,776 |
| accepted braid identities | 31,232 |
| distinct raw rank-3 tuples | 3,224 |
| cyclic rank-3 quotient states | 3,016 |
| states with an immediate \(x\)-isolator | 1,400 |
| eligible non-immediate rank-3 states | 1,616 |
| seam-cancelling one-edge moves | 317,088 |
| new one-\(x\) incidences | 512 |
| distinct raw rank-2 outputs | 90 |
| canonical rank-2 outputs | 20 |
| output Aut-orbits | 2 |
| minimum output floor | 14 |
| source trace SHA-256 | `56e80e57362966c1a3fa6cb889002b0c52f3e274db62ec20b780d57a6abba8d6` |
| full trace SHA-256 | `418393174833c114c4cc53f0fe323437b471c9d02227b748b9da3db482b398a8` |

The raw-output floor distribution is:

| floor | outputs |
|---:|---:|
| 14 | 70 |
| 28 | 20 |

All 70 minimum outputs lie in the single complete Whitehead orbit

```text
YXXYx | YYYYXyyyx
```

The 20 canonical outputs split into 16 representatives of that floor-14
orbit and four representatives of the floor-28 orbit

```text
YXXYx | YYYYYYXXYYYXXYYYXXYYYXX
```

Thus one compression edge does not merely miss floor 12: every best endpoint
lands on one specific floor-14 wall.

## The theorem

The proof is in:

```text
literature/proofs/AK3_ONE_EDGE_COMPRESSION.md
```

For cyclically reduced factors \(U,V\) with no one-\(x\) isolator, a product
whose cyclic reduction has one \(x^{\pm1}\) must cancel across a factor seam.
If the first cancellation is at the cyclic wrap seam, rotating both factors
across that cancelled pair gives the same target-first cyclic product with a
displayed cancelling seam. Cancellation cascades do not change the argument.

Consequently, seam-only rotation enumeration is complete for creating the
new isolator. The resulting multiplication is AC1--AC3, and the subsequent
substitution-and-removal is stable AC.

The theorem is deliberately not broadened to arbitrary relative conjugators
\(UcVc^{-1}\), which form an infinite class.

## Why the disposable preflight differed

The earlier scratch preflight reported 47,610 outputs and minimum 13. It mixed
in first-stage tuples that already had an \(x\)-isolator and then allowed an
extra seam move while testing the unchanged isolator. Those rows do not
belong to the theorem-complete **new isolator after failed immediate
compression** candidate.

The production certificate separates the 1,400 immediate states already
decided by the prior theorem from the 1,616 non-immediate states addressed
here. It also applies the stated relator order/rotation/inversion quotient.
The scratch numbers were marked unverified and are superseded by this
replayed certificate.

## Certificate and replay

Certificate:

```text
results/stable_ac/theory/ak3_one_edge.json
```

Replay:

```bash
PYTHONHASHSEED=0 .venv/bin/python3 -m \
  experiments.stable_ac.rank3_compression.one_edge_certificate \
  --verify
```

Verified output:

```text
CERTIFICATE VERIFIES: 1616 eligible rank3 states,
90 outputs, minimum 14, lemma REFUTED
```

The verifier:

1. re-expands every stored first-stage template;
2. independently canonicalizes and checks every stored rank-3 source;
3. independently replays each rotation/sign/seam move;
4. rechecks the one-\(x\) solution and Lemma-11 output;
5. verifies every complete Whitehead witness;
6. reruns all 11,083,776 source cases and the full seam census, requiring
   complete payload equality.

## Next proof attempt

A disposable one-step audit of all 20 canonical endpoints enumerated 4,368
full Definition-2.1 rank-two children. Its observed minimum was 15
**[unverified]**. If certified, the floor-14 orbit is a strict one-AC-edge
local minimum after compression.

The next exact candidate therefore appends one ordinary rank-two AC
multiplication after the proven stable corridor:

\[
 \mathrm{AK}(3)
 \longrightarrow_{\mathrm{st}}
 \text{one-edge compression endpoint}
 \longrightarrow_{\mathrm{AC}}
 \text{rank-two child}.
\]

The deliverable is a finite certificate over all 20 canonical endpoints and
all signed cyclic rotations. A child of Aut-floor at most 12 would give a
stable proof route; a verified minimum above 12 would refute only this
post-compression one-edge candidate and determine whether the next mechanism
must cross a genuine two-edge ridge.

The proof loop remains active.
