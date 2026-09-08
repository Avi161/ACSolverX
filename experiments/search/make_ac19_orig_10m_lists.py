"""Derive the PRE-AUT-MIN originals of the AC19 10M residue -- never by hand.

THE QUESTION
------------
Lucas Fagan, on the AC19 rows still unsolved at 10,000,000 nodes: "Did you
try the original of those presentations, before aut minimizing, on 10M
nodes?" The hypothesis is that ``Aut(F2)``-minimizing a presentation can make
it HARDER to search, so the raw dataset row might solve where its orbit
representative does not.

The test is only meaningful for an arm that does no basis work of its own.
``greedy`` and ``s20_mk2`` on ``hcompact`` qualify -- neither
``greedy_compact.py``, ``greedy_baseline.py``, ``run_leftovers_5m.py`` nor
``experiments/heuristic_search/core/`` mentions ``aut_canon``,
``reduce_basis``, ``basis_moves`` or ``canon_pair``, so the original and the
representative really are different starting points. The cascade does NOT
qualify: its first stage is ``reduce_basis_key``, a Nielsen length descent,
so it aut-minimizes internally and erases the distinction by construction.

THE LISTS
---------
For every orbit an arm failed at 10M, EVERY original whose ``Aut(F2)``
canonicalization is that orbit -- not one representative per orbit. Seven of
the 28 greedy orbits carry more than one original, which gives within-orbit
variance for free.

    greedy   28 orbits -> 40 originals   unsolved_10m_orig_baseline.csv
    s20_mk2   9 orbits -> 18 originals   unsolved_10m_orig_s20_mk2.csv

The s20_mk2 orbits are a subset of the greedy orbits, so its originals are a
subset too and the arms meet head-to-head on all 18.

Rows are named by their extended-screen id (``ac19x_<dataset index>``), carry
the orbit name and the representative's words as columns, and hold the RAW
decoded dataset pair -- ``ac19_extended_rows.csv`` is written straight from
``decode()`` with no canonicalization.

    PYTHONPATH=. python3 -m experiments.search.make_ac19_orig_10m_lists
    PYTHONPATH=. python3 -m experiments.search.make_ac19_orig_10m_lists --check
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os

from experiments.search.run_leftovers_1m import SCREEN_DIR, read_rows

RESULTS_DIR = os.path.dirname(SCREEN_DIR)
ORBITS_CSV = os.path.join(SCREEN_DIR, "ac19_autmin_orbits.csv")
DATASET_CSV = os.path.join(SCREEN_DIR, "ac19_extended_rows.csv")

JSONL_10M = {
    "greedy": os.path.join(RESULTS_DIR, "ac19_10m",
                           "ac19_10m_greedy_b10000000_mrl64.jsonl"),
    "s20_mk2": os.path.join(RESULTS_DIR, "ac19_10m",
                            "ac19_10m_s20_mk2_b10000000_mrl64.jsonl"),
}
OUT_CSV = {"greedy": "unsolved_10m_orig_baseline.csv",
           "s20_mk2": "unsolved_10m_orig_s20_mk2.csv"}
NOTE = "ORIGINALS_AT_10M.md"

FIELDS = ("name", "r1", "r2", "orbit", "rep_r1", "rep_r2",
          "orbit_members", "min_relator_length")


def unsolved_orbits(arm):
    """Orbit names this arm failed at 10,000,000 nodes, sorted."""
    path = JSONL_10M[arm]
    records = read_rows(path)
    if not records:
        raise FileNotFoundError(f"no 10M records for {arm}: {path}")
    return sorted(r["name"] for r in records if not r["solved"])


def load_orbits(path=ORBITS_CSV):
    with open(path, newline="") as fh:
        return {r["name"]: {"rep": (r["r1"], r["r2"]),
                            "members": [int(m) for m in r["members"].split()],
                            "n": int(r["n_members"])}
                for r in csv.DictReader(fh)}


def load_dataset_rows(path=DATASET_CSV):
    """dataset index -> ``{name, r1, r2}`` for every original."""
    rows = {}
    with open(path, newline="") as fh:
        for r in csv.DictReader(fh):
            if not r["members"].strip():
                continue
            rows[int(r["members"].split()[0])] = {
                "name": r["name"], "r1": r["r1"], "r2": r["r2"]}
    return rows


def derive(arm, orbits=None, dataset=None):
    """Every original behind this arm's 10M failures, in dataset order."""
    orbits = orbits if orbits is not None else load_orbits()
    dataset = dataset if dataset is not None else load_dataset_rows()
    out = []
    for orbit in unsolved_orbits(arm):
        if orbit not in orbits:
            raise KeyError(f"{orbit} is not an orbit of {ORBITS_CSV}")
        info = orbits[orbit]
        if len(info["members"]) != info["n"]:
            raise RuntimeError(f"{orbit}: n_members={info['n']} but "
                               f"{len(info['members'])} member indices")
        for index in info["members"]:
            if index not in dataset:
                raise KeyError(f"{orbit}: dataset row {index} is missing")
            row = dataset[index]
            out.append({
                "name": row["name"], "r1": row["r1"], "r2": row["r2"],
                "orbit": orbit,
                "rep_r1": info["rep"][0], "rep_r2": info["rep"][1],
                "orbit_members": info["n"],
                # The search starts here, so at node 0 this IS the minimum
                # total length seen -- the same field the run rungs record.
                "min_relator_length": len(row["r1"]) + len(row["r2"]),
            })
    names = [r["name"] for r in out]
    if len(names) != len(set(names)):
        raise RuntimeError(f"{arm}: duplicate original names")
    return out


def render(rows):
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def render_note(derived):
    g, s = derived["greedy"], derived["s20_mk2"]
    gorb = sorted({r["orbit"] for r in g})
    sorb = sorted({r["orbit"] for r in s})
    lines = [
        "# The pre-aut-min originals of the AC19 10M residue", "",
        "Generated by `experiments/search/make_ac19_orig_10m_lists.py`; do not",
        "edit by hand. `--check` reports drift, `tests/test_ac19_orig_10m.py`",
        "re-derives both lists from the 10M jsonls.", "",
        "Every original whose `Aut(F2)` canonicalization is an orbit the arm",
        "failed at 10,000,000 nodes. The paired control is that arm's own 10M",
        "record on the representative, already in `../ac19_10m/`.", "",
        "| arm | orbits failed @10M | originals | list |",
        "|---|---:|---:|---|",
        f"| `greedy` | {len(gorb)} | {len(g)} | `{OUT_CSV['greedy']}` |",
        f"| `s20_mk2` | {len(sorb)} | {len(s)} | `{OUT_CSV['s20_mk2']}` |",
        "",
        f"The {len(sorb)} `s20_mk2` orbits are a subset of the {len(gorb)} "
        "`greedy` orbits, so",
        "the arms meet head-to-head on every one of its originals.", "",
        "## Orbits carrying more than one original", "",
        "These give within-orbit variance: same orbit, different raw rows.", "",
        "| orbit | originals | rep total | original totals |",
        "|---|---:|---:|---|",
    ]
    by = {}
    for r in g:
        by.setdefault(r["orbit"], []).append(r)
    multi = [(o, rs) for o, rs in sorted(by.items()) if len(rs) > 1]
    for orbit, rs in multi:
        totals = sorted(len(r["r1"]) + len(r["r2"]) for r in rs)
        rep = len(rs[0]["rep_r1"]) + len(rs[0]["rep_r2"])
        lines.append(f"| `{orbit}` | {len(rs)} | {rep} | "
                     f"{', '.join(map(str, totals))} |")
    singles = len(by) - len(multi)
    lines += ["",
              f"{singles} of the {len(by)} greedy orbits are singletons.", "",
              "## Why this is well posed", "",
              "`greedy` and `s20_mk2` on `hcompact` do no basis work -- no",
              "`aut_canon`, `reduce_basis`, `basis_moves` or `canon_pair`",
              "anywhere in the greedy path or in",
              "`experiments/heuristic_search/core/` -- so an original and its",
              "representative are genuinely different starting points. The",
              "cascade does not qualify: `reduce_basis_key` is its first stage,",
              "so it aut-minimizes internally.", ""]
    return "\n".join(lines)


def build():
    orbits, dataset = load_orbits(), load_dataset_rows()
    return {arm: derive(arm, orbits, dataset) for arm in OUT_CSV}


def check(derived=None):
    """``[(path, reason)]`` for every file that differs from the derivation."""
    derived = derived or build()
    drift = []
    for arm, name in OUT_CSV.items():
        path = os.path.join(SCREEN_DIR, name)
        want = render(derived[arm])
        if not os.path.exists(path):
            drift.append((path, "missing"))
        elif open(path).read() != want:
            drift.append((path, "differs from the derivation"))
    path = os.path.join(SCREEN_DIR, NOTE)
    want = render_note(derived)
    if not os.path.exists(path):
        drift.append((path, "missing"))
    elif open(path).read() != want:
        drift.append((path, "differs from the derivation"))
    return drift


def write(derived=None):
    derived = derived or build()
    written = []
    for arm, name in OUT_CSV.items():
        path = os.path.join(SCREEN_DIR, name)
        with open(path, "w", newline="") as fh:
            fh.write(render(derived[arm]))
        written.append((path, len(derived[arm])))
    path = os.path.join(SCREEN_DIR, NOTE)
    with open(path, "w") as fh:
        fh.write(render_note(derived))
    written.append((path, None))
    return written


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="report drift instead of writing")
    args = ap.parse_args(argv)
    derived = build()
    for arm, rows in sorted(derived.items()):
        orbs = len({r["orbit"] for r in rows})
        print(f"  {arm:<8} {orbs:>3} orbits -> {len(rows):>3} originals")
    if args.check:
        drift = check(derived)
        for path, why in drift:
            print(f"  DRIFT {os.path.basename(path)}: {why}")
        print("  no drift" if not drift else f"  {len(drift)} file(s) differ")
        return 1 if drift else 0
    for path, n in write(derived):
        print(f"  wrote {os.path.relpath(path)}"
              + (f" ({n} rows)" if n is not None else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
