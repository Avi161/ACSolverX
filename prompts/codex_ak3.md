# Codex task — resolve AK(3) (Andrews–Curtis)

You are working inside the `ACSolverX` repo (a CPU+numba Andrews–Curtis search codebase). Attack one problem: decide whether **AK(3)** is (stably) AC-trivial or a genuine counterexample. Work from the repo's own record — verify every claim below against source; do not trust this restatement.

## Target

```
AK(3) = ⟨ x, y | xyx = yxy,  x³ = y⁴ ⟩,   total length 13.
```
Repo string encoding (lowercase = generator, uppercase = inverse): `r1 = xxxYYYY`, `r2 = xyxYXY`. Its canonical form in the data is `aca_115` (= `13_1`), stored in `data/ms_unsolved_reps/ak3_only.csv` as `YXYxyx | YYYYxxx`. It is the **unique minimal open case** of the AC conjecture (all length ≤12 are AC-trivial; every length-13 presentation is AC-equivalent to trivial or to AK(3)).

## What counts as a result — and the asymmetry that governs everything

- **Trivialize (tractable, verifiable):** a move path reducing AK(3) to `⟨x,y|x,y⟩` that passes independent replay by `experiments/stable_ac/verify_results.py`. Say whether it is **AC-trivial** (AC1–AC3 only) or **stably AC-trivial** (uses stabilization / change-of-variables) — different theorems, never conflated.
- **Counterexample (the real 60-year-open problem):** a rigorous, computable **AC-invariant obstruction** separating AK(3) from trivial. No such invariant is known, and this repo *proves* the usual layers can't supply one (`results/stable_ac/theory/OBSTRUCTION_BARRIER.md`: abelianization is forced to `|det|=1`; the complex is contractible with trivial Whitehead group). **A search that stalls is evidence of nothing** — there exist AC-trivializable presentations needing >10^10000 moves. "Unsolved at budget B" is never a counterexample; the only decidable handle for the negative direction is thickenability (below).

## Traps — do not trip these

1. **AK(3)'s stable status is OPEN.** The believed proof (MMS02 → a length-25 presentation → AK(3)) is *broken* by a misprint Shehper et al. found; Lisitsa (arXiv:2501.18601) re-proves only the *unstable* link. Any in-repo bullet saying "AK(3) is known stably AC-trivial" (e.g. the "Literature fit" bullet in `experiments/stable_ac/cov/ak_3_universal_test/RESULTS.md`) is **stale — disregard it.**
2. **Reaching `Q` or any stable-class sibling is not progress** — it shares AK(3)'s wall by construction.
3. **The length-13 floor holds two Aut-orbits** — `min_relator_length` can't see an orbit switch at equal length. The second, **orbit-2** (`YYXXyx | YYYxyXX`), is *classically AC-equivalent to AK(3)* and far better-connected (6 length-15 exits vs AK(3)'s 1).
4. **A change-of-variables solve proves *stable* triviality only**, and CoV is near-inert on AK(3) (reaches 2→12→55 orbits over 3 hops, none below length 13). Don't expect it to solve AK(3).

## Best shots (honest priors)

1. **Greedy from orbit-2 (`YYXXyx | YYYxyXX`) at production budget** — a solve there certifies AK(3) with *no stable caveat*; never run at 50k–1M nodes. Prepare + validate the pipeline locally at ≤1000 nodes, hand the big run to Colab.
2. **Thickenability certificate (the only lever that could *close* AK(3)):** Lackenby — a thickenable trivial-group presentation is AC-trivial; decidable by Neuwirth's algorithm (for 2 generators, a finite genus-0 rotation-system check). See `experiments/stable_ac/thickenable/NEUWIRTH_FEASIBILITY.md`. **A false positive silently prints a false proof — cross-check every "thickenable" verdict against Regina before believing it.**
3. **Exhaustive ceiling-18/19 AC-component enumeration** (the ≤17 component is closed at 1000 states / 168 orbits, none below length 13) — does a shorter state or new orbit appear?

## Do this

1. **Orient:** read `experiments/stable_ac/cov/ak_3_universal_test/RESULTS.md` and `results/stable_ac/theory/MU_CRITERION.md`; confirm for yourself that AK(3)'s stable status is OPEN and orbit-2 is classically AC-equivalent to it.
2. **Pick a direction and write the exact deliverable that would count** (per the section above). Highest-EV first target: greedy from orbit-2 at scale, and/or the thickenability certificate.
3. **Gate your plan before coding:** read `.claude/agents/ac-advisor.md` and adopt it as a hostile-referee reviewer persona in a separate pass over your plan; reconcile every objection against cited sources.
4. **Build new files only** (never modify the solvers/runner/notebooks). Runtime is CPU + numba, `.venv/bin/python3`. **Never run a search above node_budget 1000 yourself** — production budgets go to Colab. Verify every solved row by independent replay. Report results labelled AC-trivial vs stably-AC-trivial, and state every negative as bounded ("unsolved within budget/ceiling B"), never as a counterexample.
