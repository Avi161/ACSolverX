"""``keep_path=False`` must change the memory, never the search.

The low-memory mode swaps the parent map for a visited set, which is the trade
``greedy_baseline``'s ``high_speedup`` makes. It is only safe if the *search* is untouched: the same
states discovered, the same pops, the same solve, the same min/max relator statistics. The single
thing allowed to differ is the certificate, which is deliberately not stored.

Both directions matter and both are checked here. ``keep_path=False`` must not leak a path (it
cannot have one, so a non-empty ``path`` would mean the flag is not doing what it says), and
``keep_path=True`` must still return a certificate on every solve (a shared code path could easily
drop it for both modes and nothing else would notice until a results row came back unverifiable).

    python3 -m experiments.heuristic_search.verify_keep_path
"""
import sys
sys.path.insert(0,"/Users/avigyapaudel/Documents/Obsidian Vault/surf/ACSolverX/.claude/worktrees/hsearch-hyper")
from experiments.heuristic_search.hlab import load_split
from experiments.heuristic_search.hsolve import greedy_search_h, RECOMMENDED, LEAN_SMALL_BUDGET
from experiments.heuristic_search.perbin import bin_of

rows = load_split("train")[:6] + [r for r in load_split("train") if bin_of(r["name"]) in (4,5,6,7)][:6]
SAME = ("solved","nodes_explored","path_length","min_relator_length",
        "max_relator_length","max_relator_length_expanded")
bad=[]; nsolved=0; n=0
for cfg,label in ((None,"baseline"),(RECOMMENDED,"recommended"),(LEAN_SMALL_BUDGET,"lean")):
    for r in rows:
        a = greedy_search_h(r["r1"],r["r2"],500,max_relator_length=48,config=cfg,keep_path=True)
        b = greedy_search_h(r["r1"],r["r2"],500,max_relator_length=48,config=cfg,keep_path=False)
        n+=1
        for k in SAME:
            if a[k]!=b[k]:
                bad.append(f"{label}/{r['name']}: {k} {a[k]!r} != {b[k]!r}")
        # keep_path=False must return NO certificate, and keep_path=True must return one when solved
        if b["path"] or b["path_moves"]:
            bad.append(f"{label}/{r['name']}: keep_path=False leaked a path")
        if a["solved"]:
            nsolved+=1
            if not a["path_moves"]:
                bad.append(f"{label}/{r['name']}: keep_path=True lost its certificate")
        if set(a)!=set(b):
            bad.append(f"{label}/{r['name']}: key sets differ")
print(f"{n} paired searches, {nsolved} solved, {len(bad)} discrepancies")
for x in bad[:8]: print("  FAIL", x)
print("IDENTICAL on every scored field" if not bad else "DIVERGENCE")
