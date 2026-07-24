# AK(3) one-edge primitive-compression result

Date: 2026-07-24

## Verdict

The one-edge primitive-compression implication is **PROVEN**. Its bounded
floor-12 lemma is **REFUTED**.

The exact census starts from all 3,016 cyclic rank-three corridor states,
applies every full signed cyclic Definition-2.1 multiplication, recognizes
targets primitive only after arbitrary rank-three Whitehead reduction,
removes those primitive targets, and computes the complete rank-two
Aut-floor.

The minimum is 13. All 52 minimum outputs lie in AK(3)'s own complete
Whitehead orbit.

This closes a substantially broader class than one-letter isolation:
237,680 primitive product edges were removed after ambient rank-three
straightening. None escapes the AK(3) wall. AK(3) remains open.

## Exact census

| quantity | value |
|---|---:|
| cyclic rank-three sources | 3,016 |
| literal signed rotation products | 2,916,576 |
| literal products passing abelian gcd gate | 2,916,576 |
| deduplicated source-target product edges | 1,895,680 |
| globally distinct product words | 735,368 |
| words passing Whitehead graph gate | 230,412 |
| primitive product words | 94,090 |
| primitive product edges | 237,680 |
| distinct rank-two quotients | 26,715 |
| quotient Aut-orbits | 1,088 |
| minimum quotient floor | 13 |
| minimum quotients | 52 |
| trace SHA-256 | `9dd92f888d186be0708d079fcf40bd66bc6db37fbff22ac58f751305e66eaa75` |

The abelian gate rejects nothing in this family. The effective exact
optimization is the Whitehead cut-vertex/disconnectedness gate, which reduces
735,368 product words to 230,412 candidates for full descent.

The lower end of the quotient floor distribution is:

```text
13:52, 14:155, 15:159, 16:348, 17:202, 18:810,
19:272, 20:924, 21:1510, 22:1748, 23:2290,
24:1512, 25:1055, 26:343, 27:1214, 28:645
```

The distribution continues through floor 101 and is stored exactly in the
certificate.

Every floor-13 quotient has complete Whitehead representative:

```text
YXYxyx | YYYYxxx
```

which is AK(3)'s own orbit.

## The theorem

The proof is in:

```text
literature/proofs/AK3_ONE_EDGE_PRIMITIVE.md
```

A full rank-three AC multiplication is classical. If its target is primitive
in \(F_3\), the primitive-single theorem applies an ambient automorphism,
removes the resulting basis generator, and produces a rank-two quotient.
The quotient Aut-orbit is independent of the chosen straightening. A quotient
floor at most 12 would prove stable AC-triviality via MM03.

The exact gates are necessary:

- a primitive word has primitive abelian exponent vector;
- a cyclic primitive word of length greater than one has a disconnected
  Whitehead graph or a cut vertex.

Every graph-gated candidate receives complete rank-three Whitehead descent;
the fast implementation changes scoring only and is cross-checked against the
slower reducer.

## Certificate and replay

Certificate:

```text
results/stable_ac/theory/ak3_one_edge_primitive.json
```

Replay:

```bash
PYTHONHASHSEED=0 .venv/bin/python3 -m \
  experiments.stable_ac.rank3_compression.one_edge_primitive_certificate \
  --verify
```

Verified output:

```text
CERTIFICATE VERIFIES: 3016 rank3 states,
237680 primitive edges, 26715 outputs,
minimum 13, lemma REFUTED
```

The 44 MB artifact stores one exact product/Whitehead/removal witness for
every quotient plus every rank-two Aut witness. The verifier:

1. recursively verifies the primitive-pair and primitive-single source
   certificates;
2. checks that the graph gate accepts all 1,016 already-certified primitive
   relators;
3. independently replays all 26,715 stored product and removal witnesses;
4. verifies every rank-two Aut witness;
5. reruns all 2,916,576 literal moves and the 735,368-word global cache;
6. requires complete payload equality.

## Structural conclusion

The fixed-generator objection is now exhausted within this finite corridor.
The following all return to AK(3) or its classically equivalent orbit-2:

- immediate one-letter isolation;
- one-edge one-letter isolation;
- primitive-single removal;
- one-edge ambient primitive removal;
- the minimum classical ridge crossing.

The floor-13 return is therefore stable under both rank-three ambient
coordinate changes and a full preceding AC multiplication.

## Next proof attempt

Blindly adding a second rank-three edge would expand well beyond the
1,000-node graph cap and would ignore the repeated return theorem. The next
attempt changes category:

### Rank-three stabilized thickenability

Each of the 3,016 corridor states is a balanced trivial-group presentation
stably equivalent to AK(3). If any one is thickenable, Lackenby's theorem
makes that rank-three presentation classically AC-trivial, hence proves AK(3)
stably AC-trivial.

This is not another length descent. It asks whether stabilization has moved
AK(3) into the topologically decisive thickenable locus even though every
algebraic compression returns to floor 13.

The exact deliverable is:

1. a rank-three Neuwirth rotation-system theorem and fail-closed enumerator;
2. a complete finite certificate over the 3,016 corridor states;
3. mandatory Regina cross-check of every positive before any proof claim.

A positive would settle stable triviality. A null would be bounded to these
corridors and would not constitute a counterexample.

The proof loop remains active.
