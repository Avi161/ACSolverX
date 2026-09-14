"""Bounded nonprimitive literal defining-word stable isolators, no heap."""

from __future__ import annotations

import argparse
import csv
import json
import math
from functools import lru_cache
from pathlib import Path
from time import perf_counter

from ac_words import canon, cyclic, inv, red
from coupled_power_general_compression import red3
from coupled_power_stable_probe import nielsen_descent


def expand(word, images):
    return red3("".join(images[c.lower()] if c.islower() else inv(images[c.lower()]) for c in word))


def decompositions(word, defining, axis, maximum=64):
    inverse = inv(defining)
    @lru_cache(None)
    def visit(pos, remaining):
        if pos == len(word):
            return ("",) if remaining in (0,2) else ()
        out = []
        letter = word[pos]
        cost = 1 if axis and letter.lower() == axis else 0
        if remaining == 2 or cost <= remaining:
            next_remaining = 2 if remaining == 2 else remaining-cost
            out.extend(letter+tail for tail in visit(pos+1,next_remaining))
        for block, token in ((defining,"z"),(inverse,"Z")):
            if word.startswith(block,pos):
                out.extend(token+tail for tail in visit(pos+len(block),remaining))
        return tuple(sorted(set(out),key=lambda w:(len(w),w))[:maximum])
    return visit(0,1 if axis else 2)


def source_words(word, max_defining):
    doubled = word+word
    words = {doubled[i:i+n] for i in range(len(word)) for n in range(2,min(max_defining,len(word))+1)}
    candidates = []
    for w in words:
        if not any(c.lower()=="x" for c in w) or not any(c.lower()=="y" for c in w):
            continue
        primitive_test,_ = nielsen_descent((w,""))
        if sum(map(len,primitive_test)) == 1:
            continue
        candidates.append(w)
    return sorted(candidates,key=lambda w:(len(w),w))


def row_probe(row, limit, max_defining):
    pair = (row["r1"],row["r2"])
    best = None
    attempted = 0
    limit_hit = False
    seen = set()
    for source in (0,1):
        core,prefix = cyclic(pair[source])
        for w in source_words(core,max_defining):
            other_templates = decompositions(pair[1-source],w,None)
            for cut in range(len(core)):
                oriented = core[cut:]+core[:cut]
                for axis in ("x","y"):
                    for isolator0 in decompositions(oriented,w,axis):
                        if "z" not in isolator0.lower():
                            continue
                        isolator = red3(isolator0)
                        if sum(c.lower()==axis for c in isolator) != 1:
                            continue
                        assert expand(isolator,{"x":"x","y":"y","z":w}) == oriented
                        position = next(i for i,c in enumerate(isolator) if c.lower()==axis)
                        sign = 1 if isolator[position].islower() else -1
                        tail = isolator[position+1:]+isolator[:position]
                        v = inv(tail) if sign==1 else tail
                        assert axis not in v.lower()
                        images = {"x":"x","y":"y","z":"z"}
                        images[axis] = v
                        dprime = expand("Z"+w,images)
                        survivor = "y" if axis=="x" else "x"
                        relabel = str.maketrans(survivor+survivor.upper()+"zZ", "yYxX")
                        dprime2 = dprime.translate(relabel)
                        for companion_template in other_templates:
                            assert expand(companion_template,{"x":"x","y":"y","z":w}) == pair[1-source]
                            sprime = expand(companion_template,images)
                            sprime2 = sprime.translate(relabel)
                            key = tuple(sorted((canon(dprime2),canon(sprime2))))
                            if key in seen:
                                continue
                            seen.add(key)
                            if attempted >= limit:
                                limit_hit = True
                                break
                            attempted += 1
                            endpoint,trace = nielsen_descent((dprime2,sprime2))
                            result = {"source":source,"cyclic_prefix":prefix,"cut":cut,
                                      "oriented_source":oriented,"defining_word":w,
                                      "isolator":isolator,"eliminated_axis":axis,
                                      "unique_sign":sign,"recovered_word":v,
                                      "companion_template":companion_template,
                                      "raw_rank2_endpoint":[dprime2,sprime2],
                                      "best_pair":endpoint,"best_length":sum(map(len,endpoint)),
                                      "nielsen_trace":trace,
                                      "recorded_rank3_boundary_max_total_length":max(
                                          sum(map(len,pair))+len(w)+1,
                                          len(isolator)+len(companion_template)+len(w)+1,
                                          len(isolator)+len(sprime)+len(dprime))}
                            if best is None or result["best_length"]<best["best_length"]:
                                best = result
                        if limit_hit: break
                    if limit_hit: break
                if limit_hit: break
            if limit_hit: break
        if limit_hit: break
    return {"name":row["name"],"input":pair,"input_length":sum(map(len,pair)),
            "best":best,"attempted_endpoints":attempted,"limit_hit":limit_hit}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--ids",default="aca_9,aca_116,aca_117")
    parser.add_argument("--limit",type=int,default=500)
    parser.add_argument("--max-defining",type=int,default=6)
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[5]
    rows=list(csv.DictReader((root/"data/ms_unsolved_reps/aca_124_best.csv").open()))
    if args.ids != "all":
        ids=set(args.ids.split(","))
        rows=[r for r in rows if r["name"] in ids]
        assert {r["name"] for r in rows} == ids
    start=perf_counter()
    results=[row_probe(row,args.limit,args.max_defining) for row in rows]
    report={"status":"theorem_backed_stable_macro_witnesses_not_elementary_expanded",
            "row_limit":args.limit,"max_defining_length":args.max_defining,
            "wall_seconds":perf_counter()-start,"rows":results}
    suffix="all124" if args.ids=="all" else "panel"
    output=Path(__file__).with_name(f"coupled_power_word_compression_{suffix}.json")
    output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"output":str(output),"wall_seconds":report["wall_seconds"],
                      "rows":len(results),"attempted":sum(x["attempted_endpoints"] for x in results),
                      "limit_hits":sum(x["limit_hit"] for x in results),
                      "improvements":[{"name":x["name"],"before":x["input_length"],
                                       "after":x["best"]["best_length"],"pair":x["best"]["best_pair"]}
                                      for x in results if x["best"] and x["best"]["best_length"]<x["input_length"]]}))


if __name__=="__main__":
    main()
