# RUN_ME — morning launch instructions (2026-07-21, branch `research/stable-ac-escape`)

## THE FIVE NOTEBOOKS (final packaging — run these, one per Colab instance)

Everything below is packaged as five self-contained notebooks in **`experiments/notebooks/`**, all uphill-then-downhill attacks, all resume-safe (relaunch any dead session freely), all writing dateless `.jsonl` (solved portfolio rows now carry the winning pair + full move path: `win_r1/win_r2/win_cap/win_path_moves`), all mirroring to **`MyDrive/acsolverx_results/stable_ac_escape/`**. Open each from GitHub at this branch, run all cells, in this priority order:

1. **`nb1_floors_portfolio.ipynb`** — the 35 deepest verified orbit floors, then the 28 depth-2 descended starts (best odds of the night; ~2–3 h).
2. **`nb2_big_ladder.ipynb`** — the deep orbit-floor ladder, rungs 20 / beam 32, all 124 (pure CPU, all day; the only session that can hit the μ≤12 auto-solve line directly).
3. **`nb3_stall_escape.ipynb`** — mid-search uphill CoV escape on all 124 at 50k (~2–4 h; also logs `max_popped_total`, the cap-binding probe).
4. **`nb4_portfolio_124.ipynb`** — μ-descent + orbit-escape strategy portfolio on all 124 (~2–3 h).
5. **`nb5_static_rank.ipynb`** — rank-4/5 stabilization baseline (~1–2 h at 10k).

Check the VM first in any session: `!grep -m1 "model name" /proc/cpuinfo` — re-roll if Intel Xeon and you can spare the slot (AMD EPYC ≈ 2×). Any SOLVED/LEAD line: stop, apply the verification bar below, remember `aca_115` = AK(3). The sections below document each pipeline in detail.

Everything below is committed on `research/stable-ac-escape`, piloted locally at ≤1k nodes, tests green (118 in `tests/stable_ac`). Open each notebook **from GitHub at that branch** (a running Colab does not see pushes). Before starting each session, check the VM: `!grep -m1 "model name" /proc/cpuinfo` — AMD EPYC ≈ 2× Intel Xeon 2.20GHz on this workload; re-roll (Runtime → Disconnect and delete runtime) if you land a Xeon and have sessions to spare.

## Deliverable 1 (primary): `experiments/stable_ac/idea_bench/portfolio_124.ipynb`

Races the validated top CoV rankers + two NEW strategies against the same-budget greedy control on all 124 unsolved classes. The two new ones: `reseed_orbit` (same-orbit automorphic re-seeds — the un-harvested ms634 mechanism) and `cov_mu_lex` (ranks CoV candidates by the Aut-minimal length of their output orbit — justified by tonight's orbit-floor refutation: a CoV hop CAN strictly lower the orbit floor, AK(2) 11→10 verified, one ms640 row 6→2-standard in one hop; only 4 of the 124 have a hop-1 descent — aca_99/100: 25→22, aca_105/106: 25→24 — so μ-first ordering is cheap and the descents get searched first).

- One session per strategy group (the CONFIG cell has the exact 5-session table: mu / abel / nsubs / deepdef / reseed). Each session writes its own files — zero write races; relaunching any dead session is always safe (resume key = strategy, pres_id, budget).
- Budget ladder: **50k first, all sessions** (≈1–3 h per session on EPYC with `HIGH_SPEEDUP`). If sessions remain after 50k completes, escalate the best-performing strategy to 200k, and only then consider 500k+ (a 1M portfolio session is ~a day — only worth it on a strategy that showed movement at 50k).
- **T9 high-cap arm**: one extra session with `CAP = 48` — now LOWER priority: the overnight cap-48 depth-2 μ-scan came back an exact null (identical descents/orbit reach to cap 24), so at tree depth 2 the cap doesn't bind; the remaining cap question is in-search at 50k (watch `max_popped_total` in stall-escape rows) and deeper tree rungs. Run it only if sessions are spare.
- Results mirror to `MyDrive/acsolverx_results/stable_ac_portfolio/` every ~60 s.
- Analyze any finished file (coverage/efficiency vs the baseline control): `.venv/bin/python3 -m experiments.stable_ac.idea_bench.harness --summarize <portfolio_*.jsonl>`.

**If a `SOLVED aca_… by …` line appears (it prints in loud caps):** it is a LEAD, not yet a result. Do not announce. The verification protocol: the strategies are deterministic, so the winning start pair is re-derivable from `(pres_id, strategy, solve_idx)`; re-run that single start at the same budget with the normal (path-carrying) solver, then replay the path through `experiments/stable_ac/verify_results.py` (spec-only replay). **If the pres_id is `aca_115`, stop and treat it as the extraordinary-claim case: that class IS AK(3)** (same Aut-orbit, proven in `results/stable_ac/cov/STABLE_ORBIT_LINKS.md`), whose stable triviality is OPEN — it needs the full two-stack verification before a word is said out loud. Realistic expectation: the CoV portfolio does not touch aca_115 (AK(3) is CoV-inert); its shots are the ATP and thickenability tracks.

## Deliverable 1b (FIRST, it's short and has the best odds): the μ-descended starts

The depth-2 scan found **19 of the 124 classes have a strictly descending orbit-floor path within two CoV hops (15 visible only at hop 2** — they climb before dropping, e.g. aca_97: μ 24→27→19), and the 50k sweep never searched ANY of these descended orbits. The 28 verified descended start pairs are `data/ms_unsolved_reps/mu_descents_d2.csv` (`results/stable_ac/mu_scan/MU_SCAN_FINDINGS.md` has the analysis). In `portfolio_124.ipynb`, one short session: `BENCH = "mu_descents_d2"`, `STRATEGIES = ["cov_mu_lex", "cov_abel_len_lex"]`, `GROUP = "mud2"`, `BUDGETS = [50000]` — 28 rows, well under an hour. Then the same with `BENCH = "mu_floors_r8"`, `GROUP = "floors"` (**35 rows — the deepest floors known**, μ 15–24, produced by the full 8-rung ladder; each row's `chain` column is its stable-CoV provenance and `source_class` maps to the ledger). The older `mu_descents_d2`/`mu_descents_d4` benches are subsumed by this one — run them only if sessions are spare.

**Optional CPU-only session (no GPU, no search): the BIG ladder.** `experiments/stable_ac/cov/mu_ladder.py` is pure enumeration + Whitehead canonicalization; overnight it descended 33/124 classes at rungs 8 / beam 12 (best floor 15 — the μ ≤ 12 stable-solve finish line, see `results/stable_ac/theory/MU_CRITERION.md`, is 3 away). On a Colab CPU session: `python3 -m experiments.stable_ac.cov.mu_ladder --rungs 20 --beam 32 --jobs 8` (resume-safe per class; hours). Any `*** LEAD mu<=` line: apply the criterion note's 7-step verification bar before believing anything. A verified solve from any of these removes its `source_class` from the **stable** ledger (the CoV chain is a stable certificate prefix — segmented accounting, same as the restart tree; the aca_115 rule applies unchanged).

## Deliverable 2: `experiments/stable_ac/nocov/static_rank.ipynb`

The rank-4/5 static stabilization baseline (mentor's "dumbest possible thing", never run by anyone): adjoin 2–3 coupled relators `z⁻¹w`, search at `n_gen = 4/5`. Config `experiments/stable_ac/nocov/config_static_rank.yaml`; budget 10k first (short session), 50k on anything interesting. Local pilot at 1k: 18/110 rank-4 jobs solved (easy ladder rows only — the honest expectation is that rank-4/5 must show movement on rows the 2-gen baseline can't touch at the SAME budget to be interesting). Every solved row carries a full path: verify with `.venv/bin/python3 -m experiments.stable_ac.verify_static_rank results/stable_ac/static_rank` — believe nothing that fails it.

## Deliverable 3 (optional third/fourth session): stall-triggered CoV escape on the 124

The core mission mechanism, now empirically live: at matched TOTAL budget 1000 on the 22-benchmark it solved **12/22 vs plain greedy's 10/22 — two coverage wins (ms538, ms602), zero losses, every certificate spec-verified** (`results/stable_ac/stall_escape/`). It searches until a length plateau, takes the stuck state, fans out its μ-then-abel-ranked CoV candidates, and spends the rest of the budget in the best new coordinates; certificates are segmented (search + stable CoV junction + search) and a verified row certifies STABLE AC-triviality. On Colab (serial CLI, ~2–4 h for all 124 at 50k):

```
%env ACSOLVERX_ALLOW_BIG=1
!cd ACSolverX && python3 -m experiments.stable_ac.cov.stall_escape --bench aca_124 --budget 50000
```

Resume-safe per presentation (relaunch freely). Run the μ-priority names first if you want the highest-prior subset early: `--names aca_99 aca_100 aca_105 aca_106` (the four classes with a proven hop-1 orbit-floor descent). Rows carry `verify_ok` computed in-run; re-verify independently before believing any solve, and the `aca_115` extraordinary-claim rule applies here too. Each row also logs `max_popped_total` — the longest state the search actually popped — which is the measured answer to whether the 24-cap ever binds at 50k (T9).

## What ran overnight (already committed, read at leisure)

- **Orbit-floor refutation + n_subs≥2 length law**: `literature/proofs/STABLE_AC_NEW.tex` (two new sections; the k≥2 exact law verified on 1,995 reconstructed transforms, 0 violations; the floor counterexamples independently re-verified).
- **Obstruction barrier note**: no homotopy- or simple-homotopy-level invariant can separate stable-AC classes of trivial-group presentations (Wh(1)=0); any obstruction must live strictly at the 3-deformation layer.
- **Thickenability checker PROTOTYPE built** (`experiments/stable_ac/thickenable/check_thickenable.py` + calibration, 18 tests): 6/6 ground-truth calibration cases pass; AK(3) fully enumerates to NOT_THICKENABLE `[unverified]` (consistent with it being genuinely open — a thickenable state would already be AC-trivial by Lackenby Thm 1.3); the 35 floors are beyond pure-Python brute force (honest UNKNOWN_SIZE). Every verdict stays `[unverified]` until the Regina `isBall` validator is built (the remaining ~1-week step) and the strand-coupling reversal sign is pinned by hand — a THICKENABLE on any open target prints a suspected-bug warning, never a claim.
- **Prover9 ATP pilot**: `results/stable_ac/atp/` (encoder + pilot outcomes; ATP proofs are leads pending move-sequence extraction). **IMPORTANT UPDATE**: the pilot's timeouts/exhaustions were partly FALSE (Prover9 auto-mode weight-pruned the heavy clauses AC paths need — `results/stable_ac/theory/LISITSA_TRANSFER.md`); the encoder now sets `max_megs`/`max_weight` properly. If you want an ATP session: target **Q_{2,±1}** (the fresh-orbit normal forms, μ=14 — a proof = direct LEAD for aca_117/119): `python3 -m experiments.stable_ac.atp.run_prover9 --pres q2up XYxyxxyxYXX YxxyxxYXX --pres q2um XYxyxxyXYXX YxxyXXYXX --timeout-s 14400` (words μ-verified against the template proposition), hours-scale timeout on high-RAM.
- W&B is NOT wired into these two notebooks tonight — the jsonls are the source of truth; mirroring to W&B can be added afterwards without touching run identity.
