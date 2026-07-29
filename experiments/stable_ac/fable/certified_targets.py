"""Certified stably-AC-trivial TARGETS from the Fagan-Qiu-Wang fake-surface census.

Every search in this project has aimed at one target, the standard presentation.  The
fake-surface reformulation supplies thousands more, for free:

  Fagan-Qiu-Wang, arXiv:2412.12293 (abstract, verbatim): "The stable Andrews-Curtis
  conjecture is equivalent to the conjecture that every contractible fake surface is
  3-deformable to a point.  We prove that every contractible fake surface of complexity
  less than 6 is 3-deformable to a point by induction."

Their census of contractible fake surfaces (github.com/lucasfagan/Fake-Surfaces,
``fakesurfaces.csv``) lists 5,389 surfaces of complexity 1-5.  Collapsing a spanning
tree of each singular graph turns every one into a balanced presentation with
``V+1`` generators, ``V+1`` relators and total length ``3V+3``; by the theorem above,
each of those presentations is **stably AC-trivial**.  So:

    AK(3) is stably AC-trivial  <==  AK(3) is stable-AC-equivalent to ANY census member

which replaces a single needle with ~5,400 of them.  Nothing about the target set is
weaker than the standard presentation (all of them are in the trivial stable class);
the gain is search geometry -- thousands of short entry points, all with 2-6
generators, i.e. natively inside the AC4/AC5 territory that no published search has
explored.

Provenance and dependencies (both flagged, per project rules)
------------------------------------------------------------
* The census data and the tree-collapse dictionary were derived and validated in this
  session: every row satisfies the necessary profile (each singular edge carries
  exactly 3 face-germs; ``|det|`` of the abelianised relation matrix is 1 on
  5,389/5,389), and an independent Todd-Coxeter run certifies the TRIVIAL group on 457
  of them (all of complexity 1-3, plus random samples at 4 and 5) -- 457/457 index 1.
* [UNVERIFIED this session] the full text of arXiv:2412.12293 is proxy-blocked; only
  the abstract was sourced (verbatim, from a mirrored primary copy).  Whether the
  complexity < 6 theorem is stated for all or only *cellular* fake surfaces, and the
  exact direction/form of the equivalence, could not be checked.  Any positive result
  routed through this target set inherits that flag.
* Matching "up to generator relabelling" additionally leans on the stable ambient
  automorphism theorem (free-group automorphisms preserve the STABLE class); exact
  matches are reported separately so a reader can take the weaker, dependency-free
  reading.
"""

from __future__ import annotations

import argparse
import gzip
import itertools
import json
import os
import sys
from collections import Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from ac_words import cyclic_reduce                              # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
TARGETS_JSON = os.path.join(REPO_ROOT, "results", "stable_ac", "fable",
                            "certified_trivial_targets.json")
DEFAULT_REPORT = os.path.join(REPO_ROOT, "results", "stable_ac", "fable",
                              "certified_target_intersection.json")
UPSTREAM = "github.com/lucasfagan/Fake-Surfaces (fakesurfaces.csv)"
MAX_RELABEL_GENERATORS = 6


def canon_multi(words, relabel=None) -> tuple:
    """Canonical key of a presentation: cyclic reduction, optional generator
    relabelling, lex-min over each relator's rotations and inversion, relators sorted.

    Rotation, inversion and relator permutation are exactly the operations the
    (AUDITED) gamma_N symmetry lemma quotients by, and each is an AC composite
    (R1E Lemma P), so the key never merges states from different AC classes.
    """
    reduced = [cyclic_reduce(w) for w in words]
    reduced = [w for w in reduced if w]
    if relabel:
        reduced = ["".join(relabel[c.lower()].upper() if c.isupper() else relabel[c]
                           for c in w) for w in reduced]
    keys = []
    for word in reduced:
        candidates = []
        for variant in (word, "".join(c.swapcase() for c in reversed(word))):
            candidates.extend(variant[i:] + variant[:i] for i in range(len(variant)))
        keys.append(min(candidates))
    return tuple(sorted(keys))


def relabel_canon(words):
    """Canonical key minimised over every renaming of the generators, or None if the
    presentation has more generators than :data:`MAX_RELABEL_GENERATORS`."""
    generators = sorted({c.lower() for w in words for c in w})
    if not generators or len(generators) > MAX_RELABEL_GENERATORS:
        return None
    letters = "abcdefgh"[:len(generators)]
    best = None
    for perm in itertools.permutations(letters):
        key = canon_multi(words, dict(zip(generators, perm)))
        if best is None or key < best:
            best = key
    return best


def load_targets(path: str = TARGETS_JSON) -> dict:
    with open(path, encoding="utf-8") as handle:
        payload = json.load(handle)
    exact, relabelled = {}, {}
    for entry in payload["targets"]:
        relators = tuple(entry["relators"])
        exact.setdefault(canon_multi(relators), entry)
        key = relabel_canon(relators)
        if key is not None:
            relabelled.setdefault(key, entry)
    return {"meta": payload["meta"], "entries": payload["targets"],
            "exact": exact, "relabelled": relabelled}


def match(words, targets: dict) -> dict | None:
    """Does this presentation coincide with a certified stably-trivial target?"""
    exact_key = canon_multi(words)
    hit = targets["exact"].get(exact_key)
    if hit is not None:
        return {"kind": "exact", "target": hit}
    key = relabel_canon(words)
    if key is not None:
        hit = targets["relabelled"].get(key)
        if hit is not None:
            return {"kind": "up_to_generator_relabelling", "target": hit}
    return None


def _iter_members(path: str):
    opener = gzip.open(path, "rt", encoding="utf-8") if path.endswith(".gz") \
        else open(path, encoding="utf-8")
    with opener as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            words = row.get("canonical") or row.get("pair")
            if isinstance(words, list) and words:
                yield tuple(words), row


def intersect_corpus(sources, targets: dict) -> dict:
    """Hash-join every harvested class member against the certified target set."""
    report = {"record": "certified_target_intersection",
              "targets": targets["meta"], "sources": [], "hits": []}
    for name, path in sources:
        full = os.path.join(REPO_ROOT, path)
        if not os.path.exists(full):
            report["sources"].append({"name": name, "path": path,
                                      "status": "MISSING"})
            continue
        checked = 0
        kinds: Counter = Counter()
        status = "OK"
        try:
            for words, _row in _iter_members(full):
                checked += 1
                found = match(words, targets)
                if found is not None:
                    kinds[found["kind"]] += 1
                    report["hits"].append({"source": name, "member": list(words),
                                           "match_kind": found["kind"],
                                           "target": found["target"]})
        except (EOFError, OSError, json.JSONDecodeError) as exc:
            # an artifact still being written by a running harvest: report what was
            # read rather than crashing, and never present it as complete
            status = f"PARTIAL ({type(exc).__name__}: file still being written)"
        report["sources"].append({"name": name, "path": path, "status": status,
                                  "members_checked": checked,
                                  "matches": dict(kinds)})
        print(f"[targets] {name}: {checked} members, {sum(kinds.values())} matches",
              flush=True)
    report["total_hits"] = len(report["hits"])
    return report


DEFAULT_SOURCES = (
    ("AK(3) classical class", "results/stable_ac/fable/ak3_matched_members.jsonl.gz"),
    ("AK(2) classical class (positive control)",
     "results/stable_ac/fable/ak2_members.jsonl"),
    ("AK(3)+z stable class",
     "results/stable_ac/fable/stable_contrast_ak3z_members.jsonl.gz"),
    ("AK(2)+z stable class (positive control)",
     "results/stable_ac/fable/stable_contrast_ak2z_members.jsonl.gz"),
)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--targets", default=TARGETS_JSON)
    parser.add_argument("--out", default=DEFAULT_REPORT)
    args = parser.parse_args(argv)
    targets = load_targets(args.targets)
    print(f"[targets] {len(targets['entries'])} certified targets "
          f"({len(targets['exact'])} exact keys)", flush=True)
    report = intersect_corpus(DEFAULT_SOURCES, targets)
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=1)
    print(f"[targets] wrote {args.out}; total hits {report['total_hits']}", flush=True)


if __name__ == "__main__":
    main()
