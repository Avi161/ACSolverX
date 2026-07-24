# AK(3) five-orbit ridge-return result

Date: 2026-07-24

## Verdict

The chained five-orbit return proposition is **PROVED**. The accompanying
floor-12 candidate is **REFUTED**.

The 80 minimum children of the certified post-compression wall occupy five
complete Whitehead orbits at floor 15. The exact full one-edge image of those
five representatives has minimum floor 13. There is exactly one canonical
child at that minimum, and its Whitehead representative is AK(3)'s orbit-2.

Thus the most economical two-edge ridge crossing from this corridor returns
to AK(3)'s known classical AC class. It does not escape toward the standard
presentation.

AK(3) remains open.

## Exact census

| quantity | value |
|---|---:|
| floor-15 Whitehead roots | 5 |
| literal signed rotation products | 1,016 |
| distinct root-child edges | 540 |
| globally distinct children | 536 |
| child Aut-orbits | 528 |
| minimum child floor | 13 |
| canonical children at the minimum | 1 |
| minimum Whitehead orbit | orbit-2 |
| trace SHA-256 | `f490ef3831c08b762177084dd44fc373f3c74322acc5af84d0231a6f8343dd61` |

The distinct-child floor distribution is:

```text
13:1, 14:7, 15:5, 16:13, 17:8, 18:54, 19:31,
20:145, 21:64, 22:42, 23:48, 24:30, 25:88
```

The image contains 540 graph states, below the mandatory 1,000-node local
cap. The 1,016 literal rotation products are move spellings before
root-child deduplication, not graph nodes.

## Unique return edge

The unique minimum edge starts at the fifth floor-15 representative:

```text
YYXXyx | YXXXyxxxx
```

Using zero-based left-rotation offsets, it replaces the second relator by:

```text
rot_2(YXXXyxxxx) · rot_4((YYXXyx)^-1)
= XXyxxxxYX · yyXYxx
```

The concatenation is freely reduced. Cyclic cancellation removes:

```text
X/x, X/x, y/Y, x/X
```

and leaves:

```text
xxxYXyy
```

The canonical child is:

```text
YYXXyx | YYxyXXX
```

Its independently checked complete Whitehead representative is:

```text
YYXXyx | YYYxyXX
```

which is orbit-2.

## The theorem

The proof is in:

```text
literature/proofs/AK3_RIDGE_RETURN.md
```

Every floor-15 root is obtained from a certified stable corridor followed by
an ambient automorphism. Every ridge edge is classical AC. A floor-at-most-12
child would therefore prove stable AC-triviality via MM03. No such child
exists in the complete image.

The orbit-2 endpoint is not progress toward resolution: the repository
already contains an independently replayed classical AC path between AK(3)
and orbit-2.

## Certificate and replay

Certificate:

```text
results/stable_ac/theory/ak3_ridge_return.json
```

Replay:

```bash
PYTHONHASHSEED=0 .venv/bin/python3 -m \
  experiments.stable_ac.rank3_compression.ridge_return_certificate \
  --verify
```

Verified output:

```text
CERTIFICATE VERIFIES: 5 ridge roots, 540 edges,
minimum 13, return PROVED
```

The verifier recursively replays the complete one-edge-compression and
post-compression certificates, extracts exactly their five minimum
Whitehead representatives, independently checks all 540 edges and all
Whitehead witnesses, enforces the 1,000-state cap, and compares the entire
rerun payload.

## Structural interpretation

The stable corridor has an algebraic return map:

```text
floor-14 compression orbit
  -> one classical edge
floor-15 ridge (five Aut orbits)
  -> one classical edge
floor-13 orbit-2
  -> known classical path
AK(3)
```

The return is driven by cyclic rather than free cancellation: the unique
minimum product is freely reduced, then four inverse pairs peel from its
cyclic ends. That explains why a seam-greedy continuation misses the
mechanism and why the full Definition-2.1 image was necessary.

## Next proof attempt

More classical moves after orbit-2 repeat a known class and are not a new
proof direction. The next attempt moves back before the second removal.

### Primitive-pair elimination theorem [next]

For a rank-three corridor tuple

\[
 \langle x,z,t\mid A,B,C\rangle,
\]

if any two relators form a primitive pair in \(F(x,z,t)\)—equivalently, they
extend to a free basis—an ambient automorphism sends them to two basis
generators. Removing those generators leaves a one-generator presentation of
the trivial group, whose remaining relator must be the surviving generator
to exponent \(\pm1\). The rank-three presentation, hence AK(3), is then
stably AC-trivial.

This is a qualitatively different certificate: it tests simultaneous
two-relator primitivity rather than waiting for a one-letter isolator. The
finite target is the 3,016 cyclic rank-three corridor states already
certified. A complete rank-three Whitehead/Stallings certificate can decide
whether any of their three relator pairs extends to a basis without an AC
graph search.

The proof loop remains active.
