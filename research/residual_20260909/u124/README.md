# The 124 unsolved Miller-Schupp ACA classes: the census algorithm at 10,000 units

Probe of the round-2 census algorithm and its components on the 124
Aut(F2)-minimal representatives of the unsolved ACA classes
(`data/ms_unsolved_reps/aca_124_best.csv`, CLAUDE.md section 4), at ten times
the census budget, and on the 36 *unreduced* (initial) pairs that the mu-ladder
had shortened (`aca36_initial.csv`, from `aca_124_reduced.csv`).  Every claimed
solve or shorter state carries a replayed path (`words.replay_move` for
substitutions, `words.apply_pair` for automorphisms, the census decoders for
compiled certificates).

**Correction notice.** The first versions of `reduce_search.py` and
`mu_probe.py` re-pushed already-generated children onto the heap (the census
kernel skips them), which wasted most of their pops on duplicates.  Every file
they produced is kept under `superseded_dup_push/` and is superseded by the
corrected runs below (per-relator cap 64, the cap the 10M reference run used;
the corrected uncapped search exceeds the container's memory at 10,000 pops).
The harness screens, the orbit search, the aut-start run, the supermove sweep
and the new-rules sweep were never affected.

## A. The 124 best-known pairs: no solve, no shorter presentation

| probe (10,000 units or pops per row) | solved | rows with a shorter total | notes |
|---|---:|---:|---|
| `K3p_c14aut` (round-2 cascade, cap-14 table) | 0 / 124 | 0 | 165 M table lookups, all missed; 14.8 s per row |
| frozen published policy | 0 / 124 | 0 | identical outcome, 13.2 s per row |
| S20_MK2 search, ordinary moves (`reduce_search.py`, corrected, cap 64) | 0 / 124 | 0 | 8 rows reach an equal-length pair with a shorter longest relator |
| S20_MK2 + 4 Nielsen edges (corrected, cap 64) | 0 / 124 | 0 | 9 such rebalances |
| mu-probe: search + Whitehead minimisation of every visited state (corrected) | 0 / 124 | 0 orbit-floor descents | see `aca124_mu_10000.summary.json` |
| orbit search: re-root at the Whitehead-minimal rep after every move (`orbit_search.py`) | 0 / 124 | 0 | exhaustive for 114 classes within 8 letters of the floor (95-8,555 orbit reps each) |
| aut-start: 4,276 starting automorphisms, 1,000 pops each (`aut_start_search.py`) | 0 | 0 | descents back to the floor are smoothest after x->xy or a signed permutation, roughest after y->yx / y->Xy; none goes below it |
| all-gates supermove sweep (`supermove_sweep.py`) | 0 / 124 | 0 | 122,842 BS-donor states, all rejected by the Britton preflight; 20,282 stable-power and 15,703 stable-square rewrites, none productive |
| campaign rules F1 / F3 / BS-DEMOTE on every visited state (`newmoves_sweep.py`) | 0 / 124 | 0 | F3 fired 126 times (115 preflight-rejected, 11 dead stable-power); 7,659 stalled-BS labels, none demotable |

The 124 stored pairs are confirmed Aut-minimal by the ladder's own
canonicaliser (`autcanon_fast.aut_min`, copied here from branch
`experiments/ppo`).  Under a table terminal and every ordering tried, no
visited state comes within 14 letters of (x, y) on both relators.

## B. The 36 unreduced pairs: what an AC-move search recovers, and how fast

The mu-ladder shortened these 36 classes (2,446 -> 2,356 letters) with
*subword change-of-variables hops* (introduce z = w(x, y), substitute, delete
a generator, relabel), Tietze-type transformations outside the AC move set,
measured by the Aut(F2)-orbit-minimal length mu.  An exhaustive depth-2
enumeration of the full Definition 2.1 move set (with or without Nielsen
automorphisms and conjugation by words up to length 3) reproduces none of its
fourteen "2-hop" reductions, so those entries are not AC reductions.  The
reference AC-move attempt is the 10M-node S20_MK2 run
(`ref_u124_10m_RESULTS.md`, `ref_u124_10m_s20_mk2_b10000000_mrl64.jsonl`,
branch `codex/ac19-hybrid-10m`; 186 CPU-hours), which lowered 14 of the 36.

Corrected runs from the unreduced pairs, 10,000 pops per row, cap 64
(`analyze_speed.py`):

| method | rows strictly shortened (of 36) | pops to the shortening state, median / max | reaches the ladder floor |
|---|---:|---|---:|
| S20_MK2, ordinary moves | 8 | 628 / 2,720 | 7 |
| S20_MK2 + Nielsen edges | 14 | 2,146 / 9,773 | 8 |
| mu-probe (S20_MK2 + Whitehead minimisation of visited states) | **16** | 726 / 7,154 | **11** |
| orbit search (re-rooted at the orbit rep, slack 8) | 12 | **27 / 248** | 6 |
| aut-start (best of <= 40 starting automorphisms, 1,000 pops each) | 12 | 391 / 736 | 8 |
| 10M-node S20_MK2 reference | 14 | not recorded / 10,000,000 | 8 |

Row by row against the 10M run, our best over methods matches it on 33 rows
and beats it on 3 (aca_36: 16 vs 17, the ladder floor; aca_108 and aca_112:
24 vs 25); it never does worse.  Over the 36, the excess above the ladder
floors falls from 90 letters to 60 (`analyze_initial.py`), 11 classes sit
exactly at the ladder floor by AC moves, and aca_111 reaches 23, below the
ladder's own floor of 24.  Continuing the orbit search from the 10M run's 14
best states goes lower only on aca_36 and exhausts the reachable orbit graph
on 11 of them.  The rows the orbit search misses (aca_107, 110, 113, 114)
need a hump more than 12 letters above the start (slack 12 / 30,000 pops
still exhausts without them); plain S20_MK2 crosses it in 460-630 pops.

Full per-row tables: `PYTHONPATH=. python3 research/residual_20260909/u124/analyze_speed.py`
and `analyze_initial.py`.

## C. Files

- Harness screens: `aca124_K3p_c14aut_10000.jsonl`, `aca124_frozen_10000.jsonl`,
  `aca36_initial_K3p_c14aut_10000.jsonl`.
- Certified searches (paths stored): `aca124_reduce_10000.jsonl`,
  `aca36_initial_reduce_10000.jsonl`, `aca124_mu_10000.jsonl`,
  `aca36_initial_mu_10000.jsonl`, `aca124_orbit_10000.jsonl`,
  `aca36_initial_orbit_10000_v2.jsonl`, `aca6_initial_orbit_30000_s12.jsonl`,
  `aca14_from10m_orbit_10000.jsonl`, `aca124_autstart_1000.jsonl`,
  `aca36_initial_autstart_1000.jsonl`, `grid36_*_10000.jsonl` (weight schedules
  on the 36 unreduced pairs).
- Sweeps: `aca124_supermoves_10000.jsonl`, `aca124_newmoves_10000.jsonl`,
  `aca36_initial_newmoves_10000.jsonl`.
- Reference: `ref_u124_10m_*` (10M run), `autcanon_fast.py` (ladder canonicaliser).
- Superseded (duplicate-push bug): `superseded_dup_push/`.
