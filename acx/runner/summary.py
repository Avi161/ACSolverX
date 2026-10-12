"""``summary.json``: counts, costs and path lengths over a run's records."""
import statistics

from .caps import caps_block

COST_UNIT = {"hybrid": "units", "rl": "evaluations"}      # every other method counts pops


def describe(values):
    """``n``, ``sum``, ``mean``, ``median`` and ``max`` of the values that are not None (None if there are none)."""
    values = [v for v in values if v is not None]
    if not values:
        return None
    return dict(n=len(values), sum=sum(values), mean=round(statistics.fmean(values), 2),
                median=statistics.median(values), max=max(values))


def summarize(cfg, records, wall):
    """The ``summary.json`` dict of a run's ``records`` (one per row)."""
    solved = [r for r in records if r["solved"]]
    groups = {
        "ac_path": [r for r in solved if r["kind"] == "ac_path" and not r["aut_assisted"]],
        "aut_assisted": [r for r in solved if r["aut_assisted"]],
        "stable_cert": [r for r in solved if r["kind"] == "stable_cert"],
    }
    path_length = {
        kind: dict(sub_moves=describe(r["sub_moves"] for r in group),
                   elem_moves=describe(r["elem_moves"] for r in group))
        for kind, group in groups.items() if group
    }
    return dict(
        name=cfg["name"], method=cfg["method"], benchmark=cfg["benchmark"], rows=len(records), solved=len(solved),
        **{kind: len(group) for kind, group in groups.items()},
        skipped=sum(1 for r in records if r.get("skipped")),
        errors=sum(1 for r in records if r.get("error")),
        cost=dict(unit=COST_UNIT.get(cfg["method"], "pops"), total=sum(r["cost"] for r in records),
                  on_solved=sum(r["cost"] for r in solved)),
        path_length=path_length,
        caps=caps_block(records),
        wall_seconds=round(wall, 2), row_seconds=round(sum(r["seconds"] for r in records), 2), config=cfg)
