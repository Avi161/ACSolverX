"""Per-bin scoring, so no report can hide a gain inside the saturated easy rows.

The headline number ``23/40`` is a lie of omission. Sixteen of the forty train rows sit in
difficulty bins 0-3, which the baseline *already* solves (16/16), so every ordering scores at
least 16 there and the four bins carry no information. A feature that solved nothing new would
still read 16/40, and a feature that added six real solves reads 23/40 -- the same denominator
hides both the floor and the signal.

The honest denominator is the **decidable subset**: the rows some ordering solves and some does
not, at this budget. On the train slice that is bins 4-9 (plus any reach row, though none solve),
24 rows, and there the baseline is 1/24. The same six-solve gain that looked like a 15% relative
improvement on 40 is a 6x improvement on the rows that were ever in question.

``bin`` is the baseline's difficulty grade (its ``nodes_1M`` bucket), so it is measured under
length ordering. A knot ordering reorders difficulty -- it cracks a bin-7 row while missing an
"easier" bin-6 one -- so ``bin`` is the axis to report *against*, never the thing to optimise
toward. It is ground truth for "how hard was this for the baseline", not for the new heuristic.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.heuristic_search.hlab import bench66              # noqa: E402

_META = {r["name"]: r for r in bench66()}


def bin_of(name):
    b = _META[name].get("bin")
    return int(b) if b not in (None, "") else "reach"


def decidable(res_by_config):
    """Names that at least one config solves and at least one does not -- the informative rows.

    A row every config solves is floor; a row no config solves is (at this budget) undecidable.
    Neither separates two orderings, so both are excluded from the honest denominator.
    """
    names = set()
    for v in res_by_config.values():
        names |= set(v)
    dec = []
    for nm in names:
        outs = [v[nm]["solved"] for v in res_by_config.values() if nm in v]
        if outs_mixed(outs):
            dec.append(nm)
    return sorted(dec)


def outs_mixed(outs):
    return any(outs) and not all(outs)


def per_bin_counts(res_one, names=None):
    """{bin: (solved, total)} for one config's rows, optionally restricted to ``names``."""
    out = {}
    for nm, row in res_one.items():
        if names is not None and nm not in names:
            continue
        b = bin_of(nm)
        s, t = out.get(b, (0, 0))
        out[b] = (s + (1 if row["solved"] else 0), t + 1)
    return out


def decidable_line(res_by_config, cid, ctrl_id):
    """A one-line 'X/D decidable (baseline Y/D)' summary for config ``cid``."""
    dec = set(decidable(res_by_config))
    c = sum(1 for nm in dec if nm in res_by_config[cid] and res_by_config[cid][nm]["solved"])
    b = sum(1 for nm in dec if nm in res_by_config[ctrl_id] and res_by_config[ctrl_id][nm]["solved"])
    return c, b, len(dec)


def bin_table(res_by_config, cids, ctrl_id):
    """Markdown: one row per config, one column per bin, restricted to nothing (shows the floor too).

    The floor columns are kept visible on purpose -- the point of the table is to show *where* a
    gain lands, and a reader has to see bins 0-3 saturate to trust that the gain is in 4-9.
    """
    bins = sorted({bin_of(nm) for v in res_by_config.values() for nm in v},
                  key=lambda b: (b == "reach", b))
    head = "| config | " + " | ".join(f"bin {b}" for b in bins) + " | decidable |"
    sep = "|---" * (len(bins) + 2) + "|"
    lines = [head, sep]
    for cid in cids:
        pc = per_bin_counts(res_by_config[cid])
        cells = []
        for b in bins:
            s, t = pc.get(b, (0, 0))
            cells.append(f"{s}/{t}" if t else "—")
        c, bl, d = decidable_line(res_by_config, cid, ctrl_id)
        tag = " ← ctrl" if cid == ctrl_id else ""
        lines.append(f"| `{cid[:34]}`{tag} | " + " | ".join(cells) + f" | **{c}/{d}** |")
    return "\n".join(lines)
