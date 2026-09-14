"""Independent certificate replayer for ``capbfs`` / ``capbfs_reference`` output.

Reads the JSON (or JSON-lines) a search wrote and replays the recorded path
with plain Python string operations on the ``xXyY`` alphabet.  It shares no code
with either engine -- no numba, no import of ``capbfs``, not even of
``capbfs_reference`` -- so that a bug in the search cannot certify itself.

For every step it checks

  * the move descriptor is well formed: ``j == 1 - i``, ``e`` in ``{1, -1}``,
    rotation offsets in range, the connector ``w`` freely reduced over ``xXyY``;
  * the connector obeys the cap budget ``2|w| <= c - |r_i| - |r_j|``;
  * ``R = cyc_reduce(rot_a(r_i) . w . rot_p(r_j**e) . w**-1)`` has
    ``1 <= |R| <= c``;
  * the canonical form of ``{R, r_j}`` is the next recorded state;

and finally that every relator of every recorded state is nonempty and of
length ``<= c``, that the first state is the canonical form of the declared
initial presentation, and that the last state is the trivial presentation
``{x, y}``.

    python verify_path.py out.json [more.json ...]
    python verify_path.py runs.jsonl

Exit status: 0 when every solved result verified, 1 on any failure, 2 without
arguments, and 3 when no input contained a solved result at all -- a truncated
or edited batch must not pass silently.  ``--allow-empty`` turns 3 into 0 for
batches that are expected to be entirely unsolved (closure tables).
"""

from __future__ import annotations

import json
import sys

ALPHA = "xXyY"
#: the fixed letter order the engines canonicalise under: x < X < y < Y
_RANK = {c: i for i, c in enumerate(ALPHA)}


class VerificationError(Exception):
    pass


def _inv(w):
    return w[::-1].swapcase()


def _free_reduce(w):
    out = []
    for c in w:
        if out and out[-1] == c.swapcase():
            out.pop()
        else:
            out.append(c)
    return "".join(out)


def _cyc_reduce(w):
    w = _free_reduce(w)
    while len(w) >= 2 and w[0] == w[-1].swapcase():
        w = w[1:-1]
    return w


def _rot(w, k):
    if not w:
        return w
    k %= len(w)
    return w[k:] + w[:k]


def _rank(w):
    return [_RANK[c] for c in w]


def _canon_rel(w):
    if not w:
        raise VerificationError("empty relator")
    best = None
    for u in (w, _inv(w)):
        for k in range(len(u)):
            r = _rot(u, k)
            key = _rank(r)
            if best is None or key < best[0]:
                best = (key, r)
    return best[1]


def _canon_pair(r1, r2):
    a, b = _canon_rel(_cyc_reduce(r1)), _canon_rel(_cyc_reduce(r2))
    if (len(a), _rank(a)) > (len(b), _rank(b)):
        a, b = b, a
    return [a, b]


def _check_word(w, what):
    for c in w:
        if c not in _RANK:
            raise VerificationError("%s has a letter outside xXyY: %r" % (what, w))
    if _free_reduce(w) != w:
        raise VerificationError("%s is not freely reduced: %r" % (what, w))


def verify_result(res):
    """Verify one search result dict.  Returns a report dict or raises."""
    if not res.get("solved"):
        raise VerificationError("result is not marked solved; nothing to verify")
    cap = int(res["cap"])
    path = res["path"]
    states = [list(s) for s in res["path_states"]]
    if len(states) != len(path) + 1:
        raise VerificationError(
            "path_states has %d entries, expected %d" % (len(states), len(path) + 1))

    declared = _canon_pair(res["initial"][0], res["initial"][1])
    if states[0] != declared:
        raise VerificationError(
            "first path state %r is not the canonical initial state %r"
            % (states[0], declared))

    for t, st in enumerate(states):
        for r in st:
            _check_word(r, "state %d relator" % t)
            if not r:
                raise VerificationError("state %d has an empty relator" % t)
            if len(r) > cap:
                raise VerificationError(
                    "state %d relator %r exceeds cap %d" % (t, r, cap))
            if _cyc_reduce(r) != r:
                raise VerificationError(
                    "state %d relator %r is not cyclically reduced" % (t, r))
        if _canon_pair(st[0], st[1]) != st:
            raise VerificationError("state %d %r is not in canonical form" % (t, st))

    for t, mv in enumerate(path):
        st = states[t]
        i, j, e, a, p, w = mv["i"], mv["j"], mv["e"], mv["a"], mv["p"], mv["w"]
        if i not in (0, 1) or j != 1 - i:
            raise VerificationError("step %d: bad relator indices %r/%r" % (t, i, j))
        if e not in (1, -1):
            raise VerificationError("step %d: bad sign %r" % (t, e))
        ri, rj = st[i], st[j]
        if not (0 <= a < len(ri)):
            raise VerificationError("step %d: rotation a=%d out of range" % (t, a))
        if not (0 <= p < len(rj)):
            raise VerificationError("step %d: rotation p=%d out of range" % (t, p))
        _check_word(w, "step %d connector" % t)
        budget = (cap - len(ri) - len(rj)) // 2
        if len(w) > max(budget, 0) or (budget < 0 and w):
            raise VerificationError(
                "step %d: connector %r longer than the budget %d" % (t, w, budget))
        oj = rj if e == 1 else _inv(rj)
        product = _rot(ri, a) + w + _rot(oj, p) + _inv(w)
        new = _cyc_reduce(product)
        if not (1 <= len(new) <= cap):
            raise VerificationError(
                "step %d: new relator %r has length %d, outside [1, %d]"
                % (t, new, len(new), cap))
        got = _canon_pair(new, rj)
        if got != states[t + 1]:
            raise VerificationError(
                "step %d: move gives %r but the certificate records %r"
                % (t, got, states[t + 1]))

    if states[-1] != ["x", "y"]:
        raise VerificationError(
            "path ends at %r, not the trivial presentation ['x', 'y']" % (states[-1],))

    return {
        "ok": True,
        "initial": res["initial"],
        "cap": cap,
        "steps": len(path),
        "max_relator_length": max(len(r) for st in states for r in st),
    }


def verify_file(path):
    """Verify every solved result in a ``.json`` or ``.jsonl`` file."""
    reports = []
    with open(path) as fh:
        text = fh.read().strip()
    if not text:
        return reports
    if text.lstrip().startswith("["):
        blobs = json.loads(text)
    elif "\n" in text.strip() and not text.lstrip().startswith("{\n"):
        blobs = [json.loads(line) for line in text.splitlines() if line.strip()]
    else:
        try:
            blobs = [json.loads(text)]
        except json.JSONDecodeError:
            blobs = [json.loads(line) for line in text.splitlines() if line.strip()]
    for blob in blobs:
        if blob.get("solved"):
            reports.append(verify_result(blob))
    return reports


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    allow_empty = "--allow-empty" in argv
    argv = [a for a in argv if a != "--allow-empty"]
    if not argv:
        print("usage: python verify_path.py [--allow-empty] out.json [more.json ...]")
        return 2
    rc = 0
    verified = 0
    for path in argv:
        try:
            reports = verify_file(path)
        except VerificationError as exc:
            print("FAIL %s: %s" % (path, exc))
            rc = 1
            continue
        if not reports:
            print("NONE %s: no solved results to verify" % path)
            continue
        verified += len(reports)
        for rep in reports:
            print("OK   %s: %s cap=%d steps=%d maxlen=%d"
                  % (path, "/".join(rep["initial"]), rep["cap"], rep["steps"],
                     rep["max_relator_length"]))
    if rc == 0 and verified == 0 and not allow_empty:
        print("FAIL nothing verified: no input contained a solved result "
              "(pass --allow-empty if that is expected)")
        return 3
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
