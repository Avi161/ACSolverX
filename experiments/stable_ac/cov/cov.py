"""One-shot change of variables (case i) — the 4-pager's §3.1 as a batch transform.

``⟨x,y | r1, r2⟩`` → introduce ``z = w(x,y)`` → substitute ``w → z`` → isolate
``x`` from one relator → remove ``x`` → ``⟨y,z | r_a, r_b⟩`` → relabel
``(y,z) → (x,y)``. Words are int tuples (1=x, 2=y, 3=z; sign = exponent), the
same codec as ``experiments/greedy_tests/spec/words.py``, whose helpers this
module reuses. The output pair feeds the existing 2-gen numba greedy unchanged.

Only case (i) lives here: one CoV on the initial presentation, before any
search. ``n_cov`` is an int (not a bool) so case (ii) — CoV mid-search, applied
repeatedly — extends the schema without breaking it.

The z picker is deliberately naive: ``NAIVE_Z_FAMILY`` is a fixed ordered list,
and the first z whose FULL transform yields a valid non-degenerate pair wins.
Isolation succeeding is not enough — removal can still produce an empty relator
or a length blow-up, so each candidate is validated end to end.
"""

from dataclasses import dataclass, field

from experiments.greedy_tests.spec.words import (
    inverse,
    reduce_word,
    rotate,
    str_to_word,
    word_to_str,
)

X_GEN, Y_GEN, Z_GEN = 1, 2, 3

DEFAULT_CAP = 24        # the pipeline's baseline per-relator cap (ms640 layout)
CAP_HEADROOM = 16       # a relator pinned exactly at the cap can never lengthen
                        # over the hump, so the transformed run needs slack
REJECT_LEN = 48         # a z whose output relator exceeds this is rejected

Z_FAMILY_TAG = "zf1"    # bump when NAIVE_Z_FAMILY changes: it is part of a
                        # run's result identity (goes into the jsonl filename)

# Mixed-generator words only. Pure powers (xx, yy, ...) are excluded on
# purpose: z = xx fires on any relator with a repeated generator (e.g. AK(3)'s
# xxxYYYY) and pre-empts the mixed change of variables the method is for.
# Ordered shortest-first; xyx leads the length-3 block as the paper's canonical
# example. Order matters: the first z whose full CoV succeeds wins.
NAIVE_Z_FAMILY = tuple(str_to_word(s) for s in (
    "xy", "yx", "xY", "Yx", "Xy", "XY",
    "xyx", "yxy", "xyy", "yyx", "xxy", "yxx", "xYx", "yXy",
    "xyxY", "xyxy", "xxyy",
))


@dataclass(frozen=True)
class CoVResult:
    applicable: bool
    r1: tuple               # 2-gen output pair, relabeled back to (x,y);
    r2: tuple               # the ORIGINAL pair when not applicable
    n_cov: int              # 0 or 1 in case (i)
    cap: int                # per-relator cap the greedy should run with
    z_word: tuple = None
    iso_index: int = None   # 0 = isolated from r1', 1 = from r2'
    expr: tuple = None      # x = expr(y,z), x-free, pre-relabel alphabet
    n_subs: int = 0
    meta: dict = field(default_factory=dict)


def substitute_word(word, w, z_sym=Z_GEN):
    """Replace non-overlapping occurrences of ``w``/``w⁻¹`` with ``±z``.

    Single left-to-right pass, then free (non-cyclic) reduction. Occurrences
    straddling the cyclic seam are not matched — sound (substituting any one
    occurrence is a valid move), just less powerful. Returns (word', n_subs).
    """
    w = tuple(w)
    w_inv = inverse(w)
    n, L = len(word), len(w)
    out, i, subs = [], 0, 0
    while i < n:
        chunk = tuple(word[i:i + L])
        if chunk == w:
            out.append(z_sym)
            i += L
            subs += 1
        elif chunk == w_inv:
            out.append(-z_sym)
            i += L
            subs += 1
        else:
            out.append(word[i])
            i += 1
    return reduce_word(tuple(out), cyclic=False), subs


def isolate(relator, x=X_GEN, z=Z_GEN):
    """Solve a relator for ``x`` when it contains exactly one ±x letter.

    The count is over the CYCLICALLY reduced word (a cyclic x…X pair cancels),
    and the relator must also contain a ±z letter — a z-free isolator would
    make z redundant and defeat the change of variables. Solving: rotate the x
    letter to the front, giving ``x^ε·s`` with s x-free; ``x·s = 1 → x = s⁻¹``
    and ``X·s = 1 → x = s``. Returns (ok, expr).
    """
    cyc = reduce_word(relator, cyclic=True)
    xpos = [i for i, g in enumerate(cyc) if abs(g) == x]
    if len(xpos) != 1 or not any(abs(g) == z for g in cyc):
        return False, ()
    r = rotate(cyc, -xpos[0])
    s = r[1:]
    return True, (inverse(s) if r[0] == x else s)


def substitute_generator(word, g, expr):
    """Replace every ±g in ``word`` with ``expr``/``expr⁻¹``, then free-reduce."""
    expr_inv = inverse(expr)
    out = []
    for sym in word:
        if sym == g:
            out.extend(expr)
        elif sym == -g:
            out.extend(expr_inv)
        else:
            out.append(sym)
    return reduce_word(tuple(out), cyclic=False)


_RELABEL = {Y_GEN: X_GEN, -Y_GEN: -X_GEN, Z_GEN: Y_GEN, -Z_GEN: -Y_GEN}


def relabel(word):
    """(y,z) → (x,y) after x has been removed."""
    return tuple(_RELABEL[g] for g in word)


def defining_relator(w):
    """``Z·w``, i.e. the relator asserting z = w(x,y)."""
    return (-Z_GEN,) + tuple(w)


def apply_cov_once(r1, r2, z_word, default_cap=DEFAULT_CAP,
                   cap_headroom=CAP_HEADROOM, reject_len=REJECT_LEN):
    """Full CoV for one z candidate; None when this z fails.

    Tries isolating from r1' then r2'. A candidate isolator whose removal
    degenerates (empty relator, length > ``reject_len``) falls through to the
    other relator before the z is rejected.
    """
    w = reduce_word(tuple(z_word), cyclic=False)
    if len(w) < 2:
        return None

    r1s, n1 = substitute_word(r1, w)
    r2s, n2 = substitute_word(r2, w)
    if n1 + n2 == 0:
        return None

    r_def = defining_relator(w)
    for iso_index, (r_iso, r_other) in enumerate(((r1s, r2s), (r2s, r1s))):
        ok, expr = isolate(r_iso)
        if not ok:
            continue
        r_a = substitute_generator(r_other, X_GEN, expr)
        r_b = substitute_generator(r_def, X_GEN, expr)
        if not r_a or not r_b:
            continue
        assert not any(abs(g) == X_GEN for g in r_a + r_b)
        if max(len(r_a), len(r_b)) > reject_len:
            continue
        out1, out2 = relabel(r_a), relabel(r_b)
        cap = max(default_cap, max(len(out1), len(out2)) + cap_headroom)
        return CoVResult(
            applicable=True, r1=out1, r2=out2, n_cov=1, cap=cap,
            z_word=w, iso_index=iso_index, expr=expr, n_subs=n1 + n2,
            meta={"intermediate": (r1s, r2s, r_def)},
        )
    return None


def change_of_variables(r1, r2, family=NAIVE_Z_FAMILY, default_cap=DEFAULT_CAP,
                        cap_headroom=CAP_HEADROOM, reject_len=REJECT_LEN):
    """Case (i) entry point: first z in ``family`` whose full CoV is valid.

    Falls back to the original pair (applicable=False, n_cov=0) so the caller
    can still run the untransformed search and keep the row comparable. The
    fallback cap is ``default_cap`` — identical to the baseline pipeline's.
    """
    r1, r2 = tuple(r1), tuple(r2)
    for z_word in family:
        result = apply_cov_once(r1, r2, z_word, default_cap=default_cap,
                                cap_headroom=cap_headroom, reject_len=reject_len)
        if result is not None:
            return result
    return CoVResult(applicable=False, r1=r1, r2=r2, n_cov=0, cap=default_cap)


def cov_for_greedy(r1_str, r2_str, family=NAIVE_Z_FAMILY, **knobs):
    """String adapter for the numba greedy: (r1', r2', cap, n_cov, meta)."""
    result = change_of_variables(str_to_word(r1_str), str_to_word(r2_str),
                                 family, **knobs)
    meta = {
        "cov_applicable": result.applicable,
        "z_word": word_to_str(result.z_word) if result.z_word else None,
        "iso_index": result.iso_index,
        "n_subs": result.n_subs,
        "start_total_length_orig": len(r1_str) + len(r2_str),
        "start_total_length_cov": len(result.r1) + len(result.r2),
    }
    return (word_to_str(result.r1), word_to_str(result.r2),
            result.cap, result.n_cov, meta)


def transformed_flat(result):
    """The output pair in the ms640 flat-int layout ``[r1(cap) | r2(cap)]``.

    Built at the exact relator lengths, then re-padded to ``result.cap`` via
    envs.utils.change_max_relator_length_of_presentation — the sanctioned
    re-pad whenever the cap changes. Lazy import: ``envs`` pulls JAX, which
    must never load on the search path.
    """
    import numpy as np
    from envs.utils import change_max_relator_length_of_presentation

    slot = max(len(result.r1), len(result.r2))
    # a plain list: the util slices it and asserts list-typed relators
    flat = (list(result.r1) + [0] * (slot - len(result.r1))
            + list(result.r2) + [0] * (slot - len(result.r2)))
    out = change_max_relator_length_of_presentation(flat, result.cap)
    return [int(v) for v in np.asarray(out)]


def subword_candidates(r1, r2, min_len=2, max_len=4):
    """Every distinct subword of the relators, as z candidates.

    The data-driven family for the length-sweep experiment: unlike
    ``NAIVE_Z_FAMILY``, these w are guaranteed to occur in the presentation
    (modulo the substitution's linear-scan limitation for subwords that only
    cross the cyclic seam). Subwords are read off each CYCLICALLY reduced
    relator, seam included (via the doubled word), lengths min_len..max_len.
    ``w`` and ``w⁻¹`` yield the same CoV up to inverting z, so each pair keeps
    one canonical member: ``max(w, w⁻¹)``, which starts with a positive letter
    whenever the pair has one. Pure powers (xx, yyy, …) are candidates too —
    which words work is the sweep's empirical question, so nothing is excluded
    a priori (sweep tag sub{K}p; the mixed-only rule was the pre-p family).
    Deterministic order (length, then tuple) — row identity depends on it.
    """
    seen = set()
    for rel in (r1, r2):
        cyc = reduce_word(tuple(rel), cyclic=True)
        n = len(cyc)
        doubled = cyc + cyc
        for length in range(min_len, min(max_len, n) + 1):
            for i in range(n):
                w = doubled[i:i + length]
                seen.add(max(w, inverse(w)))
    return tuple(sorted(seen, key=lambda w: (len(w), w)))


def enumerate_cov(r1, r2, family=None, default_cap=DEFAULT_CAP,
                  cap_headroom=CAP_HEADROOM, reject_len=REJECT_LEN,
                  subword_min_len=2, subword_max_len=4):
    """All valid CoVs over ``family`` (default: the presentation's own
    subwords) — the brute-force half of the length-sweep experiment.

    Distinct z words can land on the same output pair, which would be an
    identical search run twice, so only the first (in family order) of each
    output pair is kept. Every returned result is fully validated by
    ``apply_cov_once``. Order follows family order, so it is deterministic.
    """
    r1, r2 = tuple(r1), tuple(r2)
    if family is None:
        family = subword_candidates(r1, r2, subword_min_len, subword_max_len)
    results, seen_pairs = [], set()
    for z_word in family:
        res = apply_cov_once(r1, r2, z_word, default_cap=default_cap,
                             cap_headroom=cap_headroom, reject_len=reject_len)
        if res is None or (res.r1, res.r2) in seen_pairs:
            continue
        seen_pairs.add((res.r1, res.r2))
        results.append(res)
    return tuple(results)
