# AC-SolverX — what a session needs to know before touching the search

Four settled facts. The code on this branch reflects the first two; the third
is about modules that live on other branches. Read this file before trusting a
docstring found elsewhere.

## 1. The best heuristic is `S20_MK2`

```
priority(r1, r2) = L + 20*S + 2*MK
```

`S` = smaller mean block (mean run length of the thinner generator), `MK` = max
knots over the two relators, `L` = total length. Lower pops first. `S20_MK2` is
the **recommended** heap ordering — where a default is needed, this is it.

Provenance, stated as a pair — a number without both halves is not readable:
*selected on* the ac1m_hard_aut train 120 (54/120, against the length control's
0/120); *evaluated on* an automorphism-disjoint fresh holdout (27/60, against
the length control's 0/60). On the 60-row ladder at budget 10,000 it solves
52/60 against the plain greedy's 40/60 — McNemar 12-0, a strict superset, gains
concentrated in bins 6-9. Cap caveat: those runs used `mrl=48` while the frozen
greedy column is `mrl=24`, so read the delta in solves as primary and the node
ratios as indicative.

Note the tuning grid's own top scorer, `S28_MK2_F8` (57/120), is **not** the
keeper: it falls to 22/60 on that fresh holdout. Taking the training-set maximum
would repeat the mistake described next.

## 2. `RECOMMENDED` is overfit and is NOT production

```
L + 2.53*K + 6.418*MK + 8.458*S + 3.292*xyimb        <- do not use as default
```

It was selected on a slice containing fourteen of the twenty rows it was then
validated against, and its 60-row campaign used subset-60 as its own row list.
So every margin ever published for it -- 10/20 -> 15/20, the 60-row cost tables
-- is largely in-sample: a statement about the tuner, not about the ordering.

This branch ships `S20_MK2` instead. Both the name `RECOMMENDED` and the
withdrawn weight map are guarded against returning by
`tests/test_greedy_heuristic.py::test_module_ships_no_overfit_weight_vector`.

The runs `RECOMMENDED` produced are real and should be kept as the record of
what that campaign cost (the `heur_*` columns of the arms tables); it is the
recommendation that is withdrawn, not the data.

## 3. The μ-ladder is NOT production

It does not appear on this branch at all. On the research branches
(`research/w5/*`, `cursor/*`, `experiments/ppo`) `AGENTS.md` describes it as the
active line — that framing is stale. Its modules and results stay as records.

## 4. The census

| step | count |
|---|---|
| Miller–Schupp presentations | **1,190** |
| solved | **640** |
| unsolved | **550** |
| A-equivalent reps among the 550 | **261** |
| after automorphisms and AC moves | **124** |

State it once, from here. Two precisions worth carrying: 124 is an **upper
bound** from a bounded AC-move search (caps 30–36, unanimous across five arms,
not proven converged), and the exact `Aut(F₂)` step between 261 and 124 is
**168** — no change of variables does better than 168. Derivation and the
machine-checked merges are in `results/equivalence_classes/EQUIVALENCE_FINDING.md`
on the research branches; `docs/BRANCH_MAP.md` says which branch holds what.
