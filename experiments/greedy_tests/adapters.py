"""The seam that makes this suite outlive the two-generator solver.

Every solver is wrapped as a :class:`SolverAdapter`: it declares which
presentations it ``supports`` and returns a normalised :class:`SearchStats`.
The contract and invariant tests iterate ``ALL_ADAPTERS`` x fixtures and skip
unsupported combinations.

**To add the stable-AC solver: write one adapter and append it to
``ALL_ADAPTERS``.** The entire contract suite then runs against it at
``n_gen = 3`` with no test edits. The ``Spec`` adapter already supports arbitrary
``n_gen``, so those tests are exercised today rather than sitting as dead skips.

A deliberate non-goal: the contract never asserts that two adapters explore the
same number of nodes. Exact-trace parity is a property of the *normal/heavy*
pair specifically (they are two implementations of one search) and is asserted
in ``test_solver_parity.py``. A correct stable solver may legitimately explore
in a different order.
"""

from dataclasses import dataclass, field

from experiments.search.greedy_baseline import greedy_search, str_to_move

from .spec import search as spec_search
from .spec.moves import Move, legacy_to_move
from .spec.presentation import Presentation
from .spec.words import str_to_word


@dataclass(frozen=True)
class SearchStats:
    solved: bool
    nodes_explored: int
    path_length: object          # int when solved, else None
    min_total: int
    max_total: int
    max_expanded_total: int
    min_relators: tuple
    max_relators: tuple
    max_expanded_relators: tuple
    path_moves: tuple = ()       # Move tuples
    path_states: tuple = ()      # Presentation objects
    raw: dict = field(default_factory=dict, compare=False, repr=False)


def _words(strs):
    return tuple(str_to_word(s) for s in strs)


class _NumbaAdapter:
    """Shared wrapper over ``greedy_search``; the two paths differ only by a flag."""

    high_speedup = False

    def supports(self, pres):
        # The (n, 2) bool encoding has one bit for "which generator", and
        # pack_key packs exactly two segments around one 0x00 separator.
        return pres.n_gen == 2 and pres.n_rel == 2

    def search(self, pres, budget, cap=24, cyclic=True, progress=None):
        r1, r2 = pres.to_strs()
        raw = greedy_search(
            r1, r2, budget,
            max_relator_length=cap,
            cyclic_reduce=cyclic,
            high_speedup=self.high_speedup,
            progress=progress,
        )
        return self._normalise(pres, raw)

    def _normalise(self, pres, raw):
        moves = tuple(legacy_to_move(*str_to_move(s)) for s in raw["path_moves"])
        states = tuple(
            Presentation(pres.n_gen, _words(st)) for st in raw["path"]
        )
        return SearchStats(
            solved=raw["solved"],
            nodes_explored=raw["nodes_explored"],
            path_length=raw["path_length"],
            min_total=raw["min_relator_length"],
            max_total=raw["max_relator_length"],
            max_expanded_total=raw["max_relator_length_expanded"],
            min_relators=_words(raw["min_relator"]),
            max_relators=_words(raw["max_relator"]),
            max_expanded_relators=_words(raw["max_relator_expanded"]),
            path_moves=moves,
            path_states=states,
            raw=raw,
        )


class NormalNumbaAdapter(_NumbaAdapter):
    name = "normal"
    high_speedup = False
    #: reconstructs parent pointers, so a solved run comes back with a path
    yields_path = True


class HeavyNumbaAdapter(_NumbaAdapter):
    name = "heavy"
    high_speedup = True
    #: drops ``move_in`` to save memory; the runner re-solves to recover a path
    yields_path = False


class SpecAdapter:
    name = "spec"
    yields_path = True

    def supports(self, pres):
        return pres.n_gen >= 1 and pres.n_rel >= 2

    def search(self, pres, budget, cap=24, cyclic=True, progress=None):
        raw = spec_search.search(pres, budget, cap=cap, cyclic=cyclic,
                                 progress=progress)
        return SearchStats(
            solved=raw["solved"],
            nodes_explored=raw["nodes_explored"],
            path_length=raw["path_length"],
            min_total=raw["min_relator_length"],
            max_total=raw["max_relator_length"],
            max_expanded_total=raw["max_relator_length_expanded"],
            min_relators=_words(raw["min_relator"]),
            max_relators=_words(raw["max_relator"]),
            max_expanded_relators=_words(raw["max_relator_expanded"]),
            path_moves=tuple(raw["path_moves"]),
            path_states=tuple(raw["path_states"]),
            raw=raw,
        )


NORMAL = NormalNumbaAdapter()
HEAVY = HeavyNumbaAdapter()
SPEC = SpecAdapter()

#: Append a stable-AC adapter here and the contract suite covers it.
ALL_ADAPTERS = [NORMAL, HEAVY, SPEC]

#: The two implementations of one search; only these owe exact-trace parity.
PARITY_PAIR = (NORMAL, HEAVY)


def replay_moves(pres, moves, cyclic=True):
    """Replay ``Move``s from a start presentation. Works for any adapter's path."""
    return spec_search.replay(pres, moves, cyclic=cyclic)


__all__ = [
    "SearchStats", "SolverAdapterError", "Move",
    "NormalNumbaAdapter", "HeavyNumbaAdapter", "SpecAdapter",
    "NORMAL", "HEAVY", "SPEC", "ALL_ADAPTERS", "PARITY_PAIR", "replay_moves",
]


class SolverAdapterError(RuntimeError):
    pass
