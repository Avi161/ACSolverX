#!/usr/bin/env python3
"""Build website/sample-data/ak3_test.json for the website's "AK(3) test" view.

Reads the AK(3) word-choice sweep results (results/stable_ac/3_generators_w_choices/ak_3_test/) and
emits ONE self-contained JSON the ak3.js view fetches directly (it is NOT part of the main
manifest/dataset pipeline — the AK(3) sweep is a word-choice study, a different shape from the
presentation x arm calibration). Re-runnable any time as the 1M tier finishes.

    python website/tools/build_ak3_bundle.py
"""
import glob
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = os.path.join(ROOT, "results", "stable_ac", "3_generators_w_choices", "ak_3_test")
OUT = os.path.join(ROOT, "website", "sample-data", "ak3_test.json")

FORMS = {
    "textbook": {"r1": "xyxYXY", "r2": "xxxYYYY",
                 "desc": "textbook AK(3)  ⟨x,y | xyx=yxy, x³=y⁴⟩ — where the change-of-variables words are provably isolatable"},
    "rep": {"r1": "YXyXYx", "r2": "YYYXXXX",
            "desc": "dataset representative 13_1 (ms_reps_unsolved idx 0) — the exact object in the data"},
}
BUDGETS = [100_000, 1_000_000]
FAMILY_DESC = {
    "relhalf": {"priority": 1, "desc": "relator sides xyx, yxy, x³, y⁴ + rotations/inverses (Fagan z=xyx & alts)"},
    "wk": {"priority": 2, "desc": "y⁻ᵏ·x⁻¹yxy, k∈[-8,8] (paper Thm 6/7: exact valid isolations of x)"},
    "wstar": {"priority": 3, "desc": "y⁻¹xyx⁻¹ + automorphism images (paper Thm 3)"},
    "conj": {"priority": 4, "desc": "conjugates g·x·g⁻¹, g·y·g⁻¹ (Wirtinger / Remark 17)"},
    "comm": {"priority": 5, "desc": "commutators + short double commutators (Appendix F bridge)"},
    "brute": {"priority": 6, "desc": "all freely-reduced words of length ≤3 (breadth probes)"},
    "ms": {"priority": 7, "desc": "MS(n,w) library words (w₁ = y⁻¹x⁻¹yxy, Prop 5)"},
    "control": {"priority": 8, "desc": "the dumb baselines w = r1, w = r2 (form-dependent)"},
}
_DEC = {1: "x", -1: "X", 2: "y", -2: "Y", 3: "z", -3: "Z"}


def decode(ints):
    return "".join(_DEC.get(int(a), "?") for a in ints)


def load(path):
    if not os.path.exists(path):
        return []
    return [json.loads(l) for l in open(path) if l.strip()]


def main():
    wb = {}
    wbp = os.path.join(SRC, "word_bank.json")
    if os.path.exists(wbp):
        wb = json.load(open(wbp))

    rows, summary = {}, {}
    for form in FORMS:
        for budget in BUDGETS:
            recs = load(os.path.join(SRC, "runs", f"ak3_{form}_{budget}.jsonl"))
            # dedup by word_name, keep last
            by = {}
            for r in recs:
                if r.get("form") == form and r.get("budget_nodes") == budget:
                    by[r["word_name"]] = r
            recs = list(by.values())
            out = []
            for r in recs:
                out.append({
                    "word": r["word_name"], "family": r["family"],
                    "z": decode(r.get("z_relator", [])),
                    "mtl": r.get("min_total_len"), "nodes": r.get("nodes_explored"),
                    "nps": r.get("nodes_per_sec"), "solved": bool(r.get("solved")),
                    "rss": r.get("peak_rss_mb"), "exhausted": bool(r.get("exhausted_budget")),
                    "path_len": r.get("path_len"), "verified": r.get("path_verified"),
                })
            # promise order: solved first, then closest to trivial, then fewest nodes
            out.sort(key=lambda w: (not w["solved"], w["mtl"] if w["mtl"] is not None else 10 ** 9,
                                    w["nodes"] if w["nodes"] is not None else 10 ** 9, w["word"]))
            key = f"{form}|{budget}"
            rows[key] = out
            summary[key] = {
                "n": len(out),
                "solved": sum(1 for w in out if w["solved"]),
                "exhausted": sum(1 for w in out if w["exhausted"]),
                "best_mtl": min((w["mtl"] for w in out if w["mtl"] is not None), default=None),
            }

    # family counts from the actual candidate set shown (a complete group includes the 2 controls)
    complete = rows.get("textbook|100000") or next((v for v in rows.values() if v), [])
    by_family = {}
    for w in complete:
        by_family[w["family"]] = by_family.get(w["family"], 0) + 1

    bundle = {
        "label": "AK(3) z=w word-choice sweep",
        "note": "Stabilize AK(3) to 3 generators with a chosen relator z=w(x,y), then run the greedy "
                "substitution solver. w is a free choice, so ~100 literature-grounded words are tried "
                "at up to 1,000,000 nodes on both AK(3) forms. Reaching the trivial 3-generator "
                "presentation would trivialize AK(3). A solved word writes a replayable path.",
        "trivial_len": 3,
        "n_words": sum(by_family.values()) or wb.get("n_words"),
        "by_family": by_family,
        "forms": FORMS,
        "families": FAMILY_DESC,
        "budgets": BUDGETS,
        "budget_labels": {"100000": "Screen · 100k nodes", "1000000": "Full · 1,000,000 nodes"},
        "summary": summary,
        "rows": rows,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(bundle, f, separators=(",", ":"))

    total = sum(s["n"] for s in summary.values())
    solves = sum(s["solved"] for s in summary.values())
    print(f"wrote {os.path.relpath(OUT, ROOT)}  ({total} run rows across {len(rows)} form/budget groups, "
          f"{solves} solves)")
    for k in sorted(summary):
        s = summary[k]
        print(f"  {k:20} n={s['n']:3} solved={s['solved']} exhausted={s['exhausted']} best_mtl={s['best_mtl']}")


if __name__ == "__main__":
    main()
