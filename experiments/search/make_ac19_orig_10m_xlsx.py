"""One workbook for the pre-aut-min originals: names, lines, costs, certificates.

WHAT THE NAMES MEAN
-------------------
``ac19_<n>``   the n-th ``Aut(F2)`` orbit of ``data/AC19_extended.txt``, zero-based,
               orbits ordered by their first dataset line. NOT a line number:
               ``ac19_50892`` is the 50,892nd orbit and its one member is line
               90,721. Only ``ac19_0`` coincides with a line.
``ac19x_<n>``  line ``n`` of ``data/AC19_extended.txt``, zero-based. The
               workbook also carries it one-based, for a text editor.
``AC19.txt``   ``data/AC19.txt`` (140,535 rows) is NOT a prefix of the extended
               file -- the order differs -- so an original's line there, when
               it has one, is a separate column found by exact pair match.

Everything here is read off files already in the repo: the orbit list, the
per-line dataset rows, the two originals jsonls (plus the ``_paths`` twin
that carries the s20_mk2 certificates), the transported certificates, and the
``ac19_10m`` control records. The CSV twin of the first sheet is what git
diffs; the workbook is what a person opens.

    PYTHONPATH=. python3 -m experiments.search.make_ac19_orig_10m_xlsx
    PYTHONPATH=. python3 -m experiments.search.make_ac19_orig_10m_xlsx --check
"""
from __future__ import annotations

import argparse
import csv
import io
import os

from experiments.search import make_ac19_orig_10m_lists as mk
from experiments.search import transport_ac19_orig as tr
from experiments.search.make_ac19_autmin_screen import load_dataset
from experiments.search.run_leftovers_1m import read_rows

ROOT = os.path.dirname(os.path.dirname(mk.RESULTS_DIR))
OUT_DIR = os.path.join(mk.RESULTS_DIR, "ac19_orig_10m")
AC19_TXT = os.path.join(ROOT, "data", "AC19.txt")
XLSX = os.path.join(OUT_DIR, "ac19_orig_10m_originals.xlsx")
CSV = os.path.join(OUT_DIR, "ac19_orig_10m_originals.csv")
JSONL = {"greedy": "ac19_orig_10m_greedy_b10000000_mrl64.jsonl",
         "s20_mk2": "leftovers_1m_s20_mk2_b1000000_mrl64_paths.jsonl"}
CONTROL_BUDGET = 10_000_000

ORIGINAL_COLUMNS = (
    "orbit", "orbit_position", "rep_r1", "rep_r2", "rep_total_len",
    "original", "extended_line_0based", "extended_line_1based",
    "ac19_txt_line_0based", "orig_r1", "orig_r2", "orig_total_len",
    "greedy_nodes", "greedy_path_length", "greedy_path_moves", "greedy_path_states",
    "s20_nodes", "s20_path_length", "s20_path_moves", "s20_path_states",
    "cheaper_arm",
    "rep_moves_via_greedy", "rep_tail_via_greedy",
    "rep_moves_via_s20", "rep_tail_via_s20",
    "rep_greedy_at_10M", "rep_s20_at_10M",
)
ORBIT_COLUMNS = (
    "orbit", "orbit_position", "rep_r1", "rep_r2", "rep_total_len",
    "n_originals", "extended_lines_0based",
    "greedy_min_nodes", "greedy_max_nodes", "greedy_spread",
    "s20_min_nodes", "s20_max_nodes", "s20_spread",
    "rep_moves_shortest", "rep_moves_via", "rep_moves_arm",
    "rep_greedy_at_10M", "rep_s20_at_10M",
)
NAMING = (
    ("ac19_<n>", "The n-th Aut(F2) orbit of data/AC19_extended.txt, zero-based, "
                 "orbits in order of their first dataset line. Not a line number: "
                 "ac19_50892 is the 50,892nd orbit and its one member is line 90,721."),
    ("ac19x_<n>", "Line n of data/AC19_extended.txt, zero-based "
                  "(extended_line_1based is the same line as an editor counts it)."),
    ("ac19_txt_line_0based", "Line of data/AC19.txt holding exactly this pair, or blank. "
                             "AC19.txt is not a prefix of the extended file, so this is "
                             "found by exact match and most originals have no such line."),
    ("rep_r1, rep_r2", "The orbit's Aut(F2)-minimal representative: canon_pair(phi(original)) "
                       "for the automorphism phi that aut_canon ships. Every original of the "
                       "orbit maps to the same pair."),
    ("greedy_nodes, s20_nodes", "Nodes the arm popped before solving the ORIGINAL "
                                "(greedy at a 10,000,000 ceiling, s20_mk2 at 1,000,000; "
                                "both cap 64). Blank: not on that arm's list."),
    ("*_path_moves", "The engine's move strings target_sign_k1_k2, ';'-joined, from the "
                     "original to a terminal pair; *_path_states is every state on the way, "
                     "'|'-joined."),
    ("rep_moves_via_*", "Path length of the REPRESENTATIVE obtained by transporting the "
                        "original's certificate through phi (AC moves are Aut(F2)-"
                        "equivariant) and Nielsen-reducing the resulting basis: "
                        "original path_length + rep_tail. Every one replayed from the "
                        "representative's own words to (x, y); the certificates are in "
                        "ac19_orig_10m_transported_<arm>.jsonl."),
    ("rep_*_at_10M", "What that arm did on the representative at 10,000,000 nodes, cap 64 "
                     "(results/heuristic_search/ac19_10m/)."),
)


def _ac19_txt_index():
    first = {}
    for index, pair in enumerate(load_dataset(AC19_TXT)):
        first.setdefault(pair, index)
    return first


def _records(arm):
    return {r["name"]: r for r in read_rows(os.path.join(OUT_DIR, JSONL[arm]))}


def _transported(arm):
    return {r["name"]: r for r in read_rows(os.path.join(OUT_DIR, tr.OUT[arm]))}


def _control(arm):
    """orbit -> status string from the arm's own 10M record on the representative."""
    out = {}
    for r in read_rows(mk.JSONL_10M[arm]):
        out[r["name"]] = ("unsolved at %s" % format(r["nodes_explored"], ",")
                          if not r["solved"] else
                          "solved at %s" % format(r["nodes_explored"], ","))
    return out


def _status(control, orbit):
    return control.get(orbit, "not in this arm's 10M residue")


def _spread(values):
    return round(max(values) / min(values), 1) if values else ""


def build():
    """``(originals, orbits)`` as lists of dicts, in orbit-position order."""
    derived = mk.build()
    orbits = mk.load_orbits()
    ac19 = _ac19_txt_index()
    recs = {arm: _records(arm) for arm in JSONL}
    moved = {arm: _transported(arm) for arm in JSONL}
    control = {arm: _control(arm) for arm in JSONL}
    for arm in JSONL:
        want = {r["name"] for r in derived[arm]}
        if set(recs[arm]) != want or set(moved[arm]) != want:
            raise RuntimeError(f"{arm}: records or transported rows do not cover "
                               f"the derived list")

    originals = []
    for row in derived["greedy"]:
        name, orbit = row["name"], row["orbit"]
        line = int(name.split("_")[1])
        g, s = recs["greedy"][name], recs["s20_mk2"].get(name)
        tg, ts = moved["greedy"][name], moved["s20_mk2"].get(name)
        cheaper = ""
        if s is not None:
            cheaper = ("s20_mk2" if s["nodes_explored"] < g["nodes_explored"]
                       else "greedy" if g["nodes_explored"] < s["nodes_explored"]
                       else "tie")
        originals.append({
            "orbit": orbit, "orbit_position": int(orbit.split("_")[1]),
            "rep_r1": row["rep_r1"], "rep_r2": row["rep_r2"],
            "rep_total_len": len(row["rep_r1"]) + len(row["rep_r2"]),
            "original": name, "extended_line_0based": line,
            "extended_line_1based": line + 1,
            "ac19_txt_line_0based": ac19.get((row["r1"], row["r2"]), ""),
            "orig_r1": row["r1"], "orig_r2": row["r2"],
            "orig_total_len": len(row["r1"]) + len(row["r2"]),
            "greedy_nodes": g["nodes_explored"],
            "greedy_path_length": g["path_length"],
            "greedy_path_moves": ";".join(g["path_moves"]),
            "greedy_path_states": "|".join(f"{a} {b}" for a, b in g["path"]),
            "s20_nodes": s["nodes_explored"] if s else "",
            "s20_path_length": s["path_length"] if s else "",
            "s20_path_moves": ";".join(s["path_moves"]) if s else "",
            "s20_path_states": "|".join(f"{a} {b}" for a, b in s["path"]) if s else "",
            "cheaper_arm": cheaper,
            "rep_moves_via_greedy": tg["rep_moves"], "rep_tail_via_greedy": tg["tail_moves"],
            "rep_moves_via_s20": ts["rep_moves"] if ts else "",
            "rep_tail_via_s20": ts["tail_moves"] if ts else "",
            "rep_greedy_at_10M": _status(control["greedy"], orbit),
            "rep_s20_at_10M": _status(control["s20_mk2"], orbit),
        })
    originals.sort(key=lambda r: (r["orbit_position"], r["extended_line_0based"]))

    best = {b["orbit"]: b for b in tr.per_orbit(
        {arm: list(rows.values()) for arm, rows in moved.items()})}
    by_orbit = {}
    for r in originals:
        by_orbit.setdefault(r["orbit"], []).append(r)
    orbit_rows = []
    for orbit, rs in sorted(by_orbit.items(), key=lambda kv: kv[1][0]["orbit_position"]):
        g = [r["greedy_nodes"] for r in rs]
        s = [r["s20_nodes"] for r in rs if r["s20_nodes"] != ""]
        members = orbits[orbit]["members"]
        if sorted(r["extended_line_0based"] for r in rs) != sorted(members):
            raise RuntimeError(f"{orbit}: originals are not the orbit's members")
        orbit_rows.append({
            "orbit": orbit, "orbit_position": rs[0]["orbit_position"],
            "rep_r1": rs[0]["rep_r1"], "rep_r2": rs[0]["rep_r2"],
            "rep_total_len": rs[0]["rep_total_len"],
            "n_originals": len(rs),
            "extended_lines_0based": " ".join(str(m) for m in members),
            "greedy_min_nodes": min(g), "greedy_max_nodes": max(g),
            "greedy_spread": _spread(g),
            "s20_min_nodes": min(s) if s else "", "s20_max_nodes": max(s) if s else "",
            "s20_spread": _spread(s),
            "rep_moves_shortest": best[orbit]["rep_moves"],
            "rep_moves_via": best[orbit]["via"], "rep_moves_arm": best[orbit]["arm"],
            "rep_greedy_at_10M": rs[0]["rep_greedy_at_10M"],
            "rep_s20_at_10M": rs[0]["rep_s20_at_10M"],
        })
    return originals, orbit_rows


def render_csv(originals):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=ORIGINAL_COLUMNS, lineterminator="\n")
    w.writeheader()
    w.writerows(originals)
    return buf.getvalue()


def write_xlsx(originals, orbit_rows, path=XLSX):
    from openpyxl import Workbook
    from openpyxl.styles import Font
    from openpyxl.utils import get_column_letter

    wb = Workbook()

    def sheet(ws, columns, rows, widths):
        ws.append(list(columns))
        for c in ws[1]:
            c.font = Font(bold=True)
        for r in rows:
            ws.append([r[c] for c in columns])
        ws.freeze_panes = "A2"
        for i, col in enumerate(columns, start=1):
            ws.column_dimensions[get_column_letter(i)].width = widths.get(col, 14)

    wide = {c: 40 for c in ("greedy_path_moves", "greedy_path_states",
                            "s20_path_moves", "s20_path_states",
                            "rep_greedy_at_10M", "rep_s20_at_10M",
                            "extended_lines_0based")}
    wide.update({"rep_r2": 20, "orig_r1": 20, "orig_r2": 20})
    sheet(wb.active, ORIGINAL_COLUMNS, originals, wide)
    wb.active.title = "originals"
    sheet(wb.create_sheet("orbits"), ORBIT_COLUMNS, orbit_rows, wide)
    ws = wb.create_sheet("naming")
    ws.append(["term", "meaning"])
    for c in ws[1]:
        c.font = Font(bold=True)
    for term, meaning in NAMING:
        ws.append([term, meaning])
    ws.column_dimensions["A"].width = 26
    ws.column_dimensions["B"].width = 120
    wb.save(path)
    return path


def read_xlsx(path=XLSX):
    """``{sheet: [dict]}`` with every cell as a string, for the check."""
    from openpyxl import load_workbook
    wb = load_workbook(path, read_only=True)
    out = {}
    for ws in wb.worksheets:
        rows = list(ws.iter_rows(values_only=True))
        head = [str(c) for c in rows[0]]
        out[ws.title] = [{h: ("" if v is None else str(v)) for h, v in zip(head, r)}
                         for r in rows[1:]]
    return out


def _cell(v):
    """A cell as the string openpyxl hands back: integral floats come back as ints."""
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return "" if v is None else str(v)


def check(originals=None, orbit_rows=None):
    """``[reason]`` for every way the files on disk differ from the derivation."""
    if originals is None:
        originals, orbit_rows = build()
    drift = []
    if not os.path.exists(CSV):
        drift.append(f"{os.path.basename(CSV)} missing")
    elif open(CSV).read() != render_csv(originals):
        drift.append(f"{os.path.basename(CSV)} differs from the derivation")
    if not os.path.exists(XLSX):
        drift.append(f"{os.path.basename(XLSX)} missing")
        return drift
    got = read_xlsx()
    for name, columns, rows in (("originals", ORIGINAL_COLUMNS, originals),
                                ("orbits", ORBIT_COLUMNS, orbit_rows)):
        want = [{c: _cell(r[c]) for c in columns} for r in rows]
        if got.get(name) != want:
            bad = next(((i, c) for i, (g, w) in enumerate(zip(got.get(name, []), want))
                        for c in columns if g.get(c) != w[c]), None)
            drift.append(f"sheet {name} differs from the derivation"
                         + (f" (first at row {bad[0] + 2}, column {bad[1]})" if bad else ""))
    if [(r["term"], r["meaning"]) for r in got.get("naming", [])] != list(NAMING):
        drift.append("sheet naming differs from the derivation")
    return drift


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="report drift, write nothing")
    args = ap.parse_args(argv)
    originals, orbit_rows = build()
    print(f"  originals {len(originals)}  orbits {len(orbit_rows)}")
    if args.check:
        drift = check(originals, orbit_rows)
        for d in drift:
            print(f"  DRIFT {d}")
        print("  no drift" if not drift else f"  {len(drift)} difference(s)")
        return 1 if drift else 0
    with open(CSV, "w", newline="") as fh:
        fh.write(render_csv(originals))
    write_xlsx(originals, orbit_rows)
    for p in (CSV, XLSX):
        print(f"  wrote {os.path.relpath(p)} ({os.path.getsize(p):,} B)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
