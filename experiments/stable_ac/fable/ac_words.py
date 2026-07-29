"""Word algebra on F_2 and the twelve AC moves h_1 .. h_12 of ``app/ac_paths.tex``.

Alphabet is the repo's ``xXyY`` convention: a lowercase letter is a generator, its
uppercase is that generator's inverse.

The move numbering is transcribed *literally* from the LaTeX source of the paper
appendix (``app/ac_paths.tex``), not from any solver implementation:

    h1  = r2 -> r2 r1            h5  = r2 -> x^-1 r2 x        h9  = r2 -> x r2 x^-1
    h2  = r1 -> r1 r2^-1         h6  = r1 -> y^-1 r1 y        h10 = r1 -> y r1 y^-1
    h3  = r2 -> r2 r1^-1         h7  = r2 -> y^-1 r2 y        h11 = r2 -> y r2 y^-1
    h4  = r1 -> r1 r2            h8  = r1 -> x r1 x^-1        h12 = r1 -> x^-1 r1 x

Semantics of ``cyclical=False``: the two relators of a state are always kept freely
reduced, never cyclically reduced.  Since the inputs are freely reduced, the only
cancellation a move can create is at the seam(s) it introduces, so a full free
reduction of the concatenation is exactly "free reduction at the seams".

A per-relator length cap is applied *after* reduction: a move whose rewritten relator
would exceed the cap is a no-op (it returns the input state unchanged).  This matches
the AC-Solver convention of a bounded relator length.
"""

from __future__ import annotations

LETTERS = ("x", "X", "y", "Y")
GENERATORS = ("x", "y")

# Solver alphabet order Y < y < X < x (the order used by
# ``experiments/equivalence_classes/lib/words.py``); reproduced here independently so
# this module has no dependency outside the standard library.
_ORDER = {"Y": 0, "y": 1, "X": 2, "x": 3}


def inverse_letter(c: str) -> str:
    """The inverse of a single letter."""
    return c.swapcase()


def inverse(w: str) -> str:
    """w^-1: reverse the word and invert every letter."""
    return w[::-1].swapcase()


def free_reduce(w: str) -> str:
    """Free reduction by the standard stack algorithm."""
    out: list[str] = []
    for c in w:
        if out and out[-1] == c.swapcase():
            out.pop()
        else:
            out.append(c)
    return "".join(out)


def cyclic_reduce(w: str) -> str:
    """Free reduction followed by cancellation across the cyclic seam."""
    w = free_reduce(w)
    while len(w) >= 2 and w[0] == w[-1].swapcase():
        w = free_reduce(w[1:-1])
    return w


def is_freely_reduced(w: str) -> bool:
    return all(a != b.swapcase() for a, b in zip(w, w[1:]))


def is_cyclically_reduced(w: str) -> bool:
    if not is_freely_reduced(w):
        return False
    return len(w) < 2 or w[0] != w[-1].swapcase()


def total_length(state) -> int:
    return len(state[0]) + len(state[1])


# --------------------------------------------------------------------------------------
# the twelve moves
# --------------------------------------------------------------------------------------

# Each entry is (target relator index (0-based), kind, payload).
#   kind == "concat":      r_target <- r_target . (other relator)^payload
#   kind == "conjugate":   r_target <- payload . r_target . payload^-1
_MOVE_TABLE = {
    1: (1, "concat", +1),      # r2 -> r2 r1
    2: (0, "concat", -1),      # r1 -> r1 r2^-1
    3: (1, "concat", -1),      # r2 -> r2 r1^-1
    4: (0, "concat", +1),      # r1 -> r1 r2
    5: (1, "conjugate", "X"),  # r2 -> x^-1 r2 x
    6: (0, "conjugate", "Y"),  # r1 -> y^-1 r1 y
    7: (1, "conjugate", "Y"),  # r2 -> y^-1 r2 y
    8: (0, "conjugate", "x"),  # r1 -> x r1 x^-1
    9: (1, "conjugate", "x"),  # r2 -> x r2 x^-1
    10: (0, "conjugate", "y"),  # r1 -> y r1 y^-1
    11: (1, "conjugate", "y"),  # r2 -> y r2 y^-1
    12: (0, "conjugate", "X"),  # r1 -> x^-1 r1 x
}

MOVES = tuple(sorted(_MOVE_TABLE))
MOVE_COUNT = len(MOVES)


def move_description(move: int) -> str:
    target, kind, payload = _MOVE_TABLE[move]
    name = f"r{target + 1}"
    other = f"r{2 - target}"
    if kind == "concat":
        return f"{name} -> {name} {other}" + ("" if payload == 1 else "^-1")
    return f"{name} -> {payload} {name} {inverse_letter(payload)}"


def apply_move(state, move: int, cap: int):
    """Apply h_``move`` (1-based) to ``state`` = (r1, r2).

    Returns a new ``(r1, r2)`` tuple; a no-op returns an equal tuple.  The move is a
    no-op when the rewritten relator would be longer than ``cap`` or would be empty
    (an empty relator is not a legal AC state in this convention).
    """
    if move not in _MOVE_TABLE:
        raise ValueError(f"unknown move h{move}")
    r = [state[0], state[1]]
    target, kind, payload = _MOVE_TABLE[move]
    if kind == "concat":
        other = r[1 - target]
        piece = other if payload == 1 else inverse(other)
        new = free_reduce(r[target] + piece)
    else:
        new = free_reduce(payload + r[target] + inverse_letter(payload))
    if len(new) > cap or not new:
        return (state[0], state[1])
    r[target] = new
    return (r[0], r[1])


def children(state, cap: int):
    """The twelve h-move children of ``state`` (no-ops included, in move order)."""
    return [apply_move(state, m, cap) for m in MOVES]


def replay(state, sequence, cap: int):
    """Replay a 1-based h-move ``sequence``; returns the list of states after each move."""
    out = []
    cur = (state[0], state[1])
    for move in sequence:
        cur = apply_move(cur, move, cap)
        out.append(cur)
    return out


def replay_trace(state, sequence, cap: int):
    """Replay and return the published-style ``(move, total_length)`` trace."""
    return [
        (move, total_length(s))
        for move, s in zip(sequence, replay(state, sequence, cap))
    ]


# --------------------------------------------------------------------------------------
# canonical forms (used only for de-duplication against external censuses)
# --------------------------------------------------------------------------------------


def _rot_key(w: str) -> tuple[int, ...]:
    return tuple(_ORDER[c] for c in w)


def canon_rel(w: str) -> str:
    """Lex-min over all rotations of ``cyc_reduce(w)`` and of its inverse.

    Ordering is the solver's ``Y < y < X < x``.  Implemented as a plain O(n^2) scan;
    the words handled here are tiny.
    """
    w = cyclic_reduce(w)
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


def canon_pair(r1: str, r2: str):
    """Canonical, order-normalised pair: ``canon_rel`` each side, then sort by (len, key)."""
    a, b = canon_rel(r1), canon_rel(r2)
    if (len(a), _rot_key(a)) > (len(b), _rot_key(b)):
        a, b = b, a
    return (a, b)
