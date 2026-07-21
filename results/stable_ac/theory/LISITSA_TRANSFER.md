# Lisitsa-transfer analysis: the Q normal forms are the right ATP/induction targets

*2026-07-21, follow-up to the two template propositions. Full analysis by an opus agent; constructions cross-verified against the ladder's floor reps (14/14 exact orbit matches).*

## The identification (the tightest transfer fact)

The template source families **literally ARE Miller–Schupp presentations**: `P_{n,δ}`'s parametric relator is exactly `x⁻¹yⁿx = yⁿ⁺¹` — the same Baumslag–Solitar relation Lisitsa's ATP program was built around (he trivialized `MS_n(b⁻¹aba⁻¹)`, n ≤ 7); our aca classes are MS members with different companion words that his runs never touched. And the templates hand over a normal form with BETTER regularity than his family: `Q_{n,δ}` has an explicit constant (n-free) relator — the analog of the fixed anchor his strongest (IN-style, one-sided) encoding exploits — and ONE parametric power block where his has two.

## Results

1. **≤1k greedy on all 14 Q-form members: 0 solves** (full budget exhaustion; consistent with the μ-floors 15–19 > 12). No LEAD; the MU_CRITERION bar was not triggered.
2. **The n → n+1 induction step exists structurally but was not found as a bounded raw-move witness.** CoV provably cannot supply it (μ(Q_n) = n+12 strictly increasing ⇒ orbit-disjoint); depth ≤ 2 conjugate-multiply enumeration is negative; the telescoped-unit form (`r2(n) = c·uⁿ·d` in z-coordinates) says `r2(n+1) = r2(n)·u` is one unit-multiply — but only AFTER the CoV, so the step should be searched in z-coordinates, not raw Q. If constructed, one trivialized member cascades through the family.
3. **The prior ATP nulls were partly measurement artifacts.** Prover9's auto-mode defaults (500 MB, weight-pruning) discard exactly the heavy two-hump intermediates an AC-trivialization must traverse: Q-runs returned `sos_empty` ("exhausted") in 13–38 s while silently dropping ~71k clauses by weight — a FALSE exhaustion, confirmed by re-running with `max_weight=400` (search then runs to the time limit still generating). **`encode.py` now writes `assign(max_megs, 4000)` and `assign(max_weight, 10000)` by default** — every earlier timeout/exhaustion row predates this fix and understates ATP's reach.

## Morning ATP recommendation (fixed encoder)

Target the payoff cases, not the giants: **Q_{2,±1}** (μ = 14, a FRESH orbit distinct from its non-descending sources aca_117/119 — an ATP proof there is a direct stable-solve LEAD for those classes), then Q_3/Q_4 for a *regular* proof to seed the induction skeleton. Colab high-RAM, hours-scale timeouts, `max_megs` sized to the machine. Expect Lisitsa-style exponential growth in n (his IG failed at n = 7); the realistic prize is the small-n members plus the induction step, not a family sweep.
