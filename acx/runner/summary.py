"""``summary.json``: counts, costs and path lengths over a run's records."""
import statistics

from .caps import caps_block
from .config import run_config

COST_UNIT = {"hybrid": "units", "rl": "evaluations"}      # every other method counts pops


def describe(values):
    """``n``, ``sum``, ``mean``, ``median`` and ``max`` of the values that are not None (None if there are none)."""
    values = [v for v in values if v is not None]
    if not values:
        return None
    return dict(n=len(values), sum=sum(values), mean=round(statistics.fmean(values), 2),
                median=statistics.median(values), max=max(values))


def summarize(cfg, records, wall):
    """The ``summary.json`` dict of a run's ``records`` (one per row), read as stored.

    A key that ``fields`` dropped leaves its entries empty (no ``kind``: every kind reads 0). ``cost_mean`` and
    ``cost_median`` are per row over all rows, so ``cost_mean * rows`` is ``cost.total`` up to rounding;
    ``cpu_seconds`` is the rows' CPU time, replay and decoding included (nothing of either with ``path = false``), and
    ``us_per_cost`` is its microseconds per pop, unit or evaluation; both are None when no record has ``cpu_seconds``.
    """
    solved = [r for r in records if r["solved"]]
    groups = {
        "ac_path": [r for r in solved if r.get("kind") == "ac_path" and not r.get("aut_assisted")],
        "aut_assisted": [r for r in solved if r.get("aut_assisted")],
        "stable_cert": [r for r in solved if r.get("kind") == "stable_cert"],
    }
    path_length = {
        kind: dict(sub_moves=describe(r.get("sub_moves") for r in group),
                   elem_moves=describe(r.get("elem_moves") for r in group))
        for kind, group in groups.items() if group
    }
    unit = COST_UNIT.get(cfg["method"], "pops")
    cost = describe(r.get("cost") for r in records) or {}
    timed = [r["cpu_seconds"] for r in records if "cpu_seconds" in r]       # none when ``fields`` leaves it out
    cpu = sum(timed)
    return dict(
        name=cfg["name"], method=cfg["method"], benchmark=cfg["benchmark"], rows=len(records), solved=len(solved),
        **{kind: len(group) for kind, group in groups.items()},
        skipped=sum(1 for r in records if r.get("skipped")),
        errors=sum(1 for r in records if r.get("error")),
        cost=dict(unit=unit, total=cost.get("sum", 0), on_solved=sum(r.get("cost", 0) for r in solved)),
        cost_unit=unit, cost_mean=cost.get("mean"), cost_median=cost.get("median"),
        path_length=path_length,
        caps=caps_block(records),
        wall_seconds=round(wall, 2), row_seconds=round(sum(r.get("seconds", 0) for r in records), 2),
        cpu_seconds=round(cpu, 3) if timed else None,
        us_per_cost=round(1e6 * cpu / cost["sum"], 3) if timed and cost.get("sum") else None,
        config=run_config(cfg))
