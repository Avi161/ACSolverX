"""Independent adversarial tests for `experiments/ppo/shaping.py` and `experiments/ppo/heldout.py`.

"Independent" means: no paraphrasing. `ref_blocks`/`ref_feats` below are a from-scratch
reimplementation of the block-feature definition ("a relator is a cyclic word; its blocks
are the maximal runs of one generator read around the ring; x/X are one generator, y/Y are
the other"), written without reading `hsearch.blocks`'s body for guidance beyond the English
definition, and using a structurally different algorithm (rotate to a run boundary, then
plain linear run-length encoding) instead of hsearch's "encode linearly, then merge the
seam". `shaping.features`, `hsearch.feats` and this reference are then cross-checked against
EACH OTHER on random and degenerate relator pairs, rather than trusting any one of them.

For `heldout.py`, the "580" and "54" facts are re-derived by hand (a bare membership walk
over `read_raw` output) rather than taken from `heldout.ms_prefix_length`'s own return value.
"""

import functools
import json
import os
import random

import pytest

torch = pytest.importorskip("torch")

from experiments.heuristic_search.core.hsearch import feats as hsearch_feats   # noqa: E402
from experiments.ppo import acs_data, heldout, shaping                         # noqa: E402

L = 24
SYM = {1: "x", -1: "X", 2: "y", -2: "Y"}
SEED = 20260810


# ============================================================================================
# Independent reference for the block features
# ============================================================================================

def ref_blocks(word):
    """[(generator, run_length), ...] for `word`, a list of nonzero signed ints, read as a
    CYCLIC word (1/-1 = x-family, 2/-2 = y-family; sign never distinguishes a run).

    Never calls `hsearch.blocks`. Route: rotate the word to start at a run boundary (a
    position whose generator differs from its cyclic predecessor), then do ordinary LINEAR
    run-length encoding. Because the rotation point is chosen to be a boundary, the linear
    encoding's first and last runs are never the same generator, so no seam-merge step is
    needed -- a different mechanism than hsearch.blocks' "encode linearly, then merge the
    two ends", which should agree with it only because both are correct.
    """
    n = len(word)
    if n == 0:
        return []
    gens = [1 if abs(v) == 1 else 2 for v in word]
    if n == 1 or all(g == gens[0] for g in gens):
        return [(gens[0], n)]
    b = next(i for i in range(n) if gens[i] != gens[i - 1])
    rot = gens[b:] + gens[:b]
    runs, i = [], 0
    while i < n:
        j = i
        while j + 1 < n and rot[j + 1] == rot[i]:
            j += 1
        runs.append((rot[i], j - i + 1))
        i = j + 1
    return runs


def ref_feats(r1, r2):
    """(L, K, MK, S) built from `ref_blocks` alone -- the independent oracle."""
    b1, b2 = ref_blocks(r1), ref_blocks(r2)
    x1 = [ln for g, ln in b1 if g == 1]
    y1 = [ln for g, ln in b1 if g == 2]
    x2 = [ln for g, ln in b2 if g == 1]
    y2 = [ln for g, ln in b2 if g == 2]
    k1 = 0 if not x1 or not y1 else max(len(x1), len(y1))
    k2 = 0 if not x2 or not y2 else max(len(x2), len(y2))
    xs, ys = x1 + x2, y1 + y2
    mx = sum(xs) / len(xs) if xs else 0.0
    my = sum(ys) / len(ys) if ys else 0.0
    smb = (mx or my) if (not xs or not ys) else min(mx, my)
    return len(r1) + len(r2), k1 + k2, max(k1, k2), smb


def to_str(word):
    return "".join(SYM[v] for v in word)


def pad(word, max_length=L):
    return list(word) + [0] * (max_length - len(word))


def encode(r1, r2, max_length=L):
    return pad(r1, max_length) + pad(r2, max_length)


def make_batch(pairs, max_length=L):
    return torch.tensor([encode(r1, r2, max_length) for r1, r2 in pairs], dtype=torch.int8)


def rand_word(rng, max_len, alphabet=(1, -1, 2, -2)):
    n = rng.randint(0, max_len)
    return [rng.choice(alphabet) for _ in range(n)]


def rand_state(rng, max_length=L):
    return encode(rand_word(rng, max_length), rand_word(rng, max_length), max_length)


def rotate(word, k):
    if not word:
        return list(word)
    k %= len(word)
    return word[k:] + word[:k]


def swap_xy_letter(v):
    if v == 0:
        return 0
    return (1 if v > 0 else -1) * (3 - abs(v))


# Degenerate shapes named in the task: empty relators, length-1, single-generator,
# all-padding (== an empty relator's tensor row, all zero), full-width, and the cyclic seam
# (first and last letters share a generator).
DEGENERATE = [
    ([], []),                                    # both relators empty == all-padding
    ([1], []), ([], [2]),                        # length-1 / empty
    ([1, 1, 1], []), ([], [2, 2]),                # single-generator
    ([-1, -1, -1], [-2]),                         # single-generator, inverted sign
    ([1, 2, 1], [2]),                             # the seam: r1 starts and ends on x
    ([2, 2, 1, 1, 2], [1]),                       # seam on y, longer
    ([1] * L, [2] * L),                           # full width, one generator each
    ([1, 2] * (L // 2), [1] * (L - 1) + [2]),     # full width, mixed
]


# ============================================================================================
# shaping.py -- three-way cross-check: ref_feats, hsearch.feats, shaping.features
# ============================================================================================

def test_three_way_cross_check_on_random_and_degenerate_relators():
    rng = random.Random(SEED)
    pairs = list(DEGENERATE) + [(rand_word(rng, L), rand_word(rng, L)) for _ in range(400)]
    x = make_batch(pairs)
    length, knots, max_knots, smaller = shaping.features(x)

    checked_both_generators = 0
    for i, (r1, r2) in enumerate(pairs):
        ref = ref_feats(r1, r2)
        hs = hsearch_feats(to_str(r1), to_str(r2))
        got = (int(length[i]), int(knots[i]), int(max_knots[i]))
        assert ref[:3] == hs[:3] == got, (r1, r2, ref, hs, got)
        assert abs(ref[3] - hs[3]) < 1e-9, (r1, r2, "ref vs hsearch")
        assert abs(ref[3] - float(smaller[i])) < 1e-5, (r1, r2, "ref vs shaping")
        if ref_blocks(r1) and ref_blocks(r2):
            checked_both_generators += 1
    assert checked_both_generators > 50, "random words rarely used both generators"


@pytest.mark.parametrize("r1,r2", DEGENERATE)
def test_degenerate_shapes_individually(r1, r2):
    x = make_batch([(r1, r2)])
    length, knots, max_knots, smaller = shaping.features(x)
    ref = ref_feats(r1, r2)
    hs = hsearch_feats(to_str(r1), to_str(r2))
    assert ref[:3] == hs[:3] == (int(length[0]), int(knots[0]), int(max_knots[0]))
    assert abs(ref[3] - float(smaller[0])) < 1e-6


def test_features_rejects_n_gen_other_than_2():
    x = torch.zeros((1, 3 * L), dtype=torch.int8)
    with pytest.raises(ValueError):
        shaping.features(x, n_gen=3, max_length=L)


def test_x_runs_equal_y_runs_when_a_relator_uses_both_generators():
    """The claim `shaping.py`'s vectorised implementation is built on: on a ring using both
    generators, the number of x-runs and y-runs is always equal. Checked against the
    independently-rotated `ref_blocks`, never against `shaping.py`'s own arithmetic.
    """
    rng = random.Random(SEED + 1)
    hits = 0
    for _ in range(400):
        w = rand_word(rng, L)
        runs = ref_blocks(w)
        xs = [ln for g, ln in runs if g == 1]
        ys = [ln for g, ln in runs if g == 2]
        if xs and ys:
            hits += 1
            assert len(xs) == len(ys), w
    assert hits > 50, "the both-generators branch never fired; the invariant proved nothing"


# ---------------------------------------------------------------------------------- invariants

def test_cyclic_rotation_of_a_relator_does_not_change_its_features():
    rng = random.Random(SEED + 2)
    pairs, rotated = [], []
    for _ in range(200):
        r1, r2 = rand_word(rng, L), rand_word(rng, L)
        k = rng.randint(0, len(r1) - 1) if len(r1) > 1 else 0
        pairs.append((r1, r2))
        rotated.append((rotate(r1, k), r2))

    l0, k0, mk0, s0 = shaping.features(make_batch(pairs))
    l1, k1, mk1, s1 = shaping.features(make_batch(rotated))
    assert torch.equal(l0, l1) and torch.equal(k0, k1) and torch.equal(mk0, mk1)
    assert torch.allclose(s0, s1, atol=1e-5)

    # spot-check a subset against the from-scratch reference too
    for (r1, r2), (r1r, r2r) in list(zip(pairs, rotated))[:30]:
        a, b = ref_feats(r1, r2), ref_feats(r1r, r2r)
        assert a[:3] == b[:3] and abs(a[3] - b[3]) < 1e-9, (r1, r2)


def test_swapping_r1_and_r2_does_not_change_L_K_MK_or_S():
    rng = random.Random(SEED + 3)
    pairs = list(DEGENERATE) + [(rand_word(rng, L), rand_word(rng, L)) for _ in range(200)]
    swapped = [(r2, r1) for r1, r2 in pairs]

    l0, k0, mk0, s0 = shaping.features(make_batch(pairs))
    l1, k1, mk1, s1 = shaping.features(make_batch(swapped))
    assert torch.equal(l0, l1) and torch.equal(k0, k1) and torch.equal(mk0, mk1)
    assert torch.allclose(s0, s1, atol=1e-5)


def test_inverting_every_letters_sign_does_not_change_anything():
    """`blocks()` keys on `c in "xX"` -- the SIGN of a letter is not a generator."""
    rng = random.Random(SEED + 4)
    pairs = list(DEGENERATE) + [(rand_word(rng, L), rand_word(rng, L)) for _ in range(200)]
    x0 = make_batch(pairs)
    x1 = -x0

    l0, k0, mk0, s0 = shaping.features(x0)
    l1, k1, mk1, s1 = shaping.features(x1)
    assert torch.equal(l0, l1) and torch.equal(k0, k1) and torch.equal(mk0, mk1)
    assert torch.allclose(s0, s1, atol=1e-5)
    assert torch.allclose(shaping.heuristic(x0), shaping.heuristic(x1))


def test_swapping_x_and_y_leaves_L_K_MK_and_S_unchanged():
    """S is a min over the two generators' mean run length -- symmetric under an x<->y
    relabel even though it is not symmetric between "the thinner" and "the thicker" one.
    """
    rng = random.Random(SEED + 5)
    pairs = list(DEGENERATE) + [(rand_word(rng, L), rand_word(rng, L)) for _ in range(200)]
    swapped = [([swap_xy_letter(v) for v in r1], [swap_xy_letter(v) for v in r2])
               for r1, r2 in pairs]

    l0, k0, mk0, s0 = shaping.features(make_batch(pairs))
    l1, k1, mk1, s1 = shaping.features(make_batch(swapped))
    assert torch.equal(l0, l1) and torch.equal(k0, k1) and torch.equal(mk0, mk1)
    assert torch.allclose(s0, s1, atol=1e-5)


def test_heuristic_matches_the_independent_reference_weighted_sum():
    rng = random.Random(SEED + 6)
    pairs = list(DEGENERATE) + [(rand_word(rng, L), rand_word(rng, L)) for _ in range(150)]
    x = make_batch(pairs)
    refs = [ref_feats(r1, r2) for r1, r2 in pairs]
    for name, (w_l, w_k, w_mk, w_s) in shaping.WEIGHTS.items():
        got = shaping.heuristic(x, weights=name)
        want = torch.tensor([w_l * a + w_k * b + w_mk * c + w_s * d for a, b, c, d in refs],
                            dtype=torch.float32)
        assert torch.allclose(got, want, atol=1e-4), name


# ============================================================================================
# shaping.py -- potential-based shaping theorem
# ============================================================================================

def test_potential_is_minus_lambda_times_heuristic():
    rng = random.Random(SEED + 7)
    x = make_batch([(rand_word(rng, L), rand_word(rng, L)) for _ in range(80)])
    for lam in (0.0, 0.2, 1.0, 3.5):
        got = shaping.potential(x, lam)
        want = torch.zeros(x.shape[0]) if lam == 0.0 else -lam * shaping.heuristic(x)
        assert torch.allclose(got, want, atol=1e-4), lam


def test_shaping_term_equals_gamma_phi_next_minus_phi_with_done_zeroing():
    rng = random.Random(SEED + 8)
    lam, gamma = 0.2, 0.97
    x_old = torch.tensor([rand_state(rng) for _ in range(32)], dtype=torch.int8)
    x_new = torch.tensor([rand_state(rng) for _ in range(32)], dtype=torch.int8)
    phi = shaping.potential(x_old, lam)
    phi_next = shaping.potential(x_new, lam)
    for done_val in (False, True):
        done = torch.full((32,), done_val, dtype=torch.bool)
        f = shaping.shaping_term(x_old, x_new, done, lam, gamma)
        want = -phi if done_val else gamma * phi_next - phi
        assert torch.allclose(f, want, atol=1e-4), done_val


def test_lambda_zero_is_an_exact_hard_zero_on_random_states():
    rng = random.Random(SEED + 9)
    x_old = torch.tensor([rand_state(rng) for _ in range(40)], dtype=torch.int8)
    x_new = torch.tensor([rand_state(rng) for _ in range(40)], dtype=torch.int8)
    done = torch.tensor([rng.random() < 0.3 for _ in range(40)])
    f = shaping.shaping_term(x_old, x_new, done, lam=0.0, gamma=0.99)
    assert torch.count_nonzero(f) == 0
    assert torch.count_nonzero(shaping.potential(x_old, 0.0)) == 0


def test_round_trip_sum_is_determined_only_by_the_two_endpoints():
    """s -> s' -> s, both transitions non-terminal: F(s,s') + F(s',s) must equal a formula
    of `Phi(s)` and `Phi(s')` alone -- (gamma-1)*(Phi(s)+Phi(s')) -- with no room for a
    path-dependent term to sneak in.
    """
    rng = random.Random(SEED + 10)
    lam, gamma = 0.2, 0.97
    a = torch.tensor([rand_state(rng) for _ in range(40)], dtype=torch.int8)
    b = torch.tensor([rand_state(rng) for _ in range(40)], dtype=torch.int8)
    not_done = torch.zeros(40, dtype=torch.bool)
    f_ab = shaping.shaping_term(a, b, not_done, lam, gamma)
    f_ba = shaping.shaping_term(b, a, not_done, lam, gamma)
    phi_a, phi_b = shaping.potential(a, lam), shaping.potential(b, lam)
    want = (gamma - 1.0) * (phi_a + phi_b)
    assert torch.allclose(f_ab + f_ba, want, atol=1e-4)


def test_shaping_telescopes_to_minus_phi_of_the_start_over_random_trajectories():
    """Sum of discounted F along ANY sequence of states ending in `done=True` is `-Phi(s0)`.

    Deliberately not real env rollouts: Phi is a pure function of state, so the identity
    holds for an arbitrary sequence of states, physically reachable or not. Using synthetic
    random trajectories keeps this test independent of `acs_env`/`VecACS` entirely.
    """
    rng = random.Random(SEED + 11)
    lam, gamma = 0.2, 0.97
    for trial in range(25):
        steps = rng.randint(1, 8)
        traj = [rand_state(rng) for _ in range(steps + 1)]
        total = 0.0
        for t in range(steps):
            x_old = torch.tensor([traj[t]], dtype=torch.int8)
            x_new = torch.tensor([traj[t + 1]], dtype=torch.int8)
            done = torch.tensor([t == steps - 1])
            f = shaping.shaping_term(x_old, x_new, done, lam, gamma)
            total += (gamma ** t) * f.item()
        phi0 = shaping.potential(torch.tensor([traj[0]], dtype=torch.int8), lam).item()
        assert abs(total + phi0) < 1e-3, (trial, total, phi0)


# ============================================================================================
# heldout.py
# ============================================================================================

def _read_raw_uncached(stem):
    """`json.loads` instead of `ast.literal_eval` -- proven byte-identical below, ~20x
    faster on this file format (nested lists of small ints).
    """
    with open(acs_data.data_path(stem)) as fh:
        return [json.loads(line.strip()) for line in fh if line.strip()]


@functools.lru_cache(maxsize=None)
def _fast_read_raw_cached(stem):
    return tuple(tuple(row) for row in _read_raw_uncached(stem))


def _fast_read_raw(stem):
    """Fast + memoized. Swapped in for `acs_data.read_raw` purely to keep this file's
    wall-clock down: `heldout.build` makes THREE full passes over the 156k-line
    `AC19_extended` file even when `log` is a no-op (once to filter, once inside
    `ms_prefix_length(out_stem)`, and once more because its log line eagerly evaluates
    `acs_data.ms_prefix_length(stem)` as an f-string argument regardless of what `log`
    does with the result), and this module calls `ms_prefix_length` on several stems on
    top of that -- ~24s per full pass at the real reader's speed, repeated many times
    over. None of the underlying data files change during a test run, so memoizing by
    stem name is safe; each row is returned as a list, matching `acs_data.read_raw`'s own
    contract, from a fresh top-level list so nothing here can mutate the cache. The patch
    changes nothing about `heldout.py`'s or `acs_data.py`'s own logic.
    """
    return [list(row) for row in _fast_read_raw_cached(stem)]


def test_the_fast_reader_used_below_agrees_with_the_real_one():
    assert _fast_read_raw("1190MS") == acs_data.read_raw("1190MS")


# PID-suffixed so a concurrent run of this same file (or of another test module that
# happens to be mid-build on the canonical `AC19_extended_ho60`) can never collide with
# this one on the output file.
HO_OUT_STEM = f"AC19_extended_ho60_independent_check_{os.getpid()}"


@pytest.fixture(scope="module")
def ho60_built():
    """Build `AC19_extended` minus the benchmark-60 ONCE for this whole module, under the
    fast reader above, and clean up afterwards.

    Writes to a PID-suffixed name of its own, never the canonical `AC19_extended_ho60` --
    so this suite cannot collide with anything else (a notebook, a concurrent test run,
    `tests/ppo/test_shaped_arms.py`) that manages that file's lifecycle. The canonical file
    was confirmed absent before this suite was written and is never touched here.
    """
    real_read_raw = acs_data.read_raw
    acs_data.read_raw = _fast_read_raw
    path = os.path.join(acs_data.ROOT, "data", HO_OUT_STEM + ".txt")
    assert not os.path.exists(path), f"stale artifact from a previous run, remove by hand: {path}"
    try:
        result = heldout.build("AC19_extended", 24, out_stem=HO_OUT_STEM, log=lambda *a, **k: None)
        yield result
    finally:
        acs_data.read_raw = real_read_raw
        for p in (path, path + ".tmp"):
            if os.path.exists(p):
                os.remove(p)


def test_build_removes_exactly_54_rows_and_no_benchmark_row_survives(ho60_built):
    _, n_removed, _ = ho60_built
    assert n_removed == 54

    drop = heldout.benchmark_states(24)
    kept = acs_data.read_raw(HO_OUT_STEM)
    assert len(kept) == len(acs_data.read_raw("AC19_extended")) - 54
    assert not any(tuple(acs_data.repad(r, 24)) in drop for r in kept)


def test_naive_prefix_walk_collapses_to_zero_but_filter_aware_gives_580(ho60_built):
    assert acs_data.ms_prefix_length(HO_OUT_STEM) == 0
    got = heldout.ms_prefix_length(HO_OUT_STEM, 24)
    assert got == 580     # 634 - 54

    # Independent re-derivation of "580": a bare membership walk over `read_raw`'s output,
    # exactly as `ms_prefix_length`'s docstring describes it ("walk the training file from
    # the top counting rows that are members of 1190MS, stop at the first that is not") --
    # never a call to `heldout.ms_prefix_length` itself.
    ms = {tuple(acs_data.repad(p, 24)) for p in acs_data.read_raw("1190MS")}
    rows = acs_data.read_raw(HO_OUT_STEM)
    n = 0
    while n < len(rows) and tuple(acs_data.repad(rows[n], 24)) in ms:
        n += 1
    assert n == 580


def test_filter_aware_prefix_agrees_with_the_shipped_one_on_every_shipped_stem(ho60_built):
    for stem in ("1190MS", "AC19_extended", "AC19"):
        assert heldout.ms_prefix_length(stem, 24) == acs_data.ms_prefix_length(stem), stem


def test_build_is_idempotent(ho60_built):
    path, n_removed, n_pinned = ho60_built
    before = open(path).read()
    mtime_before = os.path.getmtime(path)

    path2, n_removed2, n_pinned2 = heldout.build("AC19_extended", 24, out_stem=HO_OUT_STEM,
                                                  log=lambda *a, **k: None)
    assert (path2, n_removed2, n_pinned2) == (path, n_removed, n_pinned)
    assert open(path2).read() == before
    assert os.path.getmtime(path2) == mtime_before, "file was rewritten on the idempotent path"
