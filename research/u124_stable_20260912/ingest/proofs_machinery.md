# Proofs-branch machinery to reuse (not the AK3 destination)

From `codex/proofs` literature and `experiments/stable_ac/`.

## Substitution of a displayed block

If `D = z⁻¹ w` is a relator and another relator spells `U = u w v`, then
`U · (v⁻¹ D⁻¹ v) = u z v` by AC2+AC3. Inverse displayed blocks use a cyclic
rotation of `D`. Hidden cancellation: perform the replacement **before** free
reduction of a longer spelling.

## Isolator / Lemma-11 deletion

A relator with a unique occurrence of generator `b` is an isolator
`b^ε q`. Substitute `b ↦ e` (e is `q` or `q⁻¹`) into every other relator,
then delete `(b, isolator)` by Lemma 11. This is the rank-3 corridor engine.

## Certificate conventions on this branch

Many AK3 notes store JSON certificates under `results/stable_ac/theory/` with
independent tests under `tests/stable_ac/`. A claimed complete trivialization
must replay to a free basis and delete auxiliaries. Quotient equalities and
simultaneous automorphisms without a transported path are rejected.

## Do not continue

Period-two depth-4 obstruction ledgers, Neuwirth/SU2 sieves, and MMS02
Mahler/HNN control lanes are AK3-specific negatives. Reuse only the **move
realizations**, not the destination.

## Missing

`literature/proofs/PROOFS.tex`, `BACKGROUND.tex`, and `literature/txt/` are
not in the fetched trees. Reconstruct Lemma 11 from
`LEMMA_11_AND_THE_126_CLASSES.md` until the TeX is recovered.
