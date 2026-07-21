# RUN_ME — morning launch instructions (2026-07-21, branch `research/stable-ac-escape`)

Everything below is committed on `research/stable-ac-escape`, piloted locally at ≤1k nodes, tests green (118 in `tests/stable_ac`). Open each notebook **from GitHub at that branch** (a running Colab does not see pushes). Before starting each session, check the VM: `!grep -m1 "model name" /proc/cpuinfo` — AMD EPYC ≈ 2× Intel Xeon 2.20GHz on this workload; re-roll (Runtime → Disconnect and delete runtime) if you land a Xeon and have sessions to spare.

## Deliverable 1 (primary): `experiments/stable_ac/idea_bench/portfolio_124.ipynb`

Races the validated top CoV rankers + two NEW strategies against the same-budget greedy control on all 124 unsolved classes. The two new ones: `reseed_orbit` (same-orbit automorphic re-seeds — the un-harvested ms634 mechanism) and `cov_mu_lex` (ranks CoV candidates by the Aut-minimal length of their output orbit — justified by tonight's orbit-floor refutation: a CoV hop CAN strictly lower the orbit floor, AK(2) 11→10 verified, one ms640 row 6→2-standard in one hop; only 4 of the 124 have a hop-1 descent — aca_99/100: 25→22, aca_105/106: 25→24 — so μ-first ordering is cheap and the descents get searched first).

- One session per strategy group (the CONFIG cell has the exact 5-session table: mu / abel / nsubs / deepdef / reseed). Each session writes its own files — zero write races; relaunching any dead session is always safe (resume key = strategy, pres_id, budget).
- Budget ladder: **50k first, all sessions** (≈1–3 h per session on EPYC with `HIGH_SPEEDUP`). If sessions remain after 50k completes, escalate the best-performing strategy to 200k, and only then consider 500k+ (a 1M portfolio session is ~a day — only worth it on a strategy that showed movement at 50k).
- **T9 high-cap arm**: one extra session with `CAP = 48` (same CONFIG, `GROUP` gets `48` in the name automatically via `mrl48`). This searches the space the 24-cap structurally excludes — the cap-inertness lesson was only ever measured to cap 48 at 200k, and the ceiling-was-binding lesson proves caps can hide states unreachable at any budget.
- Results mirror to `MyDrive/acsolverx_results/stable_ac_portfolio/` every ~60 s.

**If a `SOLVED aca_… by …` line appears (it prints in loud caps):** it is a LEAD, not yet a result. Do not announce. The verification protocol: the strategies are deterministic, so the winning start pair is re-derivable from `(pres_id, strategy, solve_idx)`; re-run that single start at the same budget with the normal (path-carrying) solver, then replay the path through `experiments/stable_ac/verify_results.py` (spec-only replay). **If the pres_id is `aca_115`, stop and treat it as the extraordinary-claim case: that class IS AK(3)** (same Aut-orbit, proven in `results/stable_ac/cov/STABLE_ORBIT_LINKS.md`), whose stable triviality is OPEN — it needs the full two-stack verification before a word is said out loud. Realistic expectation: the CoV portfolio does not touch aca_115 (AK(3) is CoV-inert); its shots are the ATP and thickenability tracks.

## Deliverable 2: `experiments/stable_ac/nocov/static_rank.ipynb`

The rank-4/5 static stabilization baseline (mentor's "dumbest possible thing", never run by anyone): adjoin 2–3 coupled relators `z⁻¹w`, search at `n_gen = 4/5`. Config `experiments/stable_ac/nocov/config_static_rank.yaml`; budget 10k first (short session), 50k on anything interesting. Local pilot at 1k: 18/110 rank-4 jobs solved (easy ladder rows only — the honest expectation is that rank-4/5 must show movement on rows the 2-gen baseline can't touch at the SAME budget to be interesting). Every solved row carries a full path: verify with `.venv/bin/python3 -m experiments.stable_ac.verify_static_rank results/stable_ac/static_rank` — believe nothing that fails it.

## What ran overnight (already committed, read at leisure)

- **Orbit-floor refutation + n_subs≥2 length law**: `literature/proofs/STABLE_AC_NEW.tex` (two new sections; the k≥2 exact law verified on 1,995 reconstructed transforms, 0 violations; the floor counterexamples independently re-verified).
- **Obstruction barrier note**: no homotopy- or simple-homotopy-level invariant can separate stable-AC classes of trivial-group presentations (Wh(1)=0); any obstruction must live strictly at the 3-deformation layer.
- **Thickenability feasibility (GO)**: `experiments/stable_ac/thickenable/NEUWIRTH_FEASIBILITY.md` — for 2-generator presentations the Neuwirth decision collapses to a rotation-system check on the 4-vertex Whitehead graph; Regina validates any positive. A positive on ANY reachable state of a target = that target settled (Lackenby Thm 1.3). Next step if you want it: the ~1-week checker build.
- **Prover9 ATP pilot**: `results/stable_ac/atp/` (encoder + pilot outcomes; ATP proofs are leads pending move-sequence extraction).
- W&B is NOT wired into these two notebooks tonight — the jsonls are the source of truth; mirroring to W&B can be added afterwards without touching run identity.
