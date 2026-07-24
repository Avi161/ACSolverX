# AK(3) rank-three primitive-pair result

Date: 2026-07-24

## Verdict

The primitive-pair elimination theorem is **PROVEN**. Its bounded AK(3)
corridor lemma is **REFUTED**.

The exact rank-three Whitehead census tested all three relator pairs in all
3,016 cyclic corridor states. No pair has complete minimum total length two,
so no tested pair extends to a free basis of \(F(x,z,t)\).

The smallest pair minimum is six. This refutes only the finite corridor
candidate; it is not a stable-AC obstruction. AK(3) remains open.

## Exact census

| quantity | value |
|---|---:|
| literal first-stage cases | 11,083,776 |
| accepted braid identities | 31,232 |
| distinct raw rank-3 tuples | 3,224 |
| cyclic rank-3 states | 3,016 |
| relator-pair occurrences | 9,048 |
| distinct cyclic relator pairs | 6,928 |
| primitive pairs | 0 |
| minimum pair floor | 6 |
| source trace SHA-256 | `56e80e57362966c1a3fa6cb889002b0c52f3e274db62ec20b780d57a6abba8d6` |
| full trace SHA-256 | `f80387043f0537ede8a1d97f697f52f278a4efaea28cb4c0d7e4ace49c3cb16a` |

The complete occurrence distribution by Whitehead minimum is:

```text
6:512, 7:1664, 8:2240, 9:296, 10:608, 11:432,
12:304, 13:256, 14:240, 16:96, 19:336, 20:512,
21:208, 22:160, 23:144, 24:504, 25:328, 26:184,
28:8, 30:16
```

There are 448 distinct cyclic pair records at minimum six. Every minimum-six
shape consists of one basis letter and one length-five word; representative
shapes include:

```text
T     | XXzzz
X     | TZZTz
X     | TZTzz
X     | TTZtZ
Z     | TTTXX
```

Thus simultaneous two-relator primitivity fails, but many individual
relators are primitive.

## The theorem

The proof is in:

```text
literature/proofs/AK3_PRIMITIVE_PAIR.md
```

If two relator conjugacy classes extend to a basis, a stable ambient
automorphism makes them two basis generators. Removing those
generator-relator pairs leaves a one-generator presentation of the trivial
group. Its relator exponent is necessarily \(\pm1\), so the final pair also
removes and AK(3) is stably AC-trivial.

Whitehead's reduction theorem makes the finite test exact: a cyclic tuple
with a nonminimal total length has a strictly reducing second-kind Whitehead
automorphism. The implementation enumerates all 90 nonidentity rank-three
maps and carries a composed automorphism witness.

The rank-two specialization reproduces the repository's exact set of 12
second-kind automorphisms before rank three is trusted.

## Certificate and replay

Certificate:

```text
results/stable_ac/theory/ak3_primitive_pair.json
```

Replay:

```bash
PYTHONHASHSEED=0 .venv/bin/python3 -m \
  experiments.stable_ac.rank3_compression.primitive_pair_certificate \
  --verify
```

Verified output:

```text
CERTIFICATE VERIFIES: 3016 rank3 states,
9048 relator pairs, minimum 6, lemma REFUTED
```

The certificate stores one full descent witness for each of the 6,928
distinct cyclic pairs and references it from all 9,048 source occurrences.
The verifier:

1. replays every first-stage template and rank-three source;
2. independently composes every stored Whitehead descent;
3. directly applies the final automorphism;
4. independently regenerates all 90 second-kind maps;
5. checks that none lowers a stored endpoint;
6. reruns the entire source and Whitehead census;
7. requires complete payload equality.

## Next proof attempt

The minimum-six shapes suggest a strictly broader theorem.

### Primitive-single-relator removal

If one rank-three relator is primitive, an ambient automorphism sends it to a
basis generator. Remove that generator-relator pair and obtain a balanced
rank-two presentation stably equivalent to AK(3).

The resulting rank-two Aut-orbit is independent of the chosen straightening
automorphism: two automorphisms sending the same primitive conjugacy class to
a basis letter differ by an automorphism preserving its normal closure, hence
descend to an automorphism of the rank-two quotient.

A disposable pass using only the 512 minimum-six pair witnesses produced 36
rank-two outputs with observed floors:

```text
13:8, 14:12, 24:8, 28:8
```

All eight observed floor-13 outputs returned to AK(3)'s own Whitehead orbit.
These numbers are **[unverified]** and do not exhaust individually primitive
relators.

The next exact candidate therefore Whitehead-reduces every distinct
rank-three relator individually, removes every primitive occurrence, and
certifies the complete rank-two floor distribution. A floor at most 12 would
settle stable triviality; a null would prove that simultaneous primitivity
fails and single primitivity only returns to the known wall within these
corridors.

The proof loop remains active.
