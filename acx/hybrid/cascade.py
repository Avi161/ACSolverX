"""Stages A-C of the hybrid solver on a canonical pair, and the gates that also finish states during the search.

A step is a ``Move`` (an S-move) or ``Aut(k)`` (the canonical form of ``acx.aut.autos.AUTOS[k]`` applied). Work units:
one per Nielsen image evaluated, per automorphism accepted and per S-move applied; the gates' inspections are free.
"""
from collections import namedtuple

from ..aut.autos import TABLES, apply_table
from ..core.moves import Move, apply_raw
from ..core.priority import length
from ..core.words import booth_str, canonical_rels, canonical_word, inverse, reduce, rotate
from .pinch import bracket, conjugation_forms, from_syllables, pinch_once, pinch_preflight, syllables

Aut = namedtuple("Aut", "k")
NIELSEN = (14, 17, 8, 11)       # AUTOS indices of x -> xy, x -> xY, y -> yx, y -> yX


class Budget(Exception):
    """Raised when a ``Run`` is charged past its budget of work units."""


def image(w, k):
    """``AUTOS[k](w)``, cyclically reduced."""
    return reduce(apply_table(w, TABLES[k]))


def aut_child(state, k):
    """The canonical pair after ``AUTOS[k]``."""
    return canonical_rels(tuple(image(r, k) for r in state))


def move_child(state, m):
    """The canonical pair after the S-move ``m``."""
    return canonical_rels(tuple(reduce(r) for r in apply_raw(state, m)))


def is_terminal(state):
    """Is the pair ``(g, h)`` with ``g, h`` distinct generators?"""
    a, b = state
    return len(a) == 1 and len(b) == 1 and abs(a[0]) != abs(b[0])


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
        """Spend one work unit."""
        self.units += 1
        if self.units > self.budget:
            raise Budget()

    def mark(self):
        """A point to ``rollback`` to."""
        return len(self.steps), self.state

    def rollback(self, mark):
        """Undo the steps since ``mark``."""
        del self.steps[mark[0]:]
        self.state = mark[1]

    def apply_aut(self, k):
        """Apply ``AUTOS[k]`` (one unit)."""
        self.charge()
        self.state = aut_child(self.state, k)
        self.steps.append(Aut(k))

    def apply_move(self, m):
        """Apply the S-move ``m`` (one unit)."""
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
    """Stage A: apply, while one exists, the Nielsen map (``x -> xy, xY``, ``y -> yx, yX``) that most reduces the total
    cyclic length."""
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
    """The donor is one letter ``g``: delete every ``g^+-1`` of the companion, one S-move each. Abelianisation
    (``|det| = 1``) forces what is left to be the other generator."""
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
    """Does a generator occur exactly once in ``w``?"""
    return _count(w, 1) == 1 or _count(w, 2) == 1


def _finish_one_occurrence(run, index):
    """A relator ``g h^r`` up to rotation: replace each ``g`` of the companion by ``h^-r``, one S-move each."""
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
    """Stage B: True when relator ``index`` is primitive and the pair has been finished from it (directly if a generator
    occurs once in it, else by shortening it to one letter with Nielsen maps)."""
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
def stage_pinch(run, donor_index, form):
    """Stage C: execute the pinch cascade ``pinch_preflight`` certified (one S-move per rule use) on the companion of the
    relator ``donor_index``, then finish with stage B; True when the pair is finished."""
    g, a, h, p, q = form
    mark = run.mark()
    donor = run.state[donor_index]
    while True:
        ci = 1 - run.state.index(donor)
        syl = syllables(run.state[ci])
        if sum(1 for s in syl if s[0] == g) <= 1:
            break
        b = bracket(syl, g, a, p, q)
        if b is None:
            run.rollback(mark)
            return False
        _, position, lhs, rhs = pinch_once(syl, b[0], g, a, h, p, q)
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
    """Free structural preflight: does a finishing gate apply to the pair?"""
    if is_terminal(state):
        return True
    return any(one_occurrence(state[i]) or any(pinch_preflight(f, state[1 - i]) is not None
                                               for f in conjugation_forms(state[i])) for i in range(2))


def run_gates(run):
    """Try the finishing gates (stages B and C) on ``run.state``; True when the pair is finished."""
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
