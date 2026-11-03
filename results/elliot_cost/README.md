# Time-weighted cost of ACSolverES Dual / Triple GS

`nodes` (in `../elliot_10k`, `../elliot_100k`) counts every pop as 1, whatever kind it is. So a CoV pop counts the same
as a substitution pop, and three kinds of CoV work are free:

- seeding the start state;
- generating CoV candidates;
- the triple's empty complete-CoV pops.

This folder charges for that work.

```bash
python benchmark/elliot/time_cost.py --out results/elliot_cost --workers 2
python benchmark/elliot/time_cost.py --summarize results/elliot_cost --md results/elliot_cost/COST_TABLE.md
```

## Method

**Where the CoV work happens.** ACSolverES's C++ engine makes every CoV child through a Python callback: the
`expander` of `run_compact_dual_gs`, and `auto` / `complete` of `run_compact_triple_gs`. `time_cost.py` wraps those
callbacks with a CPU timer, without changing ACSolverES. The search results are unchanged: nodes and paths equal
`../elliot_100k`.

**What is measured per row:**

| quantity | how it is computed |
|---|---|
| `cpu_s` | total CPU time |
| `callback_s` | CPU time inside the CoV callbacks, split by kind (`single` / `auto` / `complete`) and phase (`seed` / `pop`) |
| `engine_s` | `cpu_s - callback_s`, the C++ search |

**Unit.** One substitution pop costs `t_pop = sum(engine_s) / sum(nodes)`, pooled over a benchmark and method; it is
about 0.2 ms. A row's cost is

    cost units = nodes + callback_s / t_pop

that is, the CoV work converted into substitution pops. A substitution pop does the work of one LENGTH expansion
(same S-move children, priority = total length), so cost units are LENGTH-expansion units algorithmically. The seconds
are not comparable with acx's Python timings, because this is a C++ engine.

## Result (`COST_TABLE.md`)

How much one CoV step costs, in substitution pops:

| | seeding the start | one CoV pop |
|---|---:|---:|
| single CoV | 23–34 | 25–28 |
| auto CoV (24 images) | 4–5 | 5–6 |
| triple | 6 | 7–11 |

For the triple, each complete-CoV callback is included in the per-pop average, the free empty pops too.

Overall cost / nodes:

| method | MS640 | bench60 | ladder100 |
|---|---:|---:|---:|
| Dual, single CoV | 1.42 | 1.35 | 2.01 |
| Dual, auto CoV | 1.03 | 1.02 | 1.14 |
| Triple | 1.11 | 1.07 | 1.16 |

Solved within a budget counted in nodes, and in cost units:

| benchmark | method | nodes <= 1e3 / 1e4 / 1e5 | cost <= 1e3 / 1e4 / 1e5 |
|---|---|---|---|
| MS640 | Dual, single CoV | 604 / 627 / 640 | 593 / 621 / 640 |
| MS640 | Dual, auto CoV | 618 / 634 / 640 | 614 / 634 / 640 |
| MS640 | Triple | 618 / 634 / 640 | 612 / 634 / 640 |
| bench60 | Dual, single CoV | 46 / 52 / 60 | 43 / 52 / 60 |
| bench60 | Dual, auto CoV | 51 / 56 / 60 | 51 / 56 / 60 |
| bench60 | Triple | 51 / 56 / 60 | 49 / 56 / 60 |
| ladder100 | Dual, single CoV | 64 / 92 / 100 | 56 / 82 / 100 |
| ladder100 | Dual, auto CoV | 80 / 97 / 100 | 77 / 96 / 100 |
| ladder100 | Triple | 86 / 97 / 100 | 81 / 97 / 100 |

- **Auto dual and triple:** charging the CoV work changes little, at most 5 rows lower at 10^3 and 1 at 10^4.
- **Single-CoV dual:** each single-CoV pop costs about 25 substitution pops, because the candidates are enumerated in
  Python. On ladder100 that doubles its cost and drops it to 56 / 82 rows at 10^3 / 10^4. Its hardest row
  (`ac19_70845`) costs 61,821 units.
- **Every row is still solved within 10^5 cost units** by all three methods.

## Caveats

- **Timing noise.** The run used 2 workers on a 4-core machine. CPU time per row is honest, but `t_pop` and the ratios
  are about ±10%.
- **Small rows.** On rows with a handful of nodes, the cost is mostly the seeding.
- **What is not charged.** Python glue outside the callbacks (the adapters, about microseconds a row) is counted as
  engine time.

## Fields (`<bench>__<algo>.jsonl`)

`nodes`, `pops` {`sub`, `single`, `auto`, `complete`}, `cpu_s`, `wall_s`, `callback_s`, `engine_s`, and `callbacks`
{`<kind>_<seed|pop>`: {`calls`, `s`}}.
