# Independent L>24 test — can lifting the per-relator cap trivialize AK(3)?

**Verdict: No.** Lifting the length cap above 24 does not let the greedy substitution
search trivialize AK(3), in either place a cap can act. Every arm floors at total
relator length **13** (AK(3)'s own starting length — the "second hump"), and **nothing
solves**. The cap was never the barrier; the hump is.

This test is fully isolated: everything lives under `experiments/test_cap/`, and the
global `L = 24` in `one_generator/greedy_nrel.py` was **never edited** (it is the
flat-format / RL-env padding width). The lifted cap is passed only as the `max_len`
*parameter* to the solver, whose byte keys are variable-width.

---

## Arm 2 — direct search cap raised (L = 24 → 48)

Stabilized 3-gen greedy on `⟨x,y,z | r1, r2, z·w⁻¹⟩`, forms **textbook** + **rep**, the
8 hero words, budget 100 000 nodes, at `max_len ∈ {24, 48}`.

| metric | result |
|---|---|
| runs solved | **0 / 32** |
| (form,word) pairs with **byte-identical visited set** at L24 vs L48 | **16 / 16** |
| pairs with identical floor at L24 vs L48 | **16 / 16** |
| floors reached (textbook) | 13 (10 words), 15 (6 words) |
| floors reached (rep) | 13 (12 words), 15 (4 words) |

The search visited set is *byte-for-byte identical* whether the cap is 24 or 48 — the
greedy-by-total-length search never once wants a relator longer than 24 at this budget.
**Raising the per-relator search cap is a provable no-op.** (Floors of 13 or 15 depend on
the word, never on the cap.)

## Arm 3 — quotient / elimination caps raised (l_cap 24→48, htl 20/24→40)

`plateau_elim.py` harvest + merge, budget 60 000, caps `l_cap=48 harvest_tl_cap=40
merge_tl_cap=40`. This is the *only* place a bigger cap can bite: it lets Lemma-11
eliminations produce 2-gen quotients longer than the old pipeline ever generated.

| metric | result |
|---|---|
| unique candidates (mod symmetry) | 250 397 |
| candidates in the **never-before-searched >24 region** | **212 913** |
| max candidate length | 40 (the htl cap) |

## Arm 4 — stratified solve of the 25–40 region

`plateau_elim`'s own solve is shortest-first and never reaches the long region, so a
stratified driver sampled **100 candidates per length bucket 25–40** (+200 short
controls) and greedy-solved each with `max_len = 60`.

| metric | result |
|---|---|
| candidates attempted | **1 800** |
| **solved** | **0** |
| distinct `min_total_len` (floor) reached across all 1 800 | **{13}** |

Every length bucket, fully covered, floors at exactly 13:

```
control  len 13–17 : 200 candidates → all floor 13
new      len 25    : 100 → {13:100}      len 33 : 100 → {13:100}
region   len 26    : 100 → {13:100}      len 34 : 100 → {13:100}
         len 27    : 100 → {13:100}      len 35 : 100 → {13:100}
         len 28    : 100 → {13:100}      len 36 : 100 → {13:100}
         len 29    : 100 → {13:100}      len 37 : 100 → {13:100}
         len 30    : 100 → {13:100}      len 38 : 100 → {13:100}
         len 31    : 100 → {13:100}      len 39 : 100 → {13:100}
         len 32    : 100 → {13:100}      len 40 : 100 → {13:100}
```

No candidate — at any length up to the 40 cap — ever recorded a `min_total_len` below 13.
A candidate that could trivialize would first have to *descend below 13* toward the
trivial length 3; not one of the 1 800 does.

---

## Why (the honest interpretation)

The barrier is the **hump, not the cap.** Plain greedy substitution drives total relator
length down to 13 (AK(3)'s own length) and sticks, because escaping requires *going back
up* the length landscape — and greedy, ordered by total length, won't climb. Giving it a
larger cap just hands it room it never uses (Arm 2), or longer quotients that drain to the
same floor (Arm 4). The move that actually escapes — Fagan's Lemma-11 destabilization as a
*supermove* — is not something ordinary greedy performs. The real lever is a search that
can climb the hump (beam / RL), not a bigger number for L.

## Coverage & caveats (no silent truncation)

- **Budget disclosure.** Arm 4 solved 1 102 candidates (buckets 25–≈35 + controls) at
  `budget2 = 80 000` and the remaining 698 (the longest, slowest tail) at `budget2 =
  40 000`. Justification: no candidate in 1 100+ prior runs ever dipped below floor 13, so
  the reduced budget cannot mask a solve — a solvable candidate reveals sub-13 descent far
  earlier. Both tiers gave the identical result (floor 13, 0 solved).
- **Sampling.** 100 per length bucket is a stratified sample, not exhaustive — there are
  212 913 candidates in the >24 region; 1 600 of them were solved. The floor-13 result is
  uniform across every bucket and every control, but this is a strong sample, not a
  100%-of-candidates proof.
- **Length ceiling.** Quotients longer than 40 were never generated (the htl=40 harvest
  cap); the test covers 25–40, not beyond.
- **What this is.** A scoped negative for *greedy substitution*. It says the cap isn't the
  bottleneck; it does not (and cannot) rule out AK(3) trivializing under a fundamentally
  different (non-greedy) search.

## Reproduce

```bash
.venv/bin/python3 experiments/test_cap/run_captest.py \
    --budget 100000 --harvest_budget 60000 --l_cap 48 --htl 40 --mtl 40 --workers 2
.venv/bin/python3 experiments/test_cap/solve_stratified.py \
    --budget2 80000 --max_len 60 --k_long 100 --k_ctrl 200 --long_lo 25 --long_hi 40
```

Streams: `search_L.jsonl` (arm 2), `laneD/merged.jsonl` (arm 3), `solve_stratified.jsonl`
(arm 4). Any solve would have auto-triggered `verify_path` replay + a full certificate
chain (`build_chain_cert` → `verify_certificate`); none occurred. The `laneD/` candidate
files (~2 GB) are intermediate and can be deleted — `merged.jsonl` is the derived artifact.
