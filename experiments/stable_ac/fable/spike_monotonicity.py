"""Is gamma_N monotone under SPIKES (insertion of a cancelling pair)?

A *spike* on an exact word-realized presentation inserts a letter immediately
followed by its inverse at some position of some relator::

    "xxy"  --spike(relator 0, position 0, letter 'y')-->  "yYxxy"

Spiking is the exact inverse of one free-reduction step, i.e. the inverse of one
elementary step of Lackenby's move ``(0)`` (free/cyclic reduction).  A spiked word
is never cyclically reduced: the corner ``(c, c^-1)`` it creates is an A-loop at a
germ, so the R1c-v2 rank-n solver fails closed (``UNSUPPORTED``) on every spiked
complex.  Only the factorial census ``gamma_N_factorial_n`` -- which is
loop-tolerant, since ``build_link_n`` imposes no looplessness hypothesis -- can
decide them.  Everything in this module therefore goes through the census.

Conventions (R3PRIME_GRAFT_CALCULUS.md sec. 0, GAMMA_N_SYMMETRY_LEMMA.md):
unhalved ``defect(C) = |A| - |C| + 2L(C) - |AC|`` and ``gamma_N = min_C defect(C) / 2``;
``gamma_N_factorial_n`` reports the UNHALVED ``minimum_defect``, so
``gamma_N = minimum_defect // 2``.  ``gamma_N = 0`` iff the complex is orientably
thickenable (Theorem 2 / Theorem D).

Known fact used as a fixture (recorded before this experiment): the reduced pair
``("xyXY","xxy")`` has ``gamma_N = 0`` while the spiked pair ``("xyXY","yYxxy")``
has ``gamma_N = 1`` -- reduction can DESTROY non-thickenability.  The open
direction, and the question this module settles empirically, is the converse:

    SPIKE MONOTONICITY (conjecture):  gamma_N(spike(P)) >= gamma_N(P)
    for every cyclically reduced exact presentation P and every single spike.

Three tiers are run, all pure enumeration + census (no AC-move search of any kind):

* TIER 1 -- exhaustive over all cyclically reduced rank-2 pairs of bounded total
  length, every single spike of each.
* TIER 2 -- all/sampled DOUBLE spikes on a random sample of tier-1 bases (depth-2
  failure is logically possible even if depth 1 holds, so it is measured, not
  assumed).
* TIER 3 -- AK(3), AK(2) and the smallest-census members of AK(3)'s recorded class.

Engine.  The link (``build_link_n``) and every structural datum come from the
audited ``neuwirth_rank_n`` module, which is imported and never modified.  The
census *loop* is re-implemented here as a numba kernel purely for speed; it is
validated case-by-case against the audited ``gamma_N_factorial_n`` (see
``cross_check`` and ``tests/fable/test_spike_monotonicity.py``), and the module
falls back to the audited census when numba is unavailable.
"""

from __future__ import annotations

import argparse
import gzip
import json
import math
import os
import random
import time
from itertools import product

import numpy as np

from experiments.stable_ac.fable.ac_words import (
    canon_pair,
    inverse,
    is_cyclically_reduced,
)
from experiments.stable_ac.fable.neuwirth_rank_n import (
    build_link_n,
    census_size,
    gamma_N_factorial_n,
)

__all__ = [
    "LETTERS",
    "GENERATORS",
    "spike",
    "spike_sites",
    "spiked_variants",
    "canon_exact_rel",
    "canon_exact_pair",
    "cyclically_reduced_words",
    "enumerate_bases",
    "census_defects",
    "gamma_N",
    "cross_check",
    "tier1",
    "tier2",
    "tier3",
    "main",
    "SEED",
    "DEFAULT_CAP",
]

LETTERS = ("x", "X", "y", "Y")
GENERATORS = ("x", "y")

SEED = 20260729
DEFAULT_CAP = 20_000_000

# solver alphabet order Y < y < X < x (same convention as ac_words); redefined here
# so that nothing private is imported.
_ORDER = {"Y": 0, "y": 1, "X": 2, "x": 3}

AK3 = ("xxxYYYY", "xyxYXY")
AK2 = ("xxYYY", "xyxYXY")

REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
AK3_MEMBERS = os.path.join(
    REPO_ROOT, "results", "stable_ac", "fable", "ak3_matched_members.jsonl.gz"
)
RESULT_PATH = os.path.join(
    REPO_ROOT, "results", "stable_ac", "fable", "spike_monotonicity.json"
)


# --------------------------------------------------------------------------------------
# spikes
# --------------------------------------------------------------------------------------


def spike(word: str, position: int, letter: str) -> str:
    """Insert the cancelling pair ``letter . letter^-1`` at ``position`` of ``word``."""
    if letter not in LETTERS:
        raise ValueError(f"bad letter {letter!r}")
    if not 0 <= position <= len(word):
        raise ValueError(f"position {position} out of range for {word!r}")
    return word[:position] + letter + letter.swapcase() + word[position:]


def spike_sites(words):
    """Every single-spike site ``(relator index, position, letter)`` of ``words``.

    Positions run over ``0 .. len(w)`` inclusive.  Position ``len(w)`` is a cyclic
    rotation of position ``0`` and therefore gamma_N-equivalent (GAMMA_N_SYMMETRY_LEMMA
    case (i)); it is still enumerated and removed by the canonical de-duplication in
    ``spiked_variants``, so completeness never rests on that argument.
    """
    out = []
    for j, w in enumerate(words):
        for p in range(len(w) + 1):
            for c in LETTERS:
                out.append((j, p, c))
    return out


def apply_site(words, site):
    j, p, c = site
    words = list(words)
    words[j] = spike(words[j], p, c)
    return tuple(words)


def spiked_variants(words):
    """``{canonical spiked pair: representative site}`` over all single spikes."""
    out = {}
    for site in spike_sites(words):
        got = apply_site(words, site)
        key = canon_exact_pair(got)
        if key not in out:
            out[key] = (got, site)
    return out


# --------------------------------------------------------------------------------------
# EXACT canonical form (no reduction!) -- GAMMA_N_SYMMETRY_LEMMA (i)+(ii)+(iii)
# --------------------------------------------------------------------------------------


def _rot_key(w: str):
    return tuple(_ORDER[c] for c in w)


def canon_exact_rel(w: str) -> str:
    """Lex-min over the rotations of ``w`` and of ``w^-1`` -- NO free/cyclic reduction.

    ``ac_words.canon_rel`` composes ``cyclic_reduce`` first, which is exactly what must
    NOT happen here: reduction changes the exact complex (that is the phenomenon under
    study).  gamma_N is invariant under rotation and inversion of a relator by
    GAMMA_N_SYMMETRY_LEMMA cases (i) and (ii).
    """
    if not w:
        return ""
    best = None
    for word in (w, inverse(w)):
        doubled = word + word
        n = len(word)
        for i in range(n):
            cand = doubled[i:i + n]
            key = _rot_key(cand)
            if best is None or key < best[0]:
                best = (key, cand)
    return best[1]


def canon_exact_pair(words):
    """Canonical exact key: ``canon_exact_rel`` each relator, then sort (case (iii))."""
    parts = sorted((canon_exact_rel(w) for w in words), key=lambda w: (len(w), _rot_key(w)))
    return tuple(parts)


# --------------------------------------------------------------------------------------
# base enumeration
# --------------------------------------------------------------------------------------


_CR_CACHE: dict = {}


def cyclically_reduced_words(length: int):
    """All cyclically reduced words of exactly ``length`` letters (memoised)."""
    got = _CR_CACHE.get(length)
    if got is None:
        got = tuple(w for w in ("".join(t) for t in product(LETTERS, repeat=length))
                    if is_cyclically_reduced(w))
        _CR_CACHE[length] = got
    return got


def enumerate_bases(max_total: int):
    """All canonical cyclically reduced rank-2 pairs with total length <= ``max_total``.

    "rank-2" = both generators occur in the pair (otherwise the presentation is a
    rank-1 presentation with a spurious generator and the spike alphabet would change
    the rank).  Both relators are nonempty.  ``ac_words.canon_pair`` supplies the
    rotation/inversion/swap canonical form; it also cyclically reduces, which is a
    no-op on these inputs.
    """
    seen = {}
    skipped_rank1 = 0
    raw = 0
    for a in range(1, max_total):
        for b in range(1, max_total - a + 1):
            for w1 in cyclically_reduced_words(a):
                for w2 in cyclically_reduced_words(b):
                    raw += 1
                    if set((w1 + w2).lower()) != {"x", "y"}:
                        skipped_rank1 += 1
                        continue
                    key = canon_pair(w1, w2)
                    if key not in seen:
                        seen[key] = None
    bases = sorted(seen, key=lambda p: (len(p[0]) + len(p[1]), _rot_key(p[0]), _rot_key(p[1])))
    return bases, {"raw_ordered_pairs": raw, "skipped_rank1": skipped_rank1,
                   "canonical_bases": len(bases)}


# --------------------------------------------------------------------------------------
# census engine
# --------------------------------------------------------------------------------------

try:  # pragma: no cover - exercised by whichever branch the environment provides
    from numba import njit as _njit

    HAVE_NUMBA = True
except Exception:  # pragma: no cover
    HAVE_NUMBA = False

    def _njit(*args, **kwargs):
        def deco(fn):
            return fn
        return deco


@_njit(cache=True, nogil=True)
def _census_kernel(n_darts, A, B, gdarts, goff, gdeg, gfact, total, FACT):
    """Histogram of ``|AC|`` over the whole compatible family.

    Mirrors ``neuwirth_rank_n.compatible_orders_n`` exactly: for each positive germ
    ``2k`` the first dart is pinned and the remaining ``deg - 1`` darts run over all
    permutations (decoded here from the factorial number system), and the partner germ
    ``2k + 1`` carries ``B`` of the reversed order.  ``|AC|`` is the cycle count of
    ``d -> A[C[d]]``.  The caller turns ``|AC|`` into the defect.
    """
    ngen = gdeg.shape[0]
    maxdeg = 1
    for k in range(ngen):
        if gdeg[k] > maxdeg:
            maxdeg = gdeg[k]
    hist = np.zeros(n_darts + 1, dtype=np.int64)
    C = np.zeros(n_darts, dtype=np.int64)
    seen = np.zeros(n_darts, dtype=np.uint8)
    seq = np.zeros(maxdeg, dtype=np.int64)
    neg = np.zeros(maxdeg, dtype=np.int64)
    avail = np.zeros(maxdeg, dtype=np.int64)
    for t in range(total):
        rem = t
        for k in range(ngen):
            d = gdeg[k]
            if d == 0:
                continue
            f = gfact[k]
            idx = rem % f
            rem = rem // f
            off = goff[k]
            seq[0] = gdarts[off]
            m = d - 1
            for j in range(m):
                avail[j] = gdarts[off + 1 + j]
            navail = m
            for j in range(m):
                fj = FACT[navail - 1]
                p = idx // fj
                idx = idx - p * fj
                seq[1 + j] = avail[p]
                for q in range(p, navail - 1):
                    avail[q] = avail[q + 1]
                navail -= 1
            for j in range(d):
                nxt = j + 1
                if nxt == d:
                    nxt = 0
                C[seq[j]] = seq[nxt]
            for j in range(d):
                neg[j] = B[seq[d - 1 - j]]
            for j in range(d):
                nxt = j + 1
                if nxt == d:
                    nxt = 0
                C[neg[j]] = neg[nxt]
        for i in range(n_darts):
            seen[i] = 0
        nac = 0
        for start in range(n_darts):
            if seen[start] == 1:
                continue
            nac += 1
            cur = start
            while seen[cur] == 0:
                seen[cur] = 1
                cur = A[C[cur]]
        hist[nac] += 1
    return hist


def census_defects(words, cap: int = DEFAULT_CAP, generators=GENERATORS,
                   engine: str = "auto") -> dict:
    """Exact defect histogram of the compatible family; ``SKIPPED_CAP`` beyond ``cap``.

    Keys: ``status`` (``OK`` / ``SKIPPED_CAP``), ``expected_cases``,
    ``enumerated_cases``, ``defect_histogram``, ``minimum_defect`` (UNHALVED),
    ``gamma_N``, ``link_components``, ``degrees``.
    """
    words = tuple(words)
    generators = tuple(generators)
    data = build_link_n(words, generators)
    size = census_size(data, generators)
    info = {
        "words": list(words),
        "expected_cases": int(size),
        "cap_rotations": int(cap),
        "link_components": int(data.link_components),
        "degrees": {g: int(data.degree(2 * k)) for k, g in enumerate(generators)},
    }
    if size > cap:
        info.update(status="SKIPPED_CAP", enumerated_cases=0, defect_histogram={},
                    minimum_defect=None, gamma_N=None, engine=None)
        return info
    if engine == "python" or (engine == "auto" and not HAVE_NUMBA):
        got = gamma_N_factorial_n(words, generators, cap_rotations=cap,
                                  keep_accepting=False)
        minimum = got["minimum_defect"]
        info.update(status=got["status"], enumerated_cases=got["enumerated_cases"],
                    defect_histogram={int(k): int(v)
                                      for k, v in got["defect_histogram"].items()},
                    minimum_defect=None if minimum is None else int(minimum),
                    gamma_N=None if minimum is None else int(minimum) // 2,
                    engine="python")
        return info

    ngen = len(generators)
    flat = []
    goff = np.zeros(ngen, dtype=np.int64)
    gdeg = np.zeros(ngen, dtype=np.int64)
    gfact = np.ones(ngen, dtype=np.int64)
    for k in range(ngen):
        darts = data.vertex_darts[2 * k]
        goff[k] = len(flat)
        gdeg[k] = len(darts)
        gfact[k] = math.factorial(max(len(darts) - 1, 0))
        flat.extend(darts)
    gdarts = np.array(flat if flat else [0], dtype=np.int64)
    maxdeg = int(gdeg.max()) if ngen else 1
    FACT = np.array([math.factorial(i) for i in range(max(maxdeg, 2))], dtype=np.int64)
    total = 1
    for k in range(ngen):
        total *= int(gfact[k])
    if total != size:
        raise RuntimeError(f"kernel family size {total} != census_size {size}")

    hist_nac = _census_kernel(
        int(data.n_darts),
        np.array(data.A, dtype=np.int64),
        np.array(data.B, dtype=np.int64),
        gdarts, goff, gdeg, gfact, int(total), FACT,
    )
    base = data.n_occurrences - len(data.present_germs) + 2 * data.link_components
    hist = {}
    enumerated = 0
    for nac, count in enumerate(hist_nac):
        c = int(count)
        if not c:
            continue
        enumerated += c
        hist[base - nac] = hist.get(base - nac, 0) + c
    if enumerated != total:
        raise RuntimeError(f"kernel enumerated {enumerated} != {total}")
    minimum = min(hist) if hist else None
    info.update(status="OK", enumerated_cases=enumerated, defect_histogram=hist,
                minimum_defect=minimum,
                gamma_N=None if minimum is None else minimum // 2,
                engine="numba")
    return info


def gamma_N(words, cap: int = DEFAULT_CAP, generators=GENERATORS, engine: str = "auto"):
    """``(gamma_N or None, info)`` -- ``None`` exactly when the census was capped out."""
    info = census_defects(words, cap=cap, generators=generators, engine=engine)
    return info["gamma_N"], info


def cross_check(words, cap: int = DEFAULT_CAP, generators=GENERATORS) -> dict:
    """Run BOTH engines on ``words`` and report whether the histograms agree."""
    fast = census_defects(words, cap=cap, generators=generators, engine="auto")
    slow = census_defects(words, cap=cap, generators=generators, engine="python")
    return {
        "words": list(words),
        "agree": (fast["defect_histogram"] == slow["defect_histogram"]
                  and fast["minimum_defect"] == slow["minimum_defect"]
                  and fast["enumerated_cases"] == slow["enumerated_cases"]),
        "fast": fast,
        "slow": slow,
    }


# --------------------------------------------------------------------------------------
# tiers
# --------------------------------------------------------------------------------------


def _hist_add(hist: dict, key) -> None:
    hist[key] = hist.get(key, 0) + 1


def _classify_counterexamples(counterexamples):
    """``(breakdown histogram, STRICT sublist)``.

    STRICT = the base has every relator of length >= 3 AND every relator using both
    generators, i.e. the degenerate shapes (a one-letter relator, or a relator over a
    single generator) are excluded.  This is bookkeeping, not a verdict.
    """
    breakdown: dict = {}
    strict = []
    for ce in counterexamples:
        prof = ce["base_profile"]
        key = (f"min_relator_length={prof['min_relator_length']}"
               f";both_generators_in_every_relator="
               f"{prof['every_relator_uses_both_generators']}"
               f";base_solver_verdict={ce.get('base_solver_verdict')}")
        _hist_add(breakdown, key)
        if (prof["min_relator_length"] >= 3
                and prof["every_relator_uses_both_generators"]):
            strict.append(ce)
    return dict(sorted(breakdown.items())), strict


def presentation_profile(words, generators=GENERATORS) -> dict:
    """Structural profile used to classify counterexamples (no verdict is derived)."""
    words = tuple(words)
    data = build_link_n(words, generators)
    both = all(set(w.lower()) == set(generators) for w in words)
    return {
        "relator_lengths": [len(w) for w in words],
        "min_relator_length": min(len(w) for w in words),
        "every_relator_uses_both_generators": bool(both),
        "link_components": int(data.link_components),
        "has_A_loop": bool(data.has_loop),
        "cyclically_reduced": all(is_cyclically_reduced(w) for w in words),
    }


def _solver_verdict(words, generators=GENERATORS):
    """The R1c-v2 rank-n solver verdict (recorded for context only, never as gamma_N)."""
    from experiments.stable_ac.fable.neuwirth_rank_n import solve_spherical_n
    try:
        return solve_spherical_n(words, generators).verdict
    except Exception as exc:  # pragma: no cover - defensive
        return f"ERROR: {type(exc).__name__}"


def tier1(max_total: int = 7, cap: int = 2_000_000, cross_check_every: int = 0,
          verbose: bool = False) -> dict:
    """Exhaustive single spikes on every canonical base of total length <= max_total."""
    t0 = time.time()
    bases, stats = enumerate_bases(max_total)
    counterexamples = []
    delta_hist: dict = {}
    base_gamma_hist: dict = {}
    spiked_gamma_hist: dict = {}
    attempted = measured = skipped = 0
    raw_sites = 0
    odd_defects = 0
    cross_checked = 0
    cross_failures = []
    per_base = []
    for n, base in enumerate(bases):
        g_base, info_base = gamma_N(base, cap=cap)
        if g_base is None:
            raise RuntimeError(f"base census capped out: {base} ({info_base})")
        if info_base["minimum_defect"] % 2:
            odd_defects += 1
        _hist_add(base_gamma_hist, g_base)
        variants = spiked_variants(base)
        raw_sites += len(spike_sites(base))
        worst = None
        for key, (got, site) in sorted(variants.items()):
            attempted += 1
            g_spk, info = gamma_N(got, cap=cap)
            if g_spk is None:
                skipped += 1
                continue
            measured += 1
            if info["minimum_defect"] % 2:
                odd_defects += 1
            _hist_add(spiked_gamma_hist, g_spk)
            _hist_add(delta_hist, g_spk - g_base)
            if worst is None or g_spk < worst:
                worst = g_spk
            if g_spk < g_base:
                counterexamples.append({
                    "base": list(base), "base_gamma_N": g_base,
                    "spiked": list(got), "spiked_gamma_N": g_spk,
                    "site": {"relator": site[0], "position": site[1], "letter": site[2]},
                    "base_defect_histogram": info_base["defect_histogram"],
                    "spiked_defect_histogram": info["defect_histogram"],
                    "base_profile": presentation_profile(base),
                    "spiked_profile": presentation_profile(got),
                    "base_solver_verdict": _solver_verdict(base),
                    "spiked_solver_verdict": _solver_verdict(got),
                })
            if cross_check_every and attempted % cross_check_every == 0:
                chk = cross_check(got, cap=cap)
                cross_checked += 1
                if not chk["agree"]:
                    cross_failures.append(chk)
        per_base.append({"base": list(base), "gamma_N": g_base,
                         "variants": len(variants),
                         "min_spiked_gamma_N": worst})
        if verbose and (n + 1) % 100 == 0:
            print(f"  tier1 base {n + 1}/{len(bases)} "
                  f"({time.time() - t0:.1f}s, {attempted} spikes)", flush=True)
    breakdown, strict = _classify_counterexamples(counterexamples)
    return {
        "max_total_length": max_total,
        "cap_rotations": cap,
        "enumeration": stats,
        "bases_enumerated": len(bases),
        "raw_spike_sites": raw_sites,
        "distinct_spikes_attempted": attempted,
        "spikes_measured": measured,
        "spikes_skipped_cap": skipped,
        "coverage_ok": measured + skipped == attempted,
        "counterexamples": counterexamples,
        "counterexample_count": len(counterexamples),
        "counterexample_breakdown": breakdown,
        "strict_counterexamples": strict,
        "strict_counterexample_count": len(strict),
        "delta_histogram": {str(k): v for k, v in sorted(delta_hist.items())},
        "base_gamma_histogram": {str(k): v for k, v in sorted(base_gamma_hist.items())},
        "spiked_gamma_histogram": {str(k): v for k, v in sorted(spiked_gamma_hist.items())},
        "odd_minimum_defects": odd_defects,
        "cross_checked": cross_checked,
        "cross_check_failures": cross_failures,
        "per_base": per_base,
        "seconds": round(time.time() - t0, 2),
    }


def tier2(bases, n_bases: int = 150, max_pairs_per_base: int = 200,
          cap: int = 2_000_000, seed: int = SEED, verbose: bool = False) -> dict:
    """Double spikes: does gamma_N drop below the base value at depth 2?"""
    t0 = time.time()
    rng = random.Random(seed)
    sample = sorted(rng.sample(list(bases), min(n_bases, len(bases))))
    counterexamples = []
    delta_hist: dict = {}
    attempted = measured = skipped = 0
    exhaustive_bases = sampled_bases = 0
    for n, base in enumerate(sample):
        g_base, _ = gamma_N(base, cap=cap)
        if g_base is None:
            raise RuntimeError(f"base census capped out: {base}")
        doubles = {}
        for site1 in spike_sites(base):
            once = apply_site(base, site1)
            for site2 in spike_sites(once):
                twice = apply_site(once, site2)
                key = canon_exact_pair(twice)
                if key not in doubles:
                    doubles[key] = (twice, site1, site2)
        keys = sorted(doubles)
        if len(keys) > max_pairs_per_base:
            keys = sorted(random.Random(seed + n).sample(keys, max_pairs_per_base))
            sampled_bases += 1
        else:
            exhaustive_bases += 1
        for key in keys:
            twice, site1, site2 = doubles[key]
            attempted += 1
            g_two, info = gamma_N(twice, cap=cap)
            if g_two is None:
                skipped += 1
                continue
            measured += 1
            _hist_add(delta_hist, g_two - g_base)
            if g_two < g_base:
                counterexamples.append({
                    "base": list(base), "base_gamma_N": g_base,
                    "double_spiked": list(twice), "double_spiked_gamma_N": g_two,
                    "site1": list(site1), "site2": list(site2),
                    "base_profile": presentation_profile(base),
                })
        if verbose and (n + 1) % 25 == 0:
            print(f"  tier2 base {n + 1}/{len(sample)} "
                  f"({time.time() - t0:.1f}s, {attempted} doubles)", flush=True)
    return {
        "seed": seed,
        "bases_sampled": len(sample),
        "max_pairs_per_base": max_pairs_per_base,
        "bases_exhaustive": exhaustive_bases,
        "bases_subsampled": sampled_bases,
        "cap_rotations": cap,
        "double_spikes_attempted": attempted,
        "double_spikes_measured": measured,
        "double_spikes_skipped_cap": skipped,
        "coverage_ok": measured + skipped == attempted,
        "counterexamples": counterexamples,
        "counterexample_count": len(counterexamples),
        "strict_counterexample_count": len(
            [ce for ce in counterexamples
             if ce["base_profile"]["min_relator_length"] >= 3
             and ce["base_profile"]["every_relator_uses_both_generators"]]),
        "delta_histogram": {str(k): v for k, v in sorted(delta_hist.items())},
        "seconds": round(time.time() - t0, 2),
    }


def smallest_census_members(path: str = AK3_MEMBERS, count: int = 3, exclude=()):
    """The ``count`` recorded AK(3)-class members with the smallest census family."""
    exclude = {canon_exact_pair(w) for w in exclude}
    rows = []
    with gzip.open(path, "rt") as fh:
        for line in fh:
            rec = json.loads(line)
            pair = tuple(rec["canonical"])
            if canon_exact_pair(pair) in exclude:
                continue
            rows.append((rec["census_family_size"], pair, rec.get("verdict"),
                         rec.get("total_length")))
    rows.sort(key=lambda r: (r[0], r[1]))
    return rows[:count]


def tier3(cap: int = DEFAULT_CAP, members: int = 3, verbose: bool = False) -> dict:
    """Spike the real targets: AK(3), AK(2) and the cheapest AK(3)-class members."""
    t0 = time.time()
    targets = [("AK3", AK3), ("AK2", AK2)]
    member_rows = smallest_census_members(count=members, exclude=[AK3])
    for i, (size, pair, verdict, total) in enumerate(member_rows):
        targets.append((f"AK3_class_member_{i}", tuple(pair)))
    out = []
    for name, words in targets:
        g_base, info_base = gamma_N(words, cap=cap)
        rows = []
        best = None
        attempted = measured = skipped = 0
        variants = spiked_variants(words)
        for key, (got, site) in sorted(variants.items()):
            attempted += 1
            g_spk, info = gamma_N(got, cap=cap)
            if g_spk is None:
                skipped += 1
                rows.append({"spiked": list(got), "site": list(site),
                             "gamma_N": None, "status": "SKIPPED_CAP",
                             "expected_cases": info["expected_cases"]})
                continue
            measured += 1
            if best is None or g_spk < best:
                best = g_spk
            rows.append({"spiked": list(got), "site": list(site), "gamma_N": g_spk,
                         "status": "OK", "expected_cases": info["expected_cases"],
                         "defect_histogram": {str(k): v
                                              for k, v in sorted(
                                                  info["defect_histogram"].items())}})
            if verbose:
                print(f"  {name} {got} gamma_N={g_spk} "
                      f"({info['expected_cases']} cases, {time.time() - t0:.1f}s)",
                      flush=True)
        drops = [r for r in rows if r["gamma_N"] is not None and r["gamma_N"] < g_base]
        out.append({
            "target": name,
            "words": list(words),
            "base_gamma_N": g_base,
            "base_census_size": info_base["expected_cases"],
            "base_defect_histogram": {str(k): v
                                      for k, v in sorted(
                                          info_base["defect_histogram"].items())},
            "raw_spike_sites": len(spike_sites(words)),
            "distinct_spikes_attempted": attempted,
            "spikes_measured": measured,
            "spikes_skipped_cap": skipped,
            "coverage_ok": measured + skipped == attempted,
            "coverage_fraction": (round(measured / attempted, 4) if attempted else None),
            "best_spiked_gamma_N": best,
            "reaches_gamma_le_1": bool(best is not None and best <= 1),
            "drops_below_base": drops,
            "spikes": rows,
        })
    return {"cap_rotations": cap, "targets": out,
            "seconds": round(time.time() - t0, 2)}


# --------------------------------------------------------------------------------------
# driver
# --------------------------------------------------------------------------------------


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tier1-max-total", type=int, default=8)
    ap.add_argument("--tier1-cap", type=int, default=2_000_000)
    ap.add_argument("--tier2-bases", type=int, default=150)
    ap.add_argument("--tier2-pairs", type=int, default=200)
    ap.add_argument("--tier3-cap", type=int, default=DEFAULT_CAP)
    ap.add_argument("--tier3-members", type=int, default=3)
    ap.add_argument("--cross-check-every", type=int, default=97)
    ap.add_argument("--skip-tier1", action="store_true")
    ap.add_argument("--skip-tier2", action="store_true")
    ap.add_argument("--skip-tier3", action="store_true")
    ap.add_argument("--out", default=RESULT_PATH)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    verbose = not args.quiet

    t0 = time.time()
    report = {
        "record": "spike_monotonicity",
        "seed": SEED,
        "engine": "numba" if HAVE_NUMBA else "python",
        "conventions": {
            "defect": "|A| - |C| + 2L - |AC| (UNHALVED, as gamma_N_factorial_n reports)",
            "gamma_N": "minimum_defect // 2",
            "spike": "insert letter c followed by c^-1 at a position of a relator",
        },
        "fixture": None,
        "tier1": None,
        "tier2": None,
        "tier3": None,
    }

    fixture_base = gamma_N(("xyXY", "xxy"))
    fixture_spiked = gamma_N(("xyXY", "yYxxy"))
    report["fixture"] = {
        "reduced": {"words": ["xyXY", "xxy"], "gamma_N": fixture_base[0]},
        "spiked": {"words": ["xyXY", "yYxxy"], "gamma_N": fixture_spiked[0]},
        "matches_recorded_fact": fixture_base[0] == 0 and fixture_spiked[0] == 1,
    }
    if verbose:
        print(f"fixture: {report['fixture']}", flush=True)

    if not args.skip_tier1:
        if verbose:
            print("TIER 1 ...", flush=True)
        report["tier1"] = tier1(args.tier1_max_total, cap=args.tier1_cap,
                                cross_check_every=args.cross_check_every,
                                verbose=verbose)
        if verbose:
            t = report["tier1"]
            print(f"TIER 1 done in {t['seconds']}s: {t['bases_enumerated']} bases, "
                  f"{t['distinct_spikes_attempted']} spikes, "
                  f"{t['counterexample_count']} counterexamples", flush=True)

    if not args.skip_tier2:
        if verbose:
            print("TIER 2 ...", flush=True)
        bases = ([tuple(r["base"]) for r in report["tier1"]["per_base"]]
                 if report["tier1"] else enumerate_bases(args.tier1_max_total)[0])
        report["tier2"] = tier2(bases, n_bases=args.tier2_bases,
                                max_pairs_per_base=args.tier2_pairs,
                                cap=args.tier1_cap, verbose=verbose)
        if verbose:
            t = report["tier2"]
            print(f"TIER 2 done in {t['seconds']}s: "
                  f"{t['double_spikes_measured']} measured, "
                  f"{t['counterexample_count']} counterexamples", flush=True)

    if not args.skip_tier3:
        if verbose:
            print("TIER 3 ...", flush=True)
        report["tier3"] = tier3(cap=args.tier3_cap, members=args.tier3_members,
                                verbose=verbose)
        if verbose:
            print(f"TIER 3 done in {report['tier3']['seconds']}s", flush=True)

    total_cases = 0
    refuted = []
    strict = []
    if report.get("tier1"):
        total_cases += report["tier1"]["spikes_measured"]
        refuted.extend(report["tier1"]["counterexamples"])
        strict.extend(report["tier1"]["strict_counterexamples"])
    if report.get("tier2"):
        total_cases += report["tier2"]["double_spikes_measured"]
        refuted.extend(report["tier2"]["counterexamples"])
    if report.get("tier3"):
        for tgt in report["tier3"]["targets"]:
            total_cases += tgt["spikes_measured"]
            refuted.extend(tgt["drops_below_base"])
    if refuted:
        first = strict[0] if strict else refuted[0]
        line = ("SPIKE MONOTONICITY: REFUTED by "
                f"{first.get('base', first.get('words'))} gamma_N="
                f"{first.get('base_gamma_N')} -> "
                f"{first.get('spiked', first.get('double_spiked'))} gamma_N="
                f"{first.get('spiked_gamma_N', first.get('double_spiked_gamma_N'))}"
                f" ({len(refuted)} counterexamples in {total_cases} measured cases,"
                f" {len(strict)} of them with every relator of length >= 3 over both"
                " generators)")
    else:
        line = f"SPIKE MONOTONICITY: no counterexample in {total_cases} cases"
    report["verdict"] = {
        "measured_cases": total_cases,
        "counterexamples": len(refuted),
        "strict_counterexamples": len(strict),
        "line": line,
    }
    report["seconds_total"] = round(time.time() - t0, 2)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=False)
    if verbose:
        print(report["verdict"]["line"], flush=True)
        print(f"wrote {args.out} ({os.path.getsize(args.out)} bytes, "
              f"{report['seconds_total']}s)", flush=True)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
