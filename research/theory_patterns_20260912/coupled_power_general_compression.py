"""Pure-power stable isolator templates, algebra only and no heap."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from time import perf_counter

from ac_words import cyclic, inv, red
from coupled_power_probe import power
from coupled_power_stable_probe import nielsen_descent, run_substitute


def red3(word):
    stack = []
    for c in word:
        if stack and stack[-1] == c.swapcase():
            stack.pop()
        else:
            stack.append(c)
    return "".join(stack)


def runs(word):
    result = []
    i = 0
    while i < len(word):
        j = i+1
        while j < len(word) and word[j] == word[i]:
            j += 1
        result.append((word[i].lower(), (j-i) * (1 if word[i].islower() else -1)))
        i = j
    return result


def pow3(letter, e):
    return (letter if e >= 0 else letter.upper()) * abs(e)


def templates(pair):
    seen = set()
    for source in (0, 1):
        for axis in ("x", "y"):
            normalized = list(pair) if axis == "x" else [w.translate(str.maketrans("xXyY", "yYxX")) for w in pair]
            core, prefix = cyclic(normalized[source])
            for cut in range(len(core)):
                word = core[cut:] + core[:cut]
                if word[0].lower() != "x" or word[-1].lower() == "x":
                    continue
                syllables = runs(word)
                x_runs = [(i,e) for i,(g,e) in enumerate(syllables) if g == "x"]
                for d in range(2, max(abs(e) for _,e in x_runs)+2):
                    for index, e in x_runs:
                        if any(e0 % d for i0,e0 in x_runs if i0 != index):
                            continue
                        for sign in (-1, 1):
                            if (e-sign) % d:
                                continue
                            for side in (0, 1):
                                pieces = []
                                for i,(g,e0) in enumerate(syllables):
                                    if g == "y":
                                        pieces.append(pow3("y",e0))
                                    elif i == index:
                                        z = pow3("z",(e0-sign)//d)
                                        x = pow3("x",sign)
                                        pieces.append(z+x if not side else x+z)
                                    else:
                                        pieces.append(pow3("z",e0//d))
                                isolator = red3("".join(pieces))
                                assert isolator.count("x")+isolator.count("X") == 1
                                expanded = red3(isolator.replace("z", "x"*d).replace("Z", "X"*d))
                                assert expanded == word
                                pos = next(i for i,c in enumerate(isolator) if c.lower() == "x")
                                tail = isolator[pos+1:]+isolator[:pos]
                                v = inv(tail) if sign == 1 else tail
                                assert "x" not in v.lower()
                                v = v.translate(str.maketrans("zZ", "xX"))
                                key = (source, axis, d, v)
                                if key in seen:
                                    continue
                                seen.add(key)
                                yield {"source":source,"axis":axis,"cyclic_prefix":prefix,
                                       "cut":cut,"oriented_source":word,"power":d,
                                       "isolator":isolator,"unique_sign":sign,
                                       "recovered_a":v,"companion":normalized[1-source]}


def main():
    start = perf_counter()
    root = Path(__file__).resolve().parents[5]
    rows = list(csv.DictReader((root/"data/ms_unsolved_reps/aca_124_best.csv").open()))
    output_rows = []
    for row in rows:
        pair = (row["r1"],row["r2"])
        candidates = []
        for witness in templates(pair):
            d,v = witness["power"],witness["recovered_a"]
            donor = red("X"+power(v,d))
            companion,choices = run_substitute(witness["companion"],d,v)
            best,trace = nielsen_descent((donor,companion))
            candidates.append({"witness":witness,"block_choices":choices,
                               "raw_endpoint":[donor,companion],"best_pair":best,
                               "best_length":sum(map(len,best)),"nielsen_trace":trace})
        best = min(candidates,key=lambda x:x["best_length"]) if candidates else None
        output_rows.append({"name":row["name"],"input":pair,"input_length":sum(map(len,pair)),
                            "best":best,"candidate_count":len(candidates)})
    output = Path(__file__).with_name("coupled_power_general_compression.json")
    report = {"status":"stable_isolator_macro_witnesses_not_expanded_elementary",
              "wall_seconds":perf_counter()-start,"rows":output_rows}
    output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"output":str(output),"wall_seconds":report["wall_seconds"],
                      "matched_rows":sum(x["best"] is not None for x in output_rows),
                      "candidates":sum(x["candidate_count"] for x in output_rows),
                      "improved":[{"name":x["name"],"before":x["input_length"],"after":x["best"]["best_length"],
                                   "pair":x["best"]["best_pair"]} for x in output_rows
                                  if x["best"] and x["best"]["best_length"]<x["input_length"]]}))


if __name__ == "__main__":
    main()
