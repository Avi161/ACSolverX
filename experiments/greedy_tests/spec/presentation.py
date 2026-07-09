"""Presentations, the flat-int codec, and the AC4/AC5 stabilization moves.

``Presentation`` carries ``n_gen`` explicitly rather than inferring it from the
relators, because AC4 produces ``<x,y,z | r1, r2, z>`` in which ``z`` occurs in
exactly one relator -- inferring ``n_gen`` from the letters present would be
correct there but wrong after a substitution eliminates the last occurrence of a
generator.
"""

from dataclasses import dataclass

from .words import (
    booth_order_key,
    canonical_word,
    lex_key,
    reduce_word,
    str_to_word,
    word_to_str,
)

_INT_TO_CHAR = {1: "x", -1: "X", 2: "y", -2: "Y", 3: "z", -3: "Z"}


@dataclass(frozen=True)
class Presentation:
    n_gen: int
    relators: tuple

    def __post_init__(self):
        object.__setattr__(self, "relators", tuple(tuple(r) for r in self.relators))
        for r in self.relators:
            for g in r:
                if g == 0 or abs(g) > self.n_gen:
                    raise ValueError(f"symbol {g} outside 1..{self.n_gen}")

    @property
    def n_rel(self):
        return len(self.relators)

    @property
    def is_balanced(self):
        return self.n_rel == self.n_gen

    @property
    def total_length(self):
        return sum(len(r) for r in self.relators)

    def to_strs(self):
        return tuple(word_to_str(r) for r in self.relators)

    def reduced(self, cyclic=True):
        return Presentation(
            self.n_gen, tuple(reduce_word(r, cyclic) for r in self.relators)
        )

    def canonical(self):
        """Canonicalise each relator, then order-normalise by (length, lex).

        At n_rel=2 this is exactly ``canonical_pair_nj``.
        """
        canon = [canonical_word(r) for r in self.relators]
        canon.sort(key=lambda r: (len(r), lex_key(r, booth_order_key)))
        return Presentation(self.n_gen, tuple(canon))

    # -- the solver's notion of "solved" vs the mathematical one -------------

    def all_relators_are_single_letters(self):
        """The solver's termination test: every relator has length 1.

        ``GreedyBaselineSolver`` checks ``len(r1) == 1 and len(r2) == 1``. That
        is a *necessary* condition for triviality, and sufficient only because
        AC moves preserve the presented group, so a presentation of the trivial
        group can never reach e.g. ``<x,y | x, x>`` (which presents Z).
        """
        return all(len(r) == 1 for r in self.relators)

    def is_trivial(self):
        """The mathematical trivial presentation ``<x_1..x_n | x_1..x_n>``."""
        return (
            self.is_balanced
            and self.all_relators_are_single_letters()
            and {abs(r[0]) for r in self.relators} == set(range(1, self.n_gen + 1))
        )

    # -- AC4 / AC5 ----------------------------------------------------------

    def stabilize(self):
        """AC4: ``<x..| r..>`` -> ``<x.., z | r.., z>`` with ``z`` a new generator."""
        z = self.n_gen + 1
        return Presentation(z, self.relators + ((z,),))

    def destabilize(self):
        """AC5, the inverse of AC4. Requires the trivial relator to be present."""
        z = self.n_gen
        idx = [i for i, r in enumerate(self.relators) if r == (z,) or r == (-z,)]
        if not idx:
            raise ValueError(f"no trivial relator for generator {z}")
        keep = [r for i, r in enumerate(self.relators) if i != idx[0]]
        for r in keep:
            if any(abs(g) == z for g in r):
                raise ValueError(f"generator {z} still occurs in {r}")
        return Presentation(z - 1, tuple(keep))

    # -- flat-int codec -----------------------------------------------------

    @classmethod
    def from_flat_ints(cls, ints, n_rel=2, n_gen=None):
        """Decode the dataset layout ``[r1(L) | r2(L) | ...]``, zero-padded.

        ``run_baseline.int_line_to_relators`` hardcodes ``n_rel = 2`` via
        ``len(ints) // 2``; this generalises the split.
        """
        if len(ints) % n_rel:
            raise ValueError(f"{len(ints)} ints do not split into {n_rel} slots")
        slot = len(ints) // n_rel
        relators = tuple(
            tuple(t for t in ints[k * slot:(k + 1) * slot] if t != 0)
            for k in range(n_rel)
        )
        if n_gen is None:
            n_gen = max((abs(g) for r in relators for g in r), default=1)
        return cls(n_gen, relators)

    def to_flat_ints(self, slot):
        if any(len(r) > slot for r in self.relators):
            raise ValueError(f"a relator exceeds the {slot}-int slot")
        out = []
        for r in self.relators:
            out.extend(r)
            out.extend([0] * (slot - len(r)))
        return out

    @classmethod
    def from_strs(cls, *strs, n_gen=None):
        relators = tuple(str_to_word(s) for s in strs)
        if n_gen is None:
            n_gen = max((abs(g) for r in relators for g in r), default=1)
        return cls(n_gen, relators)


TRIVIAL_2 = Presentation(2, ((1,), (2,)))


def trivial(n_gen):
    return Presentation(n_gen, tuple((g,) for g in range(1, n_gen + 1)))
