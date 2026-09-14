"""Small exact coupled-power identities; no presentation search."""

from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter

from ac_words import Factor, Trace, canon, exponent, inv, red, replay


def power(word, n):
    return red((word if n >= 0 else inv(word)) * abs(n))


def corridor(a, t, m, n, k, p, q):
    r = red(inv(t) + power(a, m) + t + power(a, -n))
    s = red(power(t, -k - 1) + power(a, p) + power(t, k) + power(a, q))
    b = red(power(t, -k) + a + power(t, k))
    trace = Trace((r, s))
    trace.conjugate(0, power(t, k))
    rk = trace.pair[0]
    tail = red(power(t, -k) + power(a, -n) + power(t, k))
    trace.append_factors(0, (Factor(-1, rk), Factor(1, tail)))
    expected = red(power(a, -q) + power(b, m) + power(a, q) + power(b, -n))
    assert trace.pair == [expected, s]
    assert replay((r, s), trace.moves) == trace.pair
    return {
        "parameters": {"a": a, "t": t, "m": m, "n": n, "k": k, "p": p, "q": q},
        "input": [r, s], "output": trace.pair,
        "canonical_donor": canon(expected), "moves": trace.moves,
        "move_count": len(trace.moves),
        "relator_uses": 2,
    }


def substitute(word, x, y):
    images = {"x": x, "X": inv(x), "y": y, "Y": inv(y)}
    return red("".join(images[c] for c in word))


def cyclic_product_normal(word, n):
    stack = []
    for c in word:
        gen, e = ("x", 1 if c == "x" else -1) if c.lower() == "x" else ("y", 1 if c == "y" else -1)
        modulus = 2 if gen == "x" else n
        if stack and stack[-1][0] == gen:
            e += stack.pop()[1]
        e %= modulus
        if e:
            stack.append((gen, e))
    while len(stack) > 1 and stack[0][0] == stack[-1][0]:
        gen, e = stack.pop(0)
        e = (e + stack.pop()[1]) % (2 if gen == "x" else n)
        if e:
            stack.insert(0, (gen, e))
    if not stack:
        return []
    candidates = [stack[i:] + stack[:i] for i in range(len(stack))]
    return min(candidates)


def primitive(p, q):
    """A cyclic Christoffel representative with signed exponent vector (p,q)."""
    if not p:
        assert abs(q) == 1
        return "x" if q > 0 else "X"
    if not q:
        assert abs(p) == 1
        return "y" if p > 0 else "Y"
    a, b = abs(p), abs(q)
    assert a >= b
    return "".join(("x" if q > 0 else "X") + ("y" if p > 0 else "Y") * (((i + 1) * a // b) - (i * a // b)) for i in range(b))


def torus_boundary(m, k):
    n = 2 * k + 1
    r = "Y" + "x" * (m + 1) + "y" + "X" * m
    s = "Y" * (k + 1) + "x" + "y" * k + "x"
    mapped_r = substitute(r, "x" + "Y" * k, "y")
    mapped_s = substitute(s, "x" + "Y" * k, "y")
    assert red("y" * (k + 1) + mapped_s + "Y" * (k + 1)) == "xx" + "Y" * n
    assert 2 * exponent(mapped_r, "y") + n * exponent(mapped_r, "x") == 1
    normal = cyclic_product_normal(mapped_r, n)
    runs = [-k] * m + [1] + [-(k + 1)] * (m - 1) + [-(n + 1)]
    expected = "".join("x" + power("y", e) for e in runs)
    assert cyclic_product_normal(expected, n) == normal
    u_count = sum(gen == "x" for gen, e in normal)
    assert u_count == 2 * m + 1
    candidates = []
    for q in (-u_count, u_count):
        p = (1 - n * q) // 2
        assert 2 * p + n * q == 1
        word = primitive(p, q)
        candidates.append({"t_exponent": p, "u_exponent": q, "word": word,
                           "same_free_product_conjugacy_class": cyclic_product_normal(word, n) == normal})
    hit = any(row["same_free_product_conjugacy_class"] for row in candidates)
    assert hit == (m == 1 and k == 1)
    return {"m": m, "k": k, "torus_order": n, "mapped_r": mapped_r,
            "mapped_s": mapped_s, "cyclic_normal": normal, "run_exponents": runs,
            "candidate_primitives": candidates, "primitive_projection_hit": hit}


def main():
    start = perf_counter()
    cases = []
    for a, t in (("x", "y"), ("X", "y"), ("y", "X")):
        for k in (1, 2, 3):
            for p, q in ((1, 1), (1, -1), (2, 1), (-2, -3)):
                cases.append(corridor(a, t, 3, 2, k, p, q))
    roots = {"aca_116": corridor("X", "y", 3, 2, 2, 1, 1),
             "aca_117": corridor("X", "y", 3, 2, 2, 1, -1),
             "aca_9": corridor("X", "y", 3, 2, 2, 2, 1)}
    torus = [torus_boundary(m, k) for m in range(1, 8) for k in range(1, 7)]
    report = {"kind": "word_identity_and_normal_form_checks_no_search",
              "corridor_case_count": len(cases), "corridor_cases": cases,
              "exact_roots": roots, "torus_cases": torus,
              "wall_seconds": perf_counter() - start}
    output = Path(__file__).with_name("coupled_power_checks.json")
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"output": str(output), "corridor_cases": len(cases),
                      "torus_cases": len(torus), "wall_seconds": report["wall_seconds"],
                      "roots": {k: {"output": v["output"], "moves": v["move_count"]} for k, v in roots.items()}}))


if __name__ == "__main__":
    main()
