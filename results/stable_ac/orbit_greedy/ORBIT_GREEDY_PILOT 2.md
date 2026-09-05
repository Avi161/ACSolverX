# Greedy from μ-ladder orbits — local pilot

Every row of a `mu_ladder_big` `*_orbits.jsonl` is a concrete 2-generator pair reached from its class's original by a chain of subword-CoV hops, produced at **zero search nodes**. So each orbit is a free alternative *start* for the same question, and the natural experiment is: run the baseline greedy from the orbits instead of from the original. Precedent: [`AUTOMORPHISMS_COV.md`](../../../experiments/stable_ac/cov/AUTOMORPHISMS_COV.md) did the one-hop version and got **17 unsolved→solved flips** at budget 100 over the 66-row benchmark.

Runner: `experiments/stable_ac/cov/orbit_greedy.py` (tests: `tests/stable_ac/test_orbit_greedy.py`).

## What a solve would prove

The chain is `original ~st orbit` (stabilize → substitute → isolate → destabilize) and the search supplies `orbit ~AC (x,y)`. Together that proves the original is **stably AC-trivial — never AC-trivial**. AK(3) is the standing warning: stably trivial, AC status open. For the same reason the reported `path_length` starts at the *transformed* pair and is not a certificate for the original ([`AUTOMORPHISMS_COV.md`](../../../experiments/stable_ac/cov/AUTOMORPHISMS_COV.md) †); only `solved` and `nodes_explored` compare like for like.

## Setup

6 classes of `aca_124` (`aca_0, 4, 9, 34, 39, 115`), ladder run locally to 200 s/class → **44,365 orbits**. Sample: `spread` 60 per class over the whole μ range (so long relators are represented, not just the moat rim), each entering as its **8 signed-permutation relabels** — the greedy reads strings, not orbits, and relabels supplied 14 of the 17 flips in the one-hop sweep. Budget 1,000, cap 96 (admits 99.8% of orbits, incl. the 174-letter ones). Control = the rung-0 row, i.e. the untransformed original, at the **same** budget and cap. 2,886 searches, 13.5 min.

## Result

`min_total` = the lowest total relator length the search *reached* (trivial = 2; same scale as μ).

| class | control start → reached | best orbit start → reached | orbit starts beating control |
|---|---|---|---|
| aca_0 | 18 → 18 | 24 → 18 (rung 18) | 0/480 |
| aca_4 | 18 → 18 | 26 → 18 (rung 6) | 0/480 |
| aca_9 | 15 → 15 | 15 → 15 (rung 3) | 0/480 |
| aca_34 | 18 → 18 | 33 → **16** (rung 17) | 56/480 |
| aca_39 | 19 → 19 | 22 → 19 (rung 2) | 0/480 |
| aca_115 | 13 → 13 | 13 → 13 (rung 3) | 0/480 |

**0 solved, 0 flips, 1/6 out-reduced.**

## Reading it

**The null is not evidence — the control has no dynamic range.** Every control reduces by exactly zero (`18 → 18`, `13 → 13`, …): from the original, 1,000 nodes buys no descent at all. So the pilot cannot separate "the transformed start does not help" from "nothing shows progress at this budget." `aca_124` is the *unsolved* set (hard at 10⁵–10⁷ nodes); the 17-flip precedent ran on a population whose control already solved 47/66. The local node ceiling is 1,000, so **the real test belongs at a production budget on Colab** — see below. Lesson: [`control-with-no-dynamic-range.md`](../../../experiments/lessons/control-with-no-dynamic-range.md).

**What the run does establish.** The greedy pulls every orbit start back down to its class floor and stops there — 24→18, 26→18, 33→16, 22→19. So Whitehead/`Aut(F₂)` canonicalisation (the ladder) and AC search (the greedy) — two independent move systems — agree on the same floor per class. aca_34's 16 is the ladder's already-known −2 descent, re-found here through AC moves from a μ=33 orbit; it is consistent, not new.

## Companion finding: the ladder's beam abandons the low shell

Instrumenting `aca_39` showed the rung-local beam is a drifting front, not a frontier: its lowest member climbs 22 (rung 2) → 24 (rung 10) → 27 (rung 40) while the candidate mass sits at μ 31–39. Replacing it with a **global best-first heap** over all discovered-but-unexpanded orbits (same hops, same dedup, same wall clock) expanded 5,831 of 22,224 orbits in μ order and therefore **closed the μ ≤ 34 ball**: its minimum is 22 against a start of 19. That is a completeness statement the beam cannot make. It is closed only for routes staying under the popped μ — a descent via a higher-μ detour is not excluded. Lesson: [`rung-local-beam-abandons-the-low-shell.md`](../../../experiments/lessons/rung-local-beam-abandons-the-low-shell.md).

## Running it at a real budget

```bash
python3 -m experiments.stable_ac.cov.orbit_greedy \
    --orbits 'results/stable_ac/mu_scan/*_orbits.jsonl' \
    --budget 100000 --cap 96 --per-class 200 --strategy spread --relabels 8
# resumable (append-only jsonl, keyed on kind/pres_id/orbit rep/relabel);
# --report-only <jsonl> re-prints the census without re-searching
```

`--strategy lowest` vs `spread` is the A/B that answers whether greedy solvability tracks μ at all — the pilot could not, because nothing solved either way.
