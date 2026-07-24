# AK(3) primitive-single-relator result

Date: 2026-07-24

## Verdict

The primitive-single removal and quotient-independence theorems are
**PROVEN**. The bounded floor-12 lemma is **REFUTED**.

Among all 3,016 cyclic rank-three corridor states, 1,016 of the 2,386
distinct relators are primitive in \(F(x,z,t)\). They occur 4,616 times.
Straightening each primitive conjugacy class, applying the automorphism to
the whole tuple, and removing the resulting basis generator produces 303
distinct rank-two outputs.

The minimum complete rank-two Aut-floor is 13. All 78 minimum outputs lie in
AK(3)'s own Whitehead orbit.

Thus individual primitivity is abundant, but within these bounds it only
returns to the known AK(3) wall. AK(3) remains open.

## Exact census

| quantity | value |
|---|---:|
| cyclic rank-three sources | 3,016 |
| relator occurrences tested | 9,048 |
| distinct cyclic relators | 2,386 |
| distinct primitive relators | 1,016 |
| primitive occurrences | 4,616 |
| distinct rank-two outputs | 303 |
| output Aut-orbits | 10 |
| minimum output floor | 13 |
| minimum outputs | 78 |
| trace SHA-256 | `c321c3142f35b34b145fcf74f344b478560b21ed647534ad1d92867be8f798af` |

The output floor distribution is:

```text
13:78, 14:82, 16:4, 23:23, 24:26,
25:23, 27:21, 28:23, 29:11, 43:12
```

Every floor-13 output has complete Whitehead representative:

```text
YXYxyx | YYYYxxx
```

which is AK(3)'s own orbit, not the standard presentation and not orbit-2.

The distinct-relator Whitehead minima are:

```text
1:1016, 5:42, 7:976, 9:8,
15:64, 17:128, 19:112, 23:40
```

There are no near misses at lengths two through four: every nonprimitive
relator has minimum at least five.

## The theorem

The proof is in:

```text
literature/proofs/AK3_PRIMITIVE_SINGLE.md
```

If one relator conjugacy class is primitive, a stable ambient automorphism
makes it a basis generator. Removing that generator-relator pair leaves a
balanced rank-two presentation.

The induced rank-two Aut-orbit is independent of the chosen straightening:
two straightenings differ by an automorphism preserving the primitive
generator's normal closure, and hence descend to an automorphism of the
rank-two quotient. One Whitehead witness per primitive relator therefore
decides the complete quotient floor.

A quotient floor at most 12 would make AK(3) stably AC-trivial via MM03. None
occurs.

## Certificate and replay

Certificate:

```text
results/stable_ac/theory/ak3_primitive_single.json
```

Replay:

```bash
PYTHONHASHSEED=0 .venv/bin/python3 -m \
  experiments.stable_ac.rank3_compression.primitive_single_certificate \
  --verify
```

Verified output:

```text
CERTIFICATE VERIFIES: 3016 rank3 states,
4616 primitive occurrences, minimum 13, lemma REFUTED
```

The chained verifier first independently replays the full primitive-pair
source certificate. It then:

1. replays all 2,386 single-word Whitehead reductions;
2. checks all 90 second-kind maps at every stored minimum;
3. applies each straightening to the full rank-three tuple;
4. independently removes all 4,616 primitive occurrences;
5. verifies every rank-two Whitehead witness;
6. reruns the complete census and requires payload equality.

## Structural conclusion

Three distinct mechanisms now exhibit the same return behavior:

- immediate or one-edge one-letter isolation;
- a two-edge classical ridge crossing;
- ambient primitive-relator straightening.

Their best endpoints are all AK(3) or orbit-2, and orbit-2 is classically
equivalent to AK(3). The wall is therefore not an artifact of fixed generator
names or failure to recognize primitive relators.

## Next proof attempt

The next strict generalization applies one rank-three AC multiplication
**before** testing primitivity:

\[
 A_i\longmapsto
 \operatorname{cyc}(
   \operatorname{rot}(A_i)
   \operatorname{rot}(A_j^\delta)
 ),
\]

then asks whether the new target relator is primitive in \(F_3\). If it is,
primitive-single removal gives a rank-two quotient. This contains the prior
one-\(x\) second-stage theorem but also recognizes isolators visible only
after an ambient rank-three automorphism.

The finite deliverable is a **one-edge primitive compression certificate**.
It must use the abelian gcd gate and canonical-word caching before exact
Whitehead reduction, enumerate a stated finite move class without graph
traversal, and independently replay every positive quotient. A floor at most
12 settles stable triviality; a null determines whether the next necessary
ingredient is a genuinely nontriangular two-edge identity.

The proof loop remains active.
