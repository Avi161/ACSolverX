"""The comparison table: the numbers of each run (``measure``), the notes on what they cover, and the markdown."""
import statistics

UNITS_NOTE = ("Units differ: a pop is one heap pop of a search; a hybrid unit also counts accepted automorphisms, "
              "image evaluations and substitution moves, so it is not a pop; an RL evaluation is one network "
              "evaluation. Compare cost and CPU per pop/unit only between runs counted in the same unit.")
HEADER = ("run", "method", "benchmark", "rows", "solved", "mean cost (solved)", "median cost (solved)",
          "mean sub_moves", "mean elem_moves", "CPU s/row", "CPU µs per pop/unit", "raise-cap rows", "errors")


# ---- numbers -------------------------------------------------------------------------------------------------

def mean(values):
    return sum(values) / len(values) if values else None


def percent(part, whole):
    """``part`` of ``whole`` in percent, to one decimal; never 0 or 100 unless it is exactly that."""
    value = round(100 * part / whole, 1)
    if part and not value:
        return 0.1
    return 99.9 if part < whole and value == 100 else value


def column(records, key):
    """The values of ``key`` that the records have (a missing or null value is skipped)."""
    return [r[key] for r in records if r.get(key) is not None]


def measure(run, ids=None):
    """The numbers of a run's table row. ``ids`` limits the cost, move and CPU means to those rows (``--common``)."""
    if run.records is None:
        return measure_summary(run.summary)
    scope = [r for r in run.records if ids is None or r["id"] in ids]
    solved = [r for r in scope if r["solved"]]
    cost, sub, elem = (column(solved, key) for key in ("cost", "sub_moves", "elem_moves"))
    # A row's CPU seconds; a run older than ``cpu_seconds`` has only the wall-clock ``seconds``.
    cpu = [s for s in (r.get("cpu_seconds", r.get("seconds")) for r in scope) if s is not None]
    total_cost = sum(column(scope, "cost"))
    return {
        "rows": len(run.records),
        "solved": sum(1 for r in run.records if r["solved"]),
        "errors": sum(1 for r in run.records if r.get("error")),
        "raise_rows": sum(1 for r in run.records if any(v for k, v in r.items() if k.endswith("_would_pop"))),
        "n": len(solved), "cost": mean(cost), "median": statistics.median(cost) if cost else None,
        "sub": mean(sub), "sub_n": len(sub), "elem": mean(elem), "elem_n": len(elem),
        "cpu_row": mean(cpu), "us": 1e6 * sum(cpu) / total_cost if cpu and total_cost else None,
        "wall": any("cpu_seconds" not in r for r in scope),          # seconds stands in for cpu_seconds
    }


def measure_summary(s):
    """The numbers of a table row from a ``summary.json`` alone: no median, and no CPU in a summary without it."""
    def path_mean(key):
        parts = [lengths[key] for lengths in s["path_length"].values() if lengths[key]]
        n = sum(part["n"] for part in parts)
        return (sum(part["sum"] for part in parts) / n if n else None), n

    (sub, sub_n), (elem, elem_n) = path_mean("sub_moves"), path_mean("elem_moves")
    raise_count = raise_rows(s["caps"].values())
    cpu, rows, solved = s.get("cpu_seconds"), s["rows"], s["solved"]
    return {"rows": rows, "solved": solved, "errors": s["errors"], "raise_rows": raise_count, "n": solved,
            "cost": s["cost"]["on_solved"] / solved if solved else None, "median": None,
            "sub": sub, "sub_n": sub_n, "elem": elem, "elem_n": elem_n,
            "cpu_row": cpu / rows if cpu is not None and rows else None, "us": s.get("us_per_cost"), "wall": False}


def raise_rows(blocks):
    """The rows where some counter would pop, from ``summary.json``'s ``caps`` blocks. Each block keeps at most 100 ids.
    With every list complete the count is exact; with a cut list it is a lower bound: the larger of the pooled kept ids
    and the biggest ``rows_would_pop`` (exact when one counter binds)."""
    binding = [block for block in blocks if block["rows_would_pop"]]
    kept = len(set().union(*(block["raise_ids"] for block in binding)))
    if all(len(block["raise_ids"]) == block["rows_would_pop"] for block in binding):
        return kept
    return max(kept, *(block["rows_would_pop"] for block in binding))


def solved_ids(run):
    return {r["id"] for r in run.records if r["solved"]}


def common_ids(runs):
    """The ids of the rows every run solved; row ids only match across runs of one benchmark."""
    benchmarks = sorted({run.benchmark for run in runs})
    if len(benchmarks) > 1:
        raise SystemExit(f"--common needs runs on one benchmark, got {benchmarks}")
    for run in runs:
        if run.records is None:
            raise SystemExit(f"--common needs paths.jsonl: {run.name} has only summary.json")
    return set.intersection(*(solved_ids(run) for run in runs))


def rows_of(n):
    return f"{n} row{'' if n == 1 else 's'}"


def head_to_head(a, b):
    """The rows two runs solved, by only a, only b, both or neither, over the rows both ran."""
    shared = {r["id"] for r in a.records} & {r["id"] for r in b.records}
    by_a, by_b = solved_ids(a) & shared, solved_ids(b) & shared
    return (f"Head to head on {a.benchmark} ({rows_of(len(shared))} in common): solved by {a.name} only "
            f"{len(by_a - by_b)}, by {b.name} only {len(by_b - by_a)}, by both {len(by_a & by_b)}, "
            f"by neither {len(shared - by_a - by_b)}.")


# ---- the table -----------------------------------------------------------------------------------------------

def fmt(value, digits=1, suffix=""):
    """``value`` with thousands separators and a suffix; ``-`` when there is none."""
    return "-" if value is None else f"{value:,.{digits}f}{suffix}"


def count_note(m, key):
    """`` (n=k)`` when a mean covers only k of the solved rows (a CoV stable certificate has no elementary path)."""
    return f" (n={m[key + '_n']})" if m[key + "_n"] not in (0, m["n"]) else ""


def cells(run, m):
    """The formatted cells of a run's table row, in the order of ``HEADER``."""
    unit, star = run.unit, "*" if m["wall"] else ""
    solved = f"{m['solved']} ({percent(m['solved'], m['rows']):.1f}%)" if m["rows"] else "0 (-)"
    return [run.name, run.method, run.benchmark, m["rows"], solved,
            fmt(m["cost"], suffix=f" {unit}"), fmt(m["median"], suffix=f" {unit}"),
            fmt(m["sub"]) + count_note(m, "sub"), fmt(m["elem"]) + count_note(m, "elem"),
            fmt(m["cpu_row"], 3, star), fmt(m["us"], 1, f"/{unit.removesuffix('s')}{star}"),
            m["raise_rows"], m["errors"]]


def notes(runs, measured, ids):
    """The lines that say what the table covers: its scope, wall-clock CPU, raise-cap rows, head to head."""
    if ids is None:
        lines = ["Cost and move columns average each run's solved rows; CPU columns cover all of its rows."]
    else:
        lines = [f"--common: cost, move and CPU columns cover only the {rows_of(len(ids))} every run solved."]
    if any(m["wall"] and m["cpu_row"] is not None for m in measured):
        lines.append("Starred (*) CPU values are wall-clock seconds, not CPU: the run has no cpu_seconds, and a "
                     "busy machine inflates them.")
    if any(run.records is None for run in runs):
        lines.append("Runs without paths.jsonl are read from summary.json: no median, and no CPU in a shipped one.")
    if any(m["raise_rows"] for m in measured):
        lines.append("raise-cap rows: rows where a relator cap dropped a state the search would have popped "
                     "(a larger cap changes that row's search).")
    if len(runs) == 2 and runs[0].benchmark == runs[1].benchmark and None not in (runs[0].records, runs[1].records):
        lines.append(head_to_head(*runs))
    return lines


def tabulate(runs, common):
    """Each run's table numbers and the notes on what they cover; the one step the markdown and the page share."""
    ids = common_ids(runs) if common else None
    measured = [measure(run, ids) for run in runs]
    return measured, notes(runs, measured, ids)


def markdown(runs, common=False):
    """``runs`` as one markdown table followed by the notes on what its numbers cover."""
    measured, lines = tabulate(runs, common)
    if len({run.unit for run in runs}) > 1:
        lines.append(UNITS_NOTE)
    rule = ["---"] * 3 + ["---:"] * (len(HEADER) - 3)
    table = [HEADER, rule] + [cells(run, m) for run, m in zip(runs, measured, strict=True)]
    rows = ["| " + " | ".join(str(cell).replace("|", "\\|") for cell in row) + " |" for row in table]
    return "\n".join(rows + [""] + [f"- {line}" for line in lines])
