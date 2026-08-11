# Shaped-reward PPO — the plan

Status: pre-registration. Nothing here has been run. The control is the reward the 610model was trained with; the treatment adds a potential built from the two heuristic features that survived a 70,723-orbit A/B. Evaluation is **benchmark-60**, per the standing rule.

## 0. What we know about benchmark-60 before anything runs

Three facts established by reading the data, all of which change how the scoreboard must be written.

**The 610model scores 49/60.** By bin: bins 0–6 all 6/6, bin 7 5/6, **bin 8 0/6**, bin 9 2/6. Reference points at *different* budgets: greedy length-only 29/60 and the tuned greedy heuristic 43/60, both at 1,000 greedy nodes; the PPO number is a 1024×150 beam. Those three numbers are **not** on a common denominator of compute and must never be tabulated without a budget column.

**54 of the 60 are in the PPO training set.** All 60 appear in `1190MS`. 54 appear in `AC19_extended`, and every one of those is inside the first 634 lines — i.e. inside the deterministically pinned prefix (`ppo_ac_s.py:98`, `parallel_sample[:634] = False`). Benchmark row `bin 0 / ms_idx 0` **is** line 0 of both files. So 49/60 is a number measured on the model's own training rows and is a reference line, never a bar.

**The membership split is perfectly confounded with difficulty.** The 6 rows *not* in `AC19_extended` are exactly the 6 bin-9 rows (`ms_idx` 668, 698, 717, 955, 1046, 1132; start lengths 23–25). Solve rates split 47/54 in-training vs 2/6 out — which looks like a generalisation gap and is not measurable as one, because the out-of-training set is also the hardest bin. The decisive counter-evidence is bin 8: all six of its rows *are* pinned training rows and the model solves **0/6**. Difficulty dominates membership on this benchmark; the leakage is real but it is not what produces the 49.

**60 rows are 45 Aut-orbits.** `aut_class` 106 appears 8×, classes 93 and 97 3× each, classes 87/99/108/110 2× each. Same defect as the 66-row benchmark. Every headline gets reported twice: rows/60 and orbits/45.

### Consequence: benchmark-60 has to be held out, and holding it out has a trap

`acs_data.ms_prefix_length` derives the pin count by walking the **leading lines** of `AC19_extended` against `1190MS` until they differ. Delete benchmark rows from the training file and the first deletion is at index 0, so the walk stops immediately and the derived pin count collapses from 634 to **0** — pinning silently switches off entirely. That would change the training recipe far more than the reward change under test, in both arms, invisibly. The held-out dataset therefore ships with an **explicit pin index list**, not a prefix count, and a test that pins the count at 580 (634 − 54).

## 1. The reward

Unchanged base, plus a potential-based shaping term (Ng, Harada & Russell 1999 — provably policy-invariant, and it telescopes, so wandering cannot farm it):

```python
base     = 1000.0 if terminated else -float(min(nnz, 10))   # exactly today's reward
h        = L + 20.0 * S + 2.0 * MK
phi      = -lam * h
phi_next = 0.0 if done else -lam * h_next                   # done = terminated OR truncated
reward   = base + (GAMMA * phi_next - phi)                  # GAMMA = 0.999
```

`L + 20·S + 2·MK` is not a guess. On the hard-100k A/B (`results/heuristic_search/hsearch_ac19_hard100k/RESULTS.md`), over a common denominator of **70,723 Aut orbits** at budget 100,000: length-only leaves 221 unsolved, `s20_mk2` leaves **39** — a 5.7× smaller residual, with 182 of length's failures recovered and none lost the other way. `xyimb` is excluded: its optimal sign flips between the two shipped configs (+3.292 vs −5.978), which is the signature of a fit to one problem family.

Why shaping at all: the baseline reward is `-min(nnz, 10)`, and `nnz` **is** `L`. Above L=10 it is flat −10, so on every presentation that matters there is no length gradient — the agent is told nothing until it terminates. The shaping term restores a per-step gradient and adds two structural features length cannot see.

**`Φ = 0` at every episode end, truncation included.** `acs_env.py:140-142` collapses `terminated | truncated` into one `done`. That is harmless for a flat reward and is exactly the leak shaping must close: bootstrapping `Φ(s')` past a horizon cut-off would make "survive to step 96 in a low-`h` state" pay.

**λ = 0.2, measured.** Over 97,280 real transitions on `AC19_extended` (1,024 envs, 96 steps, random actions), `h` at episode start is mean 46.2 / median 45.3, and on transitions that actually change the state `|γ·h′ − h|` is median **10.94**, mean 11.21, p90 19.05. So λ=0.2 puts the median shaping term at **2.19 — 22% of the flat −10** the base pays. Informative without swamping. λ=0.1 (11%) is the fallback if training destabilises. Total shaping bias over an episode telescopes to exactly `+λ·h₀` ≈ +9 against a +1000 terminal — negligible. Pinned as a band in `tests/ppo/test_shaping.py`, so a change to the feature definitions that moves the scale invalidates the chosen λ loudly instead of silently.

Two things that measurement also showed. **94.2% of random actions are no-ops**, so the per-transition figure above is conditioned on the 5.8% that move; a trained policy moves far more often, so the per-episode shaping mass will run higher than the per-transition number suggests. And a no-op still earns `(γ−1)·Φ = 0.001·λ·h ≈ +0.009` — the standard discount artefact of potential shaping, provably harmless to the optimal policy and three orders of magnitude under the base reward, but worth knowing it is positive.

**λ = 0 must reproduce today's reward bitwise.** That is a test, not an assertion.

## 2. Design

| | |
|---|---|
| dataset | `AC19_extended_ho60` — `AC19_extended` minus the 54 benchmark rows, explicit 580-index pin list |
| arms | **control** = base reward · **primary** = `L + 20·S + 2·MK` |
| seeds | 1 to start (142); more only once `seconds_per_update` is known |
| updates | 1000 (the 610model's own step count) |
| eval | benchmark-60 beam, 1024×150, every `SAVE_EVERY` checkpoint |

**One control, one treatment. There is no second treatment.** `hsolve.RECOMMENDED` is ruled out by standing user directive and is not an arm here -- it was tuned on ~60 presentations and its xyimb weight flips sign between the two shipped configs. `tests/ppo/test_shaping.py` fails if those weights are ever added back. Beyond the directive, two treatments against one control would give the winner two tickets, and at 8.7 h per arm a second treatment costs a full night to confirm something already judged overfit.

**Primary comparison is control-vs-primary, both fresh, both on the held-out data.** Leakage cancels in that difference. The 49/60 is context only.

**Log the path-length distribution per arm, not just the solve count.** S+MK certificates run ~13% longer (mean path 23.50 → 26.57 on the 70k A/B), the training horizon is 96 steps, and the baseline beam's longest path is already 94. Shaping can push episodes from termination into truncation, which would show as a *fall* in solve rate from a reward that is working.

## 3. Build list (mine)

New files. `envs/`, `network.py`, `ppo_ac_s.py`, `greedy_search.ipynb` stay read-only; `experiments/ppo/*` is this branch's own code and gets extended behind default-off flags.

1. **`experiments/ppo/shaping.py`** — batched `(L, S, MK)` on the flat `(N, 2·max_len)` int8 states.
   The whole feature set closes into arithmetic with no run enumeration, because a cyclic word alternates generators around the ring: **#x-runs == #y-runs** whenever both generators are present, so `k = (cyclic generator transitions) / 2`, and `k = 0` when a relator uses one generator or is empty. Then `mx = (#x letters over both relators) / (#x-runs over both)`, `my` likewise, `S = min(mx, my)` (or whichever is non-zero), `MK = max(k1, k2)`, `L = nnz`. Vectorised on-device, no Python loop.
   Traps: `blocks()` reads `c in "xX"` so the *sign* is irrelevant — key on `abs(v) == 1`; the seam merge is what the cyclic transition count already encodes; the empty relator is `((), ())`.
2. **`tests/ppo/test_shaping.py`** — parity against `hsearch.feats()` on ≥5,000 real states harvested from actual rollouts (not synthetic words); `λ=0` reproduces the current reward bitwise; `Φ=0` on truncation as well as termination; the `|Δh|` measurement that fixes λ.
3. **`experiments/ppo/heldout.py`** — writes `data/AC19_extended_ho60.txt` and its explicit pin-index list.
4. **`tests/ppo/test_heldout.py`** — 156,762 − 54 rows; pin list length exactly 580; **no benchmark-60 row survives anywhere in the file**; the naive prefix walk on the filtered file returns 0, proving the trap is live and that the explicit list is what is being used.
5. **`experiments/ppo/bench60.py`** + test — a `beam_eval` variant over the 60 rows, reporting rows/60, orbits/45, per-bin, and the path-length distribution. ~10 minutes of beam (60 rows; 0.82 s mean solved, 9.86 s mean unsolved), so it runs per checkpoint and gives a learning curve in the test metric.
6. **Aut-orbit leakage, timeboxed.** Exact-match removal still leaves Aut-equivalents of the 60 among the other 156k rows. `autcanon_fast.py` may make an orbit-level filter cheap; if it does not, ship exact-match and state the limitation. The arm-vs-arm comparison is immune either way — orbit leakage only touches the generalisation framing.

## 4. What the user runs, in order

Each step gates the next. Report the quoted line back before starting the next one.

**Step 1 — timing smoke, with training.** Nothing downstream can be sized without `seconds_per_update`, and it has never been measured. In CONFIG:

```python
SMOKE_RUN   = True
SMOKE_TRAIN = True     # add this line
ARMS        = ["AC19_extended"]
SEEDS       = [142]
```

Run all. Report the printed `smoke_report.json` between the `====` lines, and the `sps` from the training heartbeat.

**Step 2 — learning-happens gate, control arm.** A small run that must show the solve rate rising before either arm is worth an A100-night. Config comes from step 1's timing; I will fill it in. Reported: solve rate at update 0 vs the end. If the control cannot move, no treatment reading is interpretable.

**Step 3 — the two arms.** `ARMS = ["AC19_extended_ho60"]`, `MAX_UPDATES = 1000`, one run with `SHAPING = None`, one with `SHAPING = "s20mk2"` and the λ from step 1. `train_tag` encodes variant and λ, so the checkpoints and W&B runs cannot be confused. Both resumable — a Colab disconnect continues.

**Step 4 — benchmark-60 eval** on every saved checkpoint of both arms, plus the 1190MS beam on the final ones for comparability with the 588.2 / 607.2 paper rows.

## 5. Scoreboard, fixed now

Primary: **benchmark-60 solve count, shaped minus control, at update 1000, one seed** — reported as rows/60 *and* orbits/45, with the per-bin split. Bins 0–7 are near-saturated for a working model, so the signal lives in bins 8–9 (12 rows, 11 orbits) — a small denominator, which is stated up front rather than discovered afterwards.

Secondary, all pre-registered: path-length distribution per arm (the truncation risk); solve rate on the 6 never-trained bin-9 rows; 1190MS beam for paper comparability; wall-clock per update, since shaping adds a feature computation to every step of every env.

Reported regardless of outcome. A null result on 45 orbits is a real answer about whether a heuristic that wins decisively in best-first search transfers to a learned policy — the two have never been compared on the same problem.
