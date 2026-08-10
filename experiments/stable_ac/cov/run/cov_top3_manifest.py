"""Stage A of the ms640 CoV-top-3 experiment: freeze each rule's top-3 starts.

**Zero search nodes.** This module enumerates each ms640 presentation's subword
CoV family (``cov.enumerate_cov``, the same call ``run_cov._sweep_entries``
makes), ranks the candidates by a search-free rule, and writes the top ``K`` to a
per-rule manifest jsonl. It never calls the solver, so it is trivially inside the
repo's 1,000-node local cap, and it is the whole reason the search stage can run
unattended: the selection is fixed on disk before any search starts, so a
restarted or re-sharded run cannot disagree with itself about what it searches.

Two rules ship, one per Colab session — they are the two arms of the comparison:

```text
abel : abel(r1,r2) = |sigma_x(r1)| + |sigma_y(r1)| + |sigma_x(r2)| + |sigma_y(r2)|
len  : len(r1) + len(r2) of the TRANSFORMED pair (the shortest CoV)
```

Both keys and the tie-break are **imported**, not re-implemented, from
``experiments.heuristic_search.runners.abel_topk_cov_b1k`` (``KEYS["abel"]`` and
``KEYS["len_only"]``) — the validated budget-1,000 selection on subset-60.
One key, one tie-break, one implementation; ``tests/stable_ac/test_cov_top3.py``
pins that this module's selection reproduces that runner's on all 60 of its rows,
for both rules.

The tie-break matters: a median of ~15 candidates tie at the abel minimum (more
at the length minimum), so without a deterministic secondary key "top 3" would be
whatever order the enumeration happened to emit. ``_ident`` is the CoV's own name
``(z_word, iso_gen, iso_index, r1, r2)`` — search-free, so no ranking can read
the outcome it is supposed to predict.

Each row carries ``cap`` from ``CoVResult.cap`` (``max(24, longest + 16)``),
**not** the base cap: a CoV lengthens relators, and searching a lengthened start
under the untransformed 24-cap would silently cripple it and diverge from the
sweep that validated the keys.

Each row also carries its ``rule``. The search stage asserts that against its own
configured rule before searching anything: with two manifests on disk, a stale
path plus the other rule's name is a wrong experiment wearing a plausible
filename, and it would be undetectable in the results.

    .venv/bin/python3 -m experiments.stable_ac.cov.run.cov_top3_manifest        # both
    .venv/bin/python3 -m experiments.stable_ac.cov.run.cov_top3_manifest abel   # one
"""

import json
import os
import sys
import time

from experiments import run_baseline
from experiments.greedy_tests.spec.words import str_to_word, word_to_str
from experiments.heuristic_search.runners.abel_topk_cov_b1k import (
    KEYS, _ident, abel_magnitude)
from experiments.stable_ac.cov import cov
from experiments.stable_ac.cov.run.run_cov import find_repo_root

K = 3
DATASET = "data/ms640_solved.txt"
OUT_DIR = "results/stable_ac/cov/cov_top3"

# rule -> the ranking key, straight out of the validated b1k runner. A rule name
# is part of the run identity in both stages, so this dict is the whitelist: an
# unknown rule must fail at config time, never silently fall back to a default.
RULES = {"abel": KEYS["abel"], "len": KEYS["len_only"]}
DEFAULT_RULE = "abel"

# The enumeration knobs, pinned here rather than read from a yaml: the manifest
# IS the experiment's definition, so a config that could shift it out from under
# a half-finished search run would break resume.
DEFAULT_CAP = cov.DEFAULT_CAP          # 24 — the ms640 layout's per-relator cap
CAP_HEADROOM = cov.CAP_HEADROOM        # 16
REJECT_LEN = cov.REJECT_LEN            # 239, a structural ceiling only
FAMILY_TAG = cov.SUBWORD_FAMILY_TAG    # subnc2pxysb

ROOT = find_repo_root(os.path.dirname(os.path.abspath(__file__)))


def check_rule(rule):
    if rule not in RULES:
        raise ValueError(f"unknown rule {rule!r}; expected one of "
                         f"{sorted(RULES)}")
    return rule


def manifest_path(rule=DEFAULT_RULE, out_dir=OUT_DIR):
    """The rule's manifest path. Derived from the rule, never passed alongside it.

    Both stages call this instead of carrying a manifest path next to a rule
    name, so the two cannot drift apart.
    """
    return os.path.join(out_dir, f"manifest_ms640_{check_rule(rule)}_top{K}.jsonl")


def candidates(r1, r2):
    """Every valid subword CoV start of ``(r1, r2)``, as ranking-ready dicts.

    Field-for-field the subset of ``run_cov._sweep_entries``'s CoV rows that any
    ranking key reads — ``r1``/``r2`` are the *start* strings, never a search
    state, which is what makes both keys legitimate pre-search rankings.
    """
    out = []
    for res in cov.enumerate_cov(str_to_word(r1), str_to_word(r2), family=None,
                                 default_cap=DEFAULT_CAP,
                                 cap_headroom=CAP_HEADROOM,
                                 reject_len=REJECT_LEN,
                                 allow_defining_iso=False):
        r1t, r2t = word_to_str(res.r1), word_to_str(res.r2)
        out.append({
            "r1": r1t, "r2": r2t, "cap": res.cap,
            "z_word": word_to_str(res.z_word), "iso_gen": res.iso_gen,
            "iso_index": res.iso_index, "n_subs": res.n_subs,
            "abel": abel_magnitude(r1t, r2t),
            "start_total_length_cov": len(r1t) + len(r2t),
        })
    return out


def rank(cands, rule=DEFAULT_RULE):
    """The rule's key, ties broken by the candidate's own name (deterministic).

    ``abel_topk_cov_b1k.rank(v, KEYS[...], "ident")`` for a candidate list built
    here rather than read from a sweep jsonl.
    """
    key = RULES[check_rule(rule)]
    return sorted(cands, key=lambda d: tuple(key(d)) + _ident(d))


def top_k(cands, k=K, rule=DEFAULT_RULE):
    return rank(cands, rule)[:k]


def build(rule=DEFAULT_RULE, dataset=DATASET, out_path=None, k=K, root=ROOT,
          subset=None, verbose=True):
    """Write one manifest row per (presentation, rank). Returns the path.

    Written whole then renamed: a torn manifest is a wrong experiment, not a
    resumable one, and unlike a results jsonl there is nothing here worth
    salvaging from a partial write.
    """
    check_rule(rule)
    out_path = out_path or manifest_path(rule)
    ap = out_path if os.path.isabs(out_path) else os.path.join(root, out_path)
    os.makedirs(os.path.dirname(ap), exist_ok=True)
    tmp = ap + ".tmp"
    t0 = time.perf_counter()
    n_pres = n_rows = 0
    with open(tmp, "w") as fh:
        for pres_id, r1, r2 in run_baseline.load_dataset(
                os.path.join(root, dataset), subset=subset):
            cands = candidates(r1, r2)
            picks = top_k(cands, k, rule)
            for i, d in enumerate(picks, start=1):
                row = dict(d)
                row.update({"pres_id": pres_id, "rank": i, "k": k,
                            "rule": rule, "n_cand": len(cands),
                            "r1_orig": r1, "r2_orig": r2,
                            "family_tag": FAMILY_TAG, "dataset": dataset,
                            "default_cap": DEFAULT_CAP})
                fh.write(json.dumps(row) + "\n")
                n_rows += 1
            n_pres += 1
            if verbose and n_pres % 100 == 0:
                print(f"  [{rule}] {n_pres} presentations, {n_rows} picks, "
                      f"{time.perf_counter() - t0:.0f}s", flush=True)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, ap)
    if verbose:
        print(f"wrote {out_path}: {n_rows} picks over {n_pres} presentations "
              f"in {time.perf_counter() - t0:.0f}s", flush=True)
    return ap


def load_manifest(path=None, root=ROOT, rule=None):
    """[(pres_id, [row, ...])] in dataset order, each list rank-ordered.

    Grouped by presentation because the search stage is sequential *within* a
    presentation (rank 1, then 2, then 3, stopping at the first solve) and
    independent *across* presentations — so a presentation is the unit of
    progress, never a rank.

    Passing ``rule`` asserts every row was ranked by it: two manifests differ
    only in their row contents, so nothing downstream could otherwise notice
    that the wrong one was loaded.
    """
    path = path or manifest_path(rule or DEFAULT_RULE)
    ap = path if os.path.isabs(path) else os.path.join(root, path)
    order, by_pres = [], {}
    with open(ap) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if rule is not None and row.get("rule") != rule:
                raise ValueError(
                    f"{os.path.basename(ap)} row (pres {row.get('pres_id')}, "
                    f"rank {row.get('rank')}) was ranked by "
                    f"{row.get('rule')!r}, not the configured {rule!r} — "
                    f"searching it would measure the wrong rule")
            p = row["pres_id"]
            if p not in by_pres:
                by_pres[p] = []
                order.append(p)
            by_pres[p].append(row)
    for p in order:
        by_pres[p].sort(key=lambda r: r["rank"])
    return [(p, by_pres[p]) for p in order]


if __name__ == "__main__":
    for r in (sys.argv[1:] or sorted(RULES)):
        build(check_rule(r))
