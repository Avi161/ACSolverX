# Results and learnings — the index

## What this is

The collection branch's record of what the summer's research established, gathered from
twenty-odd branches into one place. The collection rule: **code and markdown only** — no
run JSONLs, no result CSV dumps, no checkpoints. Every raw artifact stays on the branch
that produced it, and [`BRANCH_MAP.md`](BRANCH_MAP.md) says exactly where; every number
quoted here names its denominator, its budget, and its *selected-on / evaluated-on* pair.

## The census

Stated once, in [`benchmark/README.md`](../benchmark/README.md#the-census-these-rows-sit-inside)
(and mirrored for sessions in [`CLAUDE.md`](../CLAUDE.md)). Nothing in `docs/` restates it —
point there.

## Index

| file | what it holds | status |
|---|---|---|
| [`results/heuristic-search.md`](results/heuristic-search.md) | `S20_MK2`, its selection/holdout provenance, and every scale it was validated at | measured |
| [`results/ppo-pytorch.md`](results/ppo-pytorch.md) | the PyTorch PPO reproduction and the shaped-reward A/B design | built + verified, **not yet run** |
| [`results/benchmarks.md`](results/benchmarks.md) | the subset ladder, the 640-row baseline reference, rows-vs-orbits, and the aut-min tier | measured |
| [`results/speedups.md`](results/speedups.md) | every wall-clock / memory / node-efficiency claim, with its conditions | measured |
| [`results/stable-ac-learnings.md`](results/stable-ac-learnings.md) | the stable-AC program's nulls, refutations, and retractions | closed directions |
| [`BRANCH_MAP.md`](BRANCH_MAP.md) | what every branch was for, what came here, and how to retrieve the rest | reference |

## How to read a number in these files

- **Rows are not orbits.** The 60-row ladder is 45 `Aut(F₂)` orbits; headline results are
  quoted per-row unless marked otherwise. [`results/benchmarks.md`](results/benchmarks.md)
  carries the mapping.
- **Budget and cap travel with the number.** A solve count without its node budget and
  `max_relator_length` (`mrl`) is not comparable to anything; where two arms ran at
  different caps, the doc says so and demotes node ratios to indicative.
- **A benchmark an ordering was fitted on cannot validate it.** That is the lesson of the
  withdrawn `RECOMMENDED` vector, and it is why every `S20_MK2` claim states where it was
  selected and where it was evaluated.

## What is deliberately absent

- **Proofs.** The stable-AC proof program (`codex/proofs` and relatives) stays on its
  branches; [`results/stable-ac-learnings.md`](results/stable-ac-learnings.md) records
  only conclusions.
- **Raw run artifacts** — the ~480 MB of JSONL/CSV/log output on the research branches.
- **Checkpoints** beyond the `ppo_checkpoints/610model` already shipped on main.
- **The campaign Colab notebooks** (~25 `hsearch_colab_*.ipynb`) — they drive research-only
  code with hard-coded Drive paths; see the note in [`BRANCH_MAP.md`](BRANCH_MAP.md).
