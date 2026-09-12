"""Cheap power-coordinate endpoint algebra, with no stable certificate claim."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from time import perf_counter

from ac_words import canon, inv, red
from coupled_power_probe import power, substitute


def cpair(pair):
    return tuple(sorted(canon(w) for w in pair))


def nielsen_descent(pair):
    pair = cpair(pair)
    maps = [(x, y) for x, y in
            (("xy", "y"), ("xY", "y"), ("yx", "y"), ("Yx", "y"),
             ("x", "yx"), ("x", "yX"), ("x", "xy"), ("x", "Xy"))]
    trace = []
    while True:
        candidates = [(sum(map(len, child)), child, images)
                      for images in maps
                      for child in [cpair(substitute(w, *images) for w in pair)]]
        length, child, images = min(candidates)
        if length >= sum(map(len, pair)):
            return pair, trace
        trace.append({"images": images, "before": pair, "after": child})
        pair = child


def run_substitute(companion, d, v):
    out = ""
    block_choices = []
    i = 0
    while i < len(companion):
        if companion[i].lower() == "y":
            out = red(out + companion[i])
            i += 1
            continue
        j = i
        while j < len(companion) and companion[j] == companion[i]:
            j += 1
        e = (j-i) * (1 if companion[i] == "x" else -1)
        choices = []
        for q in range(e // d - 1, e // d + 3):
            r = e - d*q
            for side in (0, 1):
                w = red(power("x", q) + power(v, r)) if not side else red(power(v, r) + power("x", q))
                choices.append((len(w), w, q, r, side))
        _, w, q, r, side = min(choices)
        block_choices.append({"offset": i, "exponent": e, "quotient": q,
                              "remainder": r, "side": side, "replacement": w})
        out = red(out + w)
        i = j
    return out, block_choices


def orientations(pair):
    seen = set()
    for source in (0, 1):
        for a, t in (("x", "y"), ("x", "Y"), ("X", "y"), ("X", "Y"),
                     ("y", "x"), ("y", "X"), ("Y", "x"), ("Y", "X")):
            dictionary = {a: "x", inv(a): "X", t: "y", inv(t): "Y"}
            normalized = ["".join(dictionary[c] for c in w) for w in pair]
            for sign in (1, -1):
                r = normalized[source] if sign == 1 else inv(normalized[source])
                for cut in range(len(r)):
                    word = r[cut:] + r[:cut]
                    for m in range(1, 15):
                        if word != "Y" + "x" * (m+1) + "y" + "X" * m:
                            continue
                        key = (m, normalized[1-source])
                        if key in seen:
                            continue
                        seen.add(key)
                        yield {"source": source, "a": a, "t": t, "sign": sign,
                               "cut": cut, "m": m, "companion": normalized[1-source]}


def main():
    start = perf_counter()
    root = Path(__file__).resolve().parents[5]
    path = root / "data/ms_unsolved_reps/aca_124_best.csv"
    rows = list(csv.DictReader(path.open()))
    results = []
    for row in rows:
        name = row["name"]
        pair = (row["r1"], row["r2"])
        candidates = []
        for orient in orientations(pair):
            m = orient["m"]
            for d, v in ((m, "yxYX"), (m+1, "xYXy")):
                donor = red("X" + power(v, d))
                companion, choices = run_substitute(orient["companion"], d, v)
                best, trace = nielsen_descent((donor, companion))
                candidates.append({"orientation": orient, "power": d, "recovered_a": v,
                                   "block_choices": choices, "raw_endpoint": [donor, companion],
                                   "best_pair": best, "best_length": sum(map(len,best)),
                                   "nielsen_trace": trace})
        best = min(candidates, key=lambda c: c["best_length"]) if candidates else None
        results.append({"name": name, "input": pair, "input_length": sum(map(len,pair)),
                        "best": best, "candidate_count": len(candidates)})
    output = Path(__file__).with_name("coupled_power_stable_probe.json")
    report = {"status": "candidate_endpoints_no_stable_certificate_yet", "rows": results,
              "wall_seconds": perf_counter()-start}
    output.write_text(json.dumps(report,indent=2)+"\n")
    improved = [r for r in results if r["best"] and r["best"]["best_length"] < r["input_length"]]
    print(json.dumps({"output":str(output), "wall_seconds":report["wall_seconds"],
                      "matched_rows":sum(r["best"] is not None for r in results),
                      "improvements":[{"name":r["name"], "before":r["input_length"],
                                       "after":r["best"]["best_length"], "pair":r["best"]["best_pair"]} for r in improved]}))


if __name__ == "__main__":
    main()
