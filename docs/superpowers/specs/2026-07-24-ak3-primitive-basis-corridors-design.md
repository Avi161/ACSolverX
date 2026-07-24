# AK(3) primitive-basis corridor design

Date: 2026-07-24

Status: selected by the standing autonomous proof loop after the original-basis
short-corridor lemma was exactly refuted.

## Objective

This is the second attempt in the same proof loop. It asks whether the
generator-isolator corridor from
`literature/proofs/AK3_RANK3_COMPRESSION.md` becomes effective after changing
to a short primitive basis.

The finite candidate is:

> **Primitive-basis short-corridor lemma [unverified].** There is an
> automorphism \(\phi\in\operatorname{Aut}(F_2)\) with
> \[
> |\phi(x)|+|\phi(y)|\le4
> \]
> such that \(\phi(\mathrm{AK}(3))\) has a hidden-cancellation corridor with
> \(1\le|w|\le4\), \(2\le|I|\le6\), exactly one isolated basis letter, at
> least two \(z^{\pm1}\)-occurrences, and output Aut-floor at most 12.

As before, a positive still requires a classical AC certificate from the
floor-at-most-12 output and an independent replay of the complete stable
chain. A negative refutes only this exact finite lemma.

## Why this is a structural enlargement

The first certificate used only the named basis \((x,y)\). A word that appears
many times in that basis can become a single occurrence of one generator in a
different primitive basis. The stable ambient automorphism theorem makes such
a preliminary basis change legitimate, but the basis must be supplied with an
explicit Nielsen witness. Merely calling a word "primitive" is insufficient.

Increasing the old \(w,I\) length bounds would enlarge the same mechanism.
This attempt instead enlarges the allowed isolator class from the two named
generators to every generator in every basis inside a complete, independently
checkable basis ball.

## Complete basis ball

Enumerate every ordered pair \((u,v)\) of nonempty freely reduced words over
\(x^{\pm1},y^{\pm1}\) satisfying

\[
 |u|+|v|\le4.
\]

Accept the pair exactly when a sequence of elementary Nielsen transformations
reduces it to two distinct signed generators. The allowed transformations are:

1. swap the two components;
2. invert either component;
3. replace one component by its product, on either side, with the other
   component or its inverse.

Every recorded step must strictly reduce total length except the final signed
permutation normalization. Classical Nielsen reduction proves completeness:
an ordered pair is a basis of \(F_2\) if and only if strictly
length-reducing Nielsen moves end at a signed permutation of \((x,y)\).

The expected exact count is 200 basis pairs. This number is a certificate
assertion, not a hard-coded acceptance rule.

## Symmetry quotient

For each accepted basis \((u,v)\), form

\[
 \phi_{u,v}(\mathrm{AK}(3)).
\]

The corridor decision is unchanged by:

- swapping the two relators;
- cyclically rotating or inverting either relator;
- applying any of the eight signed permutations of the ambient basis.

The first three are built into the source-relator and pair conventions. For a
signed permutation \(\sigma\), map every corridor datum

\[
 (w,I,\text{isolated letter})
\]

letter-for-letter through \(\sigma\). Literal substitution, free reduction,
generator isolation, and output Aut-floor commute with this map. Hence signed
renaming gives a bijection of accepted corridors and preserves the minimum
output floor.

Define the class key of a transformed pair as the lexicographically least
canonical pair among its eight signed images. The 200 basis pairs are expected
to partition into nine keys, with class sizes

```text
16, 16, 16, 16, 24, 24, 24, 24, 40
```

whose sum is 200. The theorem proving quotient soundness is load-bearing; the
counts merely check its implementation.

## Corridor decision

Run the already-verified
`enumerate_short_corridors(pair, max_word_length=4,
max_template_length=6)` on each of the nine class keys.

For each class store:

- the canonical transformed pair;
- all member basis pairs and their Nielsen witnesses;
- the complete corridor trace SHA-256;
- enumerated and accepted counts;
- the distinct output Aut-orbits;
- the minimum output floor;
- every corridor attaining that class minimum.

The global lemma is `PROVED` exactly when some class minimum is at most 12.
Otherwise it is `REFUTED`.

A preliminary read-only diagnostic found minimum 14 in each of the nine
classes **[unverified until the certificate replays]**.

## Independent replay

The verifier must:

1. regenerate every reduced candidate pair of total length at most four;
2. replay each Nielsen witness step and check that it ends at distinct signed
   generators;
3. independently apply every accepted basis to the exact AK(3) words;
4. reconstruct the eight signed images and the nine-class partition;
5. check the exact 200 count, class-size multiset, and partition digest;
6. rerun the complete corridor census for every class key;
7. compare all nine trace hashes, accepted counts, output-orbit summaries,
   minima, and minimum witnesses;
8. derive the global verdict rather than trusting the recorded string.

The verifier reuses the already-tested corridor engine but shares no stored
basis or partition inference with the certificate.

## Files and isolation

Create only:

- `literature/proofs/AK3_PRIMITIVE_BASIS_CORRIDORS.md`;
- `experiments/stable_ac/rank3_compression/primitive_bases.py`;
- `experiments/stable_ac/rank3_compression/primitive_certificate.py`;
- `tests/stable_ac/test_primitive_basis_corridors.py`;
- `results/stable_ac/theory/ak3_primitive_basis_corridors.json`;
- `results/stable_ac/theory/AK3_PRIMITIVE_BASIS_CORRIDORS.md`.

Do not change the existing corridor engine, solver, runner, notebook, or
earlier certificate. The complete decision is a finite word/basis census, not
an AC graph search, and invokes no local search above the 1,000-node rule.

## Proof-loop continuation

If the lemma is proved, expand its best corridor into a stable certificate,
attach a classical length-at-most-12 certificate, and replay the whole chain.

If it is refuted, do not increase the basis or corridor bounds automatically.
The next mechanism is a **two-stabilization simultaneous-isolator theorem**:
introduce \(z=w_1\) and \(t=w_2\), compress both AK(3) relators into isolators,
and seek a rank-2 output after two controlled removals. This changes the
topology of the corridor rather than expanding another finite radius.

## Version control

Commit and push `codex/proofs` at each theorem, implementation, certificate,
and adjudication checkpoint, never more than twenty minutes apart while
tracked work exists. Do not open a pull request or merge.
