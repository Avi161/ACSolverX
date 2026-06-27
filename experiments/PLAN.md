# PLAN 

*Concise step list. Rationale and corrections are in the detailed plan below.*

**Target:** a supervised regressor `f(state) → d-o-t` (min S-moves to the trivial  
presentation), used as a search heuristic in place of relator length so the search  
can take length-increasing detours. 

## Steps

1. **Harvest**. Greedy-solved pass → JSONL of `(idx, packed_path,
  beam_path_length, …)`, every path replay-validated before write.
2. **Label.** Replay each path; state after move *m* on a length-*N* path gets
  d-o-t = N−m. Labels are **upper bounds**, never ground truth.
3. **Aggregate to min per canonical class.** Key every on-path state with
  `canon.canon_key` (`canonical_pair_nj`), keep `min` d-o-t over the class. This
   table is the archive. New shorter paths just lower the min — self-correcting.
4. **Split by AC-equivalence class**, not by row (a whole class in one fold) +
  frozen hard hold-out never mined for labels. Cap/weight per source so greedy
   volume doesn't swamp the PPO/beam detour states.
5. **Train.** Baselines (length-only, XGBoost on scalar features) → DRT-trunk
  regressor (reuse `RelativeDualRingActorCritic`, optionally warm-start from the
   PPO critic) + heads: d-o-t (Huber on `log1p`), censored loss for unsolved,
   solvable-within-budget aux, uncertainty for OOD abstention.
6. **Evaluate on ranking, not just MAE.** Spearman + pairwise sibling-ordering;
  downstream: does f-ranking beat GS-Sub at matched node budget? Calibrate per
   difficulty band.
7. **f-guided search.** Combine, don't replace: `score = policy logp + (−f) bonus
  - novelty`, OOD abstention → fall back to policy/length where unconfident.
8. **DAgger refinement loop.** f-guided search → new/shorter paths → update min
  table → retrain. Promotion gate: no regression on the frozen baseline solves.
9. **Censored unsolved.** Record `d-o-t > B` with full search context (algo,
  budget, horizon, beam width) — no constant fill-in (Caltech's trap).
10. **Benchmark + write-up** vs GS-Sub (640), beam (mean path 12.39), and the 261
  unsolved hard classes; report new solves separately from path-shortening.

**Immediate next:** explore-seed pass (Gumbel seeds 1–4) over the 4,954
greedy-unsolved — the highest-value new-solve targets — then min-merge into the
same archive.

---

# PLAN — Detailed version (reference)

*Draft 2026-06-25.*

## 0. Goal

- Train a model `f(state) → d-o-t` = predicted number of S-moves to reach the trivial presentation.
- Use it to **rank candidate moves by predicted d-o-t, not relator length**, so search can take length-increasing detours (escape AK(3)-type traps).
- This is novel: the two papers learn a *policy/value* (PPO) and a *binary solvability* classifier — nobody has built a standalone supervised d-o-t regressor.

## 0b. Baselines & targets (two-hump paper, our S-move regime)

*All counts out of 1190 Miller–Schupp. Our action space = S-moves, so the apples-to-apples classical baseline is **GS-Sub**, not the old elementary-AC greedy. Numbers verified from the paper's results table.*

- **GS-Sub (greedy + substitutions):** 533 @614 nodes · **604 @10K · 634 @100K · 640 @1M = 640 @10M (plateau)**. The 640 are the AC-trivial, greedy-reachable "easy hump."
- **PPO-Sub-DRT:** 588.2 mean (585–591). **+AC-19: 607.2 (605–610)** · +AC-1M: 605.4 (600–610). The pretrained `610model` = max **610**.
- **Hybrid beam + PPO policy:** 610 solved, mean path length **12.39** vs PPO-alone **13.77** (~10% shorter).
- **Hard hump:** the **550** that GS-Sub never solves (1190−640) → **261** distinct AC-equivalence classes. *No current method solves any of these.*
- **Old paper (elementary AC moves — different regime, context only):** GS-AC 533, PPO-AC-ResNet 457.
- **Targets for this work, in order:** (1) match GS-Sub's 640 at *lower* node budget; (2) beat beam's 12.39 mean path length on the 610; (3) the real prize — **crack any of the 261 hard classes**.
- **634 vs 640 (resolved — not a bug):** the first **634** rows of `AC19_extended.txt` are byte-identical MS presentations (verified: clean prefix, none scattered later), and the code pins exactly those. **634 = GS-Sub solvable @100K nodes; 640 = GS-Sub @1M nodes** — same "easy hump," two budgets. So our pinned benchmark = the 634 @100K set. (Minor logging bug: `ppo_ac_s.py:265` uses `solved_ids <= 634`, which includes index 634 = the first *non*-MS row; should be `< 634`.)

## 1. Critical assessment of the plan

**Sound:**

- d-o-t instead of length is the right target — directly attacks the "must go up before going down" bias.
- Recalibrate with **min d-o-t seen per state** — correct, this is the only unbiased estimator (see §3).
- Iterative refinement loop is structurally fine.

**Risks / corrections (in priority order):**

- **[#1, fatal if ignored] Labels are upper bounds, never ground truth.** A found path of length 40 only proves d-o-t ≤ 40. Treat all labels as "best-known," always take the min, and use a **censored/ordinal loss** so the model is never punished for predicting *lower* than a loose upper bound.
- **[#2, killed the prior attempt] Distribution shift / greedy-only seed.** Caltech trained on greedy paths, then guided search into states the model never saw → V-guided solved **279 vs that repo's own greedy 533** (old AC-Solver, *elementary* AC moves — a different regime from our GS-Sub; the point is it underperformed its *own* baseline, not the number). Fixes: (a) train on a **mix of greedy + PPO + beam** paths (only PPO/beam contain length-increasing detours; greedy-only relabels length under a new name), (b) **DAgger-style** data aggregation — add states the *model's own* search visits, every refinement round, (c) **OOD abstention** — model emits an uncertainty output; when out-of-distribution, search falls back to policy/length instead of trusting a blind guess.
- **[#3] Ranking beats regression for a search heuristic.** What matters is correct *ordering* of sibling states, not absolute MAE. Evaluate with Spearman / pairwise accuracy on same-path and sibling states, and consider a pairwise ranking loss.
- **[#4] Don't naively swap length→d-o-t in the PPO reward.** Use **potential-based reward shaping** (§7) so the optimal policy is provably unchanged and you can't introduce a new wrong fixed point.
- **[#5] Don't hand-engineer 14 length features** (Caltech did; it just re-encodes length). Reuse the Dual-Ring Transformer encoder (§5, §2).
- **[#6] Label-source imbalance.** Greedy contributes ~17k rows × many intermediate states and will numerically swamp the rarer PPO/beam detour states — the exact examples that teach beneficial length increase. Cap/weight per source so the signal isn't drowned (§6).
- **[#7] Canonical-convention drift.** `1190MS.txt` (raw int8) and the env's per-move Booth rotation do *not* match the lab's full canonicalizer (`canonical_pair_nj`) — different alphabet order, and the env only normalizes one relator. Mixing them silently misaligns labels; route everything through `canon()` (§2).

## 2. Your open questions — decisions

- **Train on AC-19/AC-1M or just MS?** → Phase it. **Phase 1:** the len-8–19 GS CSV (17,636 rows) + the `610model` checkpoint's PPO `best_paths` — small, fast, and the PPO paths supply the length-increasing examples the CSV lacks. **Phase 2:** add an AC-19 subset. **Skip AC-1M initially** — too large and its "distance" = construction scramble length, a very loose upper bound that would inject noise. Your overfitting worry is real but the cure isn't *less* data — it's including **non-greedy** paths so the model sees beneficial length increases.
- **Canonical representative — which one?** → **Pinned to the lab's production canonicalizer, `canonical_pair_nj*`* (`greedy_search.ipynb`). This is the convention the two-hump GS code keys on and it's the most efficient (numba + string dict keys). Single source of truth for the archive key; do not invent another. **Correction (verified in `experiments/eda.ipynb`, P2-11):** the greedy CSV is **NOT** stored in `canonical_pair_nj` form — its relators are free+cyclically *reduced* and the pair is ordered *shortest-first*, but relators are **not** rotation/inverse-minimized. Empirically the CSV's stored strings are nonetheless **1:1 with true `canonical_pair_nj` classes** (25,209 stored == 25,209 canonical, zero d-o-t disagreement), so within the CSV the stored string works as a key — **but joining other sources (env / PPO / 1190MS) still requires canonicalizing via `canonical_pair_nj` first** (it is *not* zero-conversion). The convention:
  - Each relator is free+cyclically reduced (`reduce_relator_nj`), then set to the **lex-min over all cyclic rotations of `r` and of `r⁻¹`** (`canonical_relator_nj`), under alphabet order `**y⁻¹ < y < x⁻¹ < x**`.
  - The pair is ordered **length-then-lex** (shorter relator first; lex tie-break). The pair tie-break does **not** affect d-o-t (the label is min-path-length over the class, independent of which representative string is chosen).
  - **Relation to paper E.1:** same equivalence classes (rotation + inverse + swap); E.1's appendix statement differs only in using *pure* lex pair-order. We use the implemented `canonical_pair_nj` — consistent with the lab's data, not contradicting the paper's math. **Reconciliation is now resolved: adopt length-then-lex, do not re-derive pure-lex.**
  - **Not folded in:** generator automorphisms (x↔y, x↔X) — there's a `TODO` for it in the code. Leaving them out is *safer* (a finer key never wrongly merges states); note our class count may exceed the paper's "261" if that figure used automorphisms.
- **The env is NOT a canonical form — never key env state directly.** `s_move`/`booth_lex_min_rotation_masked` only Booth-rotates the *one* relator just modified (no inverse-min, no pair-order) and uses a *different* alphabet order (numeric int8: `y⁻¹ < x⁻¹ < x < y`). Always route env int8 through the full canonicalizer.
- **Canonical (key) vs DRT (input) — don't conflate.** The `canonical_pair_nj` form is for the **archive/dict key** (so equivalent states share one min-d-o-t label). The **model input** is separate: prefer the **DRT cyclic relative-position embeddings** (paper shows DRT > hard-canonical preprocessing by ~25 solves) — reuse/transfer the trained DRT encoder rather than feeding canonicalized input. Best of both: canonical key for labels, equivariant encoder for features.
- **First action item (before any data is built):** lift `canonical_pair_nj` + its numba helpers into a small importable module exposing `canon(pres) → (str,str)`; write the int8→char converter (`{1:x, 2:y, -1:X, -2:Y, 0:pad}`); then verify the mapping `1190MS.txt ↔ greedy CSV ↔ env state` produces the **same canonical key** on a sample (round-trip). Canonicalizing *between* moves rewrites action coordinates, so **store paths as actions in the env's own convention** for replay — canonicalize only for the archive key, not the replay tape (avoids the convention-drift trap, §1.#7).
- **Label for unsolved presentations (e.g. AK(3))?** → **Do not assign a constant** (Caltech's `200`/`5×maxlen` was a trap — it told the model AK(3) is exactly as hard as a mild case). Treat unsolved as **right-censored**: label = "d-o-t > B" where B = effective budget reached. Censoring is **algorithm-conditional**, so store the full context (algorithm, budget/nodes, horizon, beam width, action set, best length reached) — "unsolved" means unsolved *under that config*, not far/nontrivial. Use a censored loss (penalty only if prediction < B). This is exactly your intuition — AK(3) is *free* to be predicted orders of magnitude higher, no fixed number needed. Pair with a small **binary "solvable-within-budget" head** as an auxiliary task.
- **Have d-o-t data already, or must we generate it?** → Both available now: CSV greedy paths + checkpoint PPO paths. Start immediately; generate more via the refinement loop (§6). No need to run PPO from scratch first.

## 3. Data & labels (single verified archive)

- **Label = best-known d-o-t per canonical state.** From every solving path of length N, replay step-by-step (`envs/utils.py:replay_packed_path` / `decode_path`); the state after move *m* gets label **N−m**. One path → up to N labels.
- **Sources:** CSV greedy paths (parse `Path` column) + checkpoint `best_paths`/`path_lengths` (replay). **Every path is replay-validated before any label enters the archive** — no exceptions.
- **Per-path metadata (store all of it):** algorithm, budget/nodes, horizon, beam width, action set, max relator length, path length, **max intermediate relator length**, replay status. The max-intermediate-length is the direct quantifier of "had to go up before going down" — keep it; it doubles as an auxiliary target (§5) and a trap signal (§8).
- **Aggregation table:** `canonical_pair → min d-o-t ever seen`. Always relabel to the current min ⇒ old data self-corrects when a shorter path appears.
- **Outlier guard** (your "absurdly high path" worry): a path far longer than the state's current best is just not the min, so it's auto-ignored; additionally winsorize/log-transform (`log1p`) the target to tame the heavy tail.
- **Unsolved:** censored lower bound + full search context, not a point label (§2).

## 4. Featurization

- Primary input: the int8 length-48 presentation, fed to a DRT-style encoder.
- Auxiliary scalar features worth concatenating (cheap, the companion paper shows they carry signal): relator lengths, exponent sums, and — if affordable — small-radius **neighborhood size** / **persistent-homology barcode** (F1≈0.96 for solvability in that paper). Optional, gate on cost.

## 5. Model & baselines (the train-test comparison you want)

- **Baselines (fast, sanity):** length-only predictor; gradient-boosted trees (XGBoost) on scalar+barcode features.
- **Caltech-style:** FeatureMLP, 1D-CNN sequence net (re-implement only as a comparison point).
- **Main model:** DRT encoder (reuse `network.py` `RelativeDualRingActorCritic` trunk) + a regression head. Optionally **warm-start from the PPO critic** — its value is already a discounted cost-to-go.
- **Auxiliary heads** (cheap, share the trunk): solvable-within-budget probability, **predicted max-intermediate-length needed** (how big a hump to expect), and an **uncertainty/confidence** estimate (deep-ensemble or MC-dropout) used for OOD abstention in search (§1.#2c).
- Compare all on the same split (§6) by both regression error **and** ranking metrics.

## 6. Training, split & evaluation

- **Split by AC-equivalence class** (canonical key), not by row — all states of one path/class in one fold. Prevents the leakage that flatters MAE.
- **Frozen hard hold-out:** reserve a set of hard presentations that is **never mined for training labels**, even by the DAgger loop (§7). Without it the refinement loop leaks and you can't honestly measure generalization to hard cases.
- **Source weighting:** cap/balance examples per source (§1.#6) so greedy's volume doesn't drown PPO/beam detour states.
- **Losses:** Huber on `log1p(d-o-t)` for solved; censored loss for unsolved; optional pairwise ranking term on sibling states.
- **Metrics:** MAE (original scale) + **Spearman** + **pairwise sibling-ordering accuracy** (the one that predicts search quality) + a downstream test: *does ranking moves by f solve more of the 1190 than **GS-Sub at matched node budget** (§0b)?* Report **calibration per difficulty band**, not just average MAE — the average is dominated by easy cases and hides whether the model is useful on the hard hump.

## 7. Iterative refinement on the 1190 MS

- Loop: **search (f-guided) → collect new/shorter paths → update min-d-o-t table → retrain → repeat** until no new/shorter solutions.
- **DAgger:** each round, add states the model's *own* search visited (fixes distribution shift, §1.#2).
- **Emphasis on new solutions (your point):** don't hand-tune upweights blindly — relabeling to current-min already propagates improvements; add light **recency weighting** for newly-improved states.
- **Recalibration:** a shorter path to an already-solved state simply lowers its min label; retrain picks it up automatically.
- **Promotion gate:** only promote a retrained model if it improves new solves or shortens verified paths **without losing baseline solves** on the frozen set. Preserve failed attempts as censored data, never as fake-distance negatives.

## 8. Local-minima detection — known AK(n) **and** novel-basin discovery

- During search, flag a state as a trap when: (a) revisit hashes spike (cycle), (b) length plateaus, or (c) **f is a local min** — `min over neighbors f(neighbor) ≥ f(current)`. These criteria fire for **any** basin, known or not — they are the open-world detector.
- **Two buckets per trap: known vs novel.** Canonicalize each flagged state, then split:
  - **known** → in `data/derived/dot/ak_trap_set.json` → counted as an AK(n) basin (closed-world, below).
  - **novel** → NOT in the set → a **newly-discovered local minimum**. This is the open-world case the search exists to surface, and the scientifically interesting output.
- **Novel-basin registry (resumable JSONL, per CLAUDE.md durability rule):** append each novel trap to `experiments/dot_runs/<ts>/discovered_minima.jsonl` — `{canon_key, r1, r2, total_len, source_problem, search_algo, depth_at_hit, min_f_seen, n_runs_hit, escaped:bool}`, **aggregated by `canon_key`** so we count *how many distinct runs / problems* fall into each basin (recurring = a real attractor, one-off = noise). `flush()+fsync` per write; resume by reading it back.
- **Cluster, promote, feed back (the loop):** periodically cluster novel basins (by AC-neighborhood / canonical similarity), cross-reference against the paper's **261 unsolved MS equivalence classes**, and **promote** the frequently-hit ones: (1) add their canon keys to `ak_trap_set.json` (the set is *living*, not fixed), (2) inject them as **new censored hard anchors** in the next data build (DAgger-for-hardness, §7), (3) flag any short/recurring novel basin as a **candidate new counterexample** for mathematical follow-up.
- **Concrete AK(n) trap-set (the known-bucket lookup):** load `data/derived/dot/ak_trap_set.json` (built by
`scripts/build/build_anchors.py`, see `experiments/eda+data_collection/data_crafting/3.DATA_DISTRIBUTION_PLAN.md §3d`) =
`{canon_key(AK(n)) : n=3..8} ∪ {Length-14 ×2} ∪ {8 in-data cousins} ∪ {ak3_auto images}`.
For every expanded state, canonicalize via `canon.canon_key` and do **one membership test** —
"did the search fall back into an AK(n) basin?" is then exact, not heuristic. Single shared
file so the data build, the training trap-rate metric (`training/PLAN.md §8`), and this
search-time monitor all count against the identical definition.
- **Per-run logging:** trapped? / which `AK(n)` / depth at first hit / did it escape. **Aggregate
metric = trap-rate** (% of f-guided runs that end in / pass through an AK(n) basin) + a
per-`AK(n)` histogram — the number that says how often `f` re-finds the basin vs escapes it.
- Deliverable: **(known)** the AK(n) trap-rate per algorithm (greedy / PPO / beam / f-guided), showing whether the d-o-t heuristic reduces AK(n) trapping; **(novel)** a growing catalog of newly-discovered basins ranked by how many runs hit them — the candidate new hard-equivalence-classes / counterexamples this project surfaces, and the feedstock for the next anchor build.

## 9. f-guided search & d-o-t-guided PPO (benchmark vs old reward)

- **Search heuristic (do this first):** don't *replace* the policy — **combine**. Beam/greedy score = `policy log-prob + calibrated value bonus (−f) + novelty term`; still permit length-increasing moves; keep existing dedup/no-op handling. Apply OOD abstention (§1.#2c): trust f only where confident.
- **PPO:** keep the **terminal reward unchanged**; add f via **potential-based shaping** (Ng et al. 1999) `r' = r + γΦ(s') − Φ(s)`, `Φ(s) = −f(s)`, **clipped**, plus an OOD/uncertainty penalty. Keeps the optimal policy and avoids new wrong fixed points — strictly safer than swapping `count_nonzero` for d-o-t. Preserve entropy so PPO can still escape the value model's blind spots.
- Benchmark against **both** the current length-based-reward PPO **and** GS-Sub / the released beam (610, mean path 12.39), on the 640 benchmark set (§0b; reconcile the 634/640 code discrepancy first): solve count + mean path length.

## 10. Results, layout & website

- **Directory layout:** `data/` (immutable sources) · `experiments/dot_archive/` (verified paths + metadata, the single source of truth) · `experiments/dot_runs/<timestamp>/` (model/search outputs) · `experiments/reports/<timestamp>/` (benchmark summaries + website artifacts). Separate raw / archive / outputs / reports — never overwrite the archive.
- **Result-row schema:** presentation key, original dataset+index, canonical key, solver+config, solved flag, observed path length, max intermediate length, budget/horizon, replay checksum/status.
- Per algorithm (greedy / PPO / beam / f-guided): solve count, **new solves beyond each baseline**, path-length distribution, d-o-t calibration plots (predicted vs best-known), two-hump histograms. **Report path-shortening separately from new solves.**
- Update the AC-solver-style site to visualize d-o-t-ranked move sequences alongside the old length-ranked ones; side-by-side greedy vs PPO.

## 11. Phased roadmap

1. Lift the lab's `**canonical_pair_nj*`* (+ numba helpers) into an importable `canon()` module and write the env-int8→char converter; verify `1190MS ↔ greedy CSV ↔ env` all produce the same canonical key on a sample (round-trip) (§2). Everything downstream keys on this.
2. Build the min-d-o-t table from CSV + `610model` paths (replay-validated); EDA on label distribution & length-vs-d-o-t scatter (confirm short ≠ easy).
3. Train baselines + DRT regressor; report split metrics (§6).
4. f-guided search on 1190; measure vs **GS-Sub at matched node budget** (§0b). Bar to be worth it: match GS-Sub's 640 at *lower* budget, or crack any of the 261 hard classes.
5. Iterative refinement + DAgger loop (§7).
6. Trap catalog (§8).
7. d-o-t-shaped PPO benchmark (§9).
8. Results + website (§10).

**Biggest single risk:** repeating Caltech's distribution-shift failure. Mitigated by mixing PPO/beam paths in and DAgger from round 1.