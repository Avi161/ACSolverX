"""Summary of the rank-3 brute-force sweep: the comparisons fixed in PLAN.md §6.

Reads one results directory (control jsonl, one npz per word length, the
relator-subword jsonl) and writes, next to them,

* ``<stem>_summary.json`` / ``<stem>_summary.md``: every table below,
* ``<stem>_per_presentation.csv``: one line per presentation,
* ``<stem>_per_word.csv``: one line per z-word (presentations it solves).

Every statistic that mixes presentations is computed per presentation first and
then averaged, so presentations with many easy words cannot carry it. "Oracle"
rows pick the best word per presentation after the fact: they say a word
exists, not that a method finds it; the "price" rows charge for the search.

A word that is a full cyclic rotation of ``r_i^±1`` is the control in disguise
(one move turns ``Z·w`` into ``Z``), so the faster / same / slower split is also
given without those words.

``--cov`` takes a ``cov_all`` jsonl(.gz) at a budget >= this one; its rows are
cut back to this budget by the prefix property (solved within B <=> solved and
nodes <= B), which gives the CoV columns and the control at larger budgets.

CLI (repo root, ``PYTHONPATH=.``):
    python3 -m experiments.stable_ac.rank3.summarize_rank3_bf --budget 1000 \
        --cov results/stable_ac/cov_all/cov_all_suballpxyb8_ms640_b100000.jsonl.gz
"""

import argparse
import csv
import gzip
import json
import os

import numpy as np

from experiments.stable_ac.rank3 import words as W
from experiments.stable_ac.rank3.run_rank3_bf import (
    CAP, OUT_DIR, find_repo_root, load_ms640, stem,
)
from experiments.stable_ac.solvern import str_to_word, word_to_str


def _rows(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as f:
        return [json.loads(ln) for ln in f if ln.strip()]


def _first(*paths):
    for p in paths:
        if os.path.exists(p):
            return p
    return None


def _pct(x):
    return f"{100 * x:.1f}%"


def _mean(a):
    a = np.asarray(a, dtype=float)
    return float(a.mean()) if a.size else None


def _median(a):
    a = np.asarray(a, dtype=float)
    return float(np.median(a)) if a.size else None


def load(d, base):
    ctrl = {r["pres_id"]: r for r in _rows(base + "_control.jsonl")}
    lengths, n = {}, 1
    while os.path.exists(f"{base}_L{n}.npz"):
        with np.load(f"{base}_L{n}.npz") as z:
            lengths[n] = {"nodes": z["nodes"].astype(np.int32),
                          "plen": z["path_len"].astype(np.int32),
                          "secs": float(z["block_seconds"].sum()),
                          "pres_ids": [int(p) for p in z["pres_ids"]]}
        n += 1
    inv, n = {}, 1
    while os.path.exists(f"{base}_L{n}_inv.npz"):
        with np.load(f"{base}_L{n}_inv.npz") as z:
            inv[n] = {"nodes": z["nodes"].astype(np.int32),
                      "plen": z["path_len"].astype(np.int32)}
        n += 1
    sub_path = _first(base + "_relsub.jsonl", base + "_relsub.jsonl.gz")
    sub = _rows(sub_path) if sub_path else []
    return ctrl, lengths, inv, sub


def cov_tables(path, budget, pres_ids):
    """Per presentation, from a cov_all file cut back to ``budget``:
    control (solved, nodes) at the file's own budget, and per folded z-word the
    fewest nodes of any CoV class built from it that solves within ``budget``."""
    ctrl_big, best, by_word, has_row, caps = {}, {}, {}, {}, []
    file_budget = None
    for r in _rows(path):
        p = r["pres_id"]
        file_budget = r["node_budget"]
        if r.get("is_control"):
            ctrl_big[p] = (bool(r["solved"]), r["nodes_explored"])
            continue
        # one row per class of CoV outputs; z_word is the class representative
        w = word_to_str(W.fold(str_to_word(r["z_word"])))
        has_row.setdefault(p, set()).add(w)
        caps.append(r["max_relator_length_cap"])
        if r["solved"] and r["nodes_explored"] <= budget:
            n = r["nodes_explored"]
            if n < best.get(p, 10 ** 9):
                best[p] = n
            d = by_word.setdefault(p, {})
            if n < d.get(w, 10 ** 9):
                d[w] = n
    assert file_budget is None or file_budget >= budget, "cov file budget too small"
    return {"budget": file_budget, "ctrl": ctrl_big, "best": best,
            "by_word": by_word, "has_row": has_row,
            "median_cap": float(np.median(caps)) if caps else None,
            "n_pres": len({p for p in pres_ids if p in ctrl_big})}


def summarize(d, source, budget, cap, cov_path=None, dataset="data/ms640_solved.txt"):
    base = os.path.join(d, stem(source, budget, cap))
    ctrl, lengths, inv, sub = load(d, base)
    pres_ids = lengths[1]["pres_ids"]
    P, L = len(pres_ids), max(lengths)
    ms = {p: (r1, r2) for p, r1, r2 in load_ms640(dataset)}
    c_solved = np.array([ctrl[p]["solved"] for p in pres_ids])
    c_nodes = np.array([ctrl[p]["nodes_explored"] for p in pres_ids])
    views = [b for b in (100, 1000, 10000) if b <= budget]
    words = {n: [word_to_str(w) for w in W.words_of_length(n)] for n in lengths}
    index = {n: {w: k for k, w in enumerate(words[n])} for n in lengths}

    # which (presentation, word) are relator subwords, per length; is_rot marks
    # the full rotations of a relator
    is_sub = {n: np.zeros((P, W.n_words(n)), dtype=bool) for n in lengths}
    is_rot = {n: np.zeros((P, W.n_words(n)), dtype=bool) for n in lengths}
    for i, p in enumerate(pres_ids):
        for w, proper in W.relator_subwords(*ms[p]):
            if len(w) in lengths:
                k = index[len(w)][word_to_str(w)]
                is_sub[len(w)][i, k] = True
                is_rot[len(w)][i, k] = not proper

    out = {"source": source, "node_budget": budget, "max_relator_length_cap": cap,
           "n_presentations": P, "max_len": L,
           "n_words_per_presentation": sum(W.n_words(n) for n in lengths),
           "n_searches": int(sum(v["nodes"].size for v in lengths.values())),
           "core_seconds": sum(v["secs"] for v in lengths.values()),
           "views": {}}

    for b in views:
        cs = c_solved & (c_nodes <= b)
        v = {"control_solved": int(cs.sum()), "by_length": [], "oracle": []}
        any_solved = np.zeros(P, dtype=bool)
        any_faster = np.zeros(P, dtype=bool)
        best_nodes = np.full(P, 10 ** 9)
        best_word = [None] * P
        dove_nodes = np.zeros(P, dtype=np.int64)   # nodes spent in shortlex order
        dove_done = np.zeros(P, dtype=bool)
        per_word = []
        tot = {k: np.zeros(P) for k in ("solved", "faster", "equal", "slower")}
        tot_sub = {k: np.zeros(P) for k in ("n", "solved", "faster")}
        tot_non = {k: np.zeros(P) for k in ("n", "solved", "faster")}
        tot_rot = {k: np.zeros(P) for k in ("n", "solved", "faster", "equal",
                                            "slower", "extra")}
        any_faster_norot = np.zeros(P, dtype=bool)
        n_all = 0
        for n in sorted(lengths):
            N, pl = lengths[n]["nodes"], lengths[n]["plen"]
            S = (pl >= 0) & (N <= b)
            spent = np.minimum(N, b)            # pops used within budget b
            faster = S & (N < c_nodes[:, None]) & cs[:, None]
            equal = S & (N == c_nodes[:, None]) & cs[:, None]
            slower = S & (N > c_nodes[:, None]) & cs[:, None]
            wn = W.n_words(n)
            n_all += wn
            for k, a in (("solved", S), ("faster", faster), ("equal", equal),
                         ("slower", slower)):
                tot[k] += a.sum(axis=1)
            sb = is_sub[n]
            for t, m in ((tot_sub, sb), (tot_non, ~sb)):
                t["n"] += m.sum(axis=1)
                t["solved"] += (S & m).sum(axis=1)
                t["faster"] += (faster & m).sum(axis=1)
            rt = is_rot[n]
            tot_rot["n"] += rt.sum(axis=1)
            for k, a in (("solved", S), ("faster", faster), ("equal", equal),
                         ("slower", slower)):
                tot_rot[k] += (a & rt).sum(axis=1)
            tot_rot["extra"] += np.where(S & rt & cs[:, None],
                                         N - c_nodes[:, None], 0).sum(axis=1)
            any_faster_norot |= (faster & ~rt).any(axis=1)
            frac = S.mean(axis=1)
            row = {
                "len": n, "n_words": wn,
                "solve_rate": _mean(frac),
                "solve_rate_control_solved": _mean(frac[cs]),
                "solve_rate_control_unsolved": _mean(frac[~cs]),
                "faster": _mean(faster.mean(axis=1)[cs]),
                "equal": _mean(equal.mean(axis=1)[cs]),
                "slower": _mean(slower.mean(axis=1)[cs]),
                "lost": _mean((~S).mean(axis=1)[cs]),
                "median_extra_nodes": _median(
                    [np.median((N[i] - c_nodes[i])[S[i]])
                     for i in range(P) if cs[i] and S[i].any()]),
                "mean_presentations_per_word": float(S.sum(axis=0).mean()),
                "best_single_word": words[n][int(S.sum(axis=0).argmax())],
                "best_single_word_solves": int(S.sum(axis=0).max()),
                "words_beating_control": int((S.sum(axis=0) > cs.sum()).sum()),
                "ms_per_search": 1000 * lengths[n]["secs"] / N.size,
            }
            v["by_length"].append(row)
            for k in range(wn):
                per_word.append((n, k, int(S[:, k].sum()),
                                 int((S[:, k] & ~cs).sum()),
                                 int((~S[:, k] & cs).sum()),
                                 int(faster[:, k].sum())))
            # oracle and its price, cumulative in shortlex order
            any_solved |= S.any(axis=1)
            any_faster |= faster.any(axis=1)
            masked = np.where(S, N, 10 ** 9)
            k_best = masked.argmin(axis=1)
            for i in range(P):
                if masked[i, k_best[i]] < best_nodes[i]:
                    best_nodes[i] = masked[i, k_best[i]]
                    best_word[i] = words[n][k_best[i]]
                if not dove_done[i]:
                    if S[i].any():
                        first = int(S[i].argmax())
                        dove_nodes[i] += spent[i, :first + 1].sum()
                        dove_done[i] = True
                    else:
                        dove_nodes[i] += spent[i].sum()
            v["oracle"].append({
                "max_len": n, "words": n_all,
                "solved_by_some_word": int(any_solved.sum()),
                "gained_over_control": int((any_solved & ~cs).sum()),
                "control_solved_lost_by_every_word": int((cs & ~any_solved).sum()),
                "some_word_faster_than_control": int(any_faster.sum()),
                "some_non_rotation_word_faster": int(any_faster_norot.sum()),
            })
        v["overall"] = {
            k: _mean((tot[k] / n_all)[cs]) for k in ("faster", "equal", "slower")}
        v["overall"]["lost"] = _mean((1 - tot["solved"] / n_all)[cs])
        v["overall"]["solve_rate"] = _mean(tot["solved"] / n_all)
        v["overall"]["solve_rate_control_unsolved"] = _mean(
            (tot["solved"] / n_all)[~cs])
        n_norot = n_all - tot_rot["n"]
        v["overall_without_relator_rotations"] = {
            k: _mean(((tot[k] - tot_rot[k]) / n_norot)[cs])
            for k in ("faster", "equal", "slower")}
        v["overall_without_relator_rotations"]["lost"] = _mean(
            (1 - (tot["solved"] - tot_rot["solved"]) / n_norot)[cs])
        nr = int(tot_rot["n"].sum())
        nrs = float((tot_rot["faster"] + tot_rot["equal"] + tot_rot["slower"]).sum())
        v["relator_rotations"] = {
            "rows": nr, "solved": int(tot_rot["solved"].sum()),
            "faster": int(tot_rot["faster"].sum()),
            "equal": int(tot_rot["equal"].sum()),
            "slower": int(tot_rot["slower"].sum()),
            "mean_extra_nodes_when_both_solve":
                float(tot_rot["extra"].sum() / nrs) if nrs else None}
        ok = tot_sub["n"] > 0
        v["subword_vs_other_within_bf"] = {
            "presentations_with_a_subword": int(ok.sum()),
            "subword_solve_rate": _mean((tot_sub["solved"] / np.maximum(
                tot_sub["n"], 1))[ok]),
            "other_solve_rate": _mean((tot_non["solved"] / tot_non["n"])[ok]),
            "subword_faster_than_control": _mean((tot_sub["faster"] / np.maximum(
                tot_sub["n"], 1))[ok & cs]),
            "other_faster_than_control": _mean(
                (tot_non["faster"] / tot_non["n"])[ok & cs]),
        }
        # price of the oracle: shortlex until the first solve, against the
        # control given the same number of nodes
        v["price"] = {
            "solved_in_shortlex_order": int(dove_done.sum()),
            "median_nodes_to_first_solve": _median(dove_nodes[dove_done]),
            "control_nodes_median_same_presentations": _median(
                c_nodes[dove_done & cs]),
            "presentations_where_shortlex_beats_control": int(
                (dove_done & (~cs | (dove_nodes < c_nodes))).sum()),
        }
        # one fixed word for every presentation, chosen on one half
        even = np.array([p % 2 == 0 for p in pres_ids])
        folds = []
        for tr, te, name in ((even, ~even, "even->odd"), (~even, even, "odd->even")):
            bestk, bests = None, -1
            for n in sorted(lengths):
                S = (lengths[n]["plen"] >= 0) & (lengths[n]["nodes"] <= b)
                s = S[tr].sum(axis=0)
                if s.max() > bests:
                    bests, bestk = int(s.max()), (n, int(s.argmax()))
            n, k = bestk
            S = (lengths[n]["plen"] >= 0) & (lengths[n]["nodes"] <= b)
            folds.append({"fold": name, "word": words[n][k],
                          "train_solved": bests, "train_control": int(cs[tr].sum()),
                          "test_solved": int(S[te, k].sum()),
                          "test_control": int(cs[te].sum()),
                          "test_presentations": int(te.sum())})
        v["fixed_word_cross_validated"] = folds
        pw = sorted(per_word, key=lambda t: (-t[2], t[0], t[1]))
        v["top_words"] = [{"word": words[n][k], "len": n, "solved": s,
                           "gained": g, "lost": lo, "faster": f}
                          for n, k, s, g, lo, f in pw[:15]]
        v["words_beating_control"] = int(sum(t[2] > cs.sum() for t in per_word))
        v["words_matching_control"] = int(sum(t[2] == cs.sum() for t in per_word))
        v["_per_word"] = per_word
        v["_per_pres"] = {"cs": cs, "tot": tot, "n_all": n_all,
                          "any_solved": any_solved, "best_nodes": best_nodes,
                          "best_word": best_word, "dove_nodes": dove_nodes,
                          "dove_done": dove_done}
        out["views"][b] = v

    # inverse-pair check: w against w^-1, same index
    if inv:
        same = flips = n_pairs = 0
        diffs = []
        for n in inv:
            a, bb = lengths[n], inv[n]
            sa, sb_ = a["plen"] >= 0, bb["plen"] >= 0
            n_pairs += sa.size
            flips += int((sa != sb_).sum())
            same += int(((sa == sb_) & (a["nodes"] == bb["nodes"])).sum())
            both = sa & sb_
            diffs.append(np.abs(a["nodes"] - bb["nodes"])[both])
        diffs = np.concatenate(diffs)
        out["inverse_pairs"] = {
            "max_len": max(inv), "pairs": n_pairs, "identical": same,
            "solved_status_differs": flips,
            "mean_abs_node_difference_both_solved": _mean(diffs),
            "p99_abs_node_difference_both_solved": float(np.percentile(diffs, 99)),
        }

    # relator-subword arm, and CoV on the same words
    cov = cov_tables(cov_path, budget, pres_ids) if cov_path else None
    if cov:
        out["control_at_larger_budgets"] = {
            str(bb): sum(1 for p in pres_ids if cov["ctrl"].get(p, (False, 0))[0]
                         and cov["ctrl"][p][1] <= bb)
            for bb in (100, 1000, 10000, 100000) if bb <= cov["budget"]}
        b = budget
        v = out["views"][b]
        pp = v["_per_pres"]
        gained = [i for i in range(P) if pp["any_solved"][i] and not pp["cs"][i]]
        big = [cov["ctrl"].get(pres_ids[i], (False, 0)) for i in gained]
        v["gained_presentations_priced"] = {
            "gained_at_this_budget": len(gained),
            "control_file_budget": cov["budget"],
            "control_solves_them_at_file_budget": sum(s for s, _ in big),
            "best_word_cheaper_than_control": sum(
                1 for i, (s, n) in zip(gained, big)
                if not s or pp["best_nodes"][i] < n),
            "shortlex_to_first_solve_cheaper_than_control": sum(
                1 for i, (s, n) in zip(gained, big)
                if not s or pp["dove_nodes"][i] < n),
            "rows": [{"pres_id": int(pres_ids[i]), "best_word": pp["best_word"][i],
                      "best_word_nodes": int(pp["best_nodes"][i]),
                      "shortlex_nodes": int(pp["dove_nodes"][i]),
                      "control_solved": bool(s), "control_nodes": int(n)}
                     for i, (s, n) in zip(gained, big)]}
    subs = {}
    for r in sub:
        subs.setdefault(r["pres_id"], []).append(r)
    if subs:
        cs = c_solved
        at = {p: i for i, p in enumerate(pres_ids)}
        rs = {"rows": len(sub), "rows_proper": sum(r["is_proper"] for r in sub)}
        for name, keep in (("proper", lambda r: r["is_proper"]),
                           ("all", lambda r: True)):
            solved_any, faster_any, fr, ff, gained = 0, 0, [], [], 0
            for p in pres_ids:
                rows = [r for r in subs.get(p, []) if keep(r)]
                if not rows:
                    continue
                s = [r for r in rows if r["solved"]]
                i = at[p]
                solved_any += bool(s)
                gained += bool(s) and not cs[i]
                fr.append(len(s) / len(rows))
                if cs[i]:
                    f = [r for r in s if r["nodes_explored"] < c_nodes[i]]
                    faster_any += bool(f)
                    ff.append(len(f) / len(rows))
            rs[name] = {"solved_by_some_subword": solved_any,
                        "gained_over_control": gained,
                        "mean_solve_rate": _mean(fr),
                        "some_subword_faster_than_control": faster_any,
                        "mean_fraction_faster_than_control": _mean(ff)}
        if cov:
            r3 = {p for p in pres_ids
                  if any(r["solved"] and r["is_proper"] for r in subs.get(p, []))}
            cv = set(cov["best"]) & set(pres_ids)
            ctl = {p for i, p in enumerate(pres_ids) if cs[i]}
            wins = ties = losses = only_r3 = only_cov = joined = neither = 0
            for p in pres_ids:
                bw = cov["by_word"].get(p, {})
                hr = cov["has_row"].get(p, set())
                for r in subs.get(p, []):
                    # a word with no CoV row is either not a CoV (no generator
                    # can be isolated) or its outputs are filed under another word
                    if not r["is_proper"] or r["z_word"] not in hr:
                        continue
                    joined += 1
                    a = r["nodes_explored"] if r["solved"] else None
                    c = bw.get(r["z_word"])
                    if a is None and c is None:
                        neither += 1
                        continue
                    if c is None:
                        only_r3 += 1
                    elif a is None:
                        only_cov += 1
                    elif a < c:
                        wins += 1
                    elif a == c:
                        ties += 1
                    else:
                        losses += 1
            rs["vs_cov"] = {
                "cov_file_budget": cov["budget"],
                "cov_median_cap": cov["median_cap"],
                "same_word_pairs_joined": joined, "same_word_neither": neither,
                "control": len(ctl), "rank3_subword_oracle": len(r3),
                "cov_oracle": len(cv), "control_or_rank3": len(ctl | r3),
                "control_or_cov": len(ctl | cv),
                "rank3_not_cov": len(r3 - cv), "cov_not_rank3": len(cv - r3),
                "same_word_rank3_fewer_nodes": wins, "same_word_tie": ties,
                "same_word_cov_fewer_nodes": losses,
                "same_word_only_rank3_solves": only_r3,
                "same_word_only_cov_solves": only_cov}
        out["relsub"] = rs
    return out, pres_ids, ctrl, words, cov, subs


def write(out, pres_ids, ctrl, words, cov, subs, base):
    b = out["node_budget"]
    v = out["views"][b]
    pp = v.pop("_per_pres")
    per_word = v.pop("_per_word")
    for vv in out["views"].values():
        vv.pop("_per_pres", None)
        vv.pop("_per_word", None)
    with open(base + "_per_word.csv", "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["z_word", "len", "presentations_solved", "gained_over_control",
                     "lost_vs_control", "faster_than_control"])
        for n, k, s, g, lo, fa in per_word:
            wr.writerow([words[n][k], n, s, g, lo, fa])
    with open(base + "_per_presentation.csv", "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["pres_id", "r1", "r2", "control_solved", "control_nodes",
                     "control_path_length", "words", "words_solved",
                     "words_faster", "words_equal", "words_slower",
                     "best_word", "best_word_nodes", "shortlex_nodes_to_first_solve",
                     "subwords", "subwords_solved", "best_subword",
                     "best_subword_nodes", "cov_best_nodes"])
        for i, p in enumerate(pres_ids):
            c = ctrl[p]
            sr = subs.get(p, [])
            ss = sorted((r for r in sr if r["solved"]),
                        key=lambda r: (r["nodes_explored"], r["z_len"], r["z_word"]))
            wr.writerow([
                p, c["r1"], c["r2"], int(c["solved"]), c["nodes_explored"],
                c["path_length"], pp["n_all"], int(pp["tot"]["solved"][i]),
                int(pp["tot"]["faster"][i]), int(pp["tot"]["equal"][i]),
                int(pp["tot"]["slower"][i]), pp["best_word"][i] or "",
                int(pp["best_nodes"][i]) if pp["any_solved"][i] else "",
                int(pp["dove_nodes"][i]) if pp["dove_done"][i] else "",
                len(sr), len(ss), ss[0]["z_word"] if ss else "",
                ss[0]["nodes_explored"] if ss else "",
                cov["best"].get(p, "") if cov else ""])
    with open(base + "_summary.json", "w") as f:
        json.dump(out, f, indent=1)

    P = out["n_presentations"]
    md = [f"# Rank-3 brute force on {out['source']}: budget {b:,}, cap "
          f"{out['max_relator_length_cap']}, every z-word to length {out['max_len']}",
          "",
          f"{out['n_searches']:,} searches: {out['n_words_per_presentation']:,} "
          f"words on each of {P} presentations, {out['core_seconds'] / 3600:.0f} "
          f"core-hours. Start `<x,y,z | r1, r2, Z·w>`; control `<x,y | r1, r2>` "
          f"(identical to the null stabilization). Percentages are means over "
          f"presentations of the per-presentation fraction of words.", ""]
    for bb, vv in out["views"].items():
        md += [f"## At {bb:,} nodes (control solves {vv['control_solved']}/{P})", "",
               "| \\|w\\| | words | solved | on control-solved | on control-unsolved "
               "| faster than control | same | slower | lost | best single word "
               "(solves) |", "|---|---|---|---|---|---|---|---|---|---|"]
        for r in vv["by_length"]:
            cu = r["solve_rate_control_unsolved"]
            md.append(
                f"| {r['len']} | {r['n_words']:,} | {_pct(r['solve_rate'])} | "
                f"{_pct(r['solve_rate_control_solved'])} | "
                f"{_pct(cu) if cu is not None else '–'} | {_pct(r['faster'])} | "
                f"{_pct(r['equal'])} | {_pct(r['slower'])} | {_pct(r['lost'])} | "
                f"`{r['best_single_word']}` ({r['best_single_word_solves']}) |")
        o = vv["overall"]
        md += ["", f"All lengths together, on control-solved presentations: "
               f"faster {_pct(o['faster'])}, same {_pct(o['equal'])}, slower "
               f"{_pct(o['slower'])}, lost {_pct(o['lost'])}.", ""]
        o2, rr = vv["overall_without_relator_rotations"], vv["relator_rotations"]
        md += [f"Without the {rr['rows']:,} (presentation, word) pairs where w "
               f"is a whole rotation of a relator (the control in disguise: "
               f"{rr['faster']} faster, {rr['equal']} same, {rr['slower']} "
               f"slower): faster {_pct(o2['faster'])}, same {_pct(o2['equal'])}, "
               f"slower {_pct(o2['slower'])}, lost {_pct(o2['lost'])}.", "",
               "| words up to | words | solved by some word (oracle) | gained over "
               "control | some word faster than control | some word that is not "
               "a relator rotation faster |", "|---|---|---|---|---|---|"]
        for r in vv["oracle"]:
            md.append(f"| {r['max_len']} | {r['words']:,} | "
                      f"{r['solved_by_some_word']} | {r['gained_over_control']} | "
                      f"{r['some_word_faster_than_control']} | "
                      f"{r['some_non_rotation_word_faster']} |")
        pr = vv["price"]
        md += ["", f"Price of the oracle: running the words in shortlex order "
               f"until the first solve reaches {pr['solved_in_shortlex_order']} "
               f"presentations, median {pr['median_nodes_to_first_solve']:.0f} "
               f"nodes; it is cheaper than the control (or solves where the "
               f"control does not) on "
               f"{pr['presentations_where_shortlex_beats_control']}.", "",
               f"One fixed word for all presentations: "
               f"{vv['words_beating_control']} words solve more presentations "
               f"than the control, {vv['words_matching_control']} the same. "
               "Chosen on one half, scored on the other:", ""]
        for fo in vv["fixed_word_cross_validated"]:
            md.append(f"- {fo['fold']}: `{fo['word']}` solves {fo['test_solved']}/"
                      f"{fo['test_presentations']}, control {fo['test_control']}.")
        sv = vv["subword_vs_other_within_bf"]
        md += ["", f"Words that are a subword of a relator of their presentation "
               f"solve {_pct(sv['subword_solve_rate'])} and are faster than the "
               f"control {_pct(sv['subword_faster_than_control'])} of the time; "
               f"the other words {_pct(sv['other_solve_rate'])} and "
               f"{_pct(sv['other_faster_than_control'])}.", ""]
        if "gained_presentations_priced" in vv:
            g = vv["gained_presentations_priced"]
            md += [f"The {g['gained_at_this_budget']} presentations some word "
                   f"solves and the control does not, against the control at "
                   f"{g['control_file_budget']:,} nodes: the control solves "
                   f"{g['control_solves_them_at_file_budget']} of them; the best "
                   f"word (hindsight) uses fewer nodes than the control on "
                   f"{g['best_word_cheaper_than_control']}, and the words run in "
                   f"shortlex order until the first solve on "
                   f"{g['shortlex_to_first_solve_cheaper_than_control']}.", ""]
    if "inverse_pairs" in out:
        ip = out["inverse_pairs"]
        md += [f"## w against w⁻¹ (to length {ip['max_len']})", "",
               f"{ip['identical']:,} of {ip['pairs']:,} pairs give the same "
               f"result; solved status differs on {ip['solved_status_differs']:,}; "
               f"mean node difference when both solve "
               f"{ip['mean_abs_node_difference_both_solved']:.1f}.", ""]
    if "relsub" in out:
        rs = out["relsub"]
        md += ["## Relator subwords (the CoV word set, searched in rank 3)", "",
               f"{rs['rows']:,} rows, {rs['rows_proper']:,} in the CoV family.", ""]
        for name in ("proper", "all"):
            r = rs[name]
            md.append(f"- {name}: some subword solves "
                      f"{r['solved_by_some_subword']}/{P} "
                      f"(gained over control {r['gained_over_control']}), mean "
                      f"solve rate {_pct(r['mean_solve_rate'])}, faster than "
                      f"control {_pct(r['mean_fraction_faster_than_control'])}.")
        if "vs_cov" in rs:
            c = rs["vs_cov"]
            md += ["", "| | presentations solved |", "|---|---|",
                   f"| control | {c['control']} |",
                   f"| rank 3, some relator subword | {c['rank3_subword_oracle']} |",
                   f"| CoV, some class | {c['cov_oracle']} |",
                   f"| control or rank 3 | {c['control_or_rank3']} |",
                   f"| control or CoV | {c['control_or_cov']} |", "",
                   f"Same presentation and same word, on the "
                   f"{c['same_word_pairs_joined']:,} (presentation, word) pairs "
                   f"that have a CoV row (CoV keeps one row per class of outputs, "
                   f"under one representative word): rank 3 uses fewer nodes "
                   f"than the best CoV start {c['same_word_rank3_fewer_nodes']:,} "
                   f"times, the same {c['same_word_tie']:,}, more "
                   f"{c['same_word_cov_fewer_nodes']:,}; only rank 3 solves "
                   f"{c['same_word_only_rank3_solves']:,}, only CoV "
                   f"{c['same_word_only_cov_solves']:,}, neither "
                   f"{c['same_word_neither']:,}. CoV rows ran at cap "
                   f"max(24, longest relator + 16), median "
                   f"{c['cov_median_cap']:.0f}; rank 3 at cap "
                   f"{out['max_relator_length_cap']}.", ""]
    if "control_at_larger_budgets" in out:
        md += ["Control at larger budgets: " + ", ".join(
            f"{v_} at {int(k):,}" for k, v_ in
            out["control_at_larger_budgets"].items()) + ".", ""]
    with open(base + "_summary.md", "w") as f:
        f.write("\n".join(md))
    return "\n".join(md)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=OUT_DIR)
    ap.add_argument("--source", default="ms640")
    ap.add_argument("--budget", type=int, required=True)
    ap.add_argument("--cap", type=int, default=CAP)
    ap.add_argument("--cov", default=None)
    ap.add_argument("--dataset", default="data/ms640_solved.txt")
    a = ap.parse_args(argv)
    d = os.path.abspath(a.dir)
    cov = os.path.abspath(a.cov) if a.cov else None
    os.chdir(find_repo_root(os.path.dirname(os.path.abspath(__file__))))
    res = summarize(d, a.source, a.budget, a.cap, cov, a.dataset)
    print(write(*res, os.path.join(d, stem(a.source, a.budget, a.cap))))


if __name__ == "__main__":
    main()
