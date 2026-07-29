# R1d — short-member harvest around the verified path (design, pending ac-advisor gate)

Claim addressed: hunting a γ_N = 0 state in AK(3)'s CLASSICAL class (a hit ⇒ AK(3)
AC-trivial ⇒ stably AC-trivial). Status: DESIGN — do not implement before the advisor gate.

## Rationale (yield model + census-gap analysis)

- The advisor's E-yield model says sphericality odds collapse ~3^{-N} in total length N:
  the shortest class members dominate all other targets by orders of magnitude.
- Codex's height-17 component census (1,000 states, exhausted, all non-thickenable) is
  CEILING-RELATIVE: it closed the component of AK(3) in the subgraph of states with total
  length ≤ 17 (per-relator cap 16). A class member of length ≤ 17 reachable ONLY through
  intermediates of length > 17 is invisible to it. The verified 53-move path spends 32
  states at lengths 18–25 — a corridor the ceiling forbids — before descending into the
  censused region. States hanging off that corridor are exactly where un-censused short
  members can live.

## Protocol

1. Roots: the 32 path states of total length ≥ 18 (indices 0–31), plus P25 itself.
2. Per root: best-first search, priority = total length, children = the 12 h-moves at
   per-relator cap 15 (the fixture's structural cap; this bounds total length by 30),
   node budget **1,000 pops per root** (hard rule compliant), dedup within run.
3. Harvest: every distinct state with total length ≤ 21 encountered anywhere in any run
   (after cyclic reduction; record both exact and reduced forms).
4. Dedup harvest against (a) the codex 1,000-state component census, (b) the 54 path
   states, (c) itself (canonical form: lexicographic minimum over cyclic rotations,
   inversion NOT quotiented — γ_N is realization-sensitive; keep realizations distinct
   when words differ).
5. γ_N-test every novel harvested state with the fable rank solver (fail-closed; UNSUPPORTED
   routed to factorial census when ∏(deg−1)! ≤ 5·10⁶, else recorded UNKNOWN_SIZE).
6. Any YES: witness_check + TC + report immediately (it settles AK(3)).
   All-NO: certified bounded negative appended to the running corpus with exact counts.
7. Local scale: ≤ 33 roots × 1,000 pops; certificate evaluations unbounded but each
   polynomial. Production scale-up (budget ≥ 10⁴ per root, ceiling 40, more roots — e.g.
   harvested novel states become new roots iteratively): Colab runner spec for the user,
   same code, resume-safe jsonl.

## Honesty constraints

- Each search is capped: "no new short members found" is a statement about THIS protocol
  at THIS budget, never about the class. The ceiling lesson (raising a cap can expose
  states unreachable at any budget) applies to our cap-15 too — say so in the writeup.
- The E-model is a heuristic prior, not a bound; it directs effort, never justifies a
  conclusion.
- A YES on a harvested state needs its membership chain: record the full move path from
  the root (hence from AK(3)) for every harvested state — replayable membership proof.
