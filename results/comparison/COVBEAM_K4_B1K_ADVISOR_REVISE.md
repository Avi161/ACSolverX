# Advisor-REVISE claims — K=4 nonsym beam @1k (bench60)

ac-advisor verdict on the implementation: **REVISE**. This document
addresses the must-address items. The algorithm match and the
s20_mk2 terminal-only swap were **APPROVED** as implemented;
the overstated headline was not.

## What was / was not swapped

The CoV beam (nonsym hops, Aut-min every hop, global visited,
K=4) is **unchanged**. The s20_mk2 experiment only replaced the
**terminal** length-greedy ordering with `s20_mk2 = L+20S+2MK` on
the same frozen `best_rep` starts. It did **not** replace length
everywhere inside the beam (the beam ranks by μ = total length).

## Path certificates (must-address #1)

Re-ran both terminal arms @1000 with `path_moves`, replayed via
`verify_solved_row`.

- length-greedy solves: **49**/60; path replay OK: **49**
- s20_mk2 solves: **49**/60; path replay OK: **49**

## Honest scoreboard (must-address #2)

Raw presentation counts (secondary):

| arm | presentations |
|---|---:|
| plain greedy (original) | 29/60 |
| RECOMMENDED (original) | 43/60 |
| oracle best-CoV | 45/60 |
| shipped union (heur ∪ covgreedy) | 45/60 |
| K=4 beam → length @1k | **49**/60 |
| K=4 beam → s20_mk2 @1k | **49**/60 |

Aut-class counts (headline):

| arm | Aut classes / 45 |
|---|---:|
| RECOMMENDED | 40/45 |
| oracle best-CoV | 41/45 |
| K=4 beam → length | **43**/45 |

Novel vs shipped union: presentations ['568', '573', '578', '583']; Aut classes [93, 98].
Those novel rows share endpoint(s): {"('YXXyx', 'YYYXyyX')": ['568', '573', '578', '583']}.
Distinct `best_rep` endpoints among the 49 solves: **16**.

## Cap confound (must-address #3)

19/60 rows run at `treat_cap` > 24 (shipped controls use 24).
None of the novel-vs-union rows is among the elevated-cap set
(all novel run at cap 24) — so the +classes claim is not a cap
artifact, but raw 49-vs-29 comparisons still need this stated.

## Beam vs best-first (must-address #4)

The K=4 rung-local beam tied the global best-first nonsym climb
at the same 49-row solve set (prior `covbeam_nonsym_b1kfull`).
K was selected in-sample over 7 values on these 60 rows — do not
claim the beam *caused* the gain over best-first; report the tie.

## Naming note (must-address #5)

`stopped_reason == "closed"` means *this beam generation produced
no Aut-min orbit outside the global visited set* — **not** closure
of the μ-ball (rung-local beam lesson).

Wall 16.0s. Path certs: `covbeam_nonsym_beam_k4_b1k_pathcerts.jsonl`.
