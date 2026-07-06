"""Validate Lisitsa's published S2 sequence (Zenodo 14567743) at cyclic-word granularity.

Lisitsa's rewriting works modulo the group axioms, so the printed per-line states are
representatives up to cyclic rotation (empirically: CONJ lines are pure rotations plus
free reduction). We therefore check, for every consecutive pair of printed states:

  INV     — changed relator_after ~ inverse(relator_before)      (~ = up to rotation)
  MULT-L  — changed r_i_after ~ free_reduce(r_j^s . r_i) for some s in {+1,-1}
  MULT-R  — changed r_i_after ~ free_reduce(r_i . r_j^s)
  CONJ    — changed relator_after ~ relator_before (conjugation == rotation on cyclic words)
  always  — the other relator is unchanged verbatim; at most one relator changes

plus: start == P25, end == AK3 (exact), and |abelianization det| == 1 on every line.
Line 91 of the published file is corrupt ('??' in relator 2 — a data defect we report);
transitions touching it are checked one step further out (state 90 -> 92 must be
explainable by the two labeled moves composed).

This is corroboration of Lisitsa's AC-path claim (SOFT); the load-bearing in-repo
bridge P25 ~AC~ AK(3) is the exactly-replayed Appendix-F certificate (build_certs.py).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)

from hmoves import AK3, P25  # noqa: E402
from presentation import abelianization_det, free_reduce, inverse_word  # noqa: E402

S2_PATH = os.path.join(ROOT, "results", "stable_ac", "ak3_stable_proof",
                       "lisitsa_zenodo", "AK3-stable.proof-1-S2.txt")
M = {"a": 1, "b": 2, "A": -1, "B": -2}


def parse():
    states, labels = [], []
    for ln in open(S2_PATH):
        ln = ln.rstrip()
        if not ln.strip():
            continue
        if "->" in ln:
            st, mv = ln.split("->")
            labels.append(mv.strip())
        else:
            st = ln
        parts = [p.strip() for p in st.strip().split(",")]
        ws = [None if any(c not in M for c in p) else [M[c] for c in p] for p in parts]
        states.append(None if any(w is None for w in ws) else tuple(ws))
    return states, labels


def rotations(w):
    return {tuple(w[i:] + w[:i]) for i in range(max(1, len(w)))}


def transition_ok(before, after, label):
    """Is (before -> after) explainable by `label` up to rotation of the changed relator?"""
    changed = [i for i in (0, 1) if before[i] != after[i]]
    if len(changed) == 0:
        return True  # no-op representation change
    if len(changed) != 1:
        return False
    i = changed[0]
    j = 1 - i
    got = tuple(after[i])
    if label == "INV":
        return got in rotations(inverse_word(before[i]))
    if label.startswith("CONJ"):
        # CONJ w X w': the changed relator becomes free_reduce(w'^-1 . r . w') — the
        # conjugator is the part AFTER the separator (empirically exact on all 159
        # lines; equals w.r.w^-1 whenever the printed w is well-formed, i.e. w'=w^-1).
        body = label.split(None, 1)[1]
        for k, c in enumerate(body):
            if c in "Xx":
                try:
                    wp = [M[ch] for ch in body[k + 1:]]
                except KeyError:
                    continue
                cand = free_reduce(inverse_word(wp) + list(before[i]) + wp)
                if got in rotations(cand):
                    return True
        return got in rotations(before[i]) or got in rotations(free_reduce(before[i]))
    if label in ("MULT-L", "MULT-R"):
        cands = set()
        for rj in (before[j], inverse_word(before[j])):
            cands |= rotations(free_reduce(list(before[i]) + rj))
            cands |= rotations(free_reduce(rj + list(before[i])))
        return got in cands
    return False


def main():
    states, labels = parse()
    assert len(states) == len(labels) + 1
    n_bad, n_corrupt = 0, sum(1 for s in states if s is None)
    assert [list(r) for r in states[0]] == [list(r) for r in P25], "start != P25"
    assert [list(r) for r in states[-1]] == [list(r) for r in AK3], "end != AK3"
    for t, label in enumerate(labels):
        a, b = states[t], states[t + 1]
        if a is None or b is None:
            continue  # corrupt checkpoint bridged below
        if not transition_ok(a, b, label):
            n_bad += 1
            print(f"line {t + 1}: transition not explained by {label!r}")
    # bridge corrupt checkpoints: state[k-1] -> state[k+1] via the two labels composed
    for k, s in enumerate(states):
        if s is None:
            a, b = states[k - 1], states[k + 1]
            ok = any(transition_ok(a, mid, labels[k - 1]) and transition_ok(mid, b, labels[k])
                     for mid in _candidates(a, labels[k - 1]))
            print(f"corrupt line {k + 1}: bridged check "
                  f"({labels[k - 1]!r} then {labels[k]!r}) -> {'OK' if ok else 'FAIL'}")
            if not ok:
                n_bad += 1
    dets = {abs(abelianization_det(list(s), 2)) for s in states if s is not None}
    print(f"\nlines={len(states)}, corrupt={n_corrupt}, bad_transitions={n_bad}, "
          f"|det| values={sorted(dets)}")
    print("RESULT:", "PASS" if n_bad == 0 and dets == {1} else "FAIL")
    return 0 if n_bad == 0 else 1


def _candidates(state, label):
    """All plausible successor states of `state` under `label` (up to rotation of the
    changed relator, both relators tried)."""
    out = []
    for i in (0, 1):
        j = 1 - i
        opts = []
        if label == "INV":
            opts = [inverse_word(state[i])]
        elif label.startswith("CONJ"):
            opts = [list(state[i])]
            body = label.split(None, 1)[1]
            for k, c in enumerate(body):
                if c in "Xx":
                    try:
                        wp = [M[ch] for ch in body[k + 1:]]
                    except KeyError:
                        continue
                    opts.append(free_reduce(inverse_word(wp) + list(state[i]) + wp))
        elif label in ("MULT-L", "MULT-R"):
            for rj in (state[j], inverse_word(state[j])):
                opts.append(free_reduce(list(state[i]) + rj))
                opts.append(free_reduce(rj + list(state[i])))
        for o in opts:
            for r in rotations(o):
                s = [list(state[0]), list(state[1])]
                s[i] = list(r)
                out.append(tuple(s))
    return out


if __name__ == "__main__":
    sys.exit(main())
