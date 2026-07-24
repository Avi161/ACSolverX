# AK(3) primitive-free rank-three thickenability result

Date: 2026-07-24

## Verdict

The rigid six-germ synchronized-planarity theorem is **PROVEN**.  The
bounded primitive-free rank-three thickenability candidate is **REFUTED**.

The verified rank-three corridor has 3,016 exact sources.  Exactly 2,952
have a primitive relator and were handled by the primitive-quotient
certificate.  All 64 remaining sources have the same rigid simple support

\[
H=K_6-E(P_5),
\]

and every one has a certified non-spherical compatible Neuwirth link.
There is no positive requiring Regina validation.  AK(3) remains open.

## The new theorem

The proof is in:

```text
literature/proofs/AK3_RANK3_RIGID_THICKENABILITY.md
```

The graph \(H\) is planar and 3-connected.  If each edge \(uv\) of a
3-connected planar graph is replaced by a nonempty labeled parallel class
of multiplicity \(m_{uv}\), every spherical rotation has:

1. one contiguous interval for each parallel class at both endpoints;
2. reversed linear orders across that interval; and
3. one of the two reflected Whitney rotations after the intervals are
   collapsed to neighbor symbols.

The key point is that \(H-\{u,v\}\) is connected.  It puts every other
support vertex in one complementary region of the \(uv\)-dipole, leaving
one common gap at both endpoints.  This rules out the relative-shift
freedom that occurs for the middle bundle of a \(P_4\) support.

Consequently, the labeled spherical rotations are exactly

\[
2\prod_{uv\in E(H)}m_{uv}!.
\]

Global reflection preserves the \(B\)-reversal equations simultaneously
for the \(x\), \(z\), and \(t\) pipes, so only one Whitney orientation must
be searched.  Eleven all-different rank families and three cyclic phases
then give a necessary-and-sufficient finite constraint system.

## Exact certificate

Certificate:

```text
results/stable_ac/theory/ak3_rank3_rigid_thickenability.json
```

Exact counts:

| quantity | value |
|---|---:|
| rank-three corridor sources | 3,016 |
| sources with a primitive relator | 2,952 |
| primitive-relator occurrences | 4,616 |
| primitive-free sources | 64 |
| \(K_6-E(P_5)\) supports | 64 |
| phase triples exhausted | 118,976 |
| component seeds exhausted | 1,741,883 |
| non-spherical sources | 64 |
| unsupported sources | 0 |
| Regina candidates | 0 |
| ordered trace SHA-256 | `11bd5e72743f0b9b4ec8d4851b6c0f48b7e1f7cbc28ff4a2dc748b2fb437386b` |

Replay:

```bash
PYTHONHASHSEED=0 \
  '/Users/avigyapaudel/Documents/Obsidian Vault/surf/ACSolverX/.venv/bin/python3' \
  -m experiments.stable_ac.thickenable.rank3_rigid_thickenability_certificate \
  --verify
```

Verified output:

```text
CERTIFICATE VERIFIES: 64 primitive-free rank3 sources,
64 non-spherical, 0 Regina candidates
```

The verifier:

1. recursively verifies the primitive-single source certificate;
2. reconstructs the exact complement of the 2,952 primitive-source indices;
3. rechecks all 64 support graphs by explicit complement recognition;
4. independently enumerates all 6,912 simple-support rotations and finds
   exactly two spherical global reflections;
5. reruns all phases, component seeds, and rank-partition checks;
6. compares with an independent 17,280-case factorial rotation census on a
   rigid-support fixture; and
7. requires source hashes and complete payload equality.

## Bounded meaning

The combined thickenability attack now exhausts its intended test branch for
every member of this exact 3,016-state rank-three corridor:

- 2,952 primitive-bearing sources induce 303 exact rank-two quotients, all
  non-thickenable;
- all 64 primitive-free rank-three complexes are non-thickenable directly.

This does not prove that thickenability is invariant under stable moves, so
the rank-two quotient nulls cannot be transported backward to their source
complexes.  It also does not obstruct another rank-three corridor, a
different stabilization, or AK(3) itself.

The proof loop remains active.
