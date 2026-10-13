"""The steps of a hybrid certificate, the run that applies them to the canonical pair, and their JSON form.

A step is a ``Move`` (an S-move), ``Aut(k)`` (the canonical form of ``acx.aut.autos.AUTOS[k]`` applied) or a
higher-rank event (a dict, from ``dynrank``). ``Run`` charges one work unit per step it applies.
"""
from collections import namedtuple

from ..aut.autos import TABLES, apply_table
from ..core.moves import Move, apply_raw
from ..core.words import booth_str, canonical_rels, canonical_word, inverse, reduce, rotate

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


def encode_steps(steps):
    """JSON form of a certificate: ``[i, j, s, k1, k2]``, ``{"aut": k}`` or the dyn dict (lists for tuples)."""
    def js(x):
        if isinstance(x, dict):
            return {str(k): js(v) for k, v in x.items()}
        return [js(v) for v in x] if isinstance(x, (tuple, list)) else x
    return [{"aut": s.k} if isinstance(s, Aut) else js(s) if isinstance(s, dict) else list(s) for s in steps]


def decode_steps(items):
    """Inverse of ``encode_steps``."""
    def tup(x):
        return tuple(map(tup, x)) if isinstance(x, list) else x

    def dyn(d):
        ev = {k: tup(v) for k, v in d["event"].items()}
        rl = d["relabel"] and {k: {int(g): v for g, v in m.items()} for k, m in d["relabel"].items()}
        return {"op": "dyn", "event": ev, "relabel": rl, "after": tup(d["after"])}
    return tuple(Move(*s) if isinstance(s, list) else Aut(s["aut"]) if "aut" in s else dyn(s) for s in items)
