# AK(3) hidden rank-3 corridor result

Date: 2026-07-24

## Verdict

The general hidden-cancellation corridor theorem is **PROVEN**. Its first
finite AK(3) candidate is **REFUTED**.

The refuted statement was:

> There is an AK(3) one-stabilization corridor with
> \(1\le |w|\le4\), \(2\le |I|\le6\), at least two
> \(z^{\pm1}\)-occurrences in \(I\), exactly one occurrence of the eliminated
> generator, and output Aut(\(F_2\))-floor at most 12.

The complete census contains:

| quantity | exact value |
|---|---:|
| tested word/template/source/isolation tuples | 2,851,840 |
| accepted corridor identities | 2,128 |
| distinct output Aut-orbits | 8 |
| minimum output orbit floor | 14 |
| trace SHA-256 | `869576618460c04e8ee086c237b739211d53016c72856d9df44bff1ea662e43b` |

Thus no corridor in the exact stated class lands at floor at most 12.
This is an exact falsifier of the candidate lemma. It is not a bounded AC
search, and it is not a stable-AC obstruction.

## New proven stable equivalence

The braid relator of AK(3) has the hidden conjugacy spelling

\[
 xyxy^{-1}x^{-1}y^{-1}=(xy)x(xy)^{-1}y^{-1}.
\]

Stabilize with \(z=xy\). Replace the two displayed copies
\((xy)^{\pm1}\) by \(z^{\pm1}\), giving

\[
 zxz^{-1}y^{-1}.
\]

This isolates \(y=zxz^{-1}\). Substitution and removal prove

\[
 \mathrm{AK}(3)\sim_{\mathrm{st}}
 \left\langle x,z\ \middle|\
 x^3zx^{-4}z^{-1},\ z^{-1}xzxz^{-1}
 \right\rangle.
\]

After \(z\mapsto y\), the exact pair is

```text
xxxyXXXXY | YxyxY
```

with Aut-minimum representative

```text
YXXYx | YYYYXyyyx
```

and total length 14. The proof that every occurrence replacement is an
AC1--AC3 composite, followed by the Lemma-11 generator removal, is in
`literature/proofs/AK3_RANK3_COMPRESSION.md`.

## Orbit distribution

The eight exact output floors are:

| floor | Aut-minimum representative | canonical outputs |
|---:|---|---:|
| 14 | `YXXYx | YYYYXyyyx` | 56 |
| 16 | `YXXYx | YYYYXXyyyxx` | 8 |
| 23 | `YXYxyx | YYXXXyxYYxyxYYxyx` | 4 |
| 24 | `YXXYx | YYYYYYYXXYYYXXYYYXX` | 8 |
| 25 | `YXYXYx | YYYYYXXYxYXXYxYXXYx` | 4 |
| 27 | `YXXYx | YYYXXYYYXXYYYXXYYxyxyX` | 4 |
| 28 | `YXXYx | YYYYYYXXYYYXXYYYXXYYYXX` | 8 |
| 29 | `YXYXYx | YYYYXXYxYXXYxYXXYxYXXYx` | 4 |

The `canonical outputs` column counts the canonical rank-two outputs stored
under that Aut-orbit in the certificate, not distinct stable classes.

## Replay

The certificate is
`results/stable_ac/theory/ak3_rank3_corridors.json`. Replay it with:

```bash
PYTHONHASHSEED=0 .venv/bin/python3 -m \
  experiments.stable_ac.rank3_compression.certificate --verify
```

The verifier:

1. checks every accepted literal identity \(I[z\mapsto w]\);
2. independently solves the unique generator occurrence;
3. recomputes both output relators;
4. verifies every recorded Aut witness;
5. reruns all 2,851,840 cases and compares the complete trace and JSON
   payload.

The recorded replay output is:

```text
CERTIFICATE VERIFIES: 2851840 templates, 2128 corridors,
minimum floor 14, lemma REFUTED
```

Focused regressions passed:

```text
90 passed
```

from the rank-3 compression, existing CoV, and AK(3) certificate tests.

## Scope

What is proved:

- the general one-stabilization corridor theorem;
- the displayed stable equivalence from AK(3) to the length-14 orbit;
- completeness and the floor-14 minimum for the exact finite corridor class.

What is not proved:

- that longer one-stabilization corridors cannot descend;
- that a different free basis cannot expose a primitive isolator;
- that two stabilizations cannot descend;
- that AK(3) is stably trivial or nontrivial.

AK(3) therefore remains open.

## Next proof attempt

The generator-isolator hypothesis is now the narrow part of the mechanism.
The next candidate is:

> **Primitive-isolator corridor lemma [unverified].** There is an
> automorphism \(\phi\in\operatorname{Aut}(F_2)\), supplied with a Nielsen
> witness, such that \(\phi(\mathrm{AK}(3))\) has a hidden-cancellation
> corridor whose isolator contains exactly one occurrence of a basis letter
> in the \(\phi\)-basis and whose output has Aut-floor at most 12.

Running the same exact bounds on AK(3)'s Aut-minimum representative

```text
YXYxyx | YYYYxxx
```

again gives 2,128 accepted corridors and minimum floor 14. Hence merely
switching to the canonical minimum basis does not help. The next attempt must
classify a nontrivial finite family of primitive bases via explicit Nielsen
reductions; increasing \(|w|\) or \(|I|\) in the original basis is not the
next move.
