# ESCAPE_PLAN — overnight autonomous push (2026-07-20 → 07-21, branch `research/stable-ac-escape`)

**Mission (user directive):** brute-force one-shot CoV on the 124 came back 0/11,370 at 50k — find what actually escapes the local minima. Levers explicitly requested: extra stabilization with many generators (AC4/AC5, any `n_gen`), getting far from the AC presentation before descending, theory (prove or disprove pieces of stable ACC), and a Colab deliverable runnable in the morning at 50k–1M nodes. Solving any one of the 124 counts as success. Everything below derives from the already-vetted `experiments/IDEAS.md` + `experiments/IMPLEMENTATION_IDEAS.md` (ac-advisor verdicts baked in); this plan selects, sequences, and scopes for one night.

**Standing constraints (non-negotiable):** CPU+numba only; new files only (live solvers/runners/notebooks untouched); local search ≤ 1,000 nodes and ~10–20 presentations, production budgets are the user's on Colab; per-relator cap only, re-pad via `change_max_relator_length_of_presentation` when raising; every solve-claim needs a full Definition-2.1 path replayed by `verify_results.py`; "unsolved at budget B" is never a counterexample; `pytest tests/stable_ac -q` (and `tests/greedy -q` if the greedy seam is touched) before any commit that changes pipeline code; commits every 15–30 min, push immediately on any real result.

## Tracks (priority order)

### T1 — Productionized portfolio on the 124 (ideas 12 + 8 + 11) → Colab deliverable #1
The direct scale-up idea_bench was built to justify: race the validated top rankers (`cov_abel_len_lex`, `cov_nsubs_escape`, `cov_deep_z`, `cov_defining_iso`) plus the NEW same-orbit re-seed generator (idea 11, the un-harvested ms634 mechanism) on the 124 (`data/ms_unsolved_reps/aca_124.csv`) at production budget.
- Build: `experiments/stable_ac/cov/capfit.py` (idea 8, the proven per-relator cap-fit pre-filter — test against the 13712/0 CHECKED fixture, 0 false rejects allowed); `experiments/stable_ac/idea_bench/strategies/reseed_orbit.py` (idea 11 — Whitehead/Nielsen `AUTOS` compositions within the orbit, ranked by the `(abel, total_len, max_relator)` lex key, `aut_canon`-confirmed same-orbit); a `--bench aca_124` loader in `idea_bench/harness.py`'s bench table (config addition, new code path only).
- Control: plain greedy on the untransformed rep at the same budget (the harness's baseline strategy) — every comparison same-budget, same-cap.
- Local pilot: ≤1,000 nodes on ~15 of the 124 (spread over total length 13–25), assert rows/resume/schema; NOT expected to solve — proves the pipeline is budget-agnostic.
- Colab: 3-cell notebook (CONFIG/SETUP/RUN, branch `research/stable-ac-escape`), chunked like `run_cov` (flock claim + unique-key heartbeat — the orphan lesson), jsonl per (strategy, budget), Drive staging, resume-safe, budgets 50k → 1M ladder. W&B optional, entity `avigyapaudel045-aisc`, never hardcode the key.
- Failure mode owned: the 124 are genuinely unsolved; a portfolio may hit the same wall. Any solve gets `verify_results.py` replay with maximal suspicion before being believed or announced.

### T2 — Static rank-4/5 stabilization baseline (idea 10) → Colab deliverable #2
The mentor's un-run "dumbest possible thing" and the user's explicit ask: adjoin 2–3 coupled relators `z_i⁻¹w_i` up front, search at `n_gen = 4/5` with the shipped general-`n` solver (`solvern.py:search_n` / `solvern_fast.py`). NOT dynamic adjoin/destabilize mid-search (provably inert under length-sum priority — the Miasnikov null).
- Build: `experiments/stable_ac/nocov/run_static_rank.py` on the `run_nocov.py` scaffold (resume key = `(name, w_tuple)`, `ACSOLVERX_ALLOW_BIG` gate, `_repair_jsonl` first). Word-set family: pairs/triples drawn from A1 ∪ relator-subwords (A2), capped count per rep; re-pad for the added relators.
- Local pilot: one rank-4 and one rank-5 presentation at ≤1,000 nodes, cap-matched vs the rank-2 and rank-3 baselines.
- Colab: same notebook pattern; per-(rank, family) jsonl.
- Failure mode owned: may simply confirm rank-2 is as good — cheap to settle, and no one has.

### T3 — Descent-probe ranking (idea 2) — the untested challenger
Replace the abel-magnitude proxy (provably weakest on the hard residual) with a measurement: bounded ≤1,000-node probe per restart orbit, score = descent rate (`(start_total − min_total_reached) / nodes_to_reach`), tie-break by distinct-orbits-touched.
- Build: `experiments/stable_ac/cov/descent_probe.py`, pluggable as `key=` into the restart tree and as a strategy wrapper in idea_bench.
- Local: full descent-probe ranking on ≤20 reps (probes are ≤1k by design); production notebook does all 124 (probe budget stays 1k there too — it ranks, it does not solve).
- Payoff: directly answers "does a higher-start orbit offer a better descent basin"; an all-≈0 result on a rep is honest signal, not failure.

### T4 — Stall-triggered best-of-many CoV escape (idea 4) — the core mission mechanism, "get far then descend"
Mid-search Lemma-11 escape: plain-Python `heapq` loop over the existing `@njit` primitives (`get_neighbors_with_moves_nj`, `reduce_relator_nj`, `canonical_pair_nj` — imported, never copied) that can pause at a plateau (no `min_total` improvement for K pops), expose the incumbent pair, fan out its no-collapse-gated subword-CoV candidates best-of-many, resume in the winning coordinates, bounded recursion depth D.
- Build: `experiments/stable_ac/cov/stall_escape.py` (+ runner). Emit the FULL concatenated path (search prefix + CoV supermove + resumed search) for `verify_results.py`; never sum hops as linear.
- Local: 66-set at ≤1,000 nodes, D=1, control = one-shot-CoV-at-start at matched budget/cap. Mid-search triggering must beat one-shot or it adds nothing (that is the measurement).
- Bonus: its plateau leaders are exactly the candidate states T7 (thickenability) needs.

### T5 — Aut-quotient MITM diagnostic (idea 5)
Thin driver `experiments/stable_ac/cov/run_mitm_aut.py` over the shipped `equivalence_classes/search/aut_search.py:aut_multi_search` — seed each target + TRIVIAL, `stop_when_merged=True`; sweep the length *ceiling* (the binding knob), not just budget. Local: AK(3) + ~5 of the 124 at `nodes_per_source ≤ 1000`. A merge = stitched path → replay. Honest value: diagnostic on AK(3) (the balls were measured tiny/disjoint), real merge power on the 124 (this tool already cut 261→125).

### T6 — ATP oracle pilot (idea 7) — independent non-monotone solver
Prover9 has no length-monotonicity, and Lisitsa never ran the diverse-`w` residual. Feasibility-first: install Prover9 locally (time-boxed); encoder for Lisitsa's ground + non-ground encodings; pilot AK(3)→trivial (never via the broken MMS02 P-chain) + 3–5 of the 124 with a hard per-instance timeout (≤15 min each). Any returned sequence is untrusted until replayed as Definition-2.1 moves through `verify_results.py`. If install fails inside the box, document and drop.

### T7 — Thickenability feasibility (ideas 2/6) — the only lever that could *close* AK(3)
Lackenby: thickenable ⇒ settled (Thm 1.3 unstable ACC / Thm 1.2 stable bound); thickenability is decidable (Neuwirth). Tonight is feasibility only: can Regina (or equivalent) be installed and the presentation 2-complex → special-spine → thickenability decision actually be implemented? Deliverable: a memo with the exact encoding path, calibration-set design (known-thickenable + known-not at matched length), and a go/no-go. Code only if the path is tractable; any "thickenable" claim would need a second independent tool.

### T8 — Theory (opus agents, adversarially refereed)
The easy vein is mined (the adversarial hunt rejected all 9 of its own candidates); the named open targets are genuinely harder and worth one night of Opus attention:
1. A growth-rate bound (or saturation depth) for iterated-CoV orbit reachability — the missing theorem under the restart tree.
2. The `n_subs ≥ 2` length-change law — the missing generalization of the proven single-substitution bound.
3. An obstruction-barrier note: what would a stable-AC invariant have to look like, and why every abelian/quotient-type candidate dies (formalize the folklore into a checkable statement — a rigorous "no-go" is publishable-adjacent and sharpens where a disproof of stable ACC cannot come from).
Nothing gets called PROVEN without a hand-checkable argument + a ≤1,000-node computational check where finite; hostile-referee pass before anything lands in `STABLE_AC_NEW.tex`. A genuine proof/counterexample → commit + push immediately.

### T9 — High-cap escape arm (user directive, 2026-07-20 night) — cap as a *space* knob, paired with uphill mechanisms
User pushback (correct): the cap-inertness lesson was measured only at cap 24 vs 48 on 3 presentations; `ceiling-not-budget-was-binding.md` proves a cap can hide states unreachable at ANY budget, and Lackenby Thm 2.6 allows intermediate lengths exponential in input — so cap 24 may structurally exclude every solution path for some of the 124. The honest mechanism analysis: raising the cap on the plain best-first greedy is provably near-useless (the total-length heap never pops long states within feasible budgets — exactly why cap48 measured identical); the cap pays only when paired with an uphill mechanism. Arms: (a) **high-cap restart tree** — the PROVEN cap-fit bound means cap 24 rejects hop-2/3 restart orbits that cap 48/100 admits, so build the depth-2 portfolio at `default_cap ∈ {24, 48, 100}` and compare admitted-orbit counts and solves (same budget, compare only within same cap per Red line 10 — across-cap comparison is on solve/no-solve coverage only, stated as such); (b) popped-envelope instrumentation — log the max total length actually POPPED (not seen) per run so "does the cap ever bind at budget B" becomes measured; (c) T4's stall-escape runs at the elevated cap its CoV outputs need. Cap changes go in the filename identity (`mrl{cap}`).

## Advisor reconciliation (verdict: REVISE, 2026-07-20)
1. **Independent verification paths BEFORE claiming any solve** (the load-bearing REVISE): `verify_results.py` replays only flat Def-2.1 moves at `n_gen ∈ {2,3}`. T2 gets `verify_static_rank` logic: structural stabilization check (each `z_i` occurs only in its own coupled relator, `w_i ∈ F(x,y)`) + replay of the rank-4/5 path through the general-`n` spec to `trivial_n`. T4 emits segmented certificates: Def-2.1 replay per coordinate segment + structural re-derivation of each CoV junction (restart-tree convention), reported as stable-equivalence, never as a flat path. T5 uses `verify_certificates.py:replay_path` PLUS the pure-Python `words.py` replay (two independent stacks). T6: ATP output is a *lead*, not a solve, until a move sequence is extracted and spec-replayed; the encoder must pin the paper's own move numbering (AC1↔AC2 trap). Any `aca_115` solve = settles OPEN AK(3): requires both replay stacks + explicit flagging + never announced on one verifier alone.
2. **Branch base verified**: `research/stable-ac-escape` was cut from `test/stable-ac-moves-w4` at `3c29e00` (all infra present), not origin/main; notebook `BRANCH` will match.
3. **Priority**: T1 lands complete (built → ≤1k pilot → tests green → notebook + RUN_ME → pushed) before T3–T8 consume compute; T2 second. T6/T7 installs already done and smoke-tested by the feasibility probe (Prover9 proving; Regina importable, Rubinstein–Thompson available; Neuwirth is the from-scratch gap).
4. **Corrections to this plan's own text**: T2's "re-pad via `change_max_relator_length_of_presentation`" is a JAX-env artifact — `solvern.Pres` relators are unpadded tuples and the cap is `search_n`'s `cap=` argument; the structural check + spec replay replaces it. T8 target 2 must be the gap PAST `PROOFS.tex` Thm 2 (which already covers `iso_index=2` at any `n_subs`), and every candidate theorem gets grepped against the 7 shipped results + Lackenby §2 before being called new.
5. **T1 will not touch AK(3)/aca_115** (CoV-inert) — the AK(3) shots are T5/T6/T7; the morning report says so explicitly.

## Deliverables by morning
1. Colab notebook(s): T1 portfolio-124 (primary), T2 rank-4/5 (secondary), T4 stall-escape runner if it beats its control locally — each resume-safe, chunk-parallel, budget ladder 50k → 1M, with a RUN_ME.md stating exactly what to open and press.
2. Local pilot results committed under `results/stable_ac/` (new subdirs per track), verified schemas, tests green.
3. Theory outputs: any new PROVEN/CHECKED results appended to `STABLE_AC_NEW.tex` conventions (new file if substantial), plus the obstruction note.
4. Updated `IDEAS.md` annotations (first-result lines) for whatever tonight measures.

## Status (2026-07-21 ~05:00, end-of-night)
- **T1 SHIPPED**: portfolio runner + `reseed_orbit` + `cov_mu_lex` + aca_124 bench + `portfolio_124.ipynb` + RUN_ME; 15-rep pilot clean, resume no-op verified, tests green.
- **T2 SHIPPED**: `run_static_rank.py` + independent verifier + `static_rank.ipynb`; pilot 18/110 (easy rows only), all certs verify.
- **T4 SHIPPED, POSITIVE**: `stall_escape.py` — 12/22 vs greedy 10/22 at matched total 1k, +2 coverage 0 losses, certs verified; tuning: defaults robust (f12/pk400 degrade); 124-pilot 0/20 at 1k as expected.
- **T5 SHIPPED**: `run_mitm_aut.py` — dual-stack-verified merges, ceiling ladder; pilot (AK(3) + 5 shortest, time-bounded): no merges; ~2 pops/s at ceilings 26–30 (Whitehead canonicalization is the cost).
- **μ-DESCENT MAP (the night's biggest strategic find)**: 19/124 classes have a descending orbit-floor path within 2 CoV hops (15 hop-2-only, through uphill intermediates); 7 of the 28 exported starts descend FURTHER by depth 4 (aca_99: 25→19); the 50k sweep never searched any of these; benches `mu_descents_d2`/`mu_descents_d4` shipped; cap-48 arm = exact null at depth 2.
- **T6 DONE, honest negative**: Prover9 IG pilot — sanity proved; AK(3)/aca timeouts, memory-bound before time-bound; exploratory only.
- **T7 DONE, GO**: Neuwirth memo — 2-generator thickenability collapses to a 4-vertex Whitehead-graph rotation check; Regina validator mandatory; ~1-week build.
- **T8 DONE, two real results + one refutation**: the n_subs≥2 exact length law (one of the two named open targets — PROVEN + CHECKED 1995/0); the **orbit-floor refutation** (μ can descend under one gated CoV: AK(2) 11→10, ms640 row 6→2-standard; 4 of the 124 have hop-1 descents; AK(3) confirmed at a true wall); obstruction-barrier note. Committed home: `results/stable_ac/theory/` (literature/ is gitignored — see the new lesson).
- **T9 PARTIAL**: cap-48 arm in the notebook; popped-envelope instrumentation live in stall_escape (1k envelope = 27 — cap non-binding at small budgets, 50k datum pending); μ-descent depth-2 scan running.
- **T3 NOT BUILT** (descent probe): partially subsumed by `cov_mu_lex` + the μ-scan; the ≤1k realized-descent probe remains open for a future session.

## Cadence & risk
Commit every ≤30 min; push at once on any result. ac-advisor verdict gates implementation (this file is what it reviews). Recon (read-only) runs while the advisor deliberates. Subagents: sonnet for recon/mechanical, opus for theory/verification; ≤30 concurrent; intermediate artifacts only under the repo or `$CLAUDE_JOB_DIR/tmp`, never `/tmp`. If a track stalls or its local control beats it, kill it and reallocate to the tracks that are winning — the plan is a portfolio, not a promise.
