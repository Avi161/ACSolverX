# The acx-cert-v1 Certificate Schema and Its Verification {#app:certs}

Every solution and every stable-AC equivalence claimed in this paper is exported as an acx-cert-v1 JSON certificate and checked by two independently written verifiers before it is reported.

## Schema

A certificate is a JSON object with fields: `certificate_version` (schema version string); `name`; `claim` (a human-readable statement of what is being certified); `start` and `end` (each an object `{n_gen, relators}`); `end_is_trivial` (boolean, true iff `end` must equal the trivial presentation on `n_gen` generators); `steps` (an ordered list of length $T$); `states` (the list of intermediate presentations, length $T+1$, with `states[0]==start` and `states[-1]==end`); and `meta` (free-form provenance — source paper or line numbers, generator naming, and similar bookkeeping).

## Step types

Six step types are implemented; the field names below are exact, not paraphrased:

- **concat** `{i, j, sign}` — $r_i \to$ freely-reduced$(r_i \cdot r_j^{\text{sign}})$ (AC1; `sign=-1` concatenates with $r_j^{-1}$).
- **conjugate** `{i, g}` — $r_i \to$ freely-reduced$(g\cdot r_i\cdot g^{-1})$ (AC3).
- **stabilize** `{z, w}` — appends generator $z=$ `n_gen`$+1$ and the cyclically-reduced relator $z\cdot w^{-1}$ (AC4 plus realizing $z=w$).
- **eliminate** `{gen, ri, ...}` — Lemma-11 removal of `gen` using its exactly-once occurrence in relator `ri`; generators above `gen` are renumbered down by one (the packaged AC5).
- **relabel** `{perm, invert}` — a bijective, sign-respecting permutation of the generator set: an AC-equivariant renaming, not a move on relators.
- **substitution** `{ci, a, b, i, j, c_inv}` — the composite move used by the base greedy solver (\ref{sec:methods}); verified by checking that the resulting state lies in the recomputed neighbor set of the preceding state, rather than by replaying finer sub-steps.

There is no separate step type for a bare AC2 inversion of a whole relator. A full-relator sign flip is instead absorbed by the canonical-equality quotient the verifiers already apply (reorder relators, cyclically rotate, invert) — see the mutation-sensitivity note below, where this distinction mattered in practice.

## Verification levels

- **L1 (replay).** Recompute each step's post-state from its recorded parameters and the preceding state; it must equal the next recorded state exactly.
- **L2 (preconditions).** `eliminate`'s generator must occur exactly once in the cited relator; `relabel`'s permutation must be bijective and sign-consistent; every letter must lie in the valid signed-generator range for that state's `n_gen`.
- **L3 (global invariants).** Every state must be balanced (`n_gen` equal to the relator count, no empty relator); the abelianization matrix's determinant must have absolute value $1$ at every state, computed by exact-integer Bareiss elimination (no floating point); if `end_is_trivial` is claimed, the end state must equal $\langle x_1,\dots,x_k\mid x_1,\dots,x_k\rangle$ up to relator reordering.

## Two independent verifiers

Every certificate is checked by the engine author's verifier and by a second verifier authored black-box from the schema and the math above alone, with no access to the engine's source and its own free/cyclic reduction, canonicalization, integer-determinant, and step-replay logic. Across the campaign the two verifiers together performed $20{,}947$ checks with $0$ failures. All five exported chain certificates pass both (Table \ref{tab:certs}): `appendixF_P25_to_AK3` (53 steps, the literature's $\mathrm{P25}\to\mathrm{AK}(3)$ replay of \ref{app:misprint}), `laneF_F_to_AK3` (21 steps, the path from $F$ — a 2-generator presentation AC-equivalent to AK(3) — to AK(3) itself), and three small stable-solver certificates recording in-search destabilizations (3, 1, and 1 steps respectively).

## Mutation sensitivity

Sign flips, corrupted target states, swapped intermediate states, and mis-pointed eliminations are all rejected by both verifiers. One candidate mutation was initially flagged as accepted; on inspection it was not a soundness hole but a genuinely valid alternative move — inverting a relator of length one is itself a legal AC2 move, correctly treated as a no-op by the canonical-equality quotient rather than as a tamper. A semantically meaningful tamper test therefore has to flip an *interior* letter of a relator of length at least three in a middle state, not merely a sign.

## Coverage and chain composition

Of the 151 catalog leaves classified during the campaign, 14 have exported, machine-verified leaf certificates; the remaining 137 classifications are recorded as data (solved/unsolved, node count, floor reached) but were not individually exported as certificates. Certificates concatenate whenever one certificate's end state matches the next certificate's start state exactly, so a full stable-AC chain — stabilize $\to$ substitution path $\to$ eliminate $\to$ 2-generator trivialization path, further composed with the P25 bridge of \ref{app:misprint} — assembles automatically into a single machine-checkable certificate. This composition machinery already produces every certificate reported above and would apply unchanged to any future solve.
