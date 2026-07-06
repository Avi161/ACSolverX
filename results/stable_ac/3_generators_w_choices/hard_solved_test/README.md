# Hard-but-solvable “wormhole” word-choice sweep — results

AK(3) gave a *negative* result (0 solved, everything plateaus at total length 13), so it can’t tell us *which* word family is most useful. This study asks the same question on presentations the plain 2-generator greedy **did** solve, but only after many nodes and a long path — so there is a real baseline to beat. We stabilize `⟨x,y|r1,r2⟩ → `⟨x,y,z|r1,r2,z·w⁻¹⟩` for ~97 word choices `w(x,y)` (+ the dumb controls) and run the n=3 greedy solver. **Win = a word that solves in fewer nodes / shorter path than `z=r1`, or solves where the dumb words can’t.**

## Finding — what we did & what we learned

**What we did.** Took two *hard-but-solvable* Miller–Schupp presentations (idx 625, 610 — the plain 2-gen greedy solves them, but only after ~60–80k nodes and a 300–660-move path, so there is a real baseline to beat), stabilized each as `⟨x,y,z | r1, r2, z·w⁻¹⟩` for ~97 candidate words `w(x,y)` across 8 families (relator halves/inverses, the AK isolation family `wk`, `wstar`, conjugates, commutators, all freely-reduced words of length ≤3, MS library words, and the dumb `r1/r2` controls), and ran the n=3 greedy solver at a **100,000-node screen**. Win condition: a word that solves in fewer nodes / a shorter path than `z=r1`, or solves where the dumb words fail.

- **idx 625:** 98 words, **4 solved** — only `control`/`relhalf` (relator-derived); **0 generic-family** words solved. Best solve 77,395 nodes ties the `z=r1` control (77,395 n). Every unsolved word plateaus at total length ≥ 17 (trivial = 3).
- **idx 610:** 99 words, **2 solved** — only `control`/`relhalf` (relator-derived); **0 generic-family** words solved. Best solve 61,082 nodes ties the `z=r1` control (61,082 n). Every unsolved word plateaus at total length ≥ 16 (trivial = 3).

**What we learned — a clean negative at the 100k screen.** Across both targets, **only relator-derived words solve** (the `control` words `z=r1/r2` and `relhalf` words built from the target's own relators), and **none beats the dumb `z=r1` control** — the `relhalf` solvers land at the *same* node count as `z=r1` because they are a half/inverse of `r1`, i.e. the same solve in disguise. **0 of 177 generic-family (word×target) runs solved** — every structurally-different word, including the theory-motivated `wk` AK-isolation family, stalls at total length 16–17 (trivial 3). So at screen budget there is **no wormhole shortcut** on these targets: naming a clever `z=w` does not help ordinary greedy find a cheaper/shorter path. This mirrors the AK(3) sweep's negative (0 solved, hard plateau): ordinary greedy substitution does not exploit the change of variables — realizing a useful `z=w` is Fagan's Lemma-11 *atomic destabilization*, a supermove greedy does not perform. The 1,000,000-node full tier was intentionally **not** run (user-gated); on this evidence the plateau is unlikely to move.

## Target idx 625 — `r1 = YYYYYYYYXyyyyyyyx`, `r2 = YYXYxyX` (Miller–Schupp)

- **2-gen baseline** (no stabilization): solved in **77,385 nodes**, path length **663**.
- **n=3 dumb-word controls @500k** (on disk): `z=r1`: ✅ 77,399 n / 665 p · `z=r2`: ✅ 80,115 n / 668 p · `z=x`: ❌ exhausted 500,000 · `z=y`: ❌ exhausted 500,000.

### SCREEN @ 100,000 nodes — 98 words run, **4 solved**, closest *unsolved* min-total-len = 17

Best solve: **77,395 nodes** (in-sweep `z=r1` control: 77,395 nodes). Only relator-derived words (`control`/`relhalf`) solved; no generic word family solved at this budget.

**Solved words** (fewest nodes first):

| rank | family | word `w=z` | nodes | path len | nodes/s | peak GB |
|-----:|--------|------------|------:|---------:|--------:|--------:|
| 1 | control | `r1` | 77,395 | 665 | 2356 | 0.9 |
| 2 | relhalf | `XYYYYYYYxyyyyyyyy` | 77,395 | 665 | 1452 | 0.7 |
| 3 | relhalf | `xYXyxyy` | 80,111 | 668 | 1466 | 0.7 |
| 4 | control | `r2` | 80,111 | 668 | 1499 | 0.9 |

**Closest UNSOLVED words** — the actual presentation greedy got stuck on (`min_total_state`, trivial total length = 3):

| family | word `w` | min total len | closest presentation `⟨x,y,z\|·⟩` reached |
|--------|----------|--------------:|-------------------------------------------|
| brute | `yyy` | 17 | `Zyyy  |  YXyxx  |  ZZYXXzzx` |
| brute | `YYY` | 17 | `ZYYY  |  YXyxx  |  ZZXzzxxy` |
| relhalf | `yyyyyyy` | 18 | `ZYXzx  |  YXyxx  |  Zyyyyyyy` |
| relhalf | `YYYYYYYY` | 18 | `ZXzyy  |  YYxyX  |  Zyxxxxxx` |
| relhalf | `Xyyyyyyyx` | 18 | `ZYYzx  |  YYxyX  |  ZXXXXXXY` |
| wk | `yyyyyyyyXyxy` | 18 | `ZYzyx  |  YYxyX  |  ZXXXXXXX` |
| wk | `YYYYYYYYXyxy` | 18 | `ZYxzX  |  ZXzyy  |  Zyxxxxxx` |
| ms | `Xyxyy` | 18 | `ZyX  |  ZXyxyy  |  ZZYXXXzYx` |

**By family:**

| family | words | solved | best nodes-to-solve | closest (min total len) | description |
|--------|------:|-------:|--------------------:|------------------------:|-------------|
| `relhalf` | 8 | 2 | 77,395 | 3 | 1 — parts of THIS target's relators: inverses, pure-power runs (yⁿ/Yⁿ⁺¹), cyclic halves |
| `wk` | 17 | 0 | — | 18 | 2 — `y⁻ᵏ·x⁻¹yxy`, k∈[-8,8] (AK(n) isolation family, Thm 6/7) |
| `wstar` | 4 | 0 | — | 19 | 3 — `y⁻¹xyx⁻¹` + automorphism images (Thm 3) |
| `conj` | 14 | 0 | — | 19 | 4 — `g·x·g⁻¹`, `g·y·g⁻¹` for short g (Wirtinger/Rmk 17) |
| `comm` | 6 | 0 | — | 19 | 5 — commutators + short double commutators |
| `brute` | 44 | 0 | — | 17 | 6 — all freely-reduced words of length ≤3 (breadth; includes the dumb w=x, w=y) |
| `ms` | 3 | 0 | — | 18 | 7 — MS(n,w) library w-values (`w1=y⁻¹x⁻¹yxy`) |
| `control` | 2 | 2 | 77,395 | 3 | 8 — the dumb baselines w=r1, w=r2 |

## Target idx 610 — `r1 = YYYYYYYXyyyyyyx`, `r2 = YYYxYXyx` (Miller–Schupp)

- **2-gen baseline** (no stabilization): solved in **61,066 nodes**, path length **307**.
- **n=3 dumb-word controls @500k** (on disk): `z=r1`: ✅ 61,092 n / 311 p · `z=r2`: ❌ exhausted 500,000 · `z=x`: ❌ exhausted 500,000 · `z=y`: ❌ exhausted 500,000.

### SCREEN @ 100,000 nodes — 99 words run, **2 solved**, closest *unsolved* min-total-len = 16

Best solve: **61,082 nodes** (in-sweep `z=r1` control: 61,082 nodes). Only relator-derived words (`control`/`relhalf`) solved; no generic word family solved at this budget.

**Solved words** (fewest nodes first):

| rank | family | word `w=z` | nodes | path len | nodes/s | peak GB |
|-----:|--------|------------|------:|---------:|--------:|--------:|
| 1 | relhalf | `XYYYYYYxyyyyyyy` | 61,082 | 311 | 995 | 0.5 |
| 2 | control | `r1` | 61,082 | 311 | 1110 | 0.5 |

**Closest UNSOLVED words** — the actual presentation greedy got stuck on (`min_total_state`, trivial total length = 3):

| family | word `w` | min total len | closest presentation `⟨x,y,z\|·⟩` reached |
|--------|----------|--------------:|-------------------------------------------|
| relhalf | `YYY` | 16 | `ZYYY  |  YXyxx  |  ZZyXzzx` |
| brute | `yyy` | 16 | `Zyyy  |  YXyxx  |  ZZXzzxY` |
| relhalf | `yyyyyy` | 17 | `ZXzxY  |  YXyxx  |  Zyyyyyy` |
| relhalf | `YYYYYYY` | 17 | `ZXzyy  |  YYxyX  |  Zyxxxxx` |
| relhalf | `Xyyyyyyx` | 17 | `ZYYzx  |  YYxyX  |  ZXXXXXY` |
| relhalf | `YYYx` | 17 | `ZYYYx  |  ZXYxy  |  ZXXzxyx` |
| relhalf | `YXyx` | 17 | `ZYXyx  |  ZXyyy  |  ZXYXzxx` |
| wk | `yyyyyXyxy` | 17 | `ZYzx  |  ZXzxY  |  Zxxxxxxy` |

**By family:**

| family | words | solved | best nodes-to-solve | closest (min total len) | description |
|--------|------:|-------:|--------------------:|------------------------:|-------------|
| `relhalf` | 8 | 1 | 61,082 | 3 | 1 — parts of THIS target's relators: inverses, pure-power runs (yⁿ/Yⁿ⁺¹), cyclic halves |
| `wk` | 17 | 0 | — | 17 | 2 — `y⁻ᵏ·x⁻¹yxy`, k∈[-8,8] (AK(n) isolation family, Thm 6/7) |
| `wstar` | 5 | 0 | — | 17 | 3 — `y⁻¹xyx⁻¹` + automorphism images (Thm 3) |
| `conj` | 14 | 0 | — | 17 | 4 — `g·x·g⁻¹`, `g·y·g⁻¹` for short g (Wirtinger/Rmk 17) |
| `comm` | 5 | 0 | — | 17 | 5 — commutators + short double commutators |
| `brute` | 45 | 0 | — | 16 | 6 — all freely-reduced words of length ≤3 (breadth; includes the dumb w=x, w=y) |
| `ms` | 3 | 0 | — | 17 | 7 — MS(n,w) library w-values (`w1=y⁻¹x⁻¹yxy`) |
| `control` | 2 | 1 | 61,082 | 3 | 8 — the dumb baselines w=r1, w=r2 |

## What was implemented

`z=w(x,y)` stabilization + n=3 greedy with a **null-revert block** (forbids `z=1`, forcing the search to use `w`). Two-tier, crash-safe & resumable. Code (all under `experiments/stable_ac/one_generator/`): `hard_words.py` (target loader + word bank, reusing the generic families from `ak3_words.py`; only `relhalf` is re-derived from the target’s own relators), `hard_probe.py` (spawn-safe worker; records `min_total_len` **and** `min_total_state`), `run_hard_wormhole.py` (driver), `report_hard.py` (this report). Independent adversarial suite: `tests/hard_words_independent_test.py`.

Word families (same breadth as the AK(3) sweep):

| family | description |
|--------|-------------|
| `relhalf` | 1 — parts of THIS target's relators: inverses, pure-power runs (yⁿ/Yⁿ⁺¹), cyclic halves |
| `wk` | 2 — `y⁻ᵏ·x⁻¹yxy`, k∈[-8,8] (AK(n) isolation family, Thm 6/7) |
| `wstar` | 3 — `y⁻¹xyx⁻¹` + automorphism images (Thm 3) |
| `conj` | 4 — `g·x·g⁻¹`, `g·y·g⁻¹` for short g (Wirtinger/Rmk 17) |
| `comm` | 5 — commutators + short double commutators |
| `brute` | 6 — all freely-reduced words of length ≤3 (breadth; includes the dumb w=x, w=y) |
| `ms` | 7 — MS(n,w) library w-values (`w1=y⁻¹x⁻¹yxy`) |
| `control` | 8 — the dumb baselines w=r1, w=r2 |

## Reproduce / resume
```bash
cd experiments/stable_ac/one_generator
python hard_words.py                                   # build word banks + Phase-0.5 gates
python run_hard_wormhole.py --phase screen             # 100k screen, both targets (resumable)
python run_hard_wormhole.py --phase full --only <w,..> # escalate chosen words to 1M
python report_hard.py                                  # regenerate this README
python tests/hard_words_independent_test.py            # independent suite
```
Streams resume by `(idx, word_name, budget)`; re-running is a no-op, a killed run continues. `runs/hard_ms<idx>_<budget>.jsonl` (every word), `paths/hard_ms<idx>.jsonl` (a replayable path per solve).

## Caveats (honest)

- Ordinary greedy substitution on the stabilized presentation (not Fagan’s Lemma-11 atomic destabilization). A reached-trivial 3-gen presentation is a valid trivialization of the base by AC5 destabilization.
- JAX-env gold gate deferred (JAX absent; env `s_move` is n=2-only). Each solve’s evidence is `verify_path` (independent replay) + reload→replay; strong but not the executable gold gate.
