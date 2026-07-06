# AK(3) “wormhole” word-choice sweep — results

Can we trivialize **AK(3)** (the length-13 Akbulut–Kirby presentation `13_1`, a 20+ year open candidate AC-counterexample) by **stabilizing to 3 generators** with a *chosen* relator `z = w(x,y)` and running the existing greedy substitution solver? `w` is a free choice, so we throw ~100 literature-grounded words at it. Reaching the trivial 3-generator presentation would be a genuine AC-trivialization of AK(3) (destabilize `z` back out).

## Status: no solve yet

No word has trivialized AK(3) in this sweep so far — the expected outcome for a presentation that has resisted search for two decades. The greedy search drives the total relator length down to a **plateau near 13** (trivial = 3) and gets stuck there — a clean illustration of the AK(3) “second hump.” The value here is the reusable machinery + the record of which of ~100 word choices got closest, so the 1M tier (and future methods) can target them.

## What was implemented

`z = w(x,y)` stabilization `<x,y|r1,r2> -> <x,y,z|r1,r2, z·w⁻¹>` + the n-relator greedy substitution solver, with a **null-revert block** (forbids collapsing `z=1`, forcing the search to use `w`). Two-tier, crash-safe & resumable:

- **SCREEN** — every word × both AK(3) forms at **100k** nodes (parallel): fast solve detection + how close greedy got (`min_total_len`).
- **FULL** — every still-unsolved word escalated to **1,000,000** nodes, 1 worker (a 1M n=3 run peaks ~10 GB RSS), in priority order (Fagan’s flagship words first).

Code (all under `experiments/stable_ac/one_generator/`): `ak3_words.py` (word bank + `stabilize_with_word`, built from the shipped `stabilize.py` primitives), `ak3_probe.py` (spawn-safe worker), `run_ak3_wormhole.py` (driver), `report_ak3.py` (this report). Independent adversarial suite: `tests/ak3_words_independent_test.py` (18/18 pass — own-oracle + differential-vs-`stabilize.py` + structural invariants).

## Word bank

**95 unique words** (freely reduced, deduped, z-relator ≤ L=24). By family (priority = 1M escalation order):

| family | count | description |
|--------|------:|-------------|
| `relhalf` | 17 | 1 — relator sides of AK(3) `xyx,yxy,x³,y⁴` + rotations/inverses (Fagan z=xyx & alts) |
| `wk` | 17 | 2 — `y⁻ᵏ·x⁻¹yxy`, k∈[-8,8] (paper Thm 6/7: exact valid isolations of x) |
| `wstar` | 5 | 3 — `y⁻¹xyx⁻¹` + automorphism images (paper Thm 3) |
| `conj` | 14 | 4 — `g·x·g⁻¹`, `g·y·g⁻¹` for short g (Wirtinger/Rmk 17) |
| `comm` | 6 | 5 — commutators + short double commutators (App F bridge is commutator-heavy) |
| `brute` | 33 | 6 — all freely-reduced words of length ≤3 (breadth probes) |
| `ms` | 3 | 7 — MS(n,w) library w-values (`w1=y⁻¹x⁻¹yxy`, Prop 5) |

Provenance for every word (int form, z-relator, length) is in `word_bank.json`. The two forms swept (both are AK(3)): **textbook** `<x,y|xyx=yxy, x³=y⁴>` (where the theory’s words are provably isolatable) and **rep** `13_1` (`YXyXYx`/`YYYXXXX`, the exact object in `data/ms_unsolved_reps`).

## Results

### SCREEN @ 100,000 nodes

**textbook**: 97 words run, **0 solved**, 97 exhausted budget; closest total length reached = **13** (trivial=3).

| rank | family | word `w` | z-relator | min total len reached | nodes | nodes/s | peak GB |
|-----:|--------|----------|-----------|----------------------:|------:|--------:|--------:|
| 1 | relhalf | `yxx` | `zXXY` | 13 | 100,000 | 3394 | 0.7 |
| 2 | relhalf | `yyyy` | `zYYYY` | 13 | 100,000 | 3385 | 0.7 |
| 3 | relhalf | `xxx` | `zXXX` | 13 | 100,000 | 3368 | 0.7 |
| 4 | relhalf | `xxy` | `zYXX` | 13 | 100,000 | 3360 | 0.7 |
| 5 | relhalf | `yxy` | `zYXY` | 13 | 100,000 | 3095 | 0.7 |
| 6 | relhalf | `xyx` | `zXYX` | 13 | 100,000 | 3094 | 0.7 |
| 7 | relhalf | `yyx` | `zXYY` | 13 | 100,000 | 3141 | 0.7 |
| 8 | relhalf | `xyy` | `zYYX` | 13 | 100,000 | 3118 | 0.8 |
| 9 | relhalf | `XXX` | `zxxx` | 13 | 100,000 | 3161 | 0.8 |
| 10 | relhalf | `YYYY` | `zyyyy` | 13 | 100,000 | 3150 | 0.7 |

**rep**: 97 words run, **0 solved**, 97 exhausted budget; closest total length reached = **13** (trivial=3).

| rank | family | word `w` | z-relator | min total len reached | nodes | nodes/s | peak GB |
|-----:|--------|----------|-----------|----------------------:|------:|--------:|--------:|
| 1 | relhalf | `yyyy` | `zYYYY` | 13 | 100,000 | 2809 | 0.7 |
| 2 | relhalf | `xxx` | `zXXX` | 13 | 100,000 | 2805 | 0.7 |
| 3 | relhalf | `xyx` | `zXYX` | 13 | 100,000 | 2804 | 0.7 |
| 4 | relhalf | `yxy` | `zYXY` | 13 | 100,000 | 2801 | 0.7 |
| 5 | relhalf | `xxy` | `zYXX` | 13 | 100,000 | 2788 | 0.8 |
| 6 | relhalf | `yxx` | `zXXY` | 13 | 100,000 | 2783 | 0.8 |
| 7 | relhalf | `xyy` | `zYYX` | 13 | 100,000 | 2641 | 0.7 |
| 8 | relhalf | `yyx` | `zXYY` | 13 | 100,000 | 2639 | 0.7 |
| 9 | relhalf | `XXX` | `zxxx` | 13 | 100,000 | 2648 | 0.7 |
| 10 | relhalf | `XYX` | `zxyx` | 13 | 100,000 | 2627 | 0.8 |

### FULL @ 1,000,000 nodes

**textbook**: 97 words run, **0 solved**, 97 exhausted budget; closest total length reached = **13** (trivial=3).  _(of 97 words — escalation in progress if < that)_

| rank | family | word `w` | z-relator | min total len reached | nodes | nodes/s | peak GB |
|-----:|--------|----------|-----------|----------------------:|------:|--------:|--------:|
| 1 | relhalf | `xyx` | `zXYX` | 13 | 1,000,000 | 4610 | 4.1 |
| 2 | relhalf | `xxx` | `zXXX` | 13 | 1,000,000 | 3716 | 2.1 |
| 3 | relhalf | `yxy` | `zYXY` | 13 | 1,000,000 | 3709 | 2.4 |
| 4 | relhalf | `yyyy` | `zYYYY` | 13 | 1,000,000 | 3714 | 3.4 |
| 5 | wk | `Xyxy` | `zYXYx` | 13 | 1,000,000 | 3711 | 3.4 |
| 6 | wstar | `YxyX` | `zxYXy` | 13 | 1,000,000 | 3779 | 3.6 |
| 7 | relhalf | `xyxY` | `zyXYX` | 13 | 1,000,000 | 3997 | 4.0 |
| 8 | relhalf | `XXX` | `zxxx` | 13 | 1,000,000 | 3846 | 6.8 |
| 9 | relhalf | `XYX` | `zxyx` | 13 | 1,000,000 | 3682 | 3.7 |
| 10 | relhalf | `YXY` | `zyxy` | 13 | 1,000,000 | 3774 | 6.7 |

**rep**: 95 words run, **0 solved**, 95 exhausted budget; closest total length reached = **13** (trivial=3).  _(of 97 words — escalation in progress if < that)_

| rank | family | word `w` | z-relator | min total len reached | nodes | nodes/s | peak GB |
|-----:|--------|----------|-----------|----------------------:|------:|--------:|--------:|
| 1 | relhalf | `xyx` | `zXYX` | 13 | 1,000,000 | 4944 | 6.7 |
| 2 | relhalf | `yxy` | `zYXY` | 13 | 1,000,000 | 4956 | 6.9 |
| 3 | relhalf | `xxx` | `zXXX` | 13 | 1,000,000 | 4953 | 6.9 |
| 4 | relhalf | `yyyy` | `zYYYY` | 13 | 1,000,000 | 4954 | 7.2 |
| 5 | wk | `Xyxy` | `zYXYx` | 13 | 1,000,000 | 4934 | 7.1 |
| 6 | wk | `YXyxy` | `zYXYxy` | 13 | 1,000,000 | 4954 | 6.9 |
| 7 | wstar | `YxyX` | `zxYXy` | 13 | 1,000,000 | 4808 | 6.8 |
| 8 | relhalf | `xyxY` | `zyXYX` | 13 | 1,000,000 | 4926 | 6.0 |
| 9 | relhalf | `XXX` | `zxxx` | 13 | 1,000,000 | 4930 | 6.5 |
| 10 | relhalf | `XYX` | `zxyx` | 13 | 1,000,000 | 4923 | 6.3 |

## Reproduce / resume

```bash
cd experiments/stable_ac/one_generator
python ak3_words.py                         # build word_bank.json + Phase-0 gates
python run_ak3_wormhole.py --phase screen   # 100k screen, both forms (resumable)
python run_ak3_wormhole.py --phase full     # escalate unsolved to 1M, priority order (resumable)
python report_ak3.py                        # regenerate this README from the JSONL streams
python -m pytest ../../../tests/ak3_words_independent_test.py -q   # independent suite
```
Streams are append-only + fsync’d and resume by `(form, word_name, budget)`; re-running is a no-op, a killed run continues. Files: `runs/ak3_<form>_<budget>.jsonl` (every word, solved+unsolved), `paths/ak3_<form>.jsonl` (one replayable move+state path per solve).

## Caveats (honest)

- This runs **ordinary greedy substitution** on the stabilized presentation — it does *not* execute Fagan’s Lemma-11 destabilization as an atomic move; the bet is that the extra `z=w` relator opens a greedy path the 2-gen form lacks. A reached-trivial 3-gen presentation is still a valid AK(3) trivialization by AC5 destabilization.
- The JAX-env gold gate (`envs/ac_moves.py::s_move` / `check_paths`) is **deferred** (JAX absent here; that env’s `s_move` is hardcoded to relators 0/1 and can’t run n=3). Every solve’s evidence is `verify_path` (independent replay) + a reload→replay + destabilization check — strong, but not the executable gold gate.
- No literature result trivializes AK(3); families 1–2 have paper-level isolation validity, 3–8 are motivated search directions. Near-identical words differ wildly in hardness, so breadth across families is the point.

