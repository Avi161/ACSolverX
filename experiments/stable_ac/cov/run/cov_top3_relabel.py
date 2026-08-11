"""Relabel-deduplicated top-3 CoV manifests: no two picks are the same start renamed.

**Zero search nodes.** This is a stage-A variant of
``cov_top3_manifest``: same enumeration, same ranking keys, one extra filter.
After ranking, a candidate is skipped if an earlier-ranked pick of the same
presentation has the same ``relabel_class`` — the canonical form under the 8
signed permutations of ``{x, y}`` (``equivalence_classes.lib.words.relabel_key``).
The freed slot is filled by pulling deeper into the same ranking, so every
manifest still carries ``k`` picks wherever ``k`` relabel-distinct candidates
exist.

The rule the user approved, in order:

```text
1. rank by (abel | len)          -- the arm's key, unchanged
2. then by total transformed length
3. drop a candidate whose relabel_class already appeared    <-- this module
4. pull deeper to refill the slot
5. _ident (z_word, iso_gen, iso_index, r1, r2) as the last resort
```

Steps 1, 2 and 5 are ``cov_top3_manifest.rank`` verbatim — this module imports
that ordering rather than restating it, so the arms differ in the dedup and in
nothing else.

Why dedup at all — and the honest limit of the claim
----------------------------------------------------

Measured on the shipped ms640 manifests: the ``abel`` arm's 1,920 picks contain
**723 slots** (500 of 640 presentations) whose relabel_class repeats an earlier
pick, and ``len`` contains 424 (343 of 640). Those slots re-search a start the
arm had already searched under a different name.

Whether that is *waste* depends on the budget, and the answer is not the
theoretical one. A relabel is an automorphism, so it maps AC paths to AC paths
bijectively and the **existence** of a solution, and its minimal length, are
relabel-invariant. The greedy is not: it is a truncated best-first search whose
tie-break reads strings, so two relabel siblings pop in different orders. On the
169 abel sibling groups that are relabel-equivalent but Booth-distinct:

| | siblings disagree |
|---|---|
| ``nodes_explored`` | 48 / 169 |
| ``path_length`` (among solved) | 6 / 169 |
| ``solved`` at budget >= 300 | **0 / 169** |
| ``solved`` at budget 100 | 1 / 169 |

So at the production budget of 100,000 a sibling contributed nothing that its
partner had not already contributed, and the slot is free to spend on a
genuinely different candidate. At budget 100 that is no longer true — which is
consistent with, and must not be confused with, the separate finding that
relabels are valuable as *alternative starts* at low budget (they supplied 14 of
17 unsolved→solved flips in the one-hop sweep; see
``cov/AUTOMORPHISMS_COV.md`` and ``run/orbit_greedy.py``). Alternative starts
across a portfolio and duplicate starts inside one presentation's top 3 are
different things: this module removes only the second.

**What the freed slots buy is not measured here.** The replacement is the next
relabel-distinct candidate in the same ranking, which the shipped run never
searched, so no re-scoring of the frozen jsonl can price it — exactly the
caution ``results/stable_ac/cov/cov_top3/RESULTS.md`` already records for Booth
dedup. Evaluating this arm means running stage B; that is a Colab job.

Rules and run identity
----------------------

``abel_rd`` and ``len_rd`` live in this module's own :data:`RULES`, and are
spliced into ``cov_top3_manifest.RULES`` **only for the duration of a stage-B
run** (:func:`registered`). They are deliberately NOT registered at import: that
dict is read at module scope by other code, and mutating it on import would make
behaviour depend on import order —

- ``tests/stable_ac/test_cov_top3.py`` parametrizes five tests on
  ``sorted(M.RULES)`` at collection time, and would run the shipped arms' assertions
  against a deduped rule whose key it has no entry for;
- ``cov_top3_manifest``'s own CLI builds ``sorted(RULES)`` when given no
  arguments, so a stray import would make ``python3 -m ...cov_top3_manifest``
  silently overwrite the deduped manifests with **undeduped** ones.

The new names still give the arms their own manifest paths
(``manifest_ms640_abel_rd_top3.jsonl``) and their own stage-B resume prefixes
(``abel_rdtop3_...``), so they can never resume into the shipped ``abeltop3_*``
files.

Scoped registration narrows that second footgun but does not close it — a
deduped path is still writable by an undeduped build. So every row this module
writes carries ``dedup = "relabel8"``, and :func:`verify` re-derives every
relabel_class from ``(r1, r2)`` rather than trusting the tag. Load a manifest
through :func:`load_manifest` and a wrong file cannot be searched silently.

    .venv/bin/python3 -m experiments.stable_ac.cov.run.cov_top3_relabel            # build both
    .venv/bin/python3 -m experiments.stable_ac.cov.run.cov_top3_relabel abel_rd    # build one
    .venv/bin/python3 -m experiments.stable_ac.cov.run.cov_top3_relabel --audit \
        results/stable_ac/cov/cov_top3/manifest_ms640_abel_top3.jsonl              # audit any manifest

Stage B, once built (the rule name is what routes it):

    ACSOLVERX_ALLOW_BIG=1 .venv/bin/python3 \
        -m experiments.stable_ac.cov.run.cov_top3_relabel_run --rule abel_rd
"""

import argparse
import contextlib
import json
import os
import time

from experiments import run_baseline
from experiments.equivalence_classes.lib.words import relabel_key
from experiments.stable_ac.cov.run import cov_top3_manifest as manifest

K = manifest.K
DEDUP_TAG = "relabel8"

# new rule -> the shipped rule whose ranking it reuses verbatim. The dedup is
# the ONLY difference between an arm and its base, which is what lets the two be
# compared: one variable, not two.
BASE_OF = {"abel_rd": "abel", "len_rd": "len"}

# This module's own whitelist. Same contract as the base module's: an unknown
# rule fails here, never falls back to a default.
RULES = {new: manifest.RULES[base] for new, base in BASE_OF.items()}

ROOT = manifest.ROOT


def check_rule(rule):
    if rule not in RULES:
        raise ValueError(f"unknown deduped rule {rule!r}; expected one of "
                         f"{sorted(RULES)}")
    return rule


@contextlib.contextmanager
def registered(rule, rules=None):
    """Splice ``rule`` into the base module's whitelist for one stage-B run.

    Scoped, not permanent: ``cov_top3_run.load_config`` validates against
    ``cov_top3_manifest.RULES`` and ``main`` builds its ``--rule`` choices from
    it, so the name has to be there *while the run is being configured* — and
    must not be there at any other time (see the module docstring for the two
    things that break). Restores the dict on the way out, including on error.
    """
    check_rule(rule)
    rules = manifest.RULES if rules is None else rules
    had = rule in rules
    prev = rules.get(rule)
    rules[rule] = RULES[rule]
    try:
        yield rules
    finally:
        if had:
            rules[rule] = prev
        else:
            rules.pop(rule, None)


def base_rule(rule):
    """The shipped rule a deduped rule ranks by; a shipped rule is its own base."""
    return BASE_OF.get(rule, rule)


def manifest_path(rule, out_dir=manifest.OUT_DIR):
    """Same layout as ``cov_top3_manifest.manifest_path``, without needing the
    rule to be registered. Pinned against the base builder in the tests, so the
    two cannot drift into naming the same file differently."""
    return os.path.join(out_dir,
                        f"manifest_ms640_{check_rule(rule)}_top{K}.jsonl")


def relabel_class(d):
    """Canonical form of ``(r1, r2)`` under the 8 signed permutations.

    ``words.relabel_key`` — the repo's definition, shared with the equivalence
    class work; ``autcanon_fast.relabel_min`` is its numba twin and partitions
    identically (pinned in ``tests/stable_ac/test_cov_top3_relabel.py``). Equal
    keys mean the two starts are the same presentation renamed.
    """
    return relabel_key((d["r1"], d["r2"]))


def dedup_ranked(ranked, k=K):
    """Walk a ranked candidate list, keeping the first pick of each relabel class.

    Returns ``(picks, dropped)``. ``dropped`` carries the skipped candidate's
    position in the *undeduped* ranking and the rank it collided with, so every
    difference from the base arm is auditable from the manifest alone.

    Fewer than ``k`` relabel-distinct candidates yields fewer than ``k`` picks —
    counted by :func:`build`, never asserted. A presentation whose whole family
    is one relabel class is a real property of that family, not a bug.
    """
    picks, dropped, seen = [], [], {}
    for pos, d in enumerate(ranked, start=1):
        if len(picks) >= k:
            break
        cls = relabel_class(d)
        if cls in seen:
            dropped.append({"rank_raw": pos, "collides_with_rank": seen[cls],
                            "relabel_class": list(cls), "r1": d["r1"],
                            "r2": d["r2"]})
            continue
        seen[cls] = len(picks) + 1
        picks.append((pos, cls, d))
    return picks, dropped


def top_k(cands, k=K, rule="abel_rd"):
    """The deduped top ``k``. ``rank`` is the base arm's, unchanged."""
    ranked = manifest.rank(cands, base_rule(rule))
    return dedup_ranked(ranked, k)


def build(rule="abel_rd", dataset=manifest.DATASET, out_path=None, k=K,
          root=ROOT, subset=None, verbose=True):
    """Write one deduped manifest. Same schema as ``cov_top3_manifest.build``
    plus ``dedup``, ``rank_raw`` and ``relabel_class``.

    Written whole then renamed, for the same reason the base module does it: a
    torn manifest is a wrong experiment, not a resumable one.
    """
    check_rule(rule)
    out_path = out_path or manifest_path(rule)
    ap = out_path if os.path.isabs(out_path) else os.path.join(root, out_path)
    os.makedirs(os.path.dirname(ap), exist_ok=True)
    tmp = ap + ".tmp"
    t0 = time.perf_counter()
    n_pres = n_rows = n_dropped = n_short = n_changed = 0
    with open(tmp, "w") as fh:
        for pres_id, r1, r2 in run_baseline.load_dataset(
                os.path.join(root, dataset), subset=subset):
            cands = manifest.candidates(r1, r2)
            picks, dropped = top_k(cands, k, rule)
            n_dropped += len(dropped)
            n_short += len(picks) < k
            n_changed += any(pos != i for i, (pos, _, _) in
                             enumerate(picks, start=1))
            for i, (pos, cls, d) in enumerate(picks, start=1):
                row = dict(d)
                row.update({"pres_id": pres_id, "rank": i, "k": k,
                            "rule": rule, "n_cand": len(cands),
                            "r1_orig": r1, "r2_orig": r2,
                            "family_tag": manifest.FAMILY_TAG,
                            "dataset": dataset,
                            "default_cap": manifest.DEFAULT_CAP,
                            "dedup": DEDUP_TAG, "rank_raw": pos,
                            "relabel_class": list(cls),
                            "n_dropped": len(dropped)})
                fh.write(json.dumps(row) + "\n")
                n_rows += 1
            n_pres += 1
            if verbose and n_pres % 100 == 0:
                print(f"  [{rule}] {n_pres} presentations, {n_rows} picks, "
                      f"{n_dropped} relabel repeats dropped, "
                      f"{time.perf_counter() - t0:.0f}s", flush=True)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, ap)
    if verbose:
        print(f"wrote {out_path}: {n_rows} picks over {n_pres} presentations "
              f"in {time.perf_counter() - t0:.0f}s", flush=True)
        print(f"  {n_dropped} relabel repeats dropped; top-{k} differs from "
              f"{base_rule(rule)!r} on {n_changed}/{n_pres} presentations; "
              f"{n_short} presentations had fewer than {k} relabel-distinct "
              f"candidates", flush=True)
    return ap


def audit(path, root=ROOT, k=K):
    """Relabel collisions inside each presentation's picks, for ANY manifest.

    Read-only and rule-agnostic: point it at a shipped manifest to measure what
    the dedup would remove, or at a deduped one to confirm it removed it.
    """
    ap = path if os.path.isabs(path) else os.path.join(root, path)
    by_pres = {}
    with open(ap) as fh:
        for line in fh:
            line = line.strip()
            if line:
                row = json.loads(line)
                by_pres.setdefault(row["pres_id"], []).append(row)
    n_pres = len(by_pres)
    hit, slots, groups = 0, 0, 0
    detail = []
    for pres_id, rows in sorted(by_pres.items()):
        rows.sort(key=lambda r: r["rank"])
        seen = {}
        for r in rows:
            cls = relabel_class(r)
            seen.setdefault(cls, []).append(r["rank"])
        dup = {c: v for c, v in seen.items() if len(v) > 1}
        if dup:
            hit += 1
            groups += len(dup)
            slots += sum(len(v) - 1 for v in dup.values())
            detail.append((pres_id, {tuple(c): v for c, v in dup.items()}))
    return {"path": os.path.basename(ap), "n_pres": n_pres,
            "presentations_with_a_repeat": hit, "repeat_groups": groups,
            "repeat_slots": slots, "detail": detail}


def verify(path, root=ROOT, rule=None):
    """Gate: no two picks of a presentation are relabels of each other.

    Re-derives every relabel_class from ``(r1, r2)`` rather than trusting the
    stored field, so a hand-edited or wrongly-built manifest cannot pass. Also
    checks ``dedup``, which is what stops
    ``cov_top3_manifest.build("abel_rd")`` — an undeduped write to a deduped
    path — from being searched silently.
    """
    a = audit(path, root=root)
    ap = path if os.path.isabs(path) else os.path.join(root, path)
    with open(ap) as fh:
        rows = [json.loads(l) for l in fh if l.strip()]
    if rule is not None:
        bad = {r.get("rule") for r in rows} - {rule}
        if bad:
            raise ValueError(f"{a['path']}: rows ranked by {sorted(bad)}, not "
                             f"the configured {rule!r} — searching them would "
                             f"measure the wrong rule")
    missing = [r["pres_id"] for r in rows if r.get("dedup") != DEDUP_TAG]
    if missing:
        raise ValueError(
            f"{a['path']}: {len(missing)} rows lack dedup={DEDUP_TAG!r} "
            f"(first pres {missing[0]}) — this path is reserved for a "
            f"relabel-deduped manifest, so an undeduped build landed here")
    if a["repeat_slots"]:
        p, d = a["detail"][0]
        raise ValueError(
            f"{a['path']}: {a['repeat_slots']} picks repeat an earlier pick's "
            f"relabel class over {a['presentations_with_a_repeat']} "
            f"presentations (e.g. pres {p}: ranks {sorted(d.values())[0]} are "
            f"the same start renamed)")
    return a


def load_manifest(path=None, root=ROOT, rule=None):
    """``cov_top3_manifest.load_manifest`` behind :func:`verify`.

    Stage B should load through this: the base loader checks the rule name, and
    this adds the two checks that name cannot carry — that the file was actually
    deduped, and that it still is.
    """
    path = path or manifest_path(rule or "abel_rd")
    verify(path, root=root, rule=rule)
    return manifest.load_manifest(path, root=root, rule=rule)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("rules", nargs="*", default=None,
                    help=f"rules to build (default: all of {sorted(RULES)})")
    ap.add_argument("--audit", metavar="JSONL",
                    help="report relabel collisions in an existing manifest")
    ap.add_argument("--verify", metavar="JSONL",
                    help="fail if a manifest has any relabel collision")
    ap.add_argument("--subset", type=int, default=None)
    a = ap.parse_args(argv)
    if a.audit:
        r = audit(a.audit)
        print(f"{r['path']}: {r['n_pres']} presentations, "
              f"{r['presentations_with_a_repeat']} with a relabel repeat, "
              f"{r['repeat_groups']} repeat groups, "
              f"{r['repeat_slots']} redundant slots")
        return
    if a.verify:
        r = verify(a.verify)
        print(f"{r['path']}: OK — no relabel repeats over "
              f"{r['n_pres']} presentations")
        return
    for rule in (a.rules or sorted(RULES)):
        build(rule, subset=a.subset)


if __name__ == "__main__":
    main()
