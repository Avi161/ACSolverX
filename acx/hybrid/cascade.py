"""Rank-two stages of the hybrid solver: Nielsen descent, primitive deletion, pinch cascade.

Run in order on a canonical pair until it is ``(g, h)`` with ``g, h`` distinct
generators:

A. **pair descent**: apply the Nielsen map (``x -> xy, xY``, ``y -> yx, yX``)
   that most reduces the total cyclic length, while one does.
B. **primitive deletion**: shorten ONE relator to a single letter with Nielsen
   maps (the companion carried along); a one-letter relator ``g`` deletes every
   ``g`` of the companion with one S-move each, and abelianisation (``|det| = 1``)
   forces the residue to be the other generator. A relator in which some
   generator occurs once (``g h^r`` up to rotation) is finished directly: each
   ``g`` of the companion is replaced by ``h^-r`` with one S-move.
C. **pinch cascade**: a relator of cyclic shape ``g^a h^p g^-a h^q`` gives four
   rewriting rules (``g^a h^p -> h^-q g^a``, ``g^-a h^-q -> h^p g^-a``,
   ``h^-p g^-a -> g^-a h^q``, ``h^q g^a -> g^a h^-p``) that pinch the companion's
   ``g``-syllables away (Britton reduction) when the enclosed ``h``-exponent is
   divisible; each rule use is one S-move. An exponent-level dry run
   (``pinch_preflight``) decides applicability for free; a companion left as
   ``g^s h^r`` with ``|s| = 1`` or ``|r| = 1`` is primitive and B finishes.

The gates of B and C (``gate_applicable`` / ``run_gates``) are also the
finishing tests of the hybrid search. Work units (the budget): one per Nielsen
image evaluated, one per automorphism accepted, one per S-move applied; gate
inspections are free.

A step is a ``Move`` (an S-move of ``acx.core.moves`` on the canonical pair) or
an ``Aut(k)``: the state becomes the canonical form of ``AUTOS[k]`` applied to
it (``acx.aut.whitehead.AUTOS``: 8 signed permutations, then 12 Whitehead
automorphisms, among them the four Nielsen maps). ``acx.hybrid.certify``
turns such a path into elementary AC moves on the original row.

Port of ``origin/claude/vigilant-babbage-nnbuj0:research/ac_hashfree_cascade_20260914/
hfcascade.py`` (stages A-C, gates, ``Run``) on ``acx`` int words; its beam and
pure-Python best-first engines (stage D) are not ported, the hybrid search
replaces them.
"""
from collections import namedtuple
from functools import lru_cache

from ..aut.whitehead import TABLES, apply_table
from ..core.moves import Move, apply_raw
from ..core.priority import length
from ..core.words import booth_str, canonical_rels, canonical_word, inverse, reduce, rotate

Aut = namedtuple("Aut", "k")
NIELSEN = (14, 17, 8, 11)       # AUTOS indices of x -> xy, x -> xY, y -> yx, y -> yX


class Budget(Exception):
    pass


def image(w, k):
    """``AUTOS[k](w)``, cyclically reduced."""
    return reduce(apply_table(w, TABLES[k]))


def aut_child(state, k):
    return canonical_rels(tuple(image(r, k) for r in state))


def move_child(state, m):
    return canonical_rels(tuple(reduce(r) for r in apply_raw(state, m)))


def is_terminal(state):
    a, b = state
    return len(a) == 1 and len(b) == 1 and abs(a[0]) != abs(b[0])


def syllables(w):
    """Cyclic syllables ``[(generator, signed exponent)]``, the seam merged."""
    out, run, n = [], 0, 0
    for g in w:
        if g == run:
            n += 1
            continue
        if run:
            out.append((abs(run), n if run > 0 else -n))
        run, n = g, 1
    if run:
        out.append((abs(run), n if run > 0 else -n))
    if len(out) > 1 and out[0][0] == out[-1][0]:
        out[0] = (out[0][0], out[0][1] + out.pop()[1])
    return out


def from_syllables(syl):
    """The word with the syllables ``[(generator, signed exponent)]``."""
    return sum((((g if e > 0 else -g),) * abs(e) for g, e in syl), ())


def _find(hay, needle):
    return booth_str(hay).find(booth_str(needle))


def _count(w, g):
    return w.count(g) + w.count(-g)


class Run:
    """A certificate under construction: the canonical pair, the steps, the work units."""

    def __init__(self, rels, budget):
        self.budget, self.units, self.steps = budget, 0, []
        self.state = canonical_rels(tuple(reduce(r) for r in rels))

    def charge(self):
        self.units += 1
        if self.units > self.budget:
            raise Budget()

    def mark(self):
        return len(self.steps), self.state

    def rollback(self, mark):
        del self.steps[mark[0]:]
        self.state = mark[1]

    def apply_aut(self, k):
        self.charge()
        self.state = aut_child(self.state, k)
        self.steps.append(Aut(k))

    def apply_move(self, m):
        self.charge()
        self.state = move_child(self.state, m)
        self.steps.append(m)

    def rewrite_at(self, ti, word, position, lhs, rhs):
        """Replace ``lhs`` by ``rhs`` at ``position`` of the oriented spelling ``word`` of relator ``ti``
        with ONE S-move: ``lhs^-1 rhs`` must be a rotation of the other relator or of its inverse."""
        if word[position:position + len(lhs)] != lhs:
            raise AssertionError("rewrite does not match the oriented word")
        actual, donor = self.state[ti], self.state[1 - ti]
        n = len(word)
        shift = _find(word + word, actual)
        loc_lhs, loc_rhs = lhs, rhs
        if 0 <= shift < n:
            start = (position - shift) % n
        else:
            inv = inverse(word)
            shift = _find(inv + inv, actual)
            if not 0 <= shift < n:
                raise AssertionError("canonical target is not a rotation or inverse of the oriented word")
            start = (n - position - len(lhs) - shift) % n
            loc_lhs, loc_rhs = inverse(lhs), inverse(rhs)
        needed = reduce(inverse(loc_lhs) + loc_rhs, cyclic=False)
        move = next((Move(ti, 1 - ti, s, (-(start + len(loc_lhs))) % len(actual), cut)
                     for s in (1, -1) for o in [donor if s == 1 else inverse(donor)]
                     for cut in range(len(o)) if rotate(o, cut) == needed), None)
        if move is None:
            raise AssertionError("replacement is not a cyclic donor substitution")
        child = move_child(self.state, move)
        desired = canonical_word(reduce(word[:position] + rhs + word[position + len(lhs):]))
        if sorted(child) != sorted((desired, donor)):
            raise AssertionError("substitution does not produce the intended rewrite")
        self.charge()
        self.state = child
        self.steps.append(move)


# ---------------------------------------------------------------- stage A
def stage_pair_descent(run):
    """Apply, while one exists, the Nielsen map that most reduces the total cyclic length."""
    while True:
        best = None
        for k in NIELSEN:
            run.charge()
            gain = length(run.state) - sum(len(image(r, k)) for r in run.state)
            if gain > 0 and (best is None or gain > best[0]):
                best = (gain, k)
        if best is None:
            return
        run.apply_aut(best[1])


# ---------------------------------------------------------------- stage B
def _relator_descent(run, index):
    """Strictly shorten relator ``index`` with Nielsen maps; its index once it is one letter, else None."""
    donor = run.state[index]
    while len(donor) > 1:
        best = None
        for k in NIELSEN:
            run.charge()
            cand = canonical_word(image(donor, k))
            if len(cand) < len(donor) and (best is None or (len(cand), booth_str(cand)) < best[0]):
                best = ((len(cand), booth_str(cand)), k, cand)
        if best is None:
            return None
        run.apply_aut(best[1])
        donor = best[2]
        if donor not in run.state:
            raise AssertionError("tracked donor absent after an accepted map")
    return run.state.index(donor)


def _last_index(w, g):
    """The least ``k`` with ``rotate(w, k)[-1]`` a letter of generator ``g``."""
    n = len(w)
    return next(k for k in range(n) if abs(w[n - 1 - k]) == g)


def _delete_letters(run, donor_index):
    """The donor is one letter ``g``: delete every ``g^+-1`` of the companion, one S-move each."""
    g = run.state[donor_index]
    if len(g) != 1:
        raise AssertionError("deletion needs a one-letter donor")
    while True:
        di = 0 if run.state[0] == g else 1 if run.state[1] == g else None
        if di is None:
            raise AssertionError("one-letter donor lost")
        comp = run.state[1 - di]
        if not _count(comp, abs(g[0])):
            break
        k1 = _last_index(comp, abs(g[0]))
        run.apply_move(Move(1 - di, di, 1 if g[0] == -rotate(comp, k1)[-1] else -1, k1, 0))
    return is_terminal(run.state)


def one_occurrence(w):
    return _count(w, 1) == 1 or _count(w, 2) == 1


def _finish_one_occurrence(run, index):
    donor = run.state[index]
    g = 1 if _count(donor, 1) == 1 else 2
    while True:
        di = 0 if run.state[0] == donor else 1 if run.state[1] == donor else None
        if di is None:
            raise AssertionError("one-occurrence donor lost")
        comp = run.state[1 - di]
        if not _count(comp, g):
            break
        k1 = _last_index(comp, g)
        letter = rotate(comp, k1)[-1]
        s = 1 if -letter in donor else -1
        o = donor if s == 1 else inverse(donor)
        k2 = next(k for k in range(len(o)) if rotate(o, k)[0] == -letter)
        run.apply_move(Move(1 - di, di, s, k1, k2))
    di = 0 if run.state[0] == donor else 1
    if len(run.state[1 - di]) != 1:
        return False                  # not a trivial-group pair (or a non-terminal residue)
    return _delete_letters(run, 1 - di)


def stage_primitive(run, index):
    """True when relator ``index`` is primitive and the pair has been finished from it."""
    mark = run.mark()
    if one_occurrence(run.state[index]) and _finish_one_occurrence(run, index):
        return True
    run.rollback(mark)
    donor_index = _relator_descent(run, index)
    if donor_index is not None and _delete_letters(run, donor_index):
        return True
    run.rollback(mark)                # stalled, or the abelianisation obstruction
    return False


# ---------------------------------------------------------------- stage C
@lru_cache(maxsize=1 << 16)
def conjugation_forms(w):
    """Every reading of the cyclic word as ``g^a h^p g^-a h^q`` with ``a > 0`` and ``p, q != 0``."""
    syl = syllables(w)
    if len(syl) != 4:
        return []
    forms = []
    for off in range(4):
        (g, a), (h, p), (g2, b), (h2, q) = (syl[(off + t) % 4] for t in range(4))
        if g == g2 and h == h2 and a > 0 and a + b == 0:
            forms.append((g, a, h, p, q))
    return forms


def _bracket(syl, g, a, p, q):
    """First cyclically adjacent pair of ``g``-syllables ``(e1, m, e2)`` of opposite sign, both of size at
    least ``a``, whose enclosed ``h``-exponent ``m`` is a multiple of ``p`` (``e1 > 0``) or ``q`` (``e1 < 0``)."""
    n = len(syl)
    for i in range(n):
        if syl[i][0] != g:
            continue
        j = (i + 2) % n
        if n < 4 or syl[j][0] != g or syl[(i + 1) % n][0] == g:
            continue
        e1, m, e2 = syl[i][1], syl[(i + 1) % n][1], syl[j][1]
        if e1 * e2 >= 0 or abs(e1) < a or abs(e2) < a:
            continue
        d = p if e1 > 0 else q
        if m % d == 0:
            return i, d
    return None


def _merge(syl):
    out = []
    for g, e in syl:
        if e == 0:
            continue
        if out and out[-1][0] == g:
            out[-1] = (g, out[-1][1] + e)
            if out[-1][1] == 0:
                out.pop()
        else:
            out.append((g, e))
    while len(out) > 1 and out[0][0] == out[-1][0]:
        out[0] = (out[0][0], out[0][1] + out.pop()[1])
        if out[0][1] == 0:
            out.pop(0)
    return out


def _pinch_once(syl, i, g, a, h, p, q):
    """One rule use on the bracket at syllable ``i``: the new syllables and the replacement, as ``(position in the word read
    from syllable i, lhs, rhs)`` with lhs and rhs given as syllables."""
    n = len(syl)
    e1, m, e2 = syl[i][1], syl[(i + 1) % n][1], syl[(i + 2) % n][1]
    if e1 > 0:
        left = (m > 0) == (p > 0)
        if left:
            mid = [(g, e1 - a), (h, -q), (g, a), (h, m - p)]
            rw = e1 - a, [(g, a), (h, p)], [(h, -q), (g, a)]
        else:
            mid = [(g, e1), (h, m + p), (g, -a), (h, q), (g, e2 + a)]
            rw = e1 + abs(m) - abs(p), [(h, -p), (g, -a)], [(g, -a), (h, q)]
    else:
        left = (m > 0) == (q < 0)
        if left:
            mid = [(g, e1 + a), (h, p), (g, -a), (h, m + q)]
            rw = -e1 - a, [(g, -a), (h, -q)], [(h, p), (g, -a)]
        else:
            mid = [(g, e1), (h, m - q), (g, a), (h, -p), (g, e2 - a)]
            rw = -e1 + abs(m) - abs(q), [(h, q), (g, a)], [(g, a), (h, -p)]
    rest = [syl[(i + k) % n] for k in range(2 if left else 3, n)]
    return (_merge(mid + rest),) + rw


@lru_cache(maxsize=1 << 16)
def pinch_preflight(form, companion, max_rules=400):
    """Dry run of the cascade on syllables: the number of rule uses when the companion ends primitive."""
    g, a, h, p, q = form
    syl = syllables(companion)
    rules = 0
    while sum(1 for s in syl if s[0] == g) > 1:
        b = _bracket(syl, g, a, p, q)
        if b is None:
            return None
        syl = _pinch_once(syl, b[0], g, a, h, p, q)[0]
        rules += 1
        if rules > max_rules:
            return None
    if len(syl) == 2 and (abs(syl[0][1]) == 1 or abs(syl[1][1]) == 1):
        return rules
    if len(syl) == 1 and abs(syl[0][1]) == 1:
        return rules
    return None


def stage_pinch(run, donor_index, form):
    """Execute the cascade ``pinch_preflight`` certified; True when the pair is finished."""
    g, a, h, p, q = form
    mark = run.mark()
    donor = run.state[donor_index]
    while True:
        ci = 1 - run.state.index(donor)
        syl = syllables(run.state[ci])
        if sum(1 for s in syl if s[0] == g) <= 1:
            break
        b = _bracket(syl, g, a, p, q)
        if b is None:
            run.rollback(mark)
            return False
        _, position, lhs, rhs = _pinch_once(syl, b[0], g, a, h, p, q)
        run.rewrite_at(ci, from_syllables([syl[(b[0] + k) % len(syl)] for k in range(len(syl))]), position,
                       from_syllables(lhs), from_syllables(rhs))
    if stage_primitive(run, 1 - run.state.index(donor)):
        return True
    run.rollback(mark)
    return False


def try_pinch_gates(run):
    """Execute every conjugation form whose preflight succeeds; True when one finishes the pair."""
    for index in range(2):
        for form in conjugation_forms(run.state[index]):
            if pinch_preflight(form, run.state[1 - index]) is not None and stage_pinch(run, index, form):
                return True
    return False


# ---------------------------------------------------------------- gates
_GEN = bytes.maketrans(bytes([1, 2, 3, 4]), b"abab")


def gate_precheck_key(key):
    """Free test on a packed key: may a gate apply? (a one-letter relator, a generator occurring once,
    or exactly four cyclic syllables)."""
    i = key.index(0)
    for w in (key[:i], key[i + 1:]):
        if len(w) == 1:
            return True
        t = w.translate(_GEN)
        na = t.count(b"a")
        if na == 1 or len(w) - na == 1:
            return True
        tt = t + t[:1]
        if tt.count(b"ab") + tt.count(b"ba") == 4:
            return True
    return len(key) == 3


def gate_applicable(state):
    """Free structural preflight: does a finishing procedure apply here?"""
    if is_terminal(state):
        return True
    return any(one_occurrence(state[i]) or any(pinch_preflight(f, state[1 - i]) is not None
                                               for f in conjugation_forms(state[i])) for i in range(2))


def run_gates(run):
    if is_terminal(run.state):
        return True
    if any(one_occurrence(run.state[i]) and stage_primitive(run, i) for i in range(2)):
        return True
    return try_pinch_gates(run)


def cascade(run):
    """Stages A-C on ``run``; the stage that finished the pair (``"terminal"``, ``"B"``, ``"C"``) or None."""
    if is_terminal(run.state):
        return "terminal"
    stage_pair_descent(run)
    if any(stage_primitive(run, i) for i in range(2)):
        return "B"
    return "C" if try_pinch_gates(run) else None
