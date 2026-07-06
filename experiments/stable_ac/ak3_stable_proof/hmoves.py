"""AC' h-moves (Appendix B of arXiv:2408.15332, lines 2803-2806 of the txt) + replay.

    h1 = r2 -> r2 r1        h5 = r2 -> x^-1 r2 x      h9  = r2 -> x r2 x^-1
    h2 = r1 -> r1 r2^-1     h6 = r1 -> y^-1 r1 y      h10 = r1 -> y r1 y^-1
    h3 = r2 -> r2 r1^-1     h7 = r2 -> y^-1 r2 y      h11 = r2 -> y r2 y^-1
    h4 = r1 -> r1 r2        h8 = r1 -> x r1 x^-1      h12 = r1 -> x^-1 r1 x

Convention pinned by the paper text: "g r g^-1" means the relator becomes g.r.g^-1,
with FREE reduction only (cyclic reduction would cancel the conjugation). Relator
indices here are 0-based internally (r1 -> index 0).

The Appendix-F 53-move path (paper lines 3088-3090) connects the length-25
presentation P25 to AK(3); replaying it is the cross-source gold gate for our move
semantics. The printed sequence uses h1..h12 only (no h0 — verified token-by-token).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stable_moves import concat_move, conjugation_move  # noqa: E402

X, Y = 1, 2

# h -> ("concat", i, j, sign) or ("conj", i, g); i/j 0-based relator indices.
H_TABLE = {
    1:  ("concat", 1, 0, +1),
    2:  ("concat", 0, 1, -1),
    3:  ("concat", 1, 0, -1),
    4:  ("concat", 0, 1, +1),
    5:  ("conj", 1, -X),
    6:  ("conj", 0, -Y),
    7:  ("conj", 1, -Y),
    8:  ("conj", 0, +X),
    9:  ("conj", 1, +X),
    10: ("conj", 0, +Y),
    11: ("conj", 1, +Y),
    12: ("conj", 0, -X),
}

# The inverse h-move (undoes it): concat(i,j,s) after concat(i,j,-s) restores r_i
# (r_j unchanged in between); conj(i,g) inverts to conj(i,-g).
H_INverse_note = "inverse of (concat,i,j,s) is (concat,i,j,-s); of (conj,i,g) is (conj,i,-g)"


def apply_h(state, h):
    kind = H_TABLE[h]
    if kind[0] == "concat":
        _, i, j, sign = kind
        new_state, step = concat_move(state, i, j, sign)
    else:
        _, i, g = kind
        new_state, step = conjugation_move(state, i, g)
    step["h"] = h
    return new_state, step


def apply_h_inverse(state, h):
    kind = H_TABLE[h]
    if kind[0] == "concat":
        _, i, j, sign = kind
        new_state, step = concat_move(state, i, j, -sign)
    else:
        _, i, g = kind
        new_state, step = conjugation_move(state, i, -g)
    step["h_inverse_of"] = h
    return new_state, step


def replay(state, hs, inverse=False, reverse=False):
    """Apply the h-sequence; returns (states, steps). ``reverse`` iterates the list
    backwards; ``inverse`` applies each move's inverse — (reverse & inverse) together
    replay a path backwards."""
    seq = list(reversed(hs)) if reverse else list(hs)
    states = [tuple(list(r) for r in state)]
    steps = []
    for h in seq:
        s, step = (apply_h_inverse if inverse else apply_h)(states[-1], h)
        states.append(s)
        steps.append(step)
    return states, steps


def parse_h_sequence(text):
    """'h9 . h7 . h4' / 'h9 h7 h4' -> [9, 7, 4]."""
    out = []
    for tok in text.replace("·", " ").replace(".", " ").split():
        tok = tok.strip()
        if not tok:
            continue
        if not tok.startswith("h"):
            raise ValueError(f"bad token {tok!r}")
        out.append(int(tok[1:]))
    return out


# ------------------------------------------------------------------ pinned constants

# P25 (paper line 3083): <x,y | x'y'xy'x'yxy''xyx'y , y'x'yyx'y'xyxy''x>  (' = inverse)
P25 = ([-1, -2, 1, -2, -1, 2, 1, -2, -2, 1, 2, -1, 2],
       [-2, -1, 2, 2, -1, -2, 1, 2, 1, -2, -2, 1])

# AK(3) = <x,y | x^3 y^-4, xyx y^-1 x^-1 y^-1>
AK3 = ([1, 1, 1, -2, -2, -2, -2],
       [1, 2, 1, -2, -1, -2])

# Appendix F, lines 3088-3090: the 53-move AC' path "connecting the length 25
# presentation to AK(3)".
APPENDIX_F_SEQ = parse_h_sequence(
    "h9 h7 h4 h8 h11 h5 h11 h9 h3 h10 h12 h7 h7 h9 h11 h5 h3 h5 "
    "h4 h3 h12 h5 h7 h7 h1 h9 h11 h8 h3 h5 h10 h2 h6 h12 h9 h7 "
    "h5 h11 h10 h3 h8 h11 h9 h2 h10 h12 h5 h7 h9 h11 h1 h9 h8")

assert len(APPENDIX_F_SEQ) == 53, len(APPENDIX_F_SEQ)
