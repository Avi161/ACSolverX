#!/usr/bin/env python3
"""
Adversarial, INDEPENDENT test suite for the acx-cert-v1 certificate verifier.

Built black-box from the certificate spec only (no engine internals read).
Exercises every STEP type with valid (must-pass) and violated (must-fail)
hand-built certificates, unit-tests the word/determinant primitives against an
independent oracle, tampers real certificates, and finally sweeps every real
certificate under results/stable_ac/ak3_stable_proof/**/certs/*.json.

Run:  .venv/bin/python3 tests/ak3sp_independent_test.py
Exit 0 iff all hand-built expectations hold.  Real-cert rejections are reported
as FINDINGS (not assumed valid).
"""

import glob
import itertools
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
VERIFIER_DIR = os.path.join(REPO, "experiments", "stable_ac", "ak3_stable_proof")
sys.path.insert(0, VERIFIER_DIR)

import independent_verifier as IV  # noqa: E402


# --------------------------------------------------------------------------- #
# tiny assertion harness
# --------------------------------------------------------------------------- #
PASS = 0
FAIL = 0
FAILURES = []


def check(cond, msg):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        FAILURES.append(msg)
        print(f"  [XX] {msg}")


def st(n, *rels):
    return {"n_gen": n, "relators": [list(r) for r in rels]}


def cert(states, steps, end_is_trivial=False):
    return {
        "certificate_version": "1",
        "name": "handbuilt",
        "claim": "test",
        "start": states[0],
        "end": states[-1],
        "states": states,
        "steps": steps,
        "end_is_trivial": end_is_trivial,
    }


def expect_ok(name, c):
    ok, errs = IV.verify(c)
    check(ok, f"{name}: expected OK but FAILED with {errs}")


def expect_fail(name, c, needle=None):
    ok, errs = IV.verify(c)
    if ok:
        check(False, f"{name}: expected FAIL but verifier accepted it")
        return
    if needle is not None:
        joined = " | ".join(errs)
        check(needle in joined,
              f"{name}: failed (good) but no error mentioned {needle!r}; got {errs}")
    else:
        check(True, name)


# --------------------------------------------------------------------------- #
# 0. independent oracle for the word primitives + determinant
# --------------------------------------------------------------------------- #
def naive_free_reduce(w):
    changed = True
    w = list(w)
    while changed:
        changed = False
        for i in range(len(w) - 1):
            if w[i] == -w[i + 1]:
                w = w[:i] + w[i + 2:]
                changed = True
                break
    return w


def naive_cyclic_reduce(w):
    w = naive_free_reduce(w)
    while len(w) >= 2 and w[0] == -w[-1]:
        w = w[1:-1]
        w = naive_free_reduce(w)
    return w


def brute_canonical(w):
    # independent min over rotations of w and inverse(w)
    if not w:
        return ()
    inv = [-x for x in reversed(w)]
    cands = []
    for base in (list(w), inv):
        for i in range(len(base)):
            cands.append(tuple(base[i:] + base[:i]))
    return min(cands)


def test_primitives():
    print("[primitives]")
    import random
    rng = random.Random(1234)
    for _ in range(3000):
        n = rng.randint(0, 8)
        w = [rng.choice([-3, -2, -1, 1, 2, 3]) for _ in range(n)]
        check(IV.free_reduce(w) == naive_free_reduce(w), f"free_reduce {w}")
        check(IV.cyclic_reduce(w) == naive_cyclic_reduce(w), f"cyclic_reduce {w}")
        check(IV.inverse(w) == [-x for x in reversed(w)], f"inverse {w}")
        # canonical is length-preserving: compare on freely-reduced words
        fw = IV.free_reduce(w)
        check(IV.canonical_relator(fw) == brute_canonical(fw), f"canonical {fw}")

    # canonical invariance under rotation & inversion
    for _ in range(2000):
        n = rng.randint(1, 8)
        w = IV.free_reduce([rng.choice([-3, -2, -1, 1, 2, 3]) for _ in range(n)])
        if not w:
            continue
        base = IV.canonical_relator(w)
        for i in range(len(w)):
            rot = w[i:] + w[:i]
            check(IV.canonical_relator(rot) == base, f"rot-invariance {w} @ {i}")
        check(IV.canonical_relator(IV.inverse(w)) == base, f"inv-invariance {w}")

    # determinant sanity vs known values
    check(IV.int_det([[1, 0], [0, 1]]) == 1, "det I2")
    check(IV.int_det([[2, 1], [1, 1]]) == 1, "det [[2,1],[1,1]]")
    check(IV.int_det([[1, 2], [3, 4]]) == -2, "det [[1,2],[3,4]]")
    check(IV.int_det([[0, 1], [1, 0]]) == -1, "det swap")
    check(IV.int_det([[2, 0], [0, 3]]) == 6, "det diag")
    check(IV.int_det([[3]]) == 3, "det 1x1")
    check(IV.int_det([[0, 1, 2], [1, 0, 1], [2, 3, 0]]) == 8, "det zero-pivot")


# --------------------------------------------------------------------------- #
# 1. VALID hand-built certificates for every step type (must PASS)
# --------------------------------------------------------------------------- #
def test_valid_steps():
    print("[valid step certs]")
    expect_ok("concat+1",
              cert([st(2, [1], [2]), st(2, [1, 2], [2])],
                   [{"type": "concat", "i": 0, "j": 1, "sign": 1}]))
    expect_ok("concat-1",
              cert([st(2, [1], [2]), st(2, [1, -2], [2])],
                   [{"type": "concat", "i": 0, "j": 1, "sign": -1}]))
    expect_ok("conjugation",
              cert([st(2, [1], [2]), st(2, [2, 1, -2], [2])],
                   [{"type": "conjugation", "i": 0, "g": 2}]))
    # conjugation result stored as a ROTATION (equivalence must accept)
    expect_ok("conjugation-rotated",
              cert([st(2, [1], [2]), st(2, [1, -2, 2], [2])],
                   [{"type": "conjugation", "i": 0, "g": 2}]))
    # invert (no-op modulo equivalence, must still pass)
    expect_ok("invert",
              cert([st(2, [1, 2], [2]), st(2, [-2, -1], [2])],
                   [{"type": "invert", "i": 0}]))
    expect_ok("relabel-perm",
              cert([st(2, [1, 2], [2]), st(2, [2, 1], [1])],
                   [{"type": "relabel", "perm": {"1": 2, "2": 1}, "invert": []}]))
    expect_ok("relabel-invert",
              cert([st(2, [1, 2], [2]), st(2, [1, -2], [-2])],
                   [{"type": "relabel", "perm": {"1": 1, "2": 2}, "invert": [2]}]))
    expect_ok("stabilize",
              cert([st(1, [1]), st(2, [1], [2, -1])],
                   [{"type": "stabilize", "z": 2, "w": [1]}]))
    expect_ok("eliminate+trivial",
              cert([st(2, [1, 2], [2]), st(1, [1])],
                   [{"type": "eliminate", "gen": 1, "ri": 0}],
                   end_is_trivial=True))
    expect_ok("eliminate-neg",
              cert([st(2, [-1, 2], [2]), st(1, [1])],
                   [{"type": "eliminate", "gen": 1, "ri": 0}],
                   end_is_trivial=True))
    # substitution supermove (junction-cancelling); result [1] reachable
    expect_ok("substitution",
              cert([st(2, [1, 2], [2]), st(2, [1], [2])],
                   [{"type": "substitution"}]))


# --------------------------------------------------------------------------- #
# 2. VIOLATED / precondition hand-built certificates (must FAIL)
# --------------------------------------------------------------------------- #
def test_violations():
    print("[violation certs]")
    expect_fail("concat-wrong",
                cert([st(2, [1], [2]), st(2, [1, 2, 2], [2])],
                     [{"type": "concat", "i": 0, "j": 1, "sign": 1}]),
                needle="concat")
    expect_fail("concat-i==j",
                cert([st(2, [1, 2], [2]), st(2, [1, 2], [2])],
                     [{"type": "concat", "i": 0, "j": 0, "sign": 1}]),
                needle="i != j")
    expect_fail("conjugation-wrong",
                cert([st(2, [1], [2]), st(2, [2, 1, 2], [2])],
                     [{"type": "conjugation", "i": 0, "g": 2}]),
                needle="conjugation")
    expect_fail("eliminate-twice",
                cert([st(2, [1, 1, -2], [2, -1]), st(1, [1])],
                     [{"type": "eliminate", "gen": 1, "ri": 0}]),
                needle="occurs 2 times")
    # relator [1] genuinely does not contain generator 2 -> 0 occurrences
    expect_fail("eliminate-absent",
                cert([st(2, [1], [2]), st(1, [1])],
                     [{"type": "eliminate", "gen": 2, "ri": 0}]),
                needle="occurs 0 times")
    expect_fail("stabilize-badz",
                cert([st(1, [1]), st(2, [1], [2, -1])],
                     [{"type": "stabilize", "z": 3, "w": [1]}]),
                needle="stabilize z")
    expect_fail("stabilize-badw",
                cert([st(1, [1]), st(2, [1], [2, -1])],
                     [{"type": "stabilize", "z": 2, "w": [2]}]),
                needle="out of range")
    expect_fail("relabel-nonbijection",
                cert([st(2, [1, 2], [2]), st(2, [1, 1], [1])],
                     [{"type": "relabel", "perm": {"1": 1, "2": 1}, "invert": []}]),
                needle="bijection")
    expect_fail("det-tamper",
                cert([st(2, [1], [2]), st(2, [1, 1], [2])],
                     [{"type": "concat", "i": 0, "j": 1, "sign": 1}]),
                needle="det")
    expect_fail("unbalanced",
                cert([st(2, [1], [2]),
                      {"n_gen": 2, "relators": [[1]]}],
                     [{"type": "concat", "i": 0, "j": 1, "sign": 1}]),
                needle="unbalanced")
    expect_fail("letter-oor",
                cert([{"n_gen": 1, "relators": [[2]]}, st(1, [1])],
                     [{"type": "invert", "i": 0}]),
                needle="out of range")
    expect_fail("empty-relator",
                cert([{"n_gen": 1, "relators": [[]]}, st(1, [1])],
                     [{"type": "invert", "i": 0}]),
                needle="empty")
    expect_fail("trivial-lie",
                cert([st(2, [1], [2]), st(2, [1, 2], [2])],
                     [{"type": "concat", "i": 0, "j": 1, "sign": 1}],
                     end_is_trivial=True),
                needle="not the trivial presentation")
    # invert step but a DIFFERENT (untouched) relator was corrupted
    expect_fail("invert-other-corrupt",
                cert([st(2, [1, 2], [2]), st(2, [-2, -1], [1, 1, -2])],
                     [{"type": "invert", "i": 0}]))
    # substitution to an UNREACHABLE single-relator target
    expect_fail("substitution-unreachable1",
                cert([st(2, [1, 2], [2]), st(2, [1, 2, 2], [2])],
                     [{"type": "substitution"}]),
                needle="substitution")
    # substitution to a target differing in TWO relators (impossible in one move)
    expect_fail("substitution-unreachable2",
                cert([st(2, [1, 2], [2]), st(2, [1], [1])],
                     [{"type": "substitution"}]),
                needle="substitution")
    # states/steps length mismatch
    expect_fail("length-mismatch",
                cert([st(2, [1], [2])],
                     [{"type": "invert", "i": 0}]),
                needle="len(states)")


# --------------------------------------------------------------------------- #
# 3. tamper a REAL certificate: flip an interior letter of a length>=3 relator
#    in a middle state -> must be rejected.
# --------------------------------------------------------------------------- #
def test_real_tamper():
    print("[real-cert tamper]")
    targets = [
        os.path.join(REPO, "results/stable_ac/ak3_stable_proof/catalog/certs/1d001f.json"),
        os.path.join(REPO, "results/stable_ac/ak3_stable_proof/certs/laneB_M3corr_hero8_500.json"),
    ]
    for path in targets:
        with open(path) as f:
            base = json.load(f)
        ok, errs = IV.verify(base)
        check(ok, f"tamper-baseline {os.path.basename(path)}: real cert should pass; {errs}")

        tampered = json.loads(json.dumps(base))
        states = tampered["states"]
        done = False
        for si in range(1, len(states) - 1):
            for rel in states[si]["relators"]:
                if len(rel) >= 3:
                    j = 1  # interior position (not first/last)
                    orig = rel[j]
                    rel[j] = -orig
                    if rel[j] != orig:
                        done = True
                        break
            if done:
                break
        check(done, f"tamper {os.path.basename(path)}: found a length>=3 middle relator")
        if done:
            ok2, _ = IV.verify(tampered)
            check(not ok2,
                  f"tamper {os.path.basename(path)}: verifier must REJECT the tamper")


# --------------------------------------------------------------------------- #
# 4. sweep every real certificate; report verdicts (findings, not assumptions)
# --------------------------------------------------------------------------- #
def sweep_real_certs():
    print("[real-cert sweep]")
    patterns = [
        os.path.join(REPO, "results/stable_ac/ak3_stable_proof/certs/*.json"),
        os.path.join(REPO, "results/stable_ac/ak3_stable_proof/catalog/certs/*.json"),
    ]
    files = sorted(itertools.chain.from_iterable(glob.glob(p) for p in patterns))
    verdicts = {}
    findings = []
    for path in files:
        with open(path) as f:
            c = json.load(f)
        ok, errs = IV.verify(c)
        verdicts[os.path.relpath(path, REPO)] = (ok, errs)
        tag = "OK  " if ok else "FAIL"
        print(f"  {tag} {os.path.relpath(path, REPO)}")
        if not ok:
            findings.append((path, errs))
            for e in errs:
                print(f"        - {e}")
    return verdicts, findings


# --------------------------------------------------------------------------- #
def main():
    test_primitives()
    test_valid_steps()
    test_violations()
    test_real_tamper()
    verdicts, findings = sweep_real_certs()

    print("\n==================== SUMMARY ====================")
    print(f"hand-built / primitive assertions: {PASS} passed, {FAIL} failed")
    n_ok = sum(1 for ok, _ in verdicts.values() if ok)
    print(f"real certificates swept: {len(verdicts)}  ({n_ok} OK, "
          f"{len(verdicts) - n_ok} rejected-by-independent-verifier)")
    if findings:
        print("\nFINDINGS (real certs rejected by the INDEPENDENT verifier):")
        for path, errs in findings:
            print(f"  {os.path.relpath(path, REPO)}")
            for e in errs:
                print(f"    - {e}")
    if FAILURES:
        print("\nFAILED ASSERTIONS:")
        for m in FAILURES:
            print(f"  - {m}")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
