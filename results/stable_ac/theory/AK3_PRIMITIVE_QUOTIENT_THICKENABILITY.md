# AK(3) primitive-quotient thickenability result

Date: 2026-07-24

## Verdict

The four-germ \(P_4\) synchronized-planarity theorem is **PROVEN**.  The
bounded primitive-quotient thickenability candidate is **REFUTED**.

The verified primitive-single corridor contains 2,952 of the 3,016
rank-three sources and produces 303 distinct exact rank-two quotient
presentations.  Every one of those 303 exact presentation complexes is
certified non-thickenable:

| simple support | exact quotients | spherical |
|---|---:|---:|
| \(K_4\) | 82 | 0 |
| \(K_4-e\) | 138 | 0 |
| \(C_4\) | 44 | 0 |
| \(P_4\) | 39 | 0 |
| **total** | **303** | **0** |

There is no positive requiring Regina validation.  AK(3) remains open.

## What is new theoretically

The prior exact rank solver was complete only for \(K_4\), \(K_4-e\), and
\(C_4\) simple support.  All 39 unsupported quotients have the same remaining
support: a path

\[
a-b-c-d
\]

whose three simple edges are nonempty parallel bundles.

The complete classification is in:

```text
literature/proofs/AK3_P4_SYNCHRONIZED_PLANARITY.md
```

Every bundle is a cyclic interval in a spherical rotation.  If the middle
bundle has multiplicity \(m\), its endpoint orders are reversed only
cyclically: the left and right path components can occupy independently
chosen faces of the middle dipole.  A complete solver must therefore
enumerate the \(m\) relative shifts

\[
z\longmapsto m-1-z+s\pmod m,
\qquad s\in\mathbb Z/m.
\]

The number of labeled spherical rotations for bundle multiplicities
\((p,m,q)\) is

\[
p!\,m!\,m\,q!.
\]

A hostile audit independently found explicit false negatives for the naive
zero-shift-only rule.  The repaired signed-rank solver agrees with the
independent factorial Neuwirth census on all 476 canonical cyclically
reduced \(P_4\) word-pairs of total length at most seven:

```text
444 spherical, 32 non-spherical, 476 / 476 agreement
```

Of the positive calibration cases, 256 require a nonzero middle shift.

## Exact certificate

Certificate:

```text
results/stable_ac/theory/ak3_primitive_quotient_thickenability.json
```

Exact counts:

| quantity | value |
|---|---:|
| rank-three corridor sources | 3,016 |
| sources with a primitive relator | 2,952 |
| primitive-relator occurrences | 4,616 |
| distinct exact rank-two quotients | 303 |
| non-spherical quotients | 303 |
| unsupported quotients | 0 |
| Regina candidates | 0 |
| ordered trace SHA-256 | `d5c257eb0c2974a0eeb7d4c91b63fc54e4c113e32ae175fd8651070457cf1186` |

Replay:

```bash
PYTHONHASHSEED=0 .venv/bin/python3 -m \
  experiments.stable_ac.thickenable.primitive_quotient_thickenability_certificate \
  --verify
```

Verified output:

```text
CERTIFICATE VERIFIES: 303 primitive quotients,
303 non-spherical, 0 Regina candidates
```

The verifier:

1. recursively verifies the primitive-single Whitehead/removal certificate;
2. rederives the 303 exact quotient word-pairs;
3. reruns every finite support, scheme, phase, seed, and rank decision;
4. checks that every negative exhausted its exact combinatorial budget;
5. repeats the complete 476-pair factorial \(P_4\) calibration; and
6. requires source hashes and complete payload equality.

## Bounded meaning

Each quotient is proven stably equivalent to AK(3).  A thickenable quotient
would have settled stable AK(3) by Lackenby's Theorem 1.3, but none occurs.

The negative does not transport backwards to the corresponding rank-three
complex, because no thickenability invariance under primitive straightening
or stable moves is used or claimed.  It also says nothing about the 64
rank-three corridor sources with no primitive relator, other stable
representatives, or AK(3) as a whole.

The proof loop remains active.
