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
1. rank by (abel | total length)  -- the arm's key
2. then by MK (max knots)         -- "the other idea", optional
3. drop a candidate whose relabel_class already appeared    <-- this module
4. pull deeper to refill the slot
5. _ident (z_word, iso_gen, iso_index, r1, r2) as the last resort
```

The five rules
--------------

```text
abel_rd          (abel)                shipped `abel` + dedup, one variable
len_rd           (total)               shipped `len`  + dedup, one variable
abel_len_rd      (abel, total)         the validated b1k ranking + dedup
abel_len_rd_mk   (abel, total, MK)     the above + "the other idea"
len_rd_mk        (total, MK)           the length arm + "the other idea"
```

Every key is ``abel_topk_cov_b1k.KEYS`` or a ``_with_mk`` of one, so a change
there reaches these arms and the study in
``heuristic_search/runners/cov_relabel_b1k.py`` cannot drift from what the
manifests are actually built with.

``abel_rd`` and ``len_rd`` exist to isolate the dedup: they are a shipped arm
with the filter added and **nothing else changed**, which is what makes a
comparison against the shipped ms640 run a one-variable comparison. The other
three change the ranking too, so they have no shipped counterpart
(:func:`base_rule` returns ``None`` for them rather than inventing one).

Note that the shipped ``abel`` rule is bare ``(abel,)`` — it does *not* carry
the total-length term. Building the MK arms on top of it would have quietly
dropped that term; ``abel_len_rd_mk`` composes from ``KEYS["abel_len"]``
instead, and ``abel_len_rd`` is carried alongside so the MK term can be read
against the same ranking without it.

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

All five names live in this module's own :data:`RULES`, and are spliced into
``cov_top3_manifest.RULES`` **only for the duration of a stage-B run**
(:func:`registered`). They are deliberately NOT registered at import: that
dict is read at module scope by other code, and mutating it on import would make
behaviour depend on import order —

- ``tests/stable_ac/test_cov_top3.py`` parametrizes on ``sorted(M.RULES)`` at
  collection time from four sites (three decorators plus a fixture), which expand
  to **16 test functions / 32 collected ids**, and would run the shipped arms'
  assertions against a deduped rule whose key it has no entry for;
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
relabel_class from ``(r1, r2)`` rather than trusting the tag — forging the tag
onto undeduped rows does not get past it.

The gate that actually runs in production is ``cov_top3_relabel_run.preflight``,
**not** :func:`load_manifest`: stage B (``cov_top3_run.run`` / ``merge_chunks`` /
``summarize``) loads through ``cov_top3_manifest.load_manifest``, and this
module's :func:`load_manifest` is a convenience door used by the tests. Two
limits worth knowing before leaning on :func:`verify`: it proves a manifest is
*deduped*, not that it is *correctly ranked* (a correctly-deduped file with its
picks permuted still passes), and ``verify(path, rule=None)`` skips the rule
check entirely — always pass the rule, as ``preflight`` does.

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
from experiments.heuristic_search.runners import abel_tiebreak_b1k as tiebreak
from experiments.heuristic_search.runners import abel_topk_cov_b1k as b1k
from experiments.stable_ac.cov.run import cov_top3_manifest as manifest

K = manifest.K
DEDUP_TAG = "relabel8"


def _with(key, feat):
    """``key`` with one ``hlab.FEATURES`` value appended before ``_ident``.

    ``feat`` is read off the START pair (``phi(r1, r2)[i]``), so like every key
    here it is search-free and computable at manifest-build time. Appending it
    means it decides only what the name tie-break would otherwise have decided:
    it can never outvote abel or length.
    """
    return lambda d: tuple(key(d)) + (feat(d),)


def _with_s(key):
    """``key`` then ``S`` — the intended third term, `abel -> length -> S`.

    ``S`` is the smaller mean block: the mean run length of the thinner
    generator. It carries the heaviest weight in the project's one sanctioned
    heuristic, ``L + 20*S + 2*MK``, which is why it is the tie-break these arms
    are built on.
    """
    return _with(key, tiebreak._S)


def _with_mk(key):
    """``key`` then ``MK``, kept only so the two tie-breaks can be compared.

    ``MK`` is the max knot count. It is **not** the recommended third term — see
    ``S`` above — and is retained because it was already measured on subset-60,
    where its sign depends on the budget.
    """
    return _with(key, tiebreak._MK)


# new rule -> the shipped rule whose ranking it reuses **verbatim**. For these
# two the dedup is the ONLY difference from a shipped arm, which is what lets
# them be compared to it: one variable, not two. The rules below that add an
# ordering term have no shipped counterpart and are absent here.
BASE_OF = {"abel_rd": "abel", "len_rd": "len"}

# This module's own whitelist. Same contract as the base module's: an unknown
# rule fails here, never falls back to a default.
#
# Composition, not restatement: every key is ``abel_topk_cov_b1k.KEYS`` or a
# ``_with_mk`` of one, so a change to a key there reaches these arms. Writing
# ``(abel,) + MK`` here would have been the easy mistake — the shipped ``abel``
# rule is bare ``(abel,)``, so building the MK arms on ``BASE_OF`` would have
# silently dropped the total-length term that the ranking was validated with.
RULES = {
    "abel_rd": manifest.RULES["abel"],                  # (abel)
    "len_rd": manifest.RULES["len"],                    # (total)
    "abel_len_rd": b1k.KEYS["abel_len"],                # (abel, total)
    # the intended rule: abel -> length -> S, with the 8-name-change dedup
    "abel_len_rd_s": _with_s(b1k.KEYS["abel_len"]),     # (abel, total, S)
    "len_rd_s": _with_s(b1k.KEYS["len_only"]),          # (total, S)
    # MK kept only as a measured alternative to S, never the recommendation
    "abel_len_rd_mk": _with_mk(b1k.KEYS["abel_len"]),   # (abel, total, MK)
    "len_rd_mk": _with_mk(b1k.KEYS["len_only"]),        # (total, MK)
}

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
    """The shipped rule a deduped rule ranks by, or ``None`` if it has no counterpart.

    Only ``abel_rd`` and ``len_rd`` mirror a shipped arm. The rules that add an
    ordering term differ from every shipped arm in two ways, so there is no
    single base to compare them against and callers must not invent one.
    """
    return BASE_OF.get(rule)


def rank(cands, rule):
    """``cov_top3_manifest.rank``'s ordering, over a key this module owns.

    Same shape as the base module's — the rule's key, then ``_ident`` (the CoV's
    own name) as the deterministic last resort. It is restated here only because
    the base ``rank`` looks its key up in ``cov_top3_manifest.RULES``, which the
    composed rules are deliberately not permanent members of.
    """
    key = RULES[check_rule(rule)]
    return sorted(cands, key=lambda d: tuple(key(d)) + manifest._ident(d))


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
    """The deduped top ``k``. The ranking is :func:`rank`; the dedup is the filter."""
    return dedup_ranked(rank(cands, rule), k)


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
        base = base_rule(rule)
        moved = (f"top-{k} differs from {base!r} on {n_changed}/{n_pres} "
                 f"presentations" if base else
                 f"{n_changed}/{n_pres} presentations have a pick pulled deeper "
                 f"than its raw rank")
        print(f"  {n_dropped} relabel repeats dropped; {moved}; "
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
