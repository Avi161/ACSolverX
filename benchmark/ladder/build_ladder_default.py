"""Build the default ladder (ladder_default.csv/.json): 100 rows, 10 a level.

    python benchmark/ladder/build_ladder_default.py

Levels 1-6 and 9 are ladder_100's rows, unchanged. Three changes from ladder_100:
- levels 7 and 8 split at a round number, E = 3,000,000 plain-greedy pops (ladder_100 uses the logarithmic median,
  2,253,802): level 7 is 1M <= g < 3M (43 pool rows), level 8 is 3M <= g <= 10M (17 pool rows);
- level 7 takes the 10 of its 43 rows that cost S20_MK2 the most pops; level 8 takes the 10 rows with the largest g, so
  it holds every greedy-solved row closest to 10M (both ties by name);
- level 10 has only the 9 pool rows that neither plain greedy nor S20_MK2 solves at 10M pops; its tenth row is the
  S20_MK2-hardest level-9 pool row not already chosen, ac19_12445 (S20_MK2 1,297,772 pops).
Rows are pool rows verbatim except the level column, which follows E for levels 7-8 and is 10 for ac19_12445.
"""
import csv
import hashlib
import json
import os

LAD = os.path.dirname(os.path.abspath(__file__))


def read(name):
    with open(os.path.join(LAD, name), newline="") as f:
        return list(csv.DictReader(f))


E = 3_000_000


def build():
    base, pool = read("ladder_100.csv"), read("ladder_500.csv")
    assert len(base) == 99
    keep = [r for r in base if r["level"] not in ("7", "8")]
    mid = [r for r in pool if r["level"] in ("7", "8")]               # every pool row with 1M <= g <= 10M
    assert len(mid) == 60 and all(r["greedy_solved"] == "1" and 10**6 <= int(r["greedy_nodes"]) <= 10**7 for r in mid)
    l7 = sorted((r for r in mid if int(r["greedy_nodes"]) < E), key=lambda r: (-int(r["s20_nodes"]), r["name"]))[:10]
    l8 = sorted((r for r in mid if int(r["greedy_nodes"]) >= E), key=lambda r: (-int(r["greedy_nodes"]), r["name"]))[:10]
    names = {r["name"] for r in base}
    l9 = max((r for r in pool if r["level"] == "9" and r["name"] not in names), key=lambda r: int(r["s20_nodes"]))
    rows = keep + [{**r, "level": "7"} for r in l7] + [{**r, "level": "8"} for r in l8] + [{**l9, "level": "10"}]
    rows.sort(key=lambda r: int(r["level"]))                          # stable: ranked order inside a level
    assert len(rows) == 100 and all(sum(r["level"] == str(k) for r in rows) == 10 for k in range(1, 11))
    return rows, l9


def main():
    rows, l9 = build()
    fields = list(read("ladder_100.csv")[0].keys())
    with open(os.path.join(LAD, "ladder_default.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    meta = json.load(open(os.path.join(LAD, "ladder_100.json")))
    levels = [dict(lv) for lv in meta["levels"]]
    for lv in levels:
        if lv["level"] == 7:
            lv.update(hi_nodes=E, rule="1,000,000 <= g < 3,000,000")
        if lv["level"] == 8:
            lv.update(lo_nodes=E, rule="3,000,000 <= g <= 10,000,000")
    sha = lambda n: hashlib.sha256(open(os.path.join(LAD, n), "rb").read()).hexdigest()
    out = {
        "name": "ladder_default", "size": 100, "per_level": 10,
        "per_level_actual": {str(k): 10 for k in range(1, 11)}, "n_levels": 10, "nested": False,
        "built_from": "ladder_100 (99 rows); build_ladder_default.py",
        "level10_added": {"name": l9["name"], "graded_level": 9, "greedy": "unsolved at 10M",
                          "s20_nodes": int(l9["s20_nodes"])},
        "E": E,
        "E_note": "round number; ladder_100 and the nested panels use the logarithmic median 2,253,802",
        "level7_selection": "the 10 largest S20_MK2 pop counts among the 43 pool rows with 1M <= g < 3M (ties by name)",
        "level8_selection": "the 10 largest g among the 17 pool rows with 3M <= g <= 10M (ties by name)",
        "difficulty_variable": meta["difficulty_variable"], "levels": levels,
        "strata_order": meta["strata_order"], "within_level_selection": meta["within_level_selection"],
        "sources": {n: {"path": f"benchmark/ladder/{n}", "sha256": sha(n)} for n in ("ladder_100.csv", "ladder_500.csv")},
        "subset": [r["name"] for r in rows],
    }
    with open(os.path.join(LAD, "ladder_default.json"), "w") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    print(f"ladder_default: 100 rows; E = {E:,}; level 10 + {l9['name']}")


if __name__ == "__main__":
    main()
