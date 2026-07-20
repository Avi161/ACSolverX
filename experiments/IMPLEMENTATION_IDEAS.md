# IMPLEMENTATION_IDEAS.md — 13 buildable stable-AC search moves

Companion to [`IDEAS.md`](IDEAS.md). That file ranks *why* each research direction might pay off (with the load-bearing caveats and the ac-advisor verdicts); this file is *how* — thirteen concrete things to build now, each grounded in real functions in this repo (`file:line` cited from the actual code), with the new file to create, the algorithm, the local smoke-test, and the honest failure mode. Ideas 1–10 predate the benchmark; the *What idea_bench observed* section below folds in the empirical sweep ([RESULTS.md](stable_ac/idea_bench/RESULTS.md)), and ideas 11–13 are new, derived from it. Read `IDEAS.md` first for the caveats; they are cross-linked, not repeated.

## The one thing to internalize before building: AK(3) ≠ the 124

The project's own measurements (see `IDEAS.md` §Bottom line, and `experiments/stable_ac/cov/`) split the targets sharply, and every idea below is tagged by which target it actually serves:

- **The 124 Miller–Schupp residual** has real *single-hop* change-of-variables (CoV) diversity — 5–19 distinct Aut-orbits reachable per rep in one hop, growing geometrically with hop depth. CoV-based levers (restart trees, abel-ranking, cap-fit pre-filter, level-set expansion) can plausibly move the solve count here. **Tag: `124`.**
- **AK(3)** is CoV-*inert*: its whole CoV family reaches only **2 Aut-orbits single-shot**, its length-13 floor is the shortest of every orbit it can reach (2→12→55 over three hops, none below 13), and abelianized magnitude — the strongest cheap ranker — is provably weakest exactly here (near-identity abelianization, astronomical AC-distance). **Ranking restart points by abel-magnitude on AK(3) is self-undermining.** The ideas that actually point at AK(3) are the *non-CoV* ones — an empirical descent probe (idea 2), Aut-quotient meet-in-the-middle (idea 5), a thickenability certificate (idea 6, the only idea that could *close* it), and an ATP oracle (idea 7). **Tag: `AK(3)`.**

If an idea is tagged `124` do not expect it to touch AK(3), and vice-versa. Ideas that genuinely serve both are tagged **`both`**.

## What idea_bench observed (empirical update — `benchmark_combined_22`, July 2026)

`experiments/stable_ac/idea_bench/` raced 16 start-transform strategies against the greedy baseline **at the same node budget** (500 and 1000) on the canonical ladder+reach benchmark; full result and reproduce commands in [`idea_bench/RESULTS.md`](stable_ac/idea_bench/RESULTS.md). Several ideas below are now evidence-backed — with one load-bearing caveat: the presentations it cracked are known-AC-trivial *ladder* cases (CoV finds a faster route), **not** the genuinely-unsolved 124 or AK(3). What transfers is the mechanism and the ranker, not a triviality proof.

- **The CoV-restart mechanism works, and cheaply.** CoV-transformed starts turned **6 baseline-unsolvable ladder presentations into solves at ≤1000 nodes** (best strategy 16/22 vs baseline 10/22 at budget 1000), including ms634 whose *baseline* optimum is 574k nodes — solved in 39 nodes after a change of variables. This is idea 1/3's premise, confirmed on real presentations.
- **Best ranker observed: the `(abel_magnitude, total_length, max_relator)` lexicographic key** (`cov_abel_len_lex`: 6 coverage, 9 efficiency wins, 0 regressions), beating plain abel-magnitude (`cov_abel`: 6/7). **This updates the default ranking key in ideas 1 and 3 from bare abel-magnitude to the abel-then-length lexicographic key.** The descent-probe (idea 2) was not in this race — it stays the untested challenger the abel+length key now sets the bar for.
- **Only substitution buys coverage — relabels and rotations do not.** Two controls: re-seeding the same presentation under rotations (`rotation_seed`) and under the 8 signed relabels (`relabel8`) reached **0 new coverage** (relabels gave 6 *efficiency* wins — a speed lever only). So a coverage strategy MUST do a genuine change of variables; this retires relabel/rotation diversification as a *coverage* idea (it survives only as an efficiency idea).
- **The coverage mechanism is MIXED — not only orbit escape.** Spot-checks: pres 609's win was an `n_subs≥2` orbit escape (new Aut-orbit), but **ms634's win was a same-orbit automorphic re-seed** (`n_subs=1`, identical Aut-canonical form) that simply hands the greedy a solve-enabling string the relabels/rotations never reach. So "target `n_subs≥2` for new coordinates" (ideas 1/4) is only *half* the coverage story — the other half is new idea 11.
- **AK(3) and 19_40 confirmed on the wall.** Both reach cases, plus the deep ladder cases ms605/623/636/568, were **unsolved by every strategy at ≤1000**, empirically confirming the AK(3)-inert framing above. And baseline difficulty does NOT predict CoV difficulty (ms634 at 574k cracked; ms605 at 60k not) — coordinate choice is what matters, which is why the whole restart-tree program is worth running.

## Cross-cutting rules (apply to every idea — stated once)

- **CPU + numba only.** No JAX/GPU/PPO. `envs/` and `network.py` are read-only spec. New files only — never edit `search/greedy_baseline.py`, `run_baseline.py`, `stable_ac/solvern.py`, or any live runner/notebook. ([root CLAUDE.md hard rules](../CLAUDE.md))
- **Local search ≤ 1000 nodes, ≤ ~20 presentations — no exceptions.** Everything below is a *runner the user launches at production budget on Colab*; locally you smoke-test at ≤1000 to prove the pipeline is budget-agnostic, never to solve. Mirror `run_nocov.py`'s `ACSOLVERX_ALLOW_BIG=1` gate so a big budget refuses to run locally.
- **Per-relator cap only** (`MAX_RELATOR_LENGTH`, default 24). No total-length budget. Re-pad with `envs/utils.py:36 change_max_relator_length_of_presentation` whenever the cap is raised.
- **Every solve-claim emits a full Definition-2.1 path and is verified independently.** A solve is worthless until `experiments/stable_ac/verify_results.py` replays its `(target, jsign, k1, k2)` path through `greedy_tests/spec/` (never a solver — the independence is the point). A CoV/stabilization prefix is part of the path; never sum hops as if linear, never report `path_length` for a CoV run (it excludes the transform's own moves — score on `nodes_explored` / `solved`). Store paths as moves, never as string pairs ([lesson](lessons/store-paths-as-definition-2-1-moves.md)).
- **"Unsolved at budget B" is never a counterexample.** Bridson/Lishak towers survive stabilization; AK(3) stable-triviality is OPEN and nothing here claims a solve.

---

## 1. Iterated-CoV restart-tree driver — `124` · *ship-ready*

**Build:** `experiments/stable_ac/cov/run_restart_tree.py` (runner). The planner already exists — `experiments/stable_ac/cov/restart_planner.py:68 build_restart_plan` — but it only *ranks* restart points; it runs no search. This wires it to a real production sweep.

**Reuse:** `restart_planner.build_restart_plan(r1, r2, depth, cap, max_nodes)` for the ranked restart list; `experiments/run_baseline.py:22 greedy_search(...)` (the single monkeypatch seam, `solver="compact"`) to search each restart point; `run_baseline.py:159 load_dataset` + `:151 int_line_to_relators` to read `data/ms_unsolved_reps/ms_reps_126.txt`; `run_cov.py`'s jsonl+resume+`_repair_jsonl` pattern for durability (import it, don't reimplement).

**Algorithm:** for each of the 124 reps → `build_restart_plan` to get its distinct-orbit restart points (deduped by `aut_canon`, cap-fit filtered) → run `greedy_search` at production budget on each restart point best-first → stop the rep on first solve, log `(rep_id, restart_rep, hop, nodes_explored, solved)` to jsonl, resume-keyed on `(rep_id, orbit_rep)`. The ranking key is pluggable — **default now the `(abel_magnitude, total_length, max_relator)` lexicographic key** (idea_bench's observed best, `cov_abel_len_lex`), with idea 2's descent probe as the untested challenger. Note `restart_planner.py` currently ranks by bare `abel_magnitude` — swap in the lexicographic key.

**Budget/feasibility:** planner is CPU-cheap (a few hundred `aut_canon` calls, ~5 ms each). Local smoke-test: one rep, `depth=1`, `node_budget=1000`, assert jsonl rows + resume. Production: user's Colab, `depth=2–3`.

**Observed (idea_bench).** A portfolio version of exactly this — abel+length-ranked CoV starts, best-first — is what cracked 6 baseline-unsolvable ladder presentations at ≤1000 nodes. So the mechanism is validated on real presentations; the open question is only whether it carries to the *unsolved* 124 (where, unlike the ladder, no route is known to exist below the wall).

**Failure mode:** reachability is *not* solving — the restart tree reaches an order of magnitude more starting points but they may all sit at the same wall (on AK(3) they provably do). This is the honest 124 bet: *more descent basins to try*, ranked, not a trivialization. See `IDEAS.md` idea 3 + Bottom-line point 2.

---

## 2. Empirical descent-probe restart ranking — `both` · *the real value-add*

**Build:** `experiments/stable_ac/cov/descent_probe.py` (ranking function, plugs into idea 1's driver as its `key=`).

**Why this over abel-magnitude:** abel-magnitude is a *solution-depth proxy*, strong on shallow cases and provably weakest on the hard residual and AK(3) (`IDEAS.md` idea 1). Ranking the exact restart points you care about by the metric that fails exactly there is self-undermining. Replace the proxy with a *measurement*: how much does each restart orbit actually descend before it stalls?

**Reuse:** `run_baseline.py:22 greedy_search` at `node_budget ≤ 1000` per probe; from its returned stats dict read `min_relator_length` (shortest relator reached) and `nodes_explored`; `aut_canon` (`equivalence_classes/lib/autcanon.py:115`) to count distinct orbits touched if you also probe with `acmoves.children`.

**Algorithm:** for each reachable restart orbit, run a **bounded ≤1000-node probe** and score by descent rate = `(start_total_len − min_total_len_reached) / nodes_to_reach_it`, tie-broken by distinct-orbits-touched-before-stall. Rank restart points by descent rate, feed idea 1's driver best-first. This directly operationalizes the open question `IDEAS.md` poses — *"does a higher-start orbit have a better descent basin than AK(3) itself?"* — swapping a known-weak proxy for the thing it was proxying.

**Budget/feasibility:** N restart points × ≤1000-node probe each; the probe budget is a knob far below the production solve budget, so a full descent-ranking of a rep's restart tree is affordable locally *as a ranking pass* (it explores, it does not try to solve). Cap total probe nodes per rep.

**Failure mode:** if every reachable orbit sits at the wall, all descent rates are ≈0 — but that is *itself honest signal* ("this rep has no better basin in the CoV tree"), not a bug. On AK(3) this is the likely outcome and worth knowing definitively; that is exactly why it is the AK(3)-relevant CoV experiment.

---

## 3. Abelianized-magnitude try-order sweep on the 124 — `124` · *cheap baseline the probe must beat*

**Build:** `experiments/stable_ac/cov/run_abel_order.py` (runner).

**What it settles:** on the shallow 66-set, trying a presentation's CoV candidates sequentially in ascending abel-magnitude order solved **33/34 solvable reps at total budget 200 vs 20.6 for random order** (`IDEAS.md` idea 3, already run). The *load-bearing* untested claim is whether that lift survives on the hard 124 residual at production budget. This runner is that experiment — the O(1)-cost prior that idea 2's descent probe has to beat to justify its extra cost.

**Reuse:** `experiments/stable_ac/cov/cov.py:466 enumerate_cov(r1, r2, ...)` for the full candidate family (walks `cov_branches`, keeps all four key fields `(pres_id, z_word, iso_gen, iso_index)` — never `apply_cov_once`, which is first-wins); `restart_planner.py:46 abel_magnitude` for the key; `run_baseline.greedy_search` + jsonl.

**Algorithm:** per rep → `enumerate_cov` → sort candidates by the `(abel, total_length, max_relator)` lexicographic key ascending → try sequentially, each consuming its `nodes_explored` if it solves else the full per-candidate cap, stop on solve → log solved/total-budget-spent. Compare against random-order and against idea 2 at matched total budget.

**Observed (idea_bench, ladder).** This try-order (as `cov_abel_len_lex`) was the *best* strategy on `combined_22`: 6 coverage + 9 efficiency wins, 0 regressions, at both budgets — the abel+length key beats bare abel. So the order-matters claim holds on real presentations. But the ladder is known-solvable; the load-bearing test — does the lift survive on the *unsolved* 124 — is still open, so run it there next (idea 12 is the runner for it).

**Failure mode:** the caveat is the whole point — this is expected to *shrink* on the hard residual (start min-relator 7+ → 12% solve, abel-magnitude barely separates 5.6 vs 6.3). Run it precisely to measure how much. See `IDEAS.md` idea 1's "first result" + the load-bearing caveat.

---

## 4. Stall-triggered best-of-many Lemma-11 CoV escape — `124` · *the core mission mechanism*

**Build:** `experiments/stable_ac/cov/run_stall_escape.py` — and note the honest wrinkle below, it needs its **own search-orchestration wrapper**, not a call into the existing solver.

**Feasibility wrinkle (do not skip):** the mechanism needs the *incumbent frontier state at the plateau* — the actual `(r1, r2)` pair the search is stuck on. The existing solvers do **not** expose it: `GreedyBaselineSolver.solve` (`greedy_baseline.py:335`) returns `(path, moves, nodes_visited, new_seen)` with `path=None` on a stall, and the stats dict carries only `min_relator`/`max_relator` *strings*, not the frontier pair. So this idea requires a new plain-Python `heapq` loop over the existing `@njit` primitives — `get_neighbors_with_moves_nj` (`greedy_baseline.py:209`) or `expand_node_nj` (`:498`) for successors, `reduce_relator_nj`/`canonical_pair_nj` for the state — that can *pause at a plateau and return the incumbent pair*. This is exactly the sanctioned `@njit`-the-math / Python-the-orchestration split ([lesson](lessons/numba-jit-split.md)) and stays new-files-only.

**Reuse:** the `@njit` successor/reduce/canonical primitives above (imported, not copied); `cov.py:257 cov_branches(r1, r2, z_word, iso_gen=...)` to fan out escape candidates from the plateau pair; `cov.py:398 subword_candidates` (no-collapse-gated) or `word_families.py:82 build_a2` for the `z`-family; `restart_planner.abel_magnitude` to pick among branches.

**Algorithm:** run the Python greedy loop → detect a plateau (no `min_total_len` improvement for K pops) → take the incumbent leader pair → fan out its subword-CoV escape candidates (**best-of-many, not one directed `z`** — the project's data shows no single directed `z` reliably crosses the valley) → pick by abel-magnitude or idea-2 descent → resume the loop in the winning coordinates → recurse to bounded depth D. Emit the FULL concatenated Definition-2.1 path (search prefix + CoV supermove + resumed search) for `verify_results.py`.

**Budget/feasibility:** local smoke-test at ≤1000 nodes, D=1, one MS rep; the honest control is idea 1's one-shot-CoV-at-start sweep — mid-search triggering must *beat* it, cap-matched, or it adds nothing. Each recursion rung adds an uncounted unbounded CoV prefix — account for it in the emitted path, never sum rungs as linear.

**Failure mode:** `IDEAS.md` idea 6 — the supermove already absorbs the Two-Hump valley on solved paths (0.4% of steps increase length), so the payoff, if any, is on *unsolved* instances where a hump has yet to be exhibited. The burden is to exhibit one, not assume it.

---

## 5. Aut-quotient bidirectional meet-in-the-middle — `AK(3)` + `124` · *reuses shipped infrastructure*

**Build:** `experiments/stable_ac/cov/run_mitm_aut.py` (thin driver). Almost all the machinery already exists under `equivalence_classes/`.

**Why the quotient, not raw bidirectional:** raw bidirectional search (`IDEAS.md` idea 14) targets exponential *depth* while greedy's failure is a *local minimum*, and a 3-generator backward state can never equal a 2-generator forward state. But `experiments/equivalence_classes/search/aut_search.py` already runs BFS in the **Aut(F₂)-class quotient** — the graph where relabels collapse and the wall was measured *smaller* — with path-carrying merges, one CoV automorphism per step.

**Reuse:** `aut_search.py:87 aut_multi_search(sources, nodes_per_source, max_total, seam_only=False, ..., stop_when_merged=True)` — seed `sources = [("AK3", "xxxYYYY", "xyxYXY"), ("TRIV", "x", "y")]`; each returned merge carries **both full paths** as `(move, phi, rep)` steps (Definition-2.1 move + CoV automorphism), directly replayable. `aut_key` (`:63`) for the memoized `(total, rep, phi)`. Optionally `levelset.py:75 levelset_children` (idea 9) to expand full level sets.

**Algorithm:** run `aut_multi_search` with AK(3) and the trivial presentation as the two sources, `stop_when_merged=True`; a merge is a stitched forward+backward path from AK(3) to trivial in the quotient → replay to a concrete Definition-2.1 path → `verify_results.py`. For the 124, seed each rep + TRIVIAL.

**Budget/feasibility:** local at `nodes_per_source ≤ 1000`; the `max_total` *ceiling* is the binding knob, not the budget ([lesson](lessons/ceiling-not-budget-was-binding.md)) — raising the length ceiling can expose merges unreachable at any budget, so sweep the ceiling, don't just raise the budget. Production ceiling is the user's.

**Failure mode:** the frontiers still must meet, and for AK(3) the two balls were measured tiny and disjoint below the hump — MITM does not lower the 13-floor. Honest AK(3) value is *diagnostic* (does a quotient path exist at a reachable ceiling?), plus real merge-finding power on the 124 (this is the exact tool that already cut 261→125).

---

## 6. Thickenability certificate at plateau leaders — `AK(3)` · *the only idea that could close it*

**Build:** `experiments/stable_ac/thickenable/check_thickenable.py` (new package). This one leaves numba — it is 3-manifold topology, intentionally, because it is the only lever that could *certify* stable-triviality rather than search for it.

**The theorem:** Lackenby reformulates stable ACC — a presentation is stably AC-trivial **iff** it reaches *some* thickenable presentation, and thickenability is *decidable* (Neuwirth + Rubinstein–Thompson). So a state greedy discards as "not shorter" can still be a **milestone win**: reaching a thickenable state certifies the target, length-independently.

**Reuse:** the plateau-leader states from idea 4's wrapper as the tiny candidate set (never per-node — a per-node topology check mirrors the failed automorphic-number reward). Build the presentation 2-complex and hand it to an external decision tool (Regina-class C++); cross-check any positive with a second independent tool.

**Algorithm:** at each plateau leader (a handful of states, not the frontier) → build the spine/2-complex → run the Neuwirth thickenability decision → if thickenable, emit a certificate (state + decision witness); Thm 1.3 then gives stable-triviality. Calibrate first on a small set of *known*-thickenable and *known*-not-thickenable presentations at matched length to confirm the procedure before trusting it on targets.

**Budget/feasibility:** exponential per check, serious topology — this is a *certificate pipeline*, not a fast solver, and the Thm 1.1-vs-1.2 gap means no tractable search path falls out. Feasibility is the weak point; math relevance is the highest of any idea here.

**Failure mode:** heavy external dependency, exponential cost, and "thickenable" must be cross-verified (an untheoremed crossing/overlap proxy would repeat the automorphic-number-reward mistake). See `IDEAS.md` idea 2.

---

## 7. Prover9 / ATP oracle handoff — `AK(3)` + `124` · *independent, non-monotone*

**Build:** `experiments/stable_ac/atp/run_prover9.py` (new package; external solver handoff).

**Why it is orthogonal:** resolution/unification ATP has **no length-monotonicity constraint**, so it traverses paths a length-priority queue structurally cannot — an independent oracle that *boosts the solve count*, not a faster greedy. Lisitsa only ran `MS_n(b⁻¹aba⁻¹)` and P-AK(3), so the 124 diverse-`w` residual is genuinely unexplored territory for it.

**Reuse:** `run_baseline.py:159 load_dataset` to pull the floor-orbit reps; a new encoder emitting Lisitsa's ground and non-ground first-order encodings; `verify_results.py` to replay any returned sequence (an ATP proof is untrusted until replayed as a Definition-2.1 path).

**Algorithm:** pick 3–5 of the 124 residual reps → emit both Prover9 encodings with a per-instance timeout → union the ATP-solved set with the numba-solved set → replay every ATP sequence through `verify_results.py`. Route AK(3) **directly to trivial**, never through the broken MMS02 P-chain ([lesson: the MMS02 misprint](lessons/ambient-principle-unstable-is-not-a-theorem.md), Red line 1).

**Budget/feasibility:** external (Prover9 install), expensive (Lisitsa reports 42,681 s at n=7) — pilot on a handful with a hard timeout before scaling. Runs non-stable AC1-3, so it does not advance the *stable-move* mission; frame it strictly as a solve-count booster.

**Failure mode:** cost, and it sidesteps rather than answers the stable-search question. See `IDEAS.md` idea 5.

---

## 8. Per-relator cap-fit pre-filter — `124` · *efficiency enabler, ship-ready*

**Build:** `experiments/stable_ac/cov/capfit.py` (one pure function) + call it inside idea 1's candidate generation.

**The proven bound** (`literature/proofs/STABLE_AC_NEW.tex`, PROVEN + CHECKED 13712/0): each CoV output relator has length `≤ |K| + c_a(K)·(|m|+|n|)`, where `K` is the kept pre-substitution relator, `c_a(K)` its eliminated-generator count, and `|m|+|n| = |expr|−1` the isolator shift. This lets you **reject an over-cap candidate without running the transform** — currently `enumerate_cov` runs the transform *then* checks `reject_len` (`cov.py`). Pre-filtering turns an after-the-fact reject into a cheap arithmetic gate, so you can afford a deeper iterated-CoV tree (idea 1) within the same compute.

**Reuse:** `cov.py:207 isolate` to get `expr` (hence `|m|+|n|`) and `cov.py` constants (`DEFAULT_CAP=24`); the eliminated-generator count is a letter tally on `K`.

**Algorithm:** for each `(z_word, iso_gen, iso_index)` candidate → compute the bound from `expr` and the kept relator → skip if it exceeds `MAX_RELATOR_LENGTH`, *before* calling the transform. Deficit is provably even, so the bound is tight-ish; measure the skip rate.

**Budget/feasibility:** trivial cost, pure arithmetic, no search. Local test: assert on the covsweep jsonl that no candidate the transform would have kept is ever pre-filtered out (the bound is a proven upper bound, so this must hold 0 false-rejects).

**Failure mode:** none mathematically (proven bound) — the only risk is an off-by-one in `c_a(K)` or `|expr|`; the 13712/0 CHECKED result is the fixture to test against. See `STABLE_AC_NEW.tex` "Per-relator cap-fit bound".

---

## 9. Level-set expansion in the restart search — `both` · *closes a known incompleteness*

**Build:** swap the successor function in idea 1's / idea 5's search from `acmoves.children` to `levelset.py:75 levelset_children`, guarded behind a config flag in the new driver (still new-files-only).

**The gap it closes:** `aut_search` dedups by canonical orbit rep, but a rep's *minimal level set* can hold multiple length-equal states with different neighborhoods — deduping to one can prune the very state with the better descent basin. `experiments/equivalence_classes/search/levelset.py` already implements the fix: `minimal_level_set(pair)` (`:32`), `extra_members(pair)` (`:58`), and `levelset_children(r1s, r2s, cap, cyclic, seam_only)` (`:75`) is a drop-in replacement for `acmoves.children` that expands *every* member of the level set.

**Why it matters here:** `IDEAS.md` Bottom-line point 5 poses the open question — *whether one of the higher-start orbits offers a better descent basin than AK(3)*. Deduping restart points to canonical reps (as `restart_planner` does) can hide exactly that better basin. Level-set expansion is how you stop hiding it.

**Reuse:** `levelset.levelset_children` (drop-in); idea 1's driver.

**Budget/feasibility:** strictly more states per node → slower per pop; use only when the plain-orbit restart tree comes up empty and you suspect a pruned basin. Local at ≤1000 nodes on one rep, compare orbit-reach vs `acmoves.children`.

**Failure mode:** more expansion for possibly no new solve — it widens coverage, it does not add descent power on its own. Pair it with idea 2's probe so the extra states are ranked, not just enumerated.

---

## 10. Static rank-4/5 stabilization baseline — `both` · *the un-run "dumbest thing"*

**Build:** `experiments/stable_ac/nocov/run_static_rank.py` (runner; Branch-A family).

**What it is:** fix a *statically* stabilized presentation at rank 4 or 5 — adjoin coupled relators `z_i = w_i(x,y)` once, up front, and search there with the general-`n` solver — never dynamically adjoining/destabilizing mid-search (that variant is provably inert: priority = sum of relator lengths penalizes 3-relator children so they never pop; it is the known-failing naive flat stabilization). The static rank-4/5 baseline is the one un-run piece (`IDEAS.md` idea 11, the mentor's "dumbest possible thing"): each coupled `z_i⁻¹w_i` supplies short cancellation partners unavailable at rank 2.

**Reuse:** `experiments/stable_ac/solvern.py:324 search_n(pres, budget, cap, cyclic, progress)` with `Pres(n_gen=4 or 5, relators=...)` (`solvern.py:283`) — the general-`n` numba solver runs at `n_gen>2` today; `envs/utils.py:36 change_max_relator_length_of_presentation` to re-pad appropriately for the added relators; `run_nocov.py`'s runner scaffold (resume key, `ACSOLVERX_ALLOW_BIG` gate) as the template.

**Algorithm:** frame as best-of-many restart over the choice of adjoined words `{w_i}` (short subwords / relators of the target) → build the rank-4/5 `Pres` → `search_n` at production budget → log per adjoined-word-set. Correct the escape claim in any writeup: the shortening comes from the coupled `z⁻¹w`, not a bare generator; drop the arbitrary rank ≤5 bound if evidence warrants.

**Budget/feasibility:** `search_n` is the shipped general-`n` solver, so this is a config-and-runner job, not new search code. Local smoke-test one rank-4 presentation at ≤1000 nodes; production is the user's. Watch the `n_gen ≤ 26` cap.

**Failure mode:** the dynamic-adjoin variant is a known null; only the *static* baseline is live, and it may simply confirm rank-2 is as good — but it is cheap to settle and no one has. See `IDEAS.md` idea 11.

---

## 11. Same-orbit automorphic re-seed generator — `124` · *NEW, from the idea_bench ms634 finding*

**Build:** `experiments/stable_ac/cov/reseed_orbit.py` (a candidate generator plugging into idea 1's driver / the idea_bench harness).

**Mechanism.** Generate many automorphic images of a presentation *within its own Aut(F₂)-orbit* — not just the 8 signed relabels, but compositions of the Whitehead/Nielsen automorphisms — and offer them as solve-enabling re-seeds, ranked by `(abel, total_length, max_relator)`. This is a distinct lever from orbit-escape (ideas 1/4): rather than a new orbit, it hunts a *better representative of the same orbit* that the greedy happens to solve.

**Why (the evidence).** idea_bench's ms634 coverage win was exactly this — a `n_subs=1` CoV output with the *identical* Aut-canonical form as the original, solved in 39 nodes where baseline failed at 1000. The controls proved the 8 relabels and all rotations do NOT reach these representatives; CoV substitution (and richer automorphism compositions) do. So there is real, un-harvested coverage in same-orbit re-seeds that simple relabelling misses.

**Reuse:** `equivalence_classes/lib/autcanon.py`'s `AUTOS` (the 20 Whitehead autos) with `apply_hom` to enumerate same-orbit images, or `cov.enumerate_cov` filtered to `n_subs == 1` (i.e. `aut_canon(out) == aut_canon(orig)`); `restart_planner.abel_magnitude` for the key; `aut_canon` to confirm same-orbit.

**Failure mode:** a same-orbit re-seed is a search-*representation* effect — it exploits the greedy's string-sensitivity, so a win can be budget-fragile (a larger budget might solve the original directly). Measure whether the re-seed still wins as budget grows; if the gap closes, it is a shallow trick, not an escape. And it is powerless where the *orbit itself* is the wall (AK(3): every reachable rep is length ≥ 13) — so tag `124`, not AK(3).

---

## 12. Productionized top-ranker portfolio on the 124 — `124` + `both` · *NEW · the direct scale-up*

**Build:** point the **already-built, validated** idea_bench harness at the 124 residual at production budget — mostly a config job: add `data/ms_unsolved_reps/ms_reps_126.txt` as a `--bench` option in `harness.load_bench`, then `run_sweep` it on Colab at a large budget.

**Mechanism.** Race the observed top strategies — `cov_abel_len_lex`, `cov_nsubs_escape`, `cov_deep_z`, `cov_defining_iso` — as a best-first portfolio and take the union of their coverage. This generalizes idea 1 from one ranker to the four the ladder validated, and it is the concrete "find something promising, then scale the budget" step the whole idea_bench exercise was for.

**Reuse:** `experiments/stable_ac/idea_bench/run_sweep.py` (resume-safe, parallel, foreground-drivable — see [the background-wall lesson](lessons/background-job-wall-use-foreground-resume.md)); `harness.load_bench` / `harness.summarize`; the 124 reps loader.

**Failure mode:** the 124 are genuinely *unsolved* (unlike the ladder cracks), so the portfolio may hit the same wall idea 2's descent probe is meant to characterize — the ladder result validates the *mechanism*, not a 124 solve. A 124 solve would be a real new result: emit the full Definition-2.1 path and replay it through `verify_results.py` before believing it, with maximal suspicion.

---

## 13. Budget-escalation wall probe — `both` + `AK(3)` · *NEW · operationalizes "scale the budget"*

**Build:** `experiments/stable_ac/idea_bench/wall_probe.py` (thin driver over `run_sweep`).

**Mechanism.** Take the observed wall cases (ms605, ms623, ms636, ms568) plus AK(3) and 19_40, and run the top ranker at *escalating* budget (1k → 10k → 100k on Colab), logging `min_relator_length` progress against each reach case's `bar_to_beat` at every rung. ≤1000 nodes sufficed for the shallow ladder cracks; the wall needs depth, and this measures *where* (if anywhere) each case cracks rather than guessing.

**Reuse:** `run_sweep` with a budget ladder; the reach CSV's `bar_to_beat` / `baseline_min_relator_length` columns for the progress metric; `verify_results.py` on any solve.

**Failure mode:** AK(3) and 19_40 may be beyond CoV at *any* budget (the CoV-inert result, now empirically supported at ≤1000) — the escalation measures the wall's location, it does not promise to breach it. Any budget above 1000 is the **user's** to run on Colab, never local.

---

## Build order (what to do first)

For the **124 residual** (the mechanism is now ladder-validated, so this is no longer speculative): lead with **idea 12** — run the validated top-ranker portfolio on the 124 at production budget, the direct scale-up idea_bench was built to justify. Supporting it: idea 8 (cap-fit pre-filter, makes the portfolio cheaper), idea 11 (same-orbit re-seed generator — the un-harvested half of coverage the ms634 case exposed), and idea 2 (descent-probe ranking, the one untested challenger to the abel+length key idea_bench found best). idea 1 is the single-ranker precursor to idea 12; idea 3's abel-order is now the abel+length key baked into both. Ideas 9, 10 are follow-ups if the tree comes up empty.

For the **wall + AK(3)**: idea 13 (budget-escalation probe) first, to measure *where* the wall is — but the real shots to breach it are non-CoV, because idea_bench confirmed AK(3)/19_40 are CoV-inert at ≤1000: idea 5 (Aut-quotient MITM diagnostic), idea 7 (ATP oracle straight to trivial), and — the only one that could *close* it — idea 6 (thickenability certificate). Expect none to be quick; AK(3) stable-triviality is OPEN and stays that way until a verified path or certificate exists.

*Provenance: derived from `IDEAS.md` (ac-advisor-vetted, July 2026), a full read of the ACSolverX code surface (function/line refs above are from the current source), and the empirical `idea_bench` sweep on `benchmark_combined_22` ([RESULTS.md](stable_ac/idea_bench/RESULTS.md)) that validated the CoV-restart mechanism and the abel+length ranker, retired relabel/rotation as coverage levers, and exposed the same-orbit re-seed mechanism (idea 11). The ladder cracks are known-trivial cases — they validate the machinery, not a 124/AK(3) solve. Nothing here claims a solve; every idea names the failure mode that would make it not worth the compute.*
