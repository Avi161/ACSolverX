"""The replication table, built from beam jsonls and nothing else.

The paper's number is "how many of the 1190 Miller-Schupp presentations does a
beam decode of the trained policy solve", averaged over 5 seeds. Two numbers in
this repo look like that number and are not:

- **`num_solved` from training.** The env logs a solve the moment a rollout hits
  a trivial state, over whatever dataset it is training on -- 156,762 rows for
  the AC-19 arm. It is a training signal, not an evaluation, and it counts a
  different denominator.
- **A beam run over a different evaluation file.** Only `1190MS` carries the
  paper's denominator.

So this module reads `beam-*.jsonl` only, keeps only rows whose filename says
the evaluation set was `eval_stem`, and refuses anything else. The filename is
the identity (see `run_ppo.beam_tag`) -- that is what makes the scan possible
and what makes two seeds land in two files.
"""

import glob
import json
import os
import re
from collections import defaultdict

from experiments.ppo import acs_data

# `beam-{ckpt_tag}-{eval}-w{W}-t{T}-L{L}[-a{alpha}][-T{t0}_{t1}-s{seed}]`
# The checkpoint tag itself contains dashes, so anchor on the fixed suffix.
_NAME = re.compile(
    r"^beam-(?P<ckpt>.+)-(?P<eval>[^-]+)-w(?P<width>\d+)-t(?P<steps>\d+)-L(?P<L>\d+)"
    r"(?:-a(?P<alpha>[0-9.eE+-]+))?"
    r"(?:-T(?P<t0>[0-9.eE+-]+)_(?P<t1>[0-9.eE+-]+)-s(?P<seed>\d+))?$")
_TRAINED = re.compile(r"^ppo-drt-(?P<arm>.+)-s(?P<seed>\d+)-u(?P<update>\d+)$")

ARM_LABEL = {
    "1190MS": "PPO-SUB-DRT",
    "AC19_extended": "PPO-SUB-DRT + AC-19",
    # Not a paper row: `AC19.txt` pins nothing (`ms_prefix_length` is 0) and
    # shares only 171 of the 1190 MS presentations, none of them at its head.
    "AC19": "PPO-SUB-DRT + AC-19 (raw AC19.txt -- NOT the paper's arm)",
}

# Published in the Two-Hump paper, over the same 1190 denominator. Reference
# only: nothing here is measured by this repo.
PAPER_PPO = [
    ("PPO-AC-RESNET", 457.0, None, None),
    ("PPO-SUB-CANON", 562.6, 557, 567),
    ("PPO-SUB-CANON + AC-19", 575.5, 572, 579),
    ("PPO-SUB-DRT", 588.2, 585, 591),
    ("PPO-SUB-DRT + AC-1M", 605.4, 600, 610),
    ("PPO-SUB-DRT + AC-19", 607.2, 605, 610),
]
PAPER_GREEDY = [
    ("GS-AC (1M)", 533),
    ("GS-SUB (614)", 533),
    ("GS-SUB (10K) NODES", 604),
    ("GS-SUB (100K) NODES", 634),
    ("GS-SUB (1M) NODES", 640),
    ("GS-SUB (10M) NODES", 640),
]


def parse_name(stem):
    """Beam-jsonl stem -> the run's identity, or None if it is not one."""
    m = _NAME.match(stem)
    if not m:
        return None
    out = {"eval": m["eval"], "width": int(m["width"]), "steps": int(m["steps"]),
           "max_length": int(m["L"]), "alpha": float(m["alpha"] or 0.0),
           "temperature": float(m["t0"] or 0.0), "temp_end": float(m["t1"] or 0.0),
           "beam_seed": int(m["seed"]) if m["seed"] else None, "ckpt": m["ckpt"]}
    t = _TRAINED.match(m["ckpt"])
    if t:
        out.update(arm=t["arm"], seed=int(t["seed"]), update=int(t["update"]),
                   trained_here=True)
    else:
        out.update(arm=f"upstream:{m['ckpt']}", seed=None, update=None,
                   trained_here=False)
    return out


def read_run(path):
    """One beam jsonl -> its identity plus its solve count. None if not a beam file."""
    ident = parse_name(os.path.splitext(os.path.basename(path))[0])
    if ident is None:
        return None
    rows, solved, lengths = 0, 0, []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except ValueError:
                continue                       # torn trailing line
            if "presentation_idx" not in row or "solved" not in row:
                raise ValueError(f"{path} is not a beam jsonl (row lacks presentation_idx/solved)")
            rows += 1
            if row["solved"]:
                solved += 1
                lengths.append(row["path_length"])
    ident.update(path=path, rows=rows, solved=solved,
                 mean_path_length=(sum(lengths) / len(lengths)) if lengths else None)
    return ident


def scan(out_dir, eval_stem=acs_data.MS_STEM):
    """Every beam run in `out_dir` that was decoded over `eval_stem`."""
    runs = []
    for path in sorted(glob.glob(os.path.join(out_dir, "beam-*.jsonl"))):
        r = read_run(path)
        if r is not None and r["eval"] == eval_stem:
            runs.append(r)
    total = len(acs_data.read_raw(eval_stem))
    for r in runs:
        r["total"] = total
        r["complete"] = r["rows"] >= total
    return runs


def aggregate(runs):
    """Mean and range over seeds, per (arm, beam budget). Seeds are the spread."""
    groups = defaultdict(list)
    for r in runs:
        groups[(r["arm"], r["width"], r["steps"], r["alpha"])].append(r)
    out = []
    for (arm, width, steps, alpha), rs in sorted(groups.items()):
        counts = [r["solved"] for r in rs]
        out.append({
            "arm": arm, "label": ARM_LABEL.get(arm, arm), "width": width,
            "steps": steps, "alpha": alpha, "n_runs": len(rs),
            "seeds": sorted(r["seed"] for r in rs if r["seed"] is not None),
            "updates": sorted({r["update"] for r in rs if r["update"] is not None}),
            "mean": sum(counts) / len(counts), "min": min(counts), "max": max(counts),
            "total": rs[0]["total"],
            "complete": all(r["complete"] for r in rs),
            "partial_rows": [r["rows"] for r in rs if not r["complete"]],
        })
    return out


def _fmt(mean, lo, hi):
    if lo is None:
        return f"{mean:.1f}"
    return f"{mean:.1f}" if lo == hi else f"{mean:.1f} ({lo}-{hi})"


def format_table(runs, eval_stem=acs_data.MS_STEM):
    total = runs[0]["total"] if runs else len(acs_data.read_raw(eval_stem))
    w = 52
    out = [f"{'METHOD'.ljust(w)}SOLVED / {total}", "=" * (w + 16)]

    out.append("PPO Agents -- measured here (beam decode over " + eval_stem + ")")
    rows = aggregate(runs)
    if not rows:
        out.append("  (no beam runs yet)")
    for a in rows:
        note = f"  n={a['n_runs']}"
        if a["seeds"]:
            note += f" seed{'s' if len(a['seeds']) > 1 else ''}={','.join(map(str, a['seeds']))}"
        if a["updates"]:
            note += f" @update {','.join(map(str, a['updates']))}"
        note += f", beam {a['width']}x{a['steps']}"
        if a["alpha"]:
            note += f" alpha={a['alpha']:g}"
        if not a["complete"]:
            note += f"  [PARTIAL: {a['partial_rows']} of {a['total']} decoded]"
        out.append(f"  {a['label'].ljust(w - 2)}{_fmt(a['mean'], a['min'], a['max'])}")
        out.append(f"  {' ' * (w - 2)}{note.strip()}")

    out += ["", "Two-Hump paper, same denominator (reference, NOT measured here)",
            "  PPO Agents (mean over 5 seeds)"]
    for name, mean, lo, hi in PAPER_PPO:
        out.append(f"    {name.ljust(w - 4)}{_fmt(mean, lo, hi)}")
    out.append("  Greedy Search (deterministic)")
    for name, n in PAPER_GREEDY:
        out.append(f"    {name.ljust(w - 4)}{n}")
    return "\n".join(out)


def seed_from_mirror(out_dir, mirror_dir, pattern="beam-*.jsonl"):
    """Restart contract: on a fresh VM the local results dir is empty.

    The Drive mirror is the record of every earlier session, so copy back what
    is missing before scanning -- otherwise the table silently reports only the
    runs this VM happened to do. Never the other direction: a local file is the
    live one and `_mirror` owns pushing it out.
    """
    if not mirror_dir or not os.path.isdir(mirror_dir):
        return []
    os.makedirs(out_dir, exist_ok=True)
    copied = []
    for remote in sorted(glob.glob(os.path.join(mirror_dir, pattern))):
        local = os.path.join(out_dir, os.path.basename(remote))
        if not os.path.exists(local):
            with open(remote, "rb") as a, open(local, "wb") as b:
                b.write(a.read())
            copied.append(os.path.basename(remote))
    return copied


def print_table(out_dir, eval_stem=acs_data.MS_STEM, mirror_dir=None, log=print):
    copied = seed_from_mirror(out_dir, mirror_dir)
    if copied:
        log(f"seeded {len(copied)} beam jsonl(s) back from the mirror: {', '.join(copied)}")
    runs = scan(out_dir, eval_stem)
    log(format_table(runs, eval_stem))
    return {"runs": runs, "summary": aggregate(runs)}


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("out_dir", nargs="?", default=os.path.join(acs_data.ROOT, "results", "ppo"))
    p.add_argument("--eval", dest="eval_stem", default=acs_data.MS_STEM)
    a = p.parse_args()
    print_table(a.out_dir, a.eval_stem)
