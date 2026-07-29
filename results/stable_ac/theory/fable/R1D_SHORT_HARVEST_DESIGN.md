# R1d — short-member harvest around the verified path (design; gate verdict REVISE — reconciled below)

## GATE RECONCILIATION (29-07-2026, all five items adopted; overrides the text below where
they differ)

1. **Root set corrected**: roots = path indices 0–31 (32 roots; P25 IS index 0 — no
   double count). Only 12 of them have total length ≥ 18; the other 20 are short states
   sitting on the FAR side of the 18–25 corridor from AK(3) — census-gap candidates
   precisely for that reason. Indices 32–53 form the ≤16 corridor into AK(3) (likely
   censused; dedup will tell).
2. **Canonical key = quotient by cyclic rotation + relator inversion + relator swap.**
   Advisor-proved (independent implementation reproducing both codex histograms exactly,
   then verifying invariance of the FULL defect histogram under all three operations, with
   the structural reason: reversing a 2-cell's attaching orientation gives isomorphic
   (E,A,B,ν) data under d↔h). NEVER quotient by Aut(F₂). Codex's stored canonical keys use
   a different symbol order — re-canonicalize their 1,000 states with OUR key before
   deduping; a false-duplicate drop loses a real target.
3. **Independently confirm codex's closure**: their certificate reports node cap 1,000 =
   pops = component size — the signature of a capped run. Before trusting "already
   censused", run a post-hoc closure pass ourselves: enumerate all bounded children of all
   1,000 states, assert each lands in-set or out-of-bounds. If closure fails, the
   dedup labels flip from "duplicate" to "novel" for the affected states.
4. **Selection key = E descending** (E = 2∏m_uv!/((n_x−1)!(n_y−1)!) for K₄ and the
   support-appropriate spherical counts otherwise), with length ≤ 21 demoted to a cheap
   prefilter. E is non-monotone in length (measured: a length-19 path state beats the best
   length-17 one by 8.6×). Record E per tested state — the harvest then doubles as the
   at-scale YES-rate control demanded by the R1 gate (predicted vs observed).
5. **Accounting**: output-based degenerate gate (any relator < 3 letters or < 4 germs ⇒
   UNSUPPORTED, never NO); expect ~5–6% UNSUPPORTED (tree-support types) reported as a
   separate line, never folded into "all-NO"; ONE non-iterative local round (iterative
   re-rooting is Colab-tier); "novel" always means "not previously γ_N-tested", never "new
   to the class" (membership is by construction); membership chains include the root's
   prefix chain to AK(3) plus cyclic reductions recorded as AC3.
   Also adopted: the h-move generator differs from codex's Def-2.1 child generator
   (h-conjugation adds uncancelled length +2), so the harvest is census-novel even inside
   the ≤17 stratum — generator-relative as well as ceiling-relative.

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
