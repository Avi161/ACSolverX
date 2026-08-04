"""A13 -- turn S8's monotonicity NEGATIVE into a positive instrument: split-based
UPPER bounds on ``gamma_N``.

THE IDEA
--------
S9 (``results/stable_ac/theory/fable/S9_U124_THICKENABILITY.md``) decided all 124
unsolved Miller-Schupp representatives ``NOT_SPHERICAL`` by an exact procedure, so
``gamma_N >= 1`` for every one of them -- a certified LOWER bound.  To pin ``gamma_N``
exactly one also needs an UPPER bound, i.e. an explicit low-defect rotation system, and
S9's sampler goes blind above total length ~17 (measured detection 1.00 at L13 falling
to 0.00 at L19), leaving 87 of the 124 rows with an uninformative upper bound.

S8 (``S8_SPLITTING_MONOTONICITY.md``) says generator splitting is MONOTONE: ``link(P)``
is a minor of ``link(P')``, hence

    gamma_N(P) <= gamma_N(P').

Read in the direction this module needs: **a witness found for a SPLIT of P is a valid
upper bound for P itself**, and splitting redistributes a crowded germ's occurrences
across copies, which shrinks the compatible census ``prod_g (deg(g) - 1)!`` -- exactly
the quantity that makes long presentations undecidable.  So splitting buys back the
regime where the direct sampler is blind.

BOUND DIRECTION -- THE WHOLE POINT (``experiments/lessons/parallel-runs-and-bound-direction.md``)
-------------------------------------------------------------------------------------
For a certified split ``P'`` of ``P`` and ANY compatible rotation system on ``P'`` of
defect ``d``::

        d / 2  >=  gamma_N(P')  >=  gamma_N(P).

Therefore, and only therefore:

* a **witness** obtained after splitting is sound for the base -- an UPPER bound.  This
  is true whether the witness came from an exact census (which additionally pins
  ``gamma_N(P')`` exactly) or from a bounded sampler (which does not).
* a **failure** to find a low-defect witness after splitting says NOTHING extra about
  the base.  Silence here is worth exactly the measured detection rate of the search
  that produced it, and never more.
* ``gamma_N(P')`` is NEVER reported as ``gamma_N(P)``.  Every field this module writes
  that carries a split's value is named ``*_upper`` or ``split_*``; the base's value is
  only ever an interval ``[lower, upper]`` and is called ``certified`` only when the two
  ends meet.

The inequality is USED in one direction only.  Concluding anything about ``P`` from
``gamma_N(P') > k`` would be the filed bound-direction error and is refused: see
:func:`bracket_row`, which records ``upper_is_informative`` but never a lower bound from
a split.

SOUNDNESS DEPENDS ON CONJECTURE S8, WHICH IS A SKETCH, NOT A THEOREM
--------------------------------------------------------------------
S8 section 3 states monotonicity as a conjecture with a proof sketch and two open gaps
(GAP-S8-1: the defect bookkeeping ``nA - nC + 2L - nAC`` under the bigon contraction;
GAP-S8-2: degenerate splits).  Every bound this module produces is therefore
**conditional on Conjecture S8**, and every artifact says so in its ``conditional_on``
field.  Two consequences that are built into the code:

* degenerate splits are excluded by construction (:func:`split_shapes` never emits a
  shape leaving a generator of germ degree 1, which is GAP-S8-2's exclusion);
* the calibration stage is a genuine two-sided TEST of S8: a split bound strictly BELOW
  a state's known exact ``gamma_N`` would refute monotonicity outright.  The runner
  raises :class:`MonotonicityViolation` if that ever happens -- it is never voted on.

WHAT A ZERO WOULD MEAN (read before celebrating one)
----------------------------------------------------
A split bound of 0 on one of the 124 would say ``gamma_N(base) = 0``, i.e. the base is
thickenable.  But S9 already certified every one of the 124 ``NOT_SPHERICAL`` by an
exact decision procedure, i.e. ``gamma_N(base) >= 1``.  So a 0 here is FIRST a
contradiction between two instruments -- Conjecture S8 false, S9's decision wrong, or a
bug -- and only after that contradiction is resolved could it be a result.  The code
raises :class:`SplitContradiction` and refuses to write a triumphant verdict.  (If the
split itself is thickenable and the contradiction resolves against S8, the split is
still a balanced presentation of the trivial group in the base's STABLE AC class, so
Lackenby's theorem would give stable AC-triviality of the base -- a different and weaker
claim than "the base is thickenable", and it would need its own write-up.)

REUSED, NOT REWRITTEN
---------------------
* ``high_rank_refine.split_generator`` -- the tested splitting builder;
* ``high_rank_refine.certify_refinement`` -- the REPLAY certifier: it re-reads the
  definition layering out of ``P'`` alone and substitutes back, and the input relators
  must reappear up to cyclic rotation and inversion.  No plan is scored uncertified;
* ``high_rank_refine.split_minor_certificate`` -- the link-minor check behind S8;
* ``neuwirth_rank_n.gamma_N_factorial_n`` -- the exact census (two-sided on ``P'``);
* ``gateway_scan.sampled_min_defect`` / ``verify_witness`` -- the rank-generic sampler
  and its independent defect recomputation;
* ``u124_thickenability.load_reps`` / ``positive_ladder`` / ``census_size`` -- A9's data
  loading and its positive ladder;
* ``witness_check_n.check_witness_n`` -- the full Lemma-1 / Corollary-3 audit, used only
  where it applies (defect 0).

New-files-only contract: this module imports the existing stack and modifies nothing.
Plain CPU python3, single process.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments.stable_ac.fable import coset_enum as CE               # noqa: E402
from experiments.stable_ac.fable import gateway_scan as GS             # noqa: E402
from experiments.stable_ac.fable import high_rank_refine as HR         # noqa: E402
from experiments.stable_ac.fable import neuwirth_rank_n as RN          # noqa: E402
from experiments.stable_ac.fable import u124_thickenability as U9      # noqa: E402
from experiments.stable_ac.fable import witness_check_n as WCN         # noqa: E402

__all__ = [
    "SplitContradiction",
    "MonotonicityViolation",
    "SplitPlan",
    "CENSUS_CAP",
    "MAX_FRESH",
    "SAMPLE_BUDGET",
    "SAMPLE_SEEDS",
    "MASTER_SEED",
    "degrees_of",
    "census_of",
    "split_shapes",
    "bucket_pattern",
    "build_plan",
    "plan_family",
    "apply_plan",
    "certify_plan",
    "independent_defect",
    "evaluate_split",
    "bracket_row",
    "run_calibration",
    "run_targets",
]

# --------------------------------------------------------------------------------------
# budgets (every one of them is a cap, so no stage can hang)
# --------------------------------------------------------------------------------------

CENSUS_CAP = 200_000          # exact census on a SPLIT is run only up to this family size
MAX_FRESH = 12                # hard ceiling on fresh generators introduced by one plan
SAMPLE_BUDGET = 20_000        # sampler evaluations per seed when the census does not fit
SAMPLE_SEEDS = 2
MASTER_SEED = 20260804
PLANS_PER_ROW = 8             # distinct certified plans evaluated per presentation
ROW_TIME_CAP = 25.0           # seconds of evaluation per presentation, then stop

RESULTS = os.path.join(REPO_ROOT, "results", "stable_ac", "fable")
SWEEP_PATH = os.path.join(RESULTS, "u124_sweep.jsonl")
CALIBRATION_OUT = os.path.join(RESULTS, "split_bracket_calibration.json")
TARGETS_OUT = os.path.join(RESULTS, "split_bracket_targets.jsonl")
TARGETS_SUMMARY = os.path.join(RESULTS, "split_bracket_summary.json")

CONDITIONAL_ON = (
    "Conjecture S8 (generator splitting is monotone: link(P) is a minor of link(P'), "
    "hence gamma_N(P) <= gamma_N(P')).  S8_SPLITTING_MONOTONICITY.md section 3 gives a "
    "proof SKETCH with two open gaps (GAP-S8-1 defect bookkeeping, GAP-S8-2 degenerate "
    "splits).  Every upper bound in this artifact is conditional on that conjecture."
)

HIT_BANNER = (
    "A SPLIT of a Miller-Schupp unsolved representative reached defect 0.  Under "
    "Conjecture S8 this forces gamma_N(base) = 0 -- which CONTRADICTS S9's exact "
    "NOT_SPHERICAL decision on that base (gamma_N >= 1).  Resolve the contradiction "
    "before reporting anything: (i) recheck the split's witness with witness_check_n, "
    "(ii) recheck the split's exact census, (iii) recheck the base with "
    "disconnected_split.decide_pair, (iv) Todd-Coxeter on both.  One of S8, S9 or the "
    "code is wrong; which one is the result."
)


class SplitContradiction(RuntimeError):
    """Two instruments disagreed, or a split defect landed where it cannot.  Raised."""


class MonotonicityViolation(RuntimeError):
    """A certified split scored BELOW its base's known exact gamma_N: S8 would be false."""


# --------------------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------------------


def degrees_of(words, generators=None) -> dict:
    """``{generator: germ degree}`` -- how many times each generator occurs."""
    return HR.germ_degrees(tuple(words), generators)


def census_of(words, generators=None) -> int:
    """``prod_g (deg(g) - 1)!`` -- the size of the compatible-rotation family."""
    return HR.census_of(tuple(words), generators)


def _sizes(rem: int, k: int):
    """``rem`` occurrences into ``k`` near-equal POSITIVE parts, or ``None``."""
    if k <= 0 or rem < k:
        return None
    base, extra = divmod(rem, k)
    return tuple(base + (1 if i < extra else 0) for i in range(k))


def split_shapes(d: int, max_k: int) -> list:
    """Candidate splitting shapes for a generator of degree ``d``, cheapest first.

    A shape is ``(k, a0, sizes)``: ``k`` fresh copies, ``a0`` occurrences kept on the
    original generator, ``sizes[i]`` occurrences re-routed onto copy ``i``.  After the
    split the germ degrees are ``deg(g) = a0 + k`` (the ``k`` definition relators
    ``u_i g^{-1}`` each contribute one further occurrence of ``g``) and
    ``deg(u_i) = sizes[i] + 1``, so the compatible family shrinks from ``(d-1)!`` to

        (a0 + k - 1)! * prod_i sizes[i]!

    which is the whole reason this instrument exists.

    **GAP-S8-2 is excluded by construction**: a shape with ``a0 + k < 2`` would leave the
    original generator with germ degree 1 -- the degenerate split S8's sketch explicitly
    does not cover -- and is never emitted.  Every ``sizes[i] >= 1``, so no fresh copy is
    degenerate either.
    """
    out = []
    for k in range(1, max_k + 1):
        for a0 in range(0, d - k + 1):
            if a0 + k < 2:                      # would leave deg(g) = 1: degenerate
                continue
            sizes = _sizes(d - a0, k)
            if sizes is None:
                continue
            factor = math.factorial(a0 + k - 1)
            for s in sizes:
                factor *= math.factorial(s)
            out.append((factor, k, a0, sizes))
    out.sort(key=lambda t: (t[0], t[1], t[2]))
    return [(k, a0, sizes, factor) for factor, k, a0, sizes in out]


def bucket_pattern(n_occ: int, a0: int, sizes, rng: random.Random,
                   style: str = "block", offset: int = 0) -> tuple:
    """A bucket label per occurrence, in reading order: 0 keeps ``g``, ``i`` -> copy ``i``.

    ``style`` decides WHICH occurrences go together, which is the only freedom left once
    the shape is fixed -- and it is the freedom that MATTERS.  Measured on ``aca_117``
    (exact ``gamma_N = 1``): the shape ``k = 2, a0 = 2`` reaches the true defect 2 with a
    block pattern and overshoots to 4 with a round-robin pattern, and ``k = 3, a0 = 1``
    does the same.  The shape fixes the cost; the pattern fixes the tightness.  So the
    instrument searches over patterns at fixed cheap shapes rather than over shapes
    alone.  ``offset`` rotates the label sequence, which is a different block cut of the
    same cyclic word.
    """
    labels = [0] * a0
    for i, s in enumerate(sizes, 1):
        labels.extend([i] * s)
    if len(labels) != n_occ:
        raise ValueError(f"shape covers {len(labels)} occurrences, not {n_occ}")
    if style == "block":
        pattern = labels
    elif style == "roundrobin":
        counts = Counter(labels)
        order = sorted(counts)
        pattern = []
        while len(pattern) < n_occ:
            for b in order:
                if counts[b]:
                    pattern.append(b)
                    counts[b] -= 1
                    if len(pattern) == n_occ:
                        break
    elif style == "random":
        pattern = list(labels)
        rng.shuffle(pattern)
    else:
        raise ValueError(f"unknown style {style!r}")
    if offset:
        offset %= n_occ
        pattern = list(pattern[offset:]) + list(pattern[:offset])
    return tuple(pattern)


@dataclass(frozen=True)
class SplitPlan:
    """A replayable recipe: apply ``steps`` in order with ``split_generator``."""

    steps: tuple                      # ((gen, buckets), ...)
    style: str
    predicted_census: int
    n_fresh: int
    seed: int = 0

    def as_row(self) -> dict:
        return {"steps": [[g, list(b)] for g, b in self.steps], "style": self.style,
                "predicted_census": self.predicted_census, "n_fresh": self.n_fresh,
                "seed": self.seed}


def shape_combos(words, generators, census_cap: int = CENSUS_CAP,
                 max_fresh: int = MAX_FRESH, max_k_per_gen: int = 6) -> list:
    """One-round shape combinations whose PREDICTED census fits ``census_cap``.

    One entry per (shape of ``x``, shape of ``y``, ...) with ``None`` meaning "do not
    split this generator".  Returned as ``(predicted_census, n_fresh, {gen: shape})``
    sorted cheapest-first; ``n_fresh`` is what the coarseness ordering uses.
    """
    words, generators = tuple(words), tuple(generators)
    degs = degrees_of(words, generators)
    per_gen = {}
    for g in generators:
        d = degs.get(g, 0)
        options = [(None, math.factorial(max(d - 1, 0)), 0)]
        if d >= 3:
            for k, a0, sizes, factor in split_shapes(d, min(max_k_per_gen, d - 1)):
                options.append(((k, a0, sizes), factor, k))
        per_gen[g] = options
    combos: list = []

    def rec(i, acc, census, fresh):
        if census > census_cap or fresh > max_fresh:
            return
        if i == len(generators):
            if fresh == 0:
                return                             # the no-split state is handled apart
            combos.append((census, fresh, dict(acc)))
            return
        g = generators[i]
        for shape, factor, k in per_gen[g]:
            acc[g] = shape
            rec(i + 1, acc, census * factor, fresh + k)
            del acc[g]

    rec(0, {}, 1, 0)
    combos.sort(key=lambda t: (t[0], t[1]))
    return combos


def build_plan(words, generators, census_cap: int = CENSUS_CAP,
               max_fresh: int = MAX_FRESH, rng: random.Random | None = None,
               style: str = "block", shape_rank: int = 0) -> SplitPlan:
    """Greedily split the currently most crowded generator until the census fits.

    This is the FALLBACK path, used when no one-round combination of shapes gets the
    compatible family under ``census_cap`` -- which is the case for the highest-degree
    rows (a generator of degree 18 cannot be brought below ~5.6e6 in a single round,
    because the ``k`` definition relators put ``k`` new occurrences back on ``g``).
    Splitting a fresh copy again is legal and the replay certifier handles the resulting
    chain of definitions, so the loop simply repeats on whatever generator is now the
    most crowded.  ``max_fresh`` bounds the recursion; when it binds, the plan is still
    emitted and :func:`evaluate_split` scores it with the sampler instead of a census.
    """
    rng = rng or random.Random(0)
    cur_w, cur_g = tuple(words), tuple(generators)
    steps: list = []
    fresh = 0
    guard = 0
    while census_of(cur_w, cur_g) > census_cap and fresh < max_fresh:
        guard += 1
        if guard > 4 * max_fresh:
            break
        degs = degrees_of(cur_w, cur_g)
        gen = max(degs, key=lambda h: (degs[h], h))
        d = degs[gen]
        if d < 3:                                # nothing left worth splitting
            break
        room = max_fresh - fresh
        shapes = split_shapes(d, min(room, max(1, d - 1)))
        if not shapes:
            break
        k, a0, sizes, _factor = shapes[min(shape_rank, len(shapes) - 1)]
        occ = HR.occurrences_of(cur_w, gen)
        pattern = bucket_pattern(len(occ), a0, sizes, rng, style,
                                 offset=rng.randrange(len(occ)))
        ref = HR.split_generator(cur_w, cur_g, gen=gen, buckets=pattern)
        steps.append((gen, pattern))
        fresh += k
        cur_w, cur_g = ref.words, ref.generators
    return SplitPlan(tuple(steps), style, census_of(cur_w, cur_g),
                     len(cur_g) - len(generators), seed=rng.randrange(1 << 30))


_STYLE_CYCLE = ("block", "roundrobin", "random", "random", "block", "random")


def plan_family(words, generators, census_cap: int = CENSUS_CAP,
                max_fresh: int = MAX_FRESH, n_plans: int = PLANS_PER_ROW,
                master_seed: int = MASTER_SEED, combo_pool: int = 24) -> list:
    """Up to ``n_plans`` DISTINCT certifiable plans, deterministic given ``master_seed``.

    Ordering, and why: the head of the list is the COARSEST fitting combination (fewest
    fresh generators, largest surviving census) with a block pattern, because a plan that
    splits less has fewer chances to raise the defect.  The tail samples patterns at the
    CHEAPEST combinations, because the measured sensitivity is to the pattern rather than
    to the shape and a cheap shape lets many patterns be censused for the price of one
    expensive one.  If no one-round combination fits, :func:`build_plan`'s recursive
    greedy path supplies the plans instead.
    """
    words, generators = tuple(words), tuple(generators)
    combos = shape_combos(words, generators, census_cap, max_fresh)
    out: list = []
    seen: set = set()

    def offer(steps, style, predicted, fresh, seed):
        if not steps:
            return
        key = json.dumps([[g, list(b)] for g, b in steps], sort_keys=True)
        if key in seen:
            return
        seen.add(key)
        out.append(SplitPlan(tuple(steps), style, predicted, fresh, seed))

    def steps_of(shapes, rng, style, offsets):
        cur_w, cur_g = words, generators
        steps = []
        for g in generators:
            shape = shapes.get(g)
            if shape is None:
                continue
            k, a0, sizes = shape
            occ = HR.occurrences_of(cur_w, g)
            pattern = bucket_pattern(len(occ), a0, sizes, rng, style,
                                     offset=offsets.get(g, 0))
            ref = HR.split_generator(cur_w, cur_g, gen=g, buckets=pattern)
            steps.append((g, pattern))
            cur_w, cur_g = ref.words, ref.generators
        return steps, census_of(cur_w, cur_g)

    if combos:
        degs = degrees_of(words, generators)
        coarse = sorted(combos, key=lambda t: (t[1], -t[0]))
        cheap = sorted(combos, key=lambda t: (t[0], t[1]))
        seq: list = []
        for i in range(combo_pool):
            for source in (coarse, cheap):
                if i < len(source) and source[i] not in seq:
                    seq.append(source[i])
        n_off = 4
        i = 0
        for combo in seq:
            if len(out) >= n_plans:
                break
            for j in range(n_off):
                if len(out) >= n_plans:
                    break
                rng = random.Random((master_seed * 1_000_003 + i) % (2 ** 61))
                style = "block" if j < n_off - 1 else "random"
                offsets = {g: (j * max(1, degs.get(g, 1))) // n_off for g in generators}
                try:
                    steps, predicted = steps_of(combo[2], rng, style, offsets)
                except HR.RefinementError:
                    i += 1
                    continue
                offer(steps, style, predicted, combo[1], i)
                i += 1
    else:
        for i in range(4 * n_plans):
            if len(out) >= n_plans:
                break
            rng = random.Random((master_seed * 7_907 + i) % (2 ** 61))
            plan = build_plan(words, generators, census_cap, max_fresh, rng,
                              _STYLE_CYCLE[i % len(_STYLE_CYCLE)], shape_rank=0)
            offer(plan.steps, plan.style, plan.predicted_census, plan.n_fresh, i)
    return out[:n_plans]


def apply_plan(words, generators, plan: SplitPlan):
    """Replay ``plan``'s steps with the tested builder.  Returns ``(words, generators)``."""
    cur_w, cur_g = tuple(words), tuple(generators)
    for gen, buckets in plan.steps:
        ref = HR.split_generator(cur_w, cur_g, gen=gen, buckets=tuple(buckets))
        cur_w, cur_g = ref.words, ref.generators
    return cur_w, cur_g


def certify_plan(words, generators, plan: SplitPlan) -> dict:
    """Build the split and CERTIFY it by replay; no uncertified plan is ever scored.

    Two independent checks are recorded:

    * ``high_rank_refine.certify_refinement`` -- re-derives a legal definition layering
      from the split's relators ALONE (none of the builder's bookkeeping is consulted),
      expands the definitions innermost-out into the residual relators, and matches the
      freely reduced results against the input relators up to cyclic rotation and
      inversion.  A failure raises ``CertificationError`` and the plan is dropped.
    * ``high_rank_refine.split_minor_certificate`` -- for a single-step plan, that the
      input's labelled link multigraph is exactly the contraction of the split's along
      the ``k`` bigon edges.  This is the structural content of S8's sketch, checked
      instance by instance.  Multi-step plans are certified by replay only (the minor
      check composes in principle but the helper is single-step).
    """
    split_w, split_g = apply_plan(words, generators, plan)
    cert = HR.certify_refinement(HR.Presentation(tuple(words), tuple(generators)),
                                 HR.Presentation(split_w, split_g))
    minor = None
    if len(plan.steps) == 1:
        gen, buckets = plan.steps[0]
        ref = HR.split_generator(tuple(words), tuple(generators), gen=gen,
                                 buckets=tuple(buckets))
        minor = HR.split_minor_certificate(ref)
        if not minor["is_contraction"]:
            raise SplitContradiction(
                f"split_minor_certificate says link(P) is NOT the contraction of "
                f"link(P') for {words} -> {split_w}; S8's minor claim fails on this "
                f"instance and the bound would be unsound")
    return {
        "words": list(split_w),
        "generators": list(split_g),
        "rank": len(split_g),
        "census": census_of(split_w, split_g),
        "degrees": degrees_of(split_w, split_g),
        "certificate": {"relations": list(cert.relations),
                        "definition_words": [list(p) for p in cert.definition_words],
                        "expansions": [list(p) for p in cert.expansions],
                        "layerings_examined": cert.layerings_examined},
        "minor_certificate": (None if minor is None
                              else {"is_contraction": minor["is_contraction"],
                                    "contracted_edges": minor["contracted_edges"],
                                    "expected_contracted_edges":
                                        minor["expected_contracted_edges"]}),
    }


# --------------------------------------------------------------------------------------
# an INDEPENDENT defect recomputation (second code path, built from the words alone)
# --------------------------------------------------------------------------------------


def _cycles(perm) -> int:
    seen = bytearray(len(perm))
    n = 0
    for start in range(len(perm)):
        if seen[start]:
            continue
        n += 1
        cur = start
        while not seen[cur]:
            seen[cur] = 1
            cur = perm[cur]
    return n


def independent_defect(words, rotation) -> dict:
    """Recompute a rotation system's defect from the WORDS, with no shared machinery.

    ``build_link_n`` (used by the census and by ``gateway_scan``) is not called here:
    darts, the corner involution ``A``, the dart pairing ``B`` and the germ map are all
    rebuilt in this function from the letters.  The dart numbering convention (``2i`` /
    ``2i+1`` per letter in reading order, germ ``2k`` / ``2k+1`` per generator in sorted
    order) is the repo's and is reproduced deliberately so that a rotation produced by
    either instrument can be checked here.

    Returns ``defect = nA - nC + 2L - nAC`` together with its four terms.  Raises
    :class:`SplitContradiction` if the claimed rotation is not a compatible rotation
    system at all.
    """
    words = tuple(words)
    generators = tuple(sorted(set("".join(words).lower())))
    index = {g: k for k, g in enumerate(generators)}
    letters = []
    spans = []
    for w in words:
        if not w:
            raise SplitContradiction("empty relator")
        spans.append((len(letters), len(letters) + len(w)))
        letters.extend(w)
    n = len(letters)
    size = 2 * n
    B = list(range(size))
    for i in range(n):
        B[2 * i], B[2 * i + 1] = 2 * i + 1, 2 * i
    A = [None] * size
    for lo, hi in spans:
        span = hi - lo
        for k in range(span):
            i = lo + k
            j = lo + (k + 1) % span
            A[2 * i + 1] = 2 * j
            A[2 * j] = 2 * i + 1
    germ = [0] * size
    for i, c in enumerate(letters):
        k = index[c.lower()]
        lo, hi = (2 * k, 2 * k + 1) if c.islower() else (2 * k + 1, 2 * k)
        germ[2 * i], germ[2 * i + 1] = lo, hi

    orders = {}
    for key, seq in rotation.items():
        idx = int(key) if not isinstance(key, str) or key.isdigit() else None
        if idx is None:                                   # germ NAME, e.g. "x+"
            name = key
            base = name[:-1]
            sign = name[-1]
            if base not in index or sign not in "+-":
                raise SplitContradiction(f"unknown germ {key!r}")
            idx = 2 * index[base] + (0 if sign == "+" else 1)
        orders[idx] = tuple(int(d) for d in seq)

    present = sorted({germ[d] for d in range(size)})
    if sorted(orders) != present:
        raise SplitContradiction(
            f"rotation covers germs {sorted(orders)}, expected {present}")
    C = [None] * size
    for v, seq in orders.items():
        want = sorted(d for d in range(size) if germ[d] == v)
        if sorted(seq) != want:
            raise SplitContradiction(f"germ {v}: dart set mismatch")
        m = len(seq)
        for k in range(m):
            C[seq[k]] = seq[(k + 1) % m]
    if any(c is None for c in C):
        raise SplitContradiction("rotation does not cover every dart")
    Cinv = [0] * size
    for e in range(size):
        Cinv[C[e]] = e
    for e in range(size):
        if B[C[B[e]]] != Cinv[e]:
            raise SplitContradiction("compatibility B C B = C^-1 fails")

    AC = [A[C[e]] for e in range(size)]
    nA, nC, nAC = _cycles(A), _cycles(C), _cycles(AC)
    # link components: orbits of <A, C> (rotation-independent: C's cycles are the germs)
    seen = bytearray(size)
    L = 0
    for start in range(size):
        if seen[start]:
            continue
        L += 1
        stack = [start]
        seen[start] = 1
        while stack:
            cur = stack.pop()
            for nxt in (A[cur], C[cur]):
                if not seen[nxt]:
                    seen[nxt] = 1
                    stack.append(nxt)
    defect = nA - nC + 2 * L - nAC
    return {"nA": nA, "nC": nC, "link_components": L, "nAC": nAC, "defect": defect,
            "gamma_N": defect // 2 if defect % 2 == 0 else None}


# --------------------------------------------------------------------------------------
# scoring one split
# --------------------------------------------------------------------------------------


def evaluate_split(words, generators, census_cap: int = CENSUS_CAP,
                   budget: int = SAMPLE_BUDGET, seeds: int = SAMPLE_SEEDS,
                   master_seed: int = MASTER_SEED, want_witness: bool = True) -> dict:
    """Minimum defect over the split's compatible family: exact if it fits, else sampled.

    * ``method = "exact_census"`` -- the whole family was enumerated, so the value IS
      ``2 * gamma_N(P')``; two-sided ON THE SPLIT (and still only an upper bound for the
      base).
    * ``method = "sampled"`` -- a bounded hill-climb; the value is an upper bound on
      ``2 * gamma_N(P')``, hence still an upper bound for the base.  Its SILENCE is worth
      the calibration's measured detection rate and nothing more.
    """
    words, generators = tuple(words), tuple(generators)
    size = census_of(words, generators)
    t0 = time.time()
    out = {"census_family_size": size, "method": None, "min_defect": None,
           "exhaustive_on_split": None, "witness": None, "witness_check": None,
           "seconds": None}
    if size <= census_cap:
        census = RN.gamma_N_factorial_n(words, generators, cap_rotations=census_cap,
                                        keep_accepting=False)
        if census["status"] == "OK":
            out.update(method="exact_census", min_defect=census["minimum_defect"],
                       exhaustive_on_split=True,
                       enumerated_cases=census["enumerated_cases"],
                       link_components=census["link_components"])
    if out["min_defect"] is None:
        best = None
        best_orders = None
        per_seed = []
        for k in range(seeds):
            rng = random.Random((master_seed * 7_919 + k) % (2 ** 61))
            defect, orders = GS.sampled_min_defect(words, budget, rng)
            per_seed.append(defect)
            if best is None or (defect is not None and defect < best):
                best, best_orders = defect, orders
        out.update(method="sampled", min_defect=best, exhaustive_on_split=False,
                   per_seed_best_defect=per_seed, budget_per_seed=budget, seeds=seeds)
        if best_orders is not None:
            out["witness"] = {str(k): list(v) for k, v in best_orders.items()}
    # fetch an explicit witness for the exact-census path too (cheap, bounded)
    if want_witness and out["method"] == "exact_census" and out["min_defect"] is not None:
        rng = random.Random((master_seed * 104_729) % (2 ** 61))
        defect, orders = GS.sampled_min_defect(words, min(budget, 8_000), rng)
        if orders is not None and defect == out["min_defect"]:
            out["witness"] = {str(k): list(v) for k, v in orders.items()}
    if out["witness"] is not None:
        rot = {int(k): v for k, v in out["witness"].items()}
        recomputed = GS.verify_witness(words, rot)
        independent = independent_defect(words, rot)
        if recomputed != out["min_defect"] or independent["defect"] != out["min_defect"]:
            raise SplitContradiction(
                f"witness defect disagrees: search {out['min_defect']}, "
                f"gateway_scan.verify_witness {recomputed}, independent "
                f"{independent['defect']} for {words}")
        out["witness_check"] = {"gateway_scan_verify_witness": recomputed,
                                "independent_recomputation": independent}
    out["seconds"] = round(time.time() - t0, 3)
    return out


# --------------------------------------------------------------------------------------
# one presentation
# --------------------------------------------------------------------------------------


def bracket_row(pair, generators=("x", "y"), lower_bound: int | None = None,
                census_cap: int = CENSUS_CAP, max_fresh: int = MAX_FRESH,
                n_plans: int = PLANS_PER_ROW, budget: int = SAMPLE_BUDGET,
                seeds: int = SAMPLE_SEEDS, master_seed: int = MASTER_SEED,
                time_cap: float = ROW_TIME_CAP, known_gamma: int | None = None) -> dict:
    """The MINIMUM defect over all certified splits, as an UPPER bound for ``pair``.

    ``lower_bound`` is whatever a two-sided instrument already certified about the BASE
    (for the 124 rows: ``1``, from S9's exhaustive ``NOT_SPHERICAL``).  It is used for
    two things only: to stop early once the bracket closes, and to raise
    :class:`SplitContradiction` if a split's bound lands strictly below it -- which
    cannot happen if S8 and the lower bound are both right.

    ``known_gamma`` is the state's EXACT gamma_N when it is known (calibration only).  A
    split bound strictly below it raises :class:`MonotonicityViolation`: that would
    refute S8, and it is never quietly recorded as a better bound.
    """
    pair = tuple(pair)
    t0 = time.time()
    plans = plan_family(pair, generators, census_cap, max_fresh, n_plans, master_seed)
    evaluated = []
    best = None
    best_entry = None
    base_exact = None
    # The base itself, when its own compatible family fits: that is an EXACT gamma_N and
    # no split is needed.  It is recorded separately so a split's value is never confused
    # with the base's.
    if census_of(pair, generators) <= census_cap:
        base_score = evaluate_split(pair, generators, census_cap, budget, seeds,
                                    master_seed, want_witness=True)
        if base_score["method"] == "exact_census" and base_score["min_defect"] is not None:
            base_exact = base_score["min_defect"] // 2
            best = base_score["min_defect"]
            best_entry = {"plan": {"steps": [], "style": "none", "predicted_census":
                                   census_of(pair, generators), "n_fresh": 0, "seed": 0},
                          "certified": True,
                          "split": {"words": list(pair), "generators": list(generators),
                                    "rank": len(generators),
                                    "census": census_of(pair, generators),
                                    "degrees": degrees_of(pair, generators),
                                    "certificate": None, "minor_certificate": None},
                          "score": base_score}
            evaluated.append(best_entry)
    for i, plan in enumerate(plans):
        if best is not None and lower_bound is not None and best // 2 <= lower_bound:
            break
        if evaluated and time.time() - t0 > time_cap:
            break
        try:
            built = certify_plan(pair, generators, plan)
        except HR.CertificationError as exc:
            evaluated.append({"plan": plan.as_row(), "certified": False,
                              "error": f"{type(exc).__name__}: {exc}"})
            continue
        except HR.RefinementError as exc:
            evaluated.append({"plan": plan.as_row(), "certified": False,
                              "error": f"{type(exc).__name__}: {exc}"})
            continue
        score = evaluate_split(built["words"], built["generators"], census_cap,
                               budget, seeds, master_seed + 13 * i,
                               want_witness=True)
        entry = {"plan": plan.as_row(), "certified": True, "split": built,
                 "score": score}
        evaluated.append(entry)
        d = score["min_defect"]
        if d is None:
            continue
        if known_gamma is not None and d // 2 < known_gamma:
            raise MonotonicityViolation(
                f"certified split of {pair} scored defect {d} (gamma_N <= {d // 2}) "
                f"but the base's EXACT gamma_N is {known_gamma}; Conjecture S8 says a "
                f"split can only be >= the base, so S8, the exact value, or this code "
                f"is wrong.  Split: {built['words']}")
        if lower_bound is not None and d // 2 < lower_bound:
            raise SplitContradiction(
                f"certified split of {pair} gives gamma_N <= {d // 2} but a two-sided "
                f"instrument certified gamma_N >= {lower_bound} for the base.  Under "
                f"S8 this is impossible.  {HIT_BANNER if d == 0 else ''} "
                f"Split: {built['words']}")
        if best is None or d < best:
            best, best_entry = d, entry
        # early exit: the bound has met a value it provably cannot beat -- either the
        # base's certified lower bound (bracket closed) or, in calibration, its known
        # exact gamma_N (under S8 no certified split can go below it).
        if lower_bound is not None and best is not None and best // 2 <= lower_bound:
            break
        if known_gamma is not None and best is not None and best // 2 <= known_gamma:
            break
    upper = None if best is None else best // 2
    row = {
        "pair": list(pair),
        "generators": list(generators),
        "total_length": sum(len(w) for w in pair),
        "base_degrees": degrees_of(pair, generators),
        "base_census": census_of(pair, generators),
        "gamma_N_lower": lower_bound,
        "base_exact_gamma_N": base_exact,
        "split_gamma_N_upper": upper,
        "split_min_defect": best,
        "plans_built": len(plans),
        "plans_evaluated": sum(1 for e in evaluated if e.get("certified")),
        "plans_failed_certification": sum(1 for e in evaluated
                                          if not e.get("certified")),
        "best_plan": None if best_entry is None else best_entry["plan"],
        "best_split_words": None if best_entry is None else best_entry["split"]["words"],
        "best_split_generators": (None if best_entry is None
                                  else best_entry["split"]["generators"]),
        "best_split_rank": None if best_entry is None else best_entry["split"]["rank"],
        "best_split_census": None if best_entry is None else best_entry["split"]["census"],
        "best_method": None if best_entry is None else best_entry["score"]["method"],
        "best_exhaustive_on_split": (None if best_entry is None
                                     else best_entry["score"]["exhaustive_on_split"]),
        "best_witness": None if best_entry is None else best_entry["score"]["witness"],
        "best_witness_check": (None if best_entry is None
                               else best_entry["score"]["witness_check"]),
        "n_fresh_used": None if best_entry is None else best_entry["plan"]["n_fresh"],
        "defects_by_plan": [e["score"]["min_defect"] for e in evaluated
                            if e.get("certified")],
        "fresh_by_plan": [e["plan"]["n_fresh"] for e in evaluated if e.get("certified")],
        "bracket_closed": (lower_bound is not None and upper is not None
                           and upper == lower_bound),
        "seconds": round(time.time() - t0, 2),
        "bound_direction": ("split values bound gamma_N(base) from ABOVE only "
                            "(gamma_N(P) <= gamma_N(P') under Conjecture S8); a failure "
                            "to find a low-defect split says NOTHING about the base"),
        "conditional_on": CONDITIONAL_ON,
    }
    if known_gamma is not None:
        row["known_gamma_N"] = known_gamma
        row["overshoot"] = None if upper is None else upper - known_gamma
    if best == 0:
        row["HIT"] = HIT_BANNER
    return row


# --------------------------------------------------------------------------------------
# stage 1: calibration on a TWO-SIDED ladder (states with EXACT gamma_N)
# --------------------------------------------------------------------------------------


def _exact_gamma(pair, cap: int = 600_000):
    """Exact ``gamma_N`` by full census, or ``None`` when the family exceeds ``cap``."""
    generators = tuple(sorted(set("".join(pair).lower())))
    if U9.census_size(pair, generators) > cap:
        return None
    census = RN.gamma_N_factorial_n(tuple(pair), generators, cap_rotations=cap,
                                    keep_accepting=False)
    if census["status"] != "OK" or census["minimum_defect"] is None:
        return None
    return census["minimum_defect"] // 2


def calibration_ladder(sweep_path: str = SWEEP_PATH, per_length_cap: int = 4,
                       census_cap: int = 600_000, extra_cap: int = 24,
                       master_seed: int = MASTER_SEED) -> list:
    """States whose EXACT gamma_N is known, from three independent sources.

    1. the exactly-censused rows of A9's sweep (``aca_115`` = AK(3) at 2, ``aca_116`` at
       2, ``aca_117`` at 1) -- exact by a full census over the whole compatible family;
    2. A9's six certified gateways (gamma_N = 1 exactly: exhaustive ``NOT_SPHERICAL``
       from the base gives ``>= 1``, an independently re-verified defect-2 rotation gives
       ``<= 1``);
    3. rungs of A9's positive ladder (``u124_thickenability.positive_ladder``) --
       gamma_N = 0 states -- and short AK(2) members whose own census fits ``census_cap``,
       which contributes exact 0 / 1 / 2 rungs at several lengths.

    This is a TWO-SIDED ladder by construction: every rung's gamma_N is a number, not a
    bound, so ``split upper bound - true gamma_N`` is a measurable overshoot and a
    NEGATIVE overshoot would refute S8.  (T-S9b applies: the rungs' generator degrees are
    smaller than the 124 targets', so they need LESS splitting; ``n_fresh`` is recorded
    per rung and the overshoot is reported against it, not only against length.)
    """
    ladder = []
    seen = set()

    def add(pair, gamma, source, note=""):
        key = tuple(pair)
        if key in seen or gamma is None:
            return
        seen.add(key)
        ladder.append({"pair": list(pair), "total_length": sum(len(w) for w in pair),
                       "known_gamma_N": gamma, "source": source, "note": note,
                       "degrees": degrees_of(pair),
                       "min_degree": min(degrees_of(pair).values()),
                       "base_census": census_of(pair)})

    if os.path.exists(sweep_path):
        with open(sweep_path, encoding="utf-8") as fh:
            rows = [json.loads(line) for line in fh]
        for r in rows:
            if r["census"]["ran"]:
                add(tuple(r["pair"]), r["census"]["gamma_N"],
                    "u124 exact census", r["name"])
            elif r.get("gamma_N_certified"):
                add(tuple(r["pair"]), r["gamma_N_certified_value"],
                    "u124 certified bracket", r["name"])

    rng = random.Random(master_seed)
    pool = U9.positive_ladder(min_length=10, max_length=25, min_degree=3)
    by_length = defaultdict(list)
    for entry in pool:
        by_length[entry["total_length"]].append(entry)
    for length in sorted(by_length):
        rows = by_length[length]
        chosen = rows if len(rows) <= per_length_cap else rng.sample(rows,
                                                                    per_length_cap)
        for entry in chosen:
            add(tuple(entry["pair"]), 0, "positive ladder (gamma_N = 0)",
                entry["source"])

    # extra exact rungs at gamma_N >= 1: short AK(2)-class members whose census fits
    ak2 = os.path.join(RESULTS, "ak2_members.jsonl")
    if os.path.exists(ak2):
        cands = []
        with open(ak2, encoding="utf-8") as fh:
            for line in fh:
                row = json.loads(line)
                if row.get("verdict") == "SPHERICAL":
                    continue
                pair = tuple(row["canonical"])
                if tuple(pair) in seen:
                    continue
                if census_of(pair) > census_cap:
                    continue
                cands.append(pair)
        rng.shuffle(cands)
        added = 0
        for pair in cands:
            if added >= extra_cap:
                break
            gamma = _exact_gamma(pair, census_cap)
            if gamma is None:
                continue
            add(pair, gamma, "AK(2) member, exact census", "")
            added += 1
    ladder.sort(key=lambda r: (r["known_gamma_N"], r["total_length"], r["pair"]))
    return ladder


DEFAULT_REDUCTIONS = (1, 100, 10_000, 1_000_000)


def run_calibration(out_path: str = CALIBRATION_OUT, per_length_cap: int = 4,
                    extra_cap: int = 24, census_cap: int = CENSUS_CAP,
                    max_fresh: int = MAX_FRESH, n_plans: int = PLANS_PER_ROW,
                    budget: int = SAMPLE_BUDGET, seeds: int = SAMPLE_SEEDS,
                    time_cap: float = ROW_TIME_CAP, limit: int | None = None,
                    reductions=DEFAULT_REDUCTIONS, verbose: bool = True) -> dict:
    """Stage 1 (MANDATORY, runs first): the two-sided overshoot distribution.

    **The rungs are not the targets, and the mismatch is the whole difficulty (T-S9b).**
    A ladder rung of total length 13 has a compatible family of ~10^4 and needs NO split
    at all to be censused, while every one of the 124 targets has a family between
    1.6e9 and 2.6e17 and needs a reduction of 10^4 to 10^12 before anything fits.  A
    calibration that let each rung use whatever splitting it liked would therefore
    measure the instrument in a regime the targets never occupy, and would read as far
    too optimistic.

    So each rung is run at a LADDER OF FORCED REDUCTIONS: the per-split census cap is set
    to ``base_census // R`` for each ``R`` in ``reductions``, which forces the instrument
    to split as hard as a target of the corresponding crowding would force it.  The
    reported overshoot is indexed by ``R`` and by the number of fresh generators the plan
    actually used, and the targets record their own achieved reduction, so a target is
    read against the cell that matches it rather than against the easiest cell.
    """
    started = time.time()
    ladder = calibration_ladder(per_length_cap=per_length_cap, extra_cap=extra_cap)
    if limit is not None:
        ladder = ladder[:limit]
    rows = []
    violations = []
    for i, rung in enumerate(ladder, 1):
        base_census = rung["base_census"]
        for R in reductions:
            cap = min(census_cap, max(2, base_census // R))
            try:
                row = bracket_row(tuple(rung["pair"]), lower_bound=None,
                                  census_cap=cap, max_fresh=max_fresh,
                                  n_plans=n_plans, budget=budget, seeds=seeds,
                                  time_cap=time_cap, known_gamma=rung["known_gamma_N"])
            except MonotonicityViolation as exc:
                violations.append({"pair": rung["pair"], "reduction": R,
                                   "error": str(exc)})
                if verbose:
                    print(f"  [calib] !! MONOTONICITY VIOLATION on {rung['pair']} "
                          f"at R={R}: {exc}", flush=True)
                continue
            row.update({k: rung[k] for k in ("source", "note", "min_degree")})
            row["forced_reduction"] = R
            row["census_cap_used"] = cap
            row["achieved_reduction"] = (
                None if row["best_split_census"] in (None, 0)
                else round(base_census / row["best_split_census"], 1))
            rows.append(row)
            if verbose:
                print(f"  [calib] {i}/{len(ladder)} {rung['pair']} "
                      f"L{rung['total_length']} R={R} true={rung['known_gamma_N']} "
                      f"upper={row['split_gamma_N_upper']} fresh={row['n_fresh_used']} "
                      f"({time.time() - started:.0f}s)", flush=True)
    over = [r["overshoot"] for r in rows if r["overshoot"] is not None]
    by_true = defaultdict(list)
    by_fresh = defaultdict(list)
    by_length = defaultdict(list)
    by_reduction = defaultdict(list)
    for r in rows:
        if r["overshoot"] is None:
            continue
        by_true[r["known_gamma_N"]].append(r["overshoot"])
        by_fresh[r["n_fresh_used"]].append(r["overshoot"])
        by_length[r["total_length"]].append(r["overshoot"])
        by_reduction[r["forced_reduction"]].append(r["overshoot"])
    doc = {
        "record": "split_bracket_calibration",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "claims": ("MACHINERY calibration: how far ABOVE the true gamma_N a split-based "
                   "upper bound lands, on states whose gamma_N is known exactly.  No "
                   "statement about any AC class."),
        "units": "defects are UNHALVED; gamma_N = defect // 2",
        "conditional_on": CONDITIONAL_ON,
        "budgets": {"census_cap": census_cap, "max_fresh": max_fresh,
                    "plans_per_row": n_plans, "sample_budget": budget,
                    "sample_seeds": seeds, "row_time_cap": time_cap,
                    "master_seed": MASTER_SEED},
        "ladder_size": len(ladder),
        "rows_measured": len(rows),
        "monotonicity_violations": violations,
        "S8_test": ("A certified split scoring BELOW its base's exact gamma_N would "
                    "refute Conjecture S8.  Violations found: "
                    f"{len(violations)} of {len(ladder)}."),
        "overshoot_histogram": dict(sorted(Counter(over).items())),
        "overshoot_mean": (round(sum(over) / len(over), 3) if over else None),
        "overshoot_zero_fraction": (round(sum(1 for o in over if o == 0) / len(over), 4)
                                    if over else None),
        "overshoot_by_true_gamma": {str(k): dict(sorted(Counter(v).items()))
                                    for k, v in sorted(by_true.items())},
        "overshoot_by_fresh_generators": {str(k): dict(sorted(Counter(v).items()))
                                          for k, v in sorted(by_fresh.items())},
        "overshoot_by_total_length": {str(k): dict(sorted(Counter(v).items()))
                                      for k, v in sorted(by_length.items())},
        "overshoot_by_forced_reduction": {
            str(k): {"histogram": dict(sorted(Counter(v).items())),
                     "n": len(v), "mean": round(sum(v) / len(v), 3),
                     "exact_fraction": round(sum(1 for o in v if o == 0) / len(v), 4)}
            for k, v in sorted(by_reduction.items())},
        "forced_reductions": list(reductions),
        "how_to_read": (
            "Look up a target's achieved_reduction (base census / best split census) in "
            "overshoot_by_forced_reduction and read the overshoot distribution THERE.  "
            "The R = 1 cell is the easiest cell and no target occupies it: every one of "
            "the 124 needs a reduction of at least ~10^4."),
        "composition_mismatch": (
            "T-S9b.  The rungs' generator degrees are smaller than the 124 targets' "
            "(every target has min degree >= 6), so a rung needs FEWER fresh generators "
            "to fit the census cap.  Read overshoot_by_fresh_generators, not only "
            "overshoot_by_total_length: the instrument's cost is paid per split, and a "
            "rung matched only on length is not matched."),
        "rows": rows,
        "elapsed_seconds": round(time.time() - started, 1),
    }
    _write_json(out_path, doc)
    if verbose:
        print(f"[calib] {len(rows)} rungs; overshoot histogram "
              f"{doc['overshoot_histogram']}; violations {len(violations)}", flush=True)
    return doc


# --------------------------------------------------------------------------------------
# stage 2: the targets
# --------------------------------------------------------------------------------------


def _write_json(path: str, doc) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1)
        fh.write("\n")


def _write_jsonl(path: str, rows) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")


def load_sweep(sweep_path: str = SWEEP_PATH) -> list:
    """A9's per-row sweep, reused verbatim (its loader, its data, no re-derivation)."""
    with open(sweep_path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh]


def run_targets(sweep_path: str = SWEEP_PATH, out_path: str = TARGETS_OUT,
                summary_path: str = TARGETS_SUMMARY, which: str = "uncalibrated",
                census_cap: int = CENSUS_CAP, max_fresh: int = MAX_FRESH,
                n_plans: int = PLANS_PER_ROW, budget: int = SAMPLE_BUDGET,
                seeds: int = SAMPLE_SEEDS, time_cap: float = ROW_TIME_CAP,
                limit: int | None = None, resume: bool = True,
                verbose: bool = True) -> dict:
    """Stage 2: split-bracket the 124, or the subset whose upper bound is uninformative.

    ``which``: ``uncalibrated`` = the 87 rows A9 flagged ``sample_calibrated = False``;
    ``open`` = every row whose bracket is not already closed; ``all`` = all 124.

    Checkpointing: rows are appended to ``out_path`` as they finish and, with
    ``resume = True``, already-finished rows are read back and skipped, so a run that is
    cut short loses nothing.
    """
    started = time.time()
    sweep = load_sweep(sweep_path)
    if which == "uncalibrated":
        targets = [r for r in sweep if r.get("sample_calibrated") is False]
    elif which == "open":
        targets = [r for r in sweep if not r.get("gamma_N_certified")]
    else:
        targets = list(sweep)
    targets.sort(key=lambda r: (r["total_length"], r["name"]))
    if limit is not None:
        targets = targets[:limit]

    done = {}
    if resume and os.path.exists(out_path):
        with open(out_path, encoding="utf-8") as fh:
            for line in fh:
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                done[row["name"]] = row

    rows = []
    hits = []
    for i, rec in enumerate(targets, 1):
        if rec["name"] in done:
            rows.append(done[rec["name"]])
            continue
        row = bracket_row(tuple(rec["pair"]), lower_bound=rec.get("gamma_N_lower"),
                          census_cap=census_cap, max_fresh=max_fresh, n_plans=n_plans,
                          budget=budget, seeds=seeds, time_cap=time_cap)
        row["name"] = rec["name"]
        row["a9_gamma_N_upper"] = rec.get("gamma_N_upper")
        row["a9_sample_calibrated"] = rec.get("sample_calibrated")
        row["a9_gamma_N_certified"] = rec.get("gamma_N_certified")
        rows.append(row)
        with open(out_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row) + "\n")
        if row.get("split_min_defect") == 0:
            hits.append(row)
        if verbose:
            print(f"  [targets] {i}/{len(targets)} {rec['name']} "
                  f"L{row['total_length']} A9_upper={row['a9_gamma_N_upper']} "
                  f"split_upper={row['split_gamma_N_upper']} "
                  f"fresh={row['n_fresh_used']} closed={row['bracket_closed']} "
                  f"({time.time() - started:.0f}s)", flush=True)

    summary = summarise(rows, sweep, started, census_cap, max_fresh, n_plans, budget,
                        seeds, which)
    _write_json(summary_path, summary)
    if verbose:
        print(f"[targets] {len(rows)} rows, {summary['brackets_closed']} closed, "
              f"{summary['new_gamma_N_1_gateways']} new gateways", flush=True)
        if hits:
            print("!" * 78)
            print(HIT_BANNER)
            print("!" * 78, flush=True)
    return summary


def summarise(rows, sweep, started, census_cap, max_fresh, n_plans, budget, seeds,
              which) -> dict:
    """The ranking, the closures, and the Baumslag-Solitar test."""
    by_name = {r["name"]: r for r in sweep}
    closed = [r for r in rows if r.get("bracket_closed")]
    gateways = [r for r in closed if r.get("split_gamma_N_upper") == 1]
    improved = [r for r in rows
                if r.get("split_gamma_N_upper") is not None
                and r.get("a9_gamma_N_upper") is not None
                and r["split_gamma_N_upper"] < r["a9_gamma_N_upper"]]
    zeros = [r for r in rows if r.get("split_min_defect") == 0]

    # merged bracket over all 124: best (lowest) known upper bound per row
    merged = []
    got = {r["name"]: r for r in rows}
    for rec in sweep:
        a9 = rec.get("gamma_N_upper")
        mine = got.get(rec["name"], {}).get("split_gamma_N_upper")
        cands = [v for v in (a9, mine) if v is not None]
        upper = min(cands) if cands else None
        lower = rec.get("gamma_N_lower")
        merged.append({
            "name": rec["name"], "pair": rec["pair"],
            "total_length": rec["total_length"],
            "gamma_N_lower": lower, "gamma_N_upper": upper,
            "upper_source": ("split" if (mine is not None and (a9 is None or mine < a9))
                             else "A9 sampler" if a9 is not None else None),
            "certified": bool(lower is not None and upper is not None
                              and lower == upper),
            "a9_upper": a9, "split_upper": mine,
        })
    merged.sort(key=lambda r: (r["gamma_N_upper"] if r["gamma_N_upper"] is not None
                               else 10 ** 6, r["total_length"], r["name"]))
    for i, r in enumerate(merged, 1):
        r["rank"] = i

    bs = "YXXXyxx"
    def has_bs(row):
        return bs in row["pair"]
    cert = [r for r in merged if r["certified"] and r["gamma_N_upper"] == 1]
    enrichment = {
        "relator": bs,
        "meaning": "y^-1 x^3 y = x^2, the Baumslag-Solitar relation",
        "rows_with_relator": sum(1 for r in merged if has_bs(r)),
        "rows_without_relator": sum(1 for r in merged if not has_bs(r)),
        "certified_gamma_1_with_relator": sum(1 for r in cert if has_bs(r)),
        "certified_gamma_1_without_relator": sum(1 for r in cert if not has_bs(r)),
        "certified_gamma_1_rows": [r["name"] for r in cert],
        "no_p_value": ("The 124 come from a move tree and are not independent draws; "
                       "no p-value is quotable (contrast-length-confound.md)."),
    }

    return {
        "record": "split_bracket_summary",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "claims": ("MACHINERY: split-based UPPER bounds on gamma_N for the unsolved "
                   "Miller-Schupp representatives.  An upper bound is not a statement "
                   "about AC-triviality; a closed bracket is an exact gamma_N for the "
                   "PRESENTATION, not for its AC class."),
        "units": "defects are UNHALVED; gamma_N = defect // 2",
        "conditional_on": CONDITIONAL_ON,
        "bound_direction": ("splits bound gamma_N from ABOVE only; a failure to find a "
                            "low-defect split says nothing about the base"),
        "which_rows": which,
        "budgets": {"census_cap": census_cap, "max_fresh": max_fresh,
                    "plans_per_row": n_plans, "sample_budget": budget,
                    "sample_seeds": seeds, "master_seed": MASTER_SEED},
        "rows_run": len(rows),
        "brackets_closed": len(closed),
        "closed_rows": [{"name": r["name"], "pair": r["pair"],
                         "total_length": r["total_length"],
                         "gamma_N": r["split_gamma_N_upper"],
                         "n_fresh": r["n_fresh_used"],
                         "method": r["best_method"],
                         "split_words": r["best_split_words"]} for r in closed],
        "new_gamma_N_1_gateways": len(gateways),
        "new_gateway_rows": [r["name"] for r in gateways],
        "rows_improved_over_A9": len(improved),
        "improvement_histogram": dict(sorted(Counter(
            r["a9_gamma_N_upper"] - r["split_gamma_N_upper"] for r in improved).items())),
        "LOUD_ZERO_ALERT": bool(zeros),
        "zero_rows": [r["name"] for r in zeros],
        "merged_ranking": merged,
        "merged_certified_rows": [r["name"] for r in merged if r["certified"]],
        "merged_certified_count": sum(1 for r in merged if r["certified"]),
        "merged_upper_histogram": dict(sorted(Counter(
            r["gamma_N_upper"] for r in merged if r["gamma_N_upper"] is not None
        ).items())),
        "merged_upper_by_length": {
            str(L): {"n": len(v), "min": min(v), "median": sorted(v)[len(v) // 2],
                     "max": max(v)}
            for L, v in sorted(_group(merged).items())},
        "baumslag_solitar_enrichment": enrichment,
        "elapsed_seconds": round(time.time() - started, 1),
    }


def _group(merged) -> dict:
    out = defaultdict(list)
    for r in merged:
        if r["gamma_N_upper"] is not None:
            out[r["total_length"]].append(r["gamma_N_upper"])
    return out


# --------------------------------------------------------------------------------------
# stage 3: triple verification of a zero (only ever runs if one appears)
# --------------------------------------------------------------------------------------


def verify_zero(words, generators, witness) -> dict:
    """The three independent checks a defect-0 split must pass before anything is said.

    1. ``witness_check_n.check_witness_n`` -- the full Lemma-1 / Corollary-3 audit of the
       rotation system at arbitrary rank (it raises unless defect 0, ``L = 1`` and
       ``<AC, BC>`` is transitive);
    2. the exact census over the split's whole compatible family, which must report
       ``minimum_defect = 0``;
    3. Todd-Coxeter on the split, which must certify the trivial group.
    """
    words, generators = tuple(words), tuple(generators)
    rot = {int(k) if str(k).lstrip("-").isdigit() else k: v
           for k, v in witness.items()} if witness else None
    out = {"words": list(words), "generators": list(generators)}
    try:
        out["witness_check_n"] = WCN.check_witness_n(words, rot, generators=generators)
    except Exception as exc:                                    # noqa: BLE001
        out["witness_check_n"] = f"{type(exc).__name__}: {exc}"
    census = RN.gamma_N_factorial_n(words, generators, cap_rotations=4_000_000,
                                    keep_accepting=False)
    out["exact_census"] = {"status": census["status"],
                           "expected_cases": census["expected_cases"],
                           "minimum_defect": census["minimum_defect"]}
    try:
        tc = CE.is_trivial_group(words, generators=generators, cap=2_000_000)
        out["todd_coxeter"] = {"status": tc["status"], "index": tc["index"],
                               "trivial": tc["trivial"]}
    except Exception as exc:                                    # noqa: BLE001
        out["todd_coxeter"] = f"{type(exc).__name__}: {exc}"
    return out


# --------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--stage", default="calibration",
                        choices=("calibration", "targets"))
    parser.add_argument("--out", default=None)
    parser.add_argument("--summary", default=TARGETS_SUMMARY)
    parser.add_argument("--which", default="uncalibrated",
                        choices=("uncalibrated", "open", "all"))
    parser.add_argument("--census-cap", type=int, default=CENSUS_CAP)
    parser.add_argument("--max-fresh", type=int, default=MAX_FRESH)
    parser.add_argument("--plans", type=int, default=PLANS_PER_ROW)
    parser.add_argument("--samples", type=int, default=SAMPLE_BUDGET)
    parser.add_argument("--seeds", type=int, default=SAMPLE_SEEDS)
    parser.add_argument("--time-cap", type=float, default=ROW_TIME_CAP)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--per-length-cap", type=int, default=4)
    parser.add_argument("--extra-cap", type=int, default=24)
    parser.add_argument("--no-resume", action="store_true")
    args = parser.parse_args(argv)

    if args.stage == "calibration":
        run_calibration(args.out or CALIBRATION_OUT,
                        per_length_cap=args.per_length_cap, extra_cap=args.extra_cap,
                        census_cap=args.census_cap, max_fresh=args.max_fresh,
                        n_plans=args.plans, budget=args.samples, seeds=args.seeds,
                        time_cap=args.time_cap, limit=args.limit)
    else:
        run_targets(out_path=args.out or TARGETS_OUT, summary_path=args.summary,
                    which=args.which, census_cap=args.census_cap,
                    max_fresh=args.max_fresh, n_plans=args.plans,
                    budget=args.samples, seeds=args.seeds, time_cap=args.time_cap,
                    limit=args.limit, resume=not args.no_resume)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
