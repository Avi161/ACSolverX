#!/usr/bin/env python3
"""Two-block relative-basis search with a proper AC-trivial stabilizer tuple V."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import deque
from itertools import product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import search_two_block_relative_basis as b


def substitute_image(word, pattern, image):
    """Cyclic nonoverlap replacement of pattern/image and inverse pattern/inverse image."""
    marker = 9
    # Reuse the audited matching routine with a fresh marker, then expand it.
    marked, count = b.substitute(word, pattern, marker)
    out = []
    for a in marked:
        if a == marker:
            out.extend(image)
        elif a == -marker:
            out.extend(b.inv(image))
        else:
            out.append(a)
    return b.red(out), count


def ac_children(pair):
    for i in range(2):
        child = list(pair)
        child[i] = b.inv(child[i])
        yield tuple(child), ("invert", i)
    for i in range(2):
        j = 1-i
        child = list(pair)
        child[i] = b.red(child[i] + child[j])
        yield tuple(child), ("multiply_right", i, j)
    for i in range(2):
        for a in (3, -3, 4, -4):
            child = list(pair)
            child[i] = b.red((-a,) + child[i] + (a,))
            yield tuple(child), ("conjugate", i, a)


def basis2(pair):
    cur = tuple(b.red(w) for w in pair)
    while sum(map(len, cur)) > 2:
        total = sum(map(len, cur))
        best = None
        for i in range(2):
            j = 1-i
            for sign in (1, -1):
                for side in ("L", "R"):
                    other = cur[j] if sign == 1 else b.inv(cur[j])
                    child = list(cur)
                    child[i] = b.red((other+cur[i]) if side == "L" else (cur[i]+other))
                    key = (sum(map(len, child)), tuple(child), i, sign, side)
                    if key[0] < total and (best is None or key < best):
                        best = key
        if best is None:
            return False
        cur = best[1]
    return all(len(w) == 1 for w in cur) and {abs(w[0]) for w in cur} == {3,4}


def ac_ball(max_depth, max_total):
    start = ((3,), (4,))
    records = {start: ()}
    frontier = [start]
    for _ in range(max_depth):
        nxt = []
        for pair in frontier:
            for child, move in ac_children(pair):
                if sum(map(len, child)) > max_total or child in records:
                    continue
                records[child] = records[pair] + (move,)
                nxt.append(child)
        frontier = nxt
    return [(pair, moves) for pair,moves in records.items() if not basis2(pair)]


def search_row(row, v_records, max_def_len):
    original = (b.parse(row["r1"]), b.parse(row["r2"]))
    defs = b.cyclic_subwords(original, max_def_len)
    tested = bases = coupled = 0
    hits = []
    for (v1,v2), vmoves in v_records:
        for u1,u2 in product(defs, repeat=2):
            if u1 == u2:
                continue
            q1,n11 = substitute_image(original[0],u1,v1)
            q2,n12 = substitute_image(original[1],u1,v1)
            q1,n21 = substitute_image(q1,u2,v2)
            q2,n22 = substitute_image(q2,u2,v2)
            if n11+n12 == 0 or n21+n22 == 0:
                continue
            tested += 1
            cert = b.nielsen_basis((q1,q2,(3,),(4,)))
            if cert is None:
                continue
            bases += 1
            moves, inverse_images, endpoint = cert
            basis = (q1,q2,(3,),(4,))
            if tuple(b.apply_hom(w,inverse_images) for w in basis) != ((1,),(2,),(3,),(4,)):
                raise AssertionError("inverse replay")
            ex = b.specialize_old(inverse_images[0])
            ey = b.specialize_old(inverse_images[1])
            images = (ex,ey,(3,),(4,))
            d1 = b.cyc(b.inv(v1)+b.apply_hom(u1,images))
            d2 = b.cyc(b.inv(v2)+b.apply_hom(u2,images))
            if not d1 or not d2:
                continue
            target = tuple(tuple(a-2 if a>0 else a+2 for a in w) for w in (d1,d2))
            is_coupled = all(b.old_count(q,1) != 1 and b.old_count(q,2) != 1 for q in (q1,q2))
            coupled += int(is_coupled)
            hits.append({
                "name":row["name"], "source":[row["r1"],row["r2"]],
                "V":[b.text(v1),b.text(v2)], "V_ac_certificate":[list(m) for m in vmoves],
                "definitions":[b.text(u1),b.text(u2)],
                "substitution_counts":[n11+n12,n21+n22],
                "compressed":[b.text(q1),b.text(q2)], "coupled":is_coupled,
                "relative_basis_moves":[list(m) for m in moves],
                "inverse_images":[b.text(w) for w in inverse_images],
                "solutions":[b.text(ex),b.text(ey)], "target":[b.text(w) for w in target],
                "source_raw":sum(map(len,original)), "target_raw":sum(map(len,target)),
            })
    return {"name":row["name"],"definition_words":len(defs),"tested":tested,
            "relative_bases":bases,"coupled_relative_bases":coupled},hits


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--data',required=True); ap.add_argument('--out',required=True)
    ap.add_argument('--max-def-len',type=int,default=4)
    ap.add_argument('--v-depth',type=int,default=2); ap.add_argument('--v-max-total',type=int,default=8)
    ap.add_argument('--only')
    a=ap.parse_args()
    vs=ac_ball(a.v_depth,a.v_max_total)
    print(json.dumps({'proper_V':len(vs)}),flush=True)
    summaries=[]; hits=[]
    selected=set(a.only.split(',')) if a.only else None
    with open(a.data,newline='') as f:
        for row in csv.DictReader(f):
            if selected and row['name'] not in selected: continue
            summary,found=search_row(row,vs,a.max_def_len)
            summaries.append(summary);hits.extend(found);print(json.dumps(summary),flush=True)
    payload={'schema':'two-block-proper-v-v1','v_depth':a.v_depth,'v_max_total':a.v_max_total,
             'max_def_len':a.max_def_len,'proper_V_count':len(vs),'summaries':summaries,'hits':hits}
    Path(a.out).write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'rows':len(summaries),'hits':len(hits),'coupled':sum(h['coupled'] for h in hits),
                      'raw_descents':sum(h['target_raw']<h['source_raw'] for h in hits)}))


if __name__=='__main__': main()
