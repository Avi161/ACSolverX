"""Probe: replay the Appendix-F 53-move path under all 4 order/inverse conventions,
from both endpoints, and report which (if any) lands on the other endpoint.

Endpoint match is checked at three strictness levels:
  exact   — relators equal as ordered pairs of words (after free reduction)
  cyclic  — each relator equal up to rotation+inversion (ordered pair)
  canon   — unordered, rotation+inversion (canonical_state_key equality)
  relabel — canon up to signed generator relabeling
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hmoves import AK3, APPENDIX_F_SEQ, P25, replay
from presentation import (
    abelianization_det, canonical_state_key, canonical_word,
    relabel_canonical_key, total_length, word_bytes,
)


def match_level(state, target):
    if [list(r) for r in state] == [list(r) for r in target]:
        return "exact"
    if all(word_bytes(canonical_word(a)) == word_bytes(canonical_word(b))
           for a, b in zip(state, target)):
        return "cyclic"
    if canonical_state_key(state) == canonical_state_key(target):
        return "canon"
    if relabel_canonical_key(state, 2) == relabel_canonical_key(target, 2):
        return "relabel"
    return None


def run(tag, start, target, inverse, reverse):
    states, _ = replay(start, APPENDIX_F_SEQ, inverse=inverse, reverse=reverse)
    end = states[-1]
    dets = {abelianization_det(s, 2) for s in states}
    lens = [total_length(s) for s in states]
    m = match_level(end, target)
    print(f"{tag:34} end_len={total_length(end):3d} max_len={max(lens):3d} "
          f"dets={sorted(dets)} match={m}")
    return m, states


def main():
    print(f"P25 total len = {total_length(P25)}, AK3 total len = {total_length(AK3)}")
    print(f"|det| P25 = {abs(abelianization_det(P25, 2))}, AK3 = {abs(abelianization_det(AK3, 2))}")
    combos = [
        ("P25 -> fwd order, fwd moves", P25, AK3, False, False),
        ("P25 -> rev order, inv moves", P25, AK3, True, True),
        ("P25 -> fwd order, inv moves", P25, AK3, True, False),
        ("P25 -> rev order, fwd moves", P25, AK3, False, True),
        ("AK3 -> fwd order, fwd moves", AK3, P25, False, False),
        ("AK3 -> rev order, inv moves", AK3, P25, True, True),
        ("AK3 -> fwd order, inv moves", AK3, P25, True, False),
        ("AK3 -> rev order, fwd moves", AK3, P25, False, True),
    ]
    hits = []
    for tag, s, t, inv, rev in combos:
        m, _ = run(tag, s, t, inv, rev)
        if m:
            hits.append((tag, m))
    print()
    if hits:
        for tag, m in hits:
            print(f"HIT: {tag}  (match level: {m})")
    else:
        print("NO MATCH under any convention — move semantics or transcription wrong.")


if __name__ == "__main__":
    main()
