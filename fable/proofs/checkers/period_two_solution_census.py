"""W2: complete bounded census of period-two quotient solutions.

The hardest depth-four signature's recurrence, imaged in Q = <c,t | c^2> =
C2 * Z (see literature/proofs/AK3_DEPTH4_PERIOD_TWO_WITNESS.md):

    R = A h0 B^-1 h0^-1        A = t^-2 c t^-2 c t^2 c
    S = B h1 R^-1 h1^-1        B = t^-3 c t c t c
    U = R h2 S^-1 h2^-1
    Z = U^-1 h3 S h3^-1,   solution iff Z lies in Cl_Q(t).

A free-group solution of the depth-four class projects to a solution
(h0..h3) in Q^4. The codex lift tower (AK3_DEPTH4_PERIOD_TWO_FULL_LIFT_
BOUNDARY.md eq. 1.10) targets the single known witness; whether OTHER
essential quotient solutions exist bounds what a completed noncancellation
theorem can conclude. Gauge: h_i matters only through the conjugate it
produces, i.e. through the chain (R, S, U) plus the final conjugator class;
h_i -> h_i * (centralizer element) is invisible. So an ESSENTIAL solution is
a distinct chain (R, S, U).

Census design (complete for its caps, not a budgeted search):
  R ranges over A * Cl(B^-1) with len(R) <= CAP,
  S over B * Cl(R^-1) with len(S) <= CAP,
  U over R * Cl(S^-1) with len(U) <= CAP,
  final test: exists g with len(g) <= GPAD such that U * g t g^-1 is
  conjugate to S (exact cyclic-form equality) — equivalently
  Z = U^-1 h3 S h3^-1 in Cl(t).

Conjugates of a cyclically reduced w are exactly u * rot * u^-1 (reduced)
over letter rotations rot and arbitrary u; enumeration pads u over the ball
of radius (CAP + |base| - |cyc(w)|)//2 and dedupes, which is complete for
the length cap by the free-product normal form theorem.

Positive control (falsifiable): the witness chain
    R = TTctcTctc-ish, S, U from the witness document
must be found. Caps are printed with every claim; the census proves
nothing beyond its caps.

Words: strings over {c, t, T}; reduction cancels cc, tT, Tt.
"""
from __future__ import annotations

import json
import sys

CAP = 12      # max reduced length of each of R, S, U (witness: 9, 11, 8)
GPAD = 5      # max length of the final conjugator g (witness: g = t^2? see run)

_BALL_CACHE = {}


def reduce_w(s):
    out = []
    for ch in s:
        if out and (
            (out[-1] == "c" and ch == "c")
            or (out[-1] == "t" and ch == "T")
            or (out[-1] == "T" and ch == "t")
        ):
            out.pop()
        else:
            out.append(ch)
    return "".join(out)


def inv(s):
    return s[::-1].translate(str.maketrans("tT", "Tt"))


def mul(*ws):
    out = ""
    for w in ws:
        out = reduce_w(out + w)
    return out


def cyc_reduce(s):
    s = reduce_w(s)
    while len(s) >= 2 and reduce_w(s[-1] + s[0]) == "":
        s = reduce_w(s[1:-1])
    return s


def cyc_form(s):
    """Canonical form of the conjugacy class: lexicographically least letter
    rotation of the cyclic reduction (all rotations of a cyclically reduced
    word over this alphabet are reduced except possibly t-run seams, which
    reduce_w repairs)."""
    s = cyc_reduce(s)
    if not s:
        return ""
    rots = {reduce_w(s[i:] + s[:i]) for i in range(len(s))}
    return min(rots)


def ball(radius):
    """All reduced words of length <= radius (cached)."""
    if radius in _BALL_CACHE:
        return _BALL_CACHE[radius]
    out = [""]
    frontier = [""]
    for _ in range(radius):
        nxt = []
        for w in frontier:
            for ch in "ctT":
                v = reduce_w(w + ch)
                if len(v) == len(w) + 1:
                    nxt.append(v)
        frontier = nxt
        out.extend(frontier)
    _BALL_CACHE[radius] = out
    return out


def conjugates(base, max_len):
    """All reduced conjugates of `base` with length <= max_len (complete)."""
    core = cyc_reduce(base)
    rots = {reduce_w(core[i:] + core[:i]) for i in range(len(core))}
    pad = max(0, (max_len - len(core)) // 2 + 1)
    seen = set()
    for u in ball(pad):
        ui = inv(u)
        for r in rots:
            w = mul(u, r, ui)
            if len(w) <= max_len:
                seen.add(w)
    return seen


A = "TTcTTcttc"
B = "TTTctctc"


def main():
    a_chk = mul("TT", "c", "TT", "c", "tt", "c")
    b_chk = mul("TTT", "c", "t", "c", "t", "c")
    assert a_chk == A and b_chk == B, (a_chk, b_chk)
    assert cyc_form("t") != cyc_form("T"), "t and T must be non-conjugate"

    solutions = []
    n_r = n_s = n_u = 0
    gballs = [(g, inv(g)) for g in ball(GPAD)]

    r_set = sorted(
        {mul(A, x) for x in conjugates(inv(B), CAP + len(A))}
    )
    r_set = [r for r in r_set if 0 < len(r) <= CAP]
    n_r = len(r_set)
    for R in r_set:
        s_set = sorted(
            {mul(B, y) for y in conjugates(inv(R), CAP + len(B))}
        )
        s_set = [s for s in s_set if 0 < len(s) <= CAP]
        n_s += len(s_set)
        for S in s_set:
            cf_S = cyc_form(S)
            u_set = sorted(
                {mul(R, w) for w in conjugates(inv(S), CAP + len(R))}
            )
            u_set = [u for u in u_set if 0 < len(u) <= CAP]
            n_u += len(u_set)
            for U in u_set:
                for g, gi in gballs:
                    X = mul(U, g, "t", gi)
                    if cyc_form(X) == cf_S:
                        solutions.append(
                            {"R": R, "S": S, "U": U, "g": g}
                        )
                        break
    chains = sorted({(s["R"], s["S"], s["U"]) for s in solutions})
    witness = ("TTctcTctc", "TTTcttcTctt", "TTcttcTc")
    elliptic_hits = [ch for ch in chains if cyc_form(ch[1]) == "c"]
    print(json.dumps({
        "caps": {"CAP": CAP, "GPAD": GPAD},
        "counts": {"R": n_r, "S_total": n_s, "U_total": n_u},
        "solutions": len(solutions),
        "essential_chains": len(chains),
        "witness_found": witness in chains,
        "elliptic_S_hits": len(elliptic_hits),
    }))
    for cch in chains:
        print(json.dumps({"chain": list(cch),
                          "is_witness": cch == witness}))
    if witness not in chains:
        print("CONTROL FAILURE: witness chain not found — census enumeration "
              "is incomplete or the witness words are mistranscribed. "
              "No conclusion may be drawn.")
        return 2
    if elliptic_hits:
        print("CONSISTENCY FAILURE: elliptic-S hit contradicts the proved "
              "elliptic obstruction — census or obstruction is wrong.")
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
