"""One-shot change of variables (case i) — the 4-pager's §3.1 as a batch transform.

``⟨x,y | r1, r2⟩`` → introduce ``z = w(x,y)`` → substitute ``w → z`` → isolate
``x`` (or ``y``: ``iso_gen``) from one relator → remove it → a 2-generator
pair → relabel the survivors back to ``(x,y)`` (``relabel``). Words are int
tuples (1=x, 2=y, 3=z; sign = exponent), the
same codec as ``experiments/greedy_tests/spec/words.py``, whose helpers this
module reuses. The output pair feeds the existing 2-gen numba greedy unchanged.

Only case (i) lives here: one CoV on the initial presentation, before any
search. ``n_cov`` is an int (not a bool) so case (ii) — CoV mid-search, applied
repeatedly — extends the schema without breaking it.

The z picker is deliberately naive: ``NAIVE_Z_FAMILY`` (zf2 list under tag
zf3: every canonical freely+cyclically reduced word of length 2..4, nothing
excluded; zf3 adds cyclic-seam matches in ``substitute_word``) is tried in
deterministic order and the first z whose FULL transform yields a valid
non-degenerate pair wins. Isolation succeeding is not enough — removal can
still produce an empty relator or a structural blow-up past ``reject_len``,
so each candidate is validated end to end.
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
REJECT_LEN = 239        # structural ceiling ONLY, not a length prior: the
                        # packed fast solver caps relators at 255 and a row
                        # runs at cap = longest + CAP_HEADROOM, so 239 is the
                        # longest admissible output. Long starts are NOT
                        # rejected on principle — sweep evidence (629, 539)
                        # shows some presentations solve only from long
                        # transformed starts. Part of the sweep family rule:
                        # changing it requires a tag bump.

Z_FAMILY_TAG = "zf3"    # bump when NAIVE_Z_FAMILY *or* substitution semantics
                        # change: it is part of a run's result identity
                        # (goes into the jsonl filename). zf3 = zf2 family +
                        # cyclic-seam matches in substitute_word.

SUBWORD_MIN_LEN = 2     # |w| < 2 is a rename, not a CoV (apply_cov_once gates
                        # it too). Part of the subword family rule.
MIN_TRANSFORMED_LEN = 3 # no-collapse gate: a z that substitutes SOME relator
                        # down to length <= 2 is rejected. See
                        # subword_candidates. Part of the subword family rule.

SUBWORD_FAMILY_TAG = "subnc2pxysb"
                        # the length sweep's family tag — ONE source of truth
                        # (never rebuilt from config: a yaml copy shadowed the
                        # zf1->zf2->zf3 bumps once already). Bump on ANY change
                        # to the family rule, since a different family is a
                        # different experiment and must never share a resume
                        # file. Reading it: sub = z drawn from the relators'
                        # own subwords · nc2 = no-collapse, the only length
                        # rule (the pre-nc2 sub{K} tags bounded |w| by a fixed
                        # global K instead) · p = pure powers included (pre-p
                        # was mixed-generator only) · xy = both isolation
                        # targets tried per z (pre-xy was x-elimination only) ·
                        # s = cyclic-seam matches in substitution (pre-s missed
                        # seam-only occurrences) · b = every isolating BRANCH
                        # is its own row, keyed by iso_index (pre-b files kept
                        # only the first branch per (z, iso_gen), so they hold
                        # a strict subset of the rows and must never resume
                        # into a b file).


def universe_candidates(min_len=2, max_len=4):
    """Every canonical freely reduced (x,y)-word of length min_len..max_len.

    The presentation-independent z family: unlike ``subword_candidates`` these
    need not occur in the relators, so they only produce a CoV through the
    defining-relator isolation (``allow_defining_iso``) unless they happen to
    occur. Same canonicalisation as the subword family — one member per
    ``w ~ w⁻¹`` pair, ``max(w, w⁻¹)`` — and the same deterministic
    (length, tuple) order, which sweep row identity depends on.
    """
    seen = set()
    alphabet = (X_GEN, -X_GEN, Y_GEN, -Y_GEN)

    def extend(w):
        if len(w) >= min_len:
            seen.add(max(w, inverse(w)))
        if len(w) == max_len:
            return
        for g in alphabet:
            if not w or g != -w[-1]:
                extend(w + (g,))

    extend(())
    return tuple(sorted(seen, key=lambda w: (len(w), w)))


# zf2: EVERY canonical word of length 2..4 that survives free and cyclic
# reduction — no hand-picking, no exclusions (pure powers like xx/yyy are in;
# which z wins is an empirical question, never a rule). w ~ w⁻¹ deduped to
# max(w, w⁻¹); deterministic (length, tuple) order IS the first-win order.
# zf1 — 17 hand-picked mixed-generator words with xy pinned first — is
# retired; its files keep the zf1 tag and are never resumed by zf2 runs.
NAIVE_Z_FAMILY = tuple(w for w in universe_candidates(2, 4)
                       if w[0] != -w[-1])


@dataclass(frozen=True)
class CoVResult:
    applicable: bool
    r1: tuple               # 2-gen output pair, relabeled back to (x,y);
    r2: tuple               # the ORIGINAL pair when not applicable
    n_cov: int              # 0 or 1 in case (i)
    cap: int                # per-relator cap the greedy should run with
    z_word: tuple = None
    iso_index: int = None   # 0 = isolated from r1', 1 = from r2',
                            # 2 = from the defining relator Z·w (universe mode)
    iso_gen: str = "x"      # which generator the isolation eliminated
    expr: tuple = None      # eliminated generator = expr (free of it),
                            # pre-relabel alphabet
    n_subs: int = 0
    meta: dict = field(default_factory=dict)


def substitute_word(word, w, z_sym=Z_GEN):
    """Replace non-overlapping occurrences of ``w``/``w⁻¹`` with ``±z``.

    Left-to-right linear pass on the stored string, then at most one
    cyclic-seam wrap on the remaining unconsumed prefix/suffix (relators
    are cyclic words; a match straddling last→first is a real occurrence).
    Free (non-cyclic) reduction after. Returns (word', n_subs).
    """
    w = tuple(w)
    w_inv = inverse(w)
    word = tuple(word)
    n, L = len(word), len(w)
    if n == 0 or L == 0:
        return (), 0
    if L > n:
        return reduce_word(word, cyclic=False), 0

    consumed = [False] * n
    linear = []  # (start_index, ±z)
    i, subs = 0, 0
    while i < n:
        if i + L <= n and not any(consumed[j] for j in range(i, i + L)):
            chunk = word[i:i + L]
            if chunk == w or chunk == w_inv:
                sym = z_sym if chunk == w else -z_sym
                for j in range(i, i + L):
                    consumed[j] = True
                linear.append((i, sym))
                i += L
                subs += 1
                continue
        i += 1

    seam_sym, seam_k = None, None  # seam_k = suffix length
    if L >= 2:
        for k in range(1, L):
            p = L - k
            if p > n - k:
                continue
            if any(consumed[j] for j in range(p)):
                continue
            if any(consumed[j] for j in range(n - k, n)):
                continue
            chunk = word[n - k:] + word[:p]
            if chunk == w:
                seam_sym = z_sym
            elif chunk == w_inv:
                seam_sym = -z_sym
            else:
                continue
            seam_k = k
            for j in range(p):
                consumed[j] = True
            for j in range(n - k, n):
                consumed[j] = True
            subs += 1
            break

    out = []
    if seam_sym is not None:
        out.append(seam_sym)
        start, end = L - seam_k, n - seam_k
    else:
        start, end = 0, n
    linear_at = dict(linear)
    i = start
    while i < end:
        if i in linear_at:
            out.append(linear_at[i])
            i += L
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


_RELABEL = {
    # after x-elimination the survivors mention (y,z): (y,z) → (x,y)
    "x": {Y_GEN: X_GEN, -Y_GEN: -X_GEN, Z_GEN: Y_GEN, -Z_GEN: -Y_GEN},
    # after y-elimination they mention (x,z): x stays, z → y
    "y": {X_GEN: X_GEN, -X_GEN: -X_GEN, Z_GEN: Y_GEN, -Z_GEN: -Y_GEN},
}


def relabel(word, iso_gen="x"):
    """Back to the (x,y) alphabet after ``iso_gen`` has been removed."""
    return tuple(_RELABEL[iso_gen][g] for g in word)


def defining_relator(w):
    """``Z·w``, i.e. the relator asserting z = w(x,y)."""
    return (-Z_GEN,) + tuple(w)


def cov_branches(r1, r2, z_word, default_cap=DEFAULT_CAP,
                 cap_headroom=CAP_HEADROOM, reject_len=REJECT_LEN,
                 allow_defining_iso=False, iso_gen="x"):
    """EVERY valid CoV for this (z_word, iso_gen) — one per isolating relator.

    A (z, iso_gen) pair can have more than one legal destabilization: both r1′
    and r2′ may isolate the target, and they are DIFFERENT coordinate changes
    with different outputs (measured: on the 66-row benchmark 104 pairs have
    two valid branches and all 104 outputs differ, sometimes wildly — 521
    z=yy/iso=y gives total 30 from r1′ and total 16 from r2′). ``iso_index``
    names the branch, so it is part of the sweep row key: the sweep asks which
    z predicts a good outcome, and z alone does not determine the outcome —
    (z, iso_gen, iso_index) does.

    ``iso_gen`` picks which generator the destabilization eliminates: after
    stabilizing to ⟨x,y,z | …⟩ either x or y may be isolated and removed —
    both are legal; the survivors relabel back to (x,y) either way
    (``relabel``). With ``allow_defining_iso`` the defining relator Z·w is a
    third isolation candidate (iso_index 2, tried LAST so shared z words
    transform identically to the default mode): it isolates whenever w carries
    exactly one ±iso_gen — z = u·g^ε·v solves to g = expr, an elementary
    Nielsen automorphism — so w need not occur in the presentation, and the
    n_subs ≥ 1 gate is waived.

    Branches are returned in candidate order (r1′, r2′, then Z·w). A branch
    that degenerates (empty relator) or exceeds ``reject_len`` is skipped.
    """
    w = reduce_word(tuple(z_word), cyclic=False)
    if len(w) < 2:
        return ()
    gen = X_GEN if iso_gen == "x" else Y_GEN

    r1s, n1 = substitute_word(r1, w)
    r2s, n2 = substitute_word(r2, w)
    if n1 + n2 == 0 and not allow_defining_iso:
        return ()

    r_def = defining_relator(w)
    candidates = [(0, r1s, r2s, r_def), (1, r2s, r1s, r_def)]
    if allow_defining_iso:
        candidates.append((2, r_def, r1s, r2s))
    out = []
    for iso_index, r_iso, keep_a, keep_b in candidates:
        ok, expr = isolate(r_iso, x=gen)
        if not ok:
            continue
        r_a = substitute_generator(keep_a, gen, expr)
        r_b = substitute_generator(keep_b, gen, expr)
        if not r_a or not r_b:
            continue
        assert not any(abs(g) == gen for g in r_a + r_b)
        if max(len(r_a), len(r_b)) > reject_len:
            continue
        out1, out2 = relabel(r_a, iso_gen), relabel(r_b, iso_gen)
        cap = max(default_cap, max(len(out1), len(out2)) + cap_headroom)
        out.append(CoVResult(
            applicable=True, r1=out1, r2=out2, n_cov=1, cap=cap,
            z_word=w, iso_index=iso_index, iso_gen=iso_gen, expr=expr,
            n_subs=n1 + n2,
            meta={"intermediate": (r1s, r2s, r_def)},
        ))
    return tuple(out)


def apply_cov_once(r1, r2, z_word, default_cap=DEFAULT_CAP,
                   cap_headroom=CAP_HEADROOM, reject_len=REJECT_LEN,
                   allow_defining_iso=False, iso_gen="x", iso_index=None):
    """One CoV for one z candidate; None when this z fails.

    ``iso_index=None`` returns the FIRST valid branch (r1′ before r2′) — the
    single-transform entry point, e.g. ``change_of_variables``. Pass an int to
    select one specific branch. The length SWEEP must not use the default:
    first-wins silently discards the other branch, and which one you get is
    decided by candidate order, not by anything principled. Use
    ``cov_branches`` there (``enumerate_cov`` does).
    """
    branches = cov_branches(r1, r2, z_word, default_cap=default_cap,
                            cap_headroom=cap_headroom, reject_len=reject_len,
                            allow_defining_iso=allow_defining_iso,
                            iso_gen=iso_gen)
    if iso_index is None:
        return branches[0] if branches else None
    for res in branches:
        if res.iso_index == iso_index:
            return res
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
        "iso_gen": result.iso_gen if result.applicable else None,
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


def subword_candidates(r1, r2, min_len=SUBWORD_MIN_LEN,
                       min_transformed_len=MIN_TRANSFORMED_LEN):
    """Every distinct subword of the relators that does not collapse one.

    The data-driven family for the length-sweep experiment: unlike
    ``NAIVE_Z_FAMILY``, these w occur as cyclic subwords of the presentation
    (and ``substitute_word`` matches linear + seam occurrences). Subwords are
    read off each CYCLICALLY reduced relator, seam included (via the doubled
    word), at EVERY length ``min_len..n`` — there is no |w| bound, so the
    family is a function of the presentation alone (sweep tag subnc2pxysb).

    The one length rule is the NO-COLLAPSE gate, and it is about the effect of
    the substitution, not about where w was read from: a w that substitutes
    ANY relator down to fewer than ``min_transformed_len`` letters is dropped,
    even when it is a short interior subword of the other relator. A relator
    that collapses to length 2 is the two-letter isolator z^η·a^ε, which is
    exactly the hypothesis of the relator-minus-one factorization theorem
    (literature/proofs/PROOFS.tex sec. minus-one): that branch provably
    factors as an ORDINARY rank-two substitution plus a signed rename, so it
    reaches nothing the greedy could not walk to itself, and it is not a new
    coordinate system — which is the only thing a CoV is for. Collapse to
    length <= 1 is the same degeneracy one step further (z alone, or a
    primitive output that solves in ~1 node).

    Worked: r1 = xyxxy, r2 = yxxy, w = yxx. |w| = 3 <= |r1| - 2, so w is a
    legitimate interior subword of r1 (-> xzy) — but it also occurs in r2 and
    takes it to zy, length 2, so w is rejected. Its outputs would have been
    (yx, YYXY) and (X, YYx): primitive relators, i.e. free solves.

    This gate strictly contains the per-relator |w| <= |r| - 2 rule it
    replaced (|w| = n - 1 collapses that relator to 2; |w| = n collapses it to
    1), so no separate |w| bound is needed. Censused over the 66-row
    benchmark: it keeps 6625 of 6655 rows and 394 of 398 Aut-orbits, and cuts
    primitive-output rows from 25 to 9.

    ``w`` and ``w⁻¹`` yield the same CoV up to inverting z, so each pair keeps
    one canonical member: ``max(w, w⁻¹)``, which starts with a positive letter
    whenever the pair has one. Pure powers (xx, yyy, …) are candidates too —
    which words work is the sweep's empirical question, so nothing is excluded
    a priori (the mixed-only rule was the pre-p family).
    Deterministic order (length, then tuple) — row identity depends on it.
    """
    r1, r2 = tuple(r1), tuple(r2)
    seen = set()
    for rel in (r1, r2):
        cyc = reduce_word(rel, cyclic=True)
        n = len(cyc)
        doubled = cyc + cyc
        for length in range(min_len, n + 1):
            for i in range(n):
                w = doubled[i:i + length]
                seen.add(max(w, inverse(w)))
    kept = []
    for w in seen:
        # "brought to" length <= 2: only a relator the substitution actually
        # fired on can be collapsed BY it. n_subs == 0 leaves a relator at its
        # input length, which is the input's property, not this z's.
        collapses = False
        for rel in (r1, r2):
            sub, n_subs = substitute_word(rel, w)
            if n_subs and len(sub) < min_transformed_len:
                collapses = True
                break
        if not collapses:
            kept.append(w)
    return tuple(sorted(kept, key=lambda w: (len(w), w)))


def enumerate_cov(r1, r2, family=None, default_cap=DEFAULT_CAP,
                  cap_headroom=CAP_HEADROOM, reject_len=REJECT_LEN,
                  subword_min_len=SUBWORD_MIN_LEN,
                  min_transformed_len=MIN_TRANSFORMED_LEN,
                  allow_defining_iso=False, iso_targets=("x", "y")):
    """All valid CoVs over ``family`` (default: the presentation's own
    subwords) — the brute-force half of the length-sweep experiment.

    Brute force means every axis, so this enumerates
    ``(z_word, iso_gen, iso_index)`` — NOT ``(z_word, iso_gen)``:

    * each isolation target in ``iso_targets`` (eliminate x AND eliminate y —
      both are legal destabilizations and which works is empirical), and
    * every isolating branch per target (``cov_branches``): when both r1′ and
      r2′ isolate, they are two different coordinate changes with different
      outputs. Taking only the first would let candidate order — an
      implementation detail — pick the row, and would bias any "which z helps"
      correlation by a branch nobody chose.

    Distinct combinations can still land on the same output pair, which would
    be an identical search run twice, so only the first (family order, then
    target, then branch) of each output pair is kept. Order is deterministic —
    sweep row identity depends on it.
    """
    r1, r2 = tuple(r1), tuple(r2)
    if family is None:
        family = subword_candidates(r1, r2, subword_min_len, min_transformed_len)
    results, seen_pairs = [], set()
    for z_word in family:
        for target in iso_targets:
            for res in cov_branches(r1, r2, z_word, default_cap=default_cap,
                                    cap_headroom=cap_headroom,
                                    reject_len=reject_len,
                                    allow_defining_iso=allow_defining_iso,
                                    iso_gen=target):
                if (res.r1, res.r2) in seen_pairs:
                    continue
                seen_pairs.add((res.r1, res.r2))
                results.append(res)
    return tuple(results)
