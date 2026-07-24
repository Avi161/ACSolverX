"""EXP-11 -- the depth axis, which the earlier rounds ruled out on principle instead of measuring.

The brief asked for an ordering "dynamic according to depth and length". Length became the
segment boundary; **depth was excluded by argument** -- the priority was required to be a pure
function of the state, because the visited set keeps a state's first discovery with no
decrease-key, so a depth term makes a state's key depend on the route that found it.

That argument is real but it is not a reason to skip the measurement. It describes exactly the
bargain weighted A* makes: ``g`` (depth, path-dependent) plus ``h`` (structure, state-dependent),
inadmissible, still perfectly deterministic. Whether it *helps* is an empirical question, and the
earlier rounds answered it with a principle. This answers it with data.

Three placements, because they mean different things:

- ``all`` -- depth added in every segment. Pure weighted A*: a positive weight prefers shallow
  states (breadth-first-ish, conservative), a negative one prefers deep states (dive-first).
- ``long`` -- depth only in the structural segment, so the climb is depth-aware while the endgame
  stays pure length. If the climb is where wandering costs most, this is where a ``g`` term should
  pay.
- ``short`` -- depth only in the endgame segment; the control on placement.

Swept over the orderings that already won, at both budgets, so a gain has to beat a strong
incumbent rather than the length baseline.

    python3 -m experiments.heuristic_search.exp11_depth
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.heuristic_search.hlab import (                    # noqa: E402
    BASELINE_CONFIG, LOGS, cfg_name,
)
from experiments.heuristic_search.lab import evaluate, rank, read, score  # noqa: E402
from experiments.heuristic_search.perbin import decidable          # noqa: E402

MRL = 48
SLICE = "train"
DEPTHS = (-2.0, -1.0, -0.5, -0.25, 0.25, 0.5, 1.0, 2.0, 4.0)
OUT = os.path.join(LOGS, "EXP11_depth.jsonl")

# The incumbents. Each is a (name, segments) pair; depth is injected into a copy.
BASES = {
    "length": [{"upto": None, "w": {"L": 1.0}}],
    "phasedK8": [{"upto": 16, "w": {"L": 1.0}}, {"upto": None, "w": {"L": 1.0, "K": 8.0}}],
    "win500": [{"upto": 16, "w": {"L": 1.0}},
               {"upto": None, "w": {"L": 1.0, "K": 8.936, "xyimb": -5.978}}],
    "win1000": [{"upto": 16, "w": {"L": 1.0}},
                {"upto": None, "w": {"L": 1.0, "K": 2.53, "MK": 6.418, "S": 8.458,
                                     "xyimb": 3.292}}],
}


def with_depth(segs, w, where):
    """A copy of ``segs`` carrying depth weight ``w`` in the chosen segments."""
    out = []
    last = len(segs) - 1
    for i, s in enumerate(segs):
        c = {"upto": s["upto"], "w": dict(s["w"])}
        is_long = (i == last)
        if where == "all" or (where == "long" and is_long) or (where == "short" and not is_long):
            c["depth"] = w
        out.append(c)
    return {"segments": out}


def configs():
    out, meta = [], {}
    for base, segs in BASES.items():
        plain = {"segments": [dict(s) for s in segs]}
        cid = cfg_name(plain)
        if cid not in meta:
            out.append(plain)
            meta[cid] = {"base": base, "depth": 0.0, "where": "none"}
        places = ("all",) if len(segs) == 1 else ("all", "long", "short")
        for where in places:
            for w in DEPTHS:
                c = with_depth(segs, w, where)
                # cfg_name does not render the depth term, so two placements can collide on id;
                # keep the first and let the meta record which one it was.
                cid = cfg_name(c) + f"|d{w:g}@{where}"
                if cid in meta:
                    continue
                out.append(c)
                meta[cid] = {"base": base, "depth": w, "where": where}
    return out, meta


def main():
    # cfg_name ignores the depth term, so the harness would treat every depth arm of one base as
    # the same config and resume over them. Run each arm under an explicit id instead.
    from experiments.heuristic_search.hfast import search_fast
    from experiments.heuristic_search.hlab import load_split
    rows = load_split(SLICE)

    done = set()
    if os.path.exists(OUT):
        for line in open(OUT):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            done.add((r["config_id"], r["name"], r["budget"]))

    cfgs, meta = configs()
    ids = list(meta)
    with open(OUT, "a") as f:
        for budget in (500, 1000):
            for cid, cfg in zip(ids, cfgs):
                for row in rows:
                    if (cid, row["name"], budget) in done:
                        continue
                    res = search_fast(row["r1"], row["r2"], budget, cfg, MRL)
                    f.write(json.dumps({
                        "config_id": cid, "name": row["name"], "budget": budget, "mrl": MRL,
                        "base": meta[cid]["base"], "depth": meta[cid]["depth"],
                        "where": meta[cid]["where"],
                        "solved": res["solved"], "nodes": res["nodes"],
                        "path_length": res["path_length"], "min_total": res["min_total"],
                        "max_pop": res["max_pop"], "start_K": res["start_K"],
                        "min_K": res["min_K"], "min_K_len": res["min_K_len"],
                        "source": row["source"]}) + "\n")
                    f.flush()
                    os.fsync(f.fileno())

    data = [json.loads(l) for l in open(OUT)]
    lines = ["# EXP-11 — does a depth term help? (the axis the earlier rounds argued away)", "",
             "A segment may carry `depth: w`, adding `w · depth` to its score — the `g` of a "
             "weighted A*, with the structural features as `h`. Positive prefers **shallow** "
             "states, negative prefers **deep** ones. Swept over the orderings that already won, "
             "so a gain must beat a strong incumbent, not the length baseline.", "",
             "`all` = depth in every segment · `long` = only the structural climb · `short` = only "
             "the endgame (the placement control).", ""]

    for budget in (500, 1000):
        lines += [f"## Budget {budget}", "",
                  "| base | placement | " + " | ".join(f"d={d:g}" for d in DEPTHS) + " | d=0 |",
                  "|---" * (len(DEPTHS) + 3) + "|"]
        for base in BASES:
            zero = [r for r in data
                    if r["base"] == base and r["depth"] == 0.0 and r["budget"] == budget]
            z = sum(r["solved"] for r in zero)
            for where in ("all", "long", "short"):
                cells = []
                any_cell = False
                for d in DEPTHS:
                    sub = [r for r in data if r["base"] == base and r["depth"] == d
                           and r["where"] == where and r["budget"] == budget]
                    if not sub:
                        cells.append("—")
                        continue
                    any_cell = True
                    s = sum(r["solved"] for r in sub)
                    cells.append(f"**{s}**" if s > z else str(s))
                if any_cell:
                    lines.append(f"| {base} | {where} | " + " | ".join(cells) + f" | {z} |")
        lines.append("")

    # The verdict: did any depth arm beat its own zero-depth incumbent?
    wins = []
    for budget in (500, 1000):
        for base in BASES:
            z = sum(r["solved"] for r in data
                    if r["base"] == base and r["depth"] == 0.0 and r["budget"] == budget)
            for where in ("all", "long", "short"):
                for d in DEPTHS:
                    sub = [r for r in data if r["base"] == base and r["depth"] == d
                           and r["where"] == where and r["budget"] == budget]
                    if sub and sum(r["solved"] for r in sub) > z:
                        wins.append((budget, base, where, d,
                                     sum(r["solved"] for r in sub), z))
    lines += ["## Verdict", ""]
    if wins:
        lines += [f"{len(wins)} depth arms beat their own zero-depth incumbent:", ""]
        for b, base, where, d, s, z in sorted(wins, key=lambda t: -(t[4] - t[5]))[:12]:
            lines.append(f"- budget {b}, `{base}` + depth {d:g} @{where}: **{s}/40** vs {z}/40")
        lines += ["", "A single arm beating its incumbent on 40 rows is within the noise of a "
                  f"{len(DEPTHS) * 3 * len(BASES) * 2}-arm sweep; treat a gain as real only if it "
                  "repeats at both budgets and in the same placement.", ""]
    else:
        lines += ["**No depth arm beat its zero-depth incumbent, at either budget, in any "
                  "placement.** The earlier decision to exclude depth was right — but it is now a "
                  "measurement rather than an argument from the data structure.", ""]

    with open(os.path.join(LOGS, "EXP11_depth.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
