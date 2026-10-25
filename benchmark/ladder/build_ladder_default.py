"""Build the default ladder (ladder_default.csv/.json): 100 rows, 10 a level, from ladder_100 (99 rows).

    python benchmark/ladder/build_ladder_default.py

ladder_100 holds 10 rows in every level except level 10, which has only the 9 pool rows that neither plain greedy nor
S20_MK2 solves at 10M pops. Two changes give 10 a level and keep the levels ordered by difficulty:
- level 10 adds the S20_MK2-hardest level-9 pool row not already in ladder_100 (plain greedy unsolved at 10M):
  ac19_12445, S20_MK2 1,297,772 pops;
- level 8 swaps its last-ranked row (ac19_52553) for the greedy-solved row closest to 10M that ladder_100 lacks:
  ac19_44158, greedy 8,009,273 pops, so level 8's top is not a single outlier.
Every other row is ladder_100's, unchanged; rows are pool rows verbatim except the level of the level-10 addition.
"""
import csv
import hashlib
import json
import os

LAD = os.path.dirname(os.path.abspath(__file__))


def read(name):
    with open(os.path.join(LAD, name), newline="") as f:
        return list(csv.DictReader(f))


def build():
    base, pool = read("ladder_100.csv"), read("ladder_500.csv")
    names = {r["name"] for r in base}
    assert len(base) == 99
    # level 10: the S20_MK2-hardest level-9 pool row not on ladder_100
    l9 = max((r for r in pool if r["level"] == "9" and r["name"] not in names), key=lambda r: int(r["s20_nodes"]))
    top10 = {**l9, "level": "10"}
    # level 8: the greedy-solved row closest to 10M not on ladder_100 replaces level 8's last-ranked row
    g8 = max((r for r in pool if r["greedy_solved"] == "1" and r["name"] not in names), key=lambda r: int(r["greedy_nodes"]))
    assert g8["level"] == "8"
    drop = [r["name"] for r in base if r["level"] == "8"][-1]        # ladder_100 lists a level in ranked order
    rows = [r for r in base if r["name"] != drop]
    rows.insert(max(i for i, r in enumerate(rows) if r["level"] == "8") + 1, g8)
    rows.append(top10)
    rows.sort(key=lambda r: int(r["level"]))
    assert len(rows) == 100 and all(sum(r["level"] == str(k) for r in rows) == 10 for k in range(1, 11))
    return rows, l9, g8, drop


def main():
    rows, l9, g8, drop = build()
    fields = list(read("ladder_100.csv")[0].keys())
    with open(os.path.join(LAD, "ladder_default.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    meta = json.load(open(os.path.join(LAD, "ladder_100.json")))
    sha = lambda n: hashlib.sha256(open(os.path.join(LAD, n), "rb").read()).hexdigest()
    out = {
        "name": "ladder_default", "size": 100, "per_level": 10,
        "per_level_actual": {str(k): 10 for k in range(1, 11)}, "n_levels": 10, "nested": False,
        "built_from": "ladder_100 (99 rows); build_ladder_default.py",
        "level10_added": {"name": l9["name"], "graded_level": 9, "greedy": "unsolved at 10M",
                          "s20_nodes": int(l9["s20_nodes"])},
        "level8_swap": {"out": drop, "in": g8["name"], "greedy_nodes": int(g8["greedy_nodes"])},
        "difficulty_variable": meta["difficulty_variable"], "levels": meta["levels"], "E": meta["E"],
        "strata_order": meta["strata_order"], "within_level_selection": meta["within_level_selection"],
        "sources": {n: {"path": f"benchmark/ladder/{n}", "sha256": sha(n)} for n in ("ladder_100.csv", "ladder_500.csv")},
        "subset": [r["name"] for r in rows],
    }
    with open(os.path.join(LAD, "ladder_default.json"), "w") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    print(f"ladder_default: 100 rows; level 10 + {l9['name']}; level 8 {drop} -> {g8['name']}")


if __name__ == "__main__":
    main()
