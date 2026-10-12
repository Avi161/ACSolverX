"""Relabeling-class view of the rank-3/4/5 sweeps against the control.

MS640 lists most presentations more than once: as signed relabelings of the
generators (x <-> y, x -> X, y -> Y), up to the order, rotation and inversion
of the two relators. The greedy is not invariant under a relabeling (heap ties
break differently), so two copies of one presentation get different node
counts, and sometimes a different solved flag, from the same algorithm. This
script measures that gap and re-reads the headline counts with one vote per
class of copies:

* control noise: over pairs of copies, how often the solved flag differs and
  the relative node gap ``|a - b| / max(a, b)`` when both solve;
* start noise (rank 3): the same for a start ``(p, w)`` against the relabeled
  start ``(s.p, s.w)``, on the words whose image ``s.w`` is again the stored
  representative of ``{w, w^-1}``;
* per class: solved by the control on some copy, by some start on some copy,
  gained (some start solves, the control solves no copy) and cheaper (the best
  start of the class uses fewer nodes than the control's best copy).

    python -m experiments.stable_ac.rank3.class_view --rank3 DIR --budget 1000
    python -m experiments.stable_ac.rank3.class_view --rankn FILE.npz

Writes ``<stem>_class_view.json`` and ``.md`` next to the inputs.
"""

import argparse
import json
import os
from collections import Counter, defaultdict

import numpy as np

from experiments.equivalence_classes.lib import words as L
from experiments.stable_ac.rank3.run_rank3_bf import CAP, load_ms640, stem
from experiments.stable_ac.solvern import str_to_word, word_to_str

BIG = np.int64(2 ** 62)     # "no solve" in a minimum over node counts


def classes(dataset, ids):
    """-> class index per entry of ``ids`` and the twin pairs
    ``[(a, b, relabeling name, int word map)]`` with ``relabel(a) == b``."""
    pairs = {p: (word_to_str(r1), word_to_str(r2)) for p, r1, r2 in load_ms640(dataset)}
    members = defaultdict(list)
    for p in ids:
        members[L.relabel_key(pairs[p])].append(p)
    index = {p: c for c, ms in enumerate(members.values()) for p in ms}
    twins = []
    for ms in members.values():
        for i, a in enumerate(ms):
            for b in ms[i + 1:]:
                name, img = next((n, im) for n, im in L.SIGNED_PERMS
                                 if L.apply_pair(pairs[a], im) == L.canon_pair(*pairs[b]))
                m = {1: L.CHAR_TO_INT[img["x"]], 2: L.CHAR_TO_INT[img["y"]]}
                twins.append((a, b, name,
                              lambda w, m=m: tuple(m[g] if g > 0 else -m[-g] for g in w)))
    return np.array([index[p] for p in ids]), twins


def gap_stats(a_solved, b_solved, a_nodes, b_nodes):
    """Two aligned sets of searches that differ by a relabeling only."""
    both = a_solved & b_solved
    out = {"pairs": int(a_solved.size),
           "solved_flag_differs": int((a_solved != b_solved).sum()),
           "both_solved": int(both.sum())}
    if both.any():
        x, y = a_nodes[both].astype(np.float64), b_nodes[both].astype(np.float64)
        gap = np.abs(x - y) / np.maximum(x, y)
        out.update(same_nodes=float((gap == 0).mean()), gap_median=float(np.median(gap)),
                   gap_p90=float(np.quantile(gap, 0.9)), gap_p99=float(np.quantile(gap, 0.99)))
    return out


def start_noise(twins, row, words, nodes, solved):
    """gap_stats over (p, w) against (s.p, s.w) for every twin pair and every
    word of one length whose image is itself in ``words``."""
    idx = {w: k for k, w in enumerate(words)}
    cols, parts = {}, []
    for a, b, name, f in twins:
        if name not in cols:
            hit = [(k, idx[f(w)]) for k, w in enumerate(words) if f(w) in idx]
            cols[name] = (np.array([k for k, _ in hit], dtype=np.int64),
                          np.array([j for _, j in hit], dtype=np.int64))
        ka, kb = cols[name]
        if ka.size:
            parts.append((solved[row[a], ka], solved[row[b], kb],
                          nodes[row[a], ka], nodes[row[b], kb]))
    if not parts:
        return {"pairs": 0, "solved_flag_differs": 0, "both_solved": 0}
    return gap_stats(*(np.concatenate(c) for c in zip(*parts)))


def view(cls, c_solved, c_nodes, best, noise):
    """Headline counts per presentation and per class. ``best[p]`` is the
    fewest nodes of any start of presentation p that solves, BIG if none."""
    some = best < BIG
    c_best = np.where(c_solved, c_nodes, BIG)
    n_cls = int(cls.max()) + 1
    k_ctrl = np.full(n_cls, BIG)
    k_start = np.full(n_cls, BIG)
    np.minimum.at(k_ctrl, cls, c_best)
    np.minimum.at(k_start, cls, best)
    gained = some & ~c_solved
    return {
        "presentations": {
            "n": int(cls.size), "control": int(c_solved.sum()), "some_start": int(some.sum()),
            "gained": int(gained.sum()),
            "gained_but_control_solves_a_copy": int((gained & (k_ctrl[cls] < BIG)).sum()),
            "lost": int((c_solved & ~some).sum()),
            "cheaper": int((some & (best < c_best)).sum()),
            "cheaper_beyond_noise": int((gained | (some & c_solved
                                                   & (best < c_nodes * (1 - noise)))).sum()),
            "cheaper_than_every_copy_of_control": int((some & (best < k_ctrl[cls])).sum())},
        "classes": {
            "n": n_cls, "control": int((k_ctrl < BIG).sum()), "some_start": int((k_start < BIG).sum()),
            "gained": int(((k_start < BIG) & (k_ctrl == BIG)).sum()),
            "lost": int(((k_ctrl < BIG) & (k_start == BIG)).sum()),
            "cheaper": int((k_start < k_ctrl).sum())},
    }


def best_nodes(nodes, solved):
    return np.where(solved, nodes, BIG).min(axis=1)


def load_rank3(d, source, budget, cap):
    base = os.path.join(d, stem(source, budget, cap))
    ctrl = {}
    with open(base + "_control.jsonl") as f:
        for ln in f:
            if ln.strip():
                r = json.loads(ln)
                ctrl[r["pres_id"]] = r
    blocks, ids, n = {}, None, 1
    while os.path.exists(f"{base}_L{n}.npz"):
        with np.load(f"{base}_L{n}.npz") as z:
            p = [int(x) for x in z["pres_ids"]]
            assert ids is None or p == ids, f"L{n}: presentation order differs"
            ids = p
            blocks[n] = ([str_to_word(str(w)) for w in z["words"]],
                         z["nodes"].astype(np.int64), z["path_len"] >= 0)
        n += 1
    assert blocks, f"no {base}_L*.npz"
    return (base, ids, np.array([bool(ctrl[p]["solved"]) for p in ids]),
            np.array([int(ctrl[p]["nodes_explored"]) for p in ids], dtype=np.int64), blocks)


def _pct(x):
    return f"{100 * x:.1f}%"


def _noise_row(name, g):
    if not g.get("both_solved"):
        return f"| {name} | {g['pairs']:,} | {g['solved_flag_differs']:,} | 0 | | | | |"
    return (f"| {name} | {g['pairs']:,} | {g['solved_flag_differs']:,} "
            f"({_pct(g['solved_flag_differs'] / g['pairs'])}) | {g['both_solved']:,} | "
            f"{_pct(g['same_nodes'])} | {_pct(g['gap_median'])} | {_pct(g['gap_p90'])} | "
            f"{_pct(g['gap_p99'])} |")


def write(base, out, noise):
    with open(base + "_class_view.json", "w") as f:
        json.dump(out, f, indent=1)
    c = out["classes"]
    md = [f"# Relabeling classes: `{os.path.basename(base)}`", "",
          f"The {c['presentations']} presentations are {c['n']} classes of copies (the same "
          "presentation after renaming x, y, X, Y, up to the order, rotation and inversion of "
          "the relators); class sizes " + ", ".join(
              f"{k}: {v}" for k, v in sorted(c["sizes"].items(), key=lambda kv: int(kv[0]))) + ".",
          "", "## How far a relabeling alone moves the search", "",
          "Pairs of searches that differ only by the relabeling. Node gap = |a - b| / max(a, b) "
          "when both solve.", "",
          "| searches | pairs | solved flag differs | both solve | same nodes | median gap | "
          "p90 gap | p99 gap |", "|---|---|---|---|---|---|---|---|",
          _noise_row("control", out["noise"]["control"])]
    for name, g in out["noise"].get("starts", {}).items():
        md.append(_noise_row(f"starts, word length {name}", g))
    md += ["", "## Headline counts, one vote per presentation and one per class", "",
           "Gained = some start solves and the control does not. Cheaper = the best start "
           "uses fewer nodes than the control (a gain counts). Per class: the control and the "
           "starts both take their best copy.", "",
           f"| starts | per presentation | some start solves | gained | of those, the control "
           f"solves a copy | lost | cheaper | cheaper by more than {noise:.0%} | cheaper than "
           "every copy of the control | classes: control solves | some start solves | gained | "
           "lost | cheaper |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in out["rows"]:
        p, k = r["presentations"], r["classes"]
        md.append(f"| {r['name']} | {r['starts']:,} | {p['some_start']} | {p['gained']} | "
                  f"{p['gained_but_control_solves_a_copy']} | {p['lost']} | {p['cheaper']} | "
                  f"{p['cheaper_beyond_noise']} | {p['cheaper_than_every_copy_of_control']} | "
                  f"{k['control']} | {k['some_start']} | {k['gained']} | {k['lost']} | "
                  f"{k['cheaper']} |")
    md += ["", f"Control: {out['rows'][0]['presentations']['control']} of "
           f"{c['presentations']} presentations."]
    with open(base + "_class_view.md", "w") as f:
        f.write("\n".join(md) + "\n")
    print("\n".join(md))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--rank3", default=None, help="results directory of run_rank3_bf")
    ap.add_argument("--rankn", default=None, help="one rankn_bf_*_r<rank>.npz")
    ap.add_argument("--source", default="ms640")
    ap.add_argument("--budget", type=int, default=1000)
    ap.add_argument("--cap", type=int, default=CAP)
    ap.add_argument("--dataset", default="data/ms640_solved.txt")
    ap.add_argument("--noise", type=float, default=0.17)
    a = ap.parse_args(argv)
    assert (a.rank3 is None) != (a.rankn is None), "give exactly one of --rank3, --rankn"
    rows, starts = [], {}
    if a.rank3:
        base, ids, c_solved, c_nodes, blocks = load_rank3(a.rank3, a.source, a.budget, a.cap)
        cls, twins = classes(a.dataset, ids)
        row = {p: i for i, p in enumerate(ids)}
        best, total = np.full(len(ids), BIG), 0
        for n in sorted(blocks):
            words, nodes, solved = blocks[n]
            starts[str(n)] = start_noise(twins, row, words, nodes, solved)
            best = np.minimum(best, best_nodes(nodes, solved))
            total += len(words)
            rows.append({"name": f"words up to length {n}", "starts": total,
                         **view(cls, c_solved, c_nodes, best, a.noise)})
    else:
        base = os.path.splitext(a.rankn)[0]
        with np.load(a.rankn) as z:
            ids = [int(x) for x in z["pres_ids"]]
            meta = json.loads(str(z["meta"]))
            c_solved, c_nodes = z["base"][:, 0] == 1, z["base"][:, 1].astype(np.int64)
            nodes, solved = z["nodes"].astype(np.int64), z["path_len"] >= 0
        cls, twins = classes(a.dataset, ids)
        row = {p: i for i, p in enumerate(ids)}
        rows.append({"name": f"every {meta['extra_generators']} words up to length "
                             f"{meta['max_word_len']} (rank {meta['rank']})",
                     "starts": int(nodes.shape[1]),
                     **view(cls, c_solved, c_nodes, best_nodes(nodes, solved), a.noise)})
    ia = np.array([row[t[0]] for t in twins], dtype=np.int64)
    ib = np.array([row[t[1]] for t in twins], dtype=np.int64)
    out = {"classes": {"presentations": len(ids), "n": int(cls.max()) + 1,
                       "sizes": {str(k): v for k, v in sorted(Counter(Counter(cls.tolist()).values()).items())},
                       "twin_pairs": len(twins),
                       "twin_relabelings": dict(Counter(t[2] for t in twins)),
                       "class_of": {str(p): int(c) for p, c in zip(ids, cls)}},
           "noise": {"control": gap_stats(c_solved[ia], c_solved[ib], c_nodes[ia], c_nodes[ib]),
                     "starts": starts},
           "noise_threshold": a.noise, "rows": rows}
    write(base, out, a.noise)


if __name__ == "__main__":
    main()
