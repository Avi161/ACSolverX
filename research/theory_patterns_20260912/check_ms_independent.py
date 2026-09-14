"""Independent, search-free audit of the MS residue certificate constructor."""

from __future__ import annotations

import hashlib
import csv
import itertools
import json
import time
from pathlib import Path

import ac_words
import ms_family_verify as author


HERE = Path(__file__).resolve().parent
ENCODE = {"x": 1, "X": -1, "y": 2, "Y": -2}
DECODE = {v: k for k, v in ENCODE.items()}


def require(value, detail):
    if not value:
        raise AssertionError(detail)


def reduce_int(symbols):
    result = []
    for symbol in symbols:
        if result and result[-1] == -symbol:
            result.pop()
        else:
            result.append(symbol)
    return tuple(result)


def parse(word):
    return reduce_int(ENCODE[c] for c in word)


def invert(word):
    return tuple(-v for v in reversed(word))


def product(*words):
    return reduce_int(itertools.chain.from_iterable(words))


def word(symbols):
    return "".join(DECODE[v] for v in symbols)


def power(c, n):
    return (c if n >= 0 else c.swapcase()) * abs(n)


def independent_replay(initial, moves):
    require(len(initial) == 2, "wrong rank")
    pair = [parse(w) for w in initial]
    peak = max(map(len, pair))
    for op, target, arg in moves:
        require(type(target) is int and target in (0, 1), "invalid target")
        if op == "invert":
            require(arg is None, "invalid inversion argument")
            pair[target] = invert(pair[target])
        elif op == "multiply":
            require(type(arg) is int and arg == 1 - target, "invalid donor")
            pair[target] = product(pair[target], pair[arg])
        elif op == "conjugate":
            require(arg in ENCODE, "conjugator is not one generator")
            c = (ENCODE[arg],)
            pair[target] = product(invert(c), pair[target], c)
        else:
            raise AssertionError("not an ordinary AC move: " + str(op))
        peak = max(peak, *(len(w) for w in pair))
    return [word(w) for w in pair], peak


def external_moves(moves):
    result = []
    for op, target, arg in moves:
        item = {"op": op, "target": target + 1}
        if op == "multiply":
            item["source"] = arg + 1
        if op == "conjugate":
            item["by"] = arg
        result.append(item)
    return result


def check_certificate(e, expected, full=False):
    endpoint, peak = independent_replay(e.initial, e.moves)
    require(endpoint == expected, (e.initial, endpoint, expected))
    require(ac_words.replay(e.initial, external_moves(e.moves)) == expected,
            "ac_words replay mismatch")
    require(peak == e.peak, "peak mismatch")
    result = {"moves": len(e.moves), "multiplications": sum(m[0] == "multiply" for m in e.moves),
              "peak_relator_length": peak, "endpoint": endpoint}
    if full:
        result.update(initial=e.initial, elementary_moves=e.moves)
    return result


def balanced(value, modulus):
    residue = value % modulus
    return residue - modulus if 2 * residue > modulus else residue


def explicit_shift_identities(n, k, r, s):
    y = lambda exponent: power("y", exponent)
    t = [y(k) + "x" + y(-s) + "X" + y(-r) + "x",
         y(k - n) + "x" + y(n + 1 - s) + "X" + y(-r) + "x",
         y(r) + "x" + y(s - n - 1) + "X" + y(n - k) + "X",
         y(r - n) + "x" + y(s) + "X" + y(n - k) + "X",
         y(n - k) + "X" + y(r - n) + "x" + y(s) + "X",
         y(-k - 1) + "X" + y(r) + "x" + y(s) + "X"]
    unary = [(author.S(k, r, s), t[0], -1, y(-s) + "X" + y(-r) + "x"),
             (t[1], t[2], -1, "X"),
             (t[3], t[4], 1, "x" + y(k - n)),
             (t[5], author.S(k + 1, r, s), 1, "x")]
    for before, after, sign, by in unary:
        u, q = parse(before), parse(by)
        require(product(invert(q), u if sign == 1 else invert(u), q) == parse(after),
                (n, k, r, s, "explicit unary witness"))
    donor = parse(author.R(n))
    uses = [(t[0], t[1], -1, y(n + 1 - s) + "X" + y(-r) + "x"),
            (t[2], t[3], -1, y(s) + "X" + y(n - k) + "X"),
            (t[4], t[5], 1, "X" + y(r) + "x" + y(s) + "X")]
    for before, after, sign, by in uses:
        q = parse(by)
        require(product(invert(parse(before)), parse(after)) ==
                product(invert(q), donor if sign == 1 else invert(donor), q),
                (n, k, r, s, "explicit donor witness"))


def cyclic_core(symbols):
    result = reduce_int(symbols)
    while len(result) > 1 and result[0] == -result[-1]:
        result = result[1:-1]
    return result


def cyclic_key(symbols):
    z = cyclic_core(symbols)
    if not z:
        return ()
    return min(w[i:] + w[:i] for w in (z, invert(z)) for i in range(len(z)))


def independent_scan(path):
    rows = list(csv.DictReader(path.open()))
    donor_rows, matched_rows, noncyclic = set(), set(), set()
    for row in rows:
        raw = [parse(row[key]) for key in ("r1", "r2")]
        if any(cyclic_core(w) != w for w in raw):
            noncyclic.add(row["name"])
        for swapped, sx, sy, donor_index in itertools.product((False, True), (-1, 1), (-1, 1), (0, 1)):
            base_map = {1: sx * (2 if swapped else 1), 2: sy * (1 if swapped else 2)}
            transformed = [cyclic_core((1 if v > 0 else -1) * base_map[abs(v)] for v in w) for w in raw]
            donor, recipient = transformed[donor_index], transformed[1 - donor_index]
            n = (len(donor) - 3) // 2
            if n < 1 or cyclic_key(donor) != cyclic_key(parse(author.R(n))):
                continue
            donor_rows.add(row["name"])
            stable_letters = [v for v in recipient if abs(v) == 1]
            if len(stable_letters) in (1, 3) and abs(sum(stable_letters)) == 1:
                matched_rows.add(row["name"])
    return {"path": str(path.relative_to(HERE.parents[1])), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "rows": len(rows), "rows_with_consecutive_bs_donor": sorted(donor_rows),
            "rows_with_companion_shape": sorted(matched_rows), "noncyclic_input_rows": sorted(noncyclic)}


def arbitrary_w_certificate(n, a, b, c, epsilon):
    raw_w = power("y", a) + power("x", epsilon) + power("y", b)
    raw_w += power("x", -epsilon) + power("y", c)
    reduced_w = word(parse(raw_w))
    e = author.Elementary([author.R(n), "X" + reduced_w])
    if epsilon == -1:
        k, r, s = -a, b, c
    else:
        k, r, s = -c, a, b
    e.orient(1, author.S(k, r, s))
    suffix = author.solve(n, k, r, s)
    require(e.pair == suffix.initial, "arbitrary-w boundary mismatch")
    for move in suffix.moves:
        e.emit(*move)
    return e, reduced_w


def main():
    start_wall, start_cpu = time.perf_counter(), time.process_time()
    snapshot_files = ["ms_family_extensions.md", "ms_family_verify.py", "ms_family_checks.json",
                      "ac_words.py", "check_ms_independent.py"]
    hashes = {p: hashlib.sha256((HERE / p).read_bytes()).hexdigest() for p in snapshot_files}
    output = {"status": "PASS", "source_sha256": hashes, "heap_nodes": 0, "jit": False}

    identities = 0
    for n, a, b in itertools.product((1, 2, 3, 5), range(-3, 4), range(-3, 4)):
        donor = parse(author.R(n))
        for stable, left_shift, right_shift, sign in (("x", n, n + 1, -1), ("X", n + 1, n, 1)):
            left = parse(power("y", a) + stable + power("y", b))
            right = parse(power("y", a - left_shift) + stable + power("y", b + right_shift))
            q = parse(power("y", b + n + 1) if stable == "x" else "X" + power("y", n + b))
            expected = product(invert(q), donor if sign == 1 else invert(donor), q)
            require(product(invert(left), right) == expected, (n, a, b, stable))
            identities += 1
    output["free_word_identity_checks"] = identities

    shifts, normalizations = [], []
    for n, k, r, s in itertools.product((1, 2, 3, 5), range(-1, 2), range(-2, 3), range(-2, 3)):
        parameters = [n, k, r, s]
        explicit_shift_identities(n, k, r, s)
        e = author.Elementary([author.R(n), author.S(k, r, s)])
        author.shift(e, n, k, r, s)
        checked = check_certificate(e, [author.R(n), author.S(k + 1, r, s)])
        require(checked["multiplications"] == 3, (parameters, "shift cost"))
        shifts.append({"parameters": parameters, **checked})
        rr, ss = balanced(r, n), balanced(s, n + 1)
        u, v = (r - rr) // n, (s - ss) // (n + 1)
        bound = 2 * abs(u) + abs(v) + 3 * abs(k - n * (u + v))
        e = author.Elementary([author.R(n), author.S(k, r, s)])
        author.normalize(e, n, k, r, s, rr, ss)
        checked = check_certificate(e, [author.R(n), author.S(0, rr, ss)])
        require(checked["multiplications"] <= bound, (parameters, "residue cost"))
        require(sum(map(len, checked["endpoint"])) <= 3 * n + 6, "endpoint length bound")
        normalizations.append({"parameters": parameters, "residues": [rr, ss],
                               "multiplication_bound": bound, **checked})
    output.update(shift_checks=shifts, normalization_checks=normalizations)
    output["explicit_shift_free_word_equalities"] = 7 * len(shifts)

    terminal = []
    for n in range(1, 6):
        for rr, ss in itertools.product(range(n), range(n + 1)):
            if author.terminal_residues(n, rr, ss) is None:
                continue
            for direction in (-1, 1):
                k, r, s = direction, rr + direction * n, ss - direction * (n + 1)
                e = author.solve(n, k, r, s)
                terminal.append({"parameters": [n, k, r, s], "residue_class": [rr, ss],
                                 **check_certificate(e, ["x", "y"])})
    output["terminal_checks"] = terminal
    output["ms2_all_residue_pairs_terminal"] = all(author.terminal_residues(2, r, s) is not None
                                                    for r in range(2) for s in range(3))

    boundary = []
    for parameters in ((2, 0, 1, 0), (2, 0, -1, 0), (3, 0, 1, 0),
                       (4, -2, 3, -5), (2, 0, 0, 0), (5, 0, -1, 1)):
        e = author.solve(*parameters)
        boundary.append({"parameters": parameters, **check_certificate(e, ["x", "y"], full=True)})
    output["adversarial_boundary_certificates"] = boundary

    arbitrary = []
    for a, b, c, epsilon in itertools.product(range(-1, 2), range(-2, 3), range(-1, 2), (-1, 1)):
        e, reduced_w = arbitrary_w_certificate(2, a, b, c, epsilon)
        require(reduced_w.count("x") == reduced_w.count("X") <= 1, "bad arbitrary-w hypothesis")
        arbitrary.append({"parameters": [a, b, c, epsilon], "reduced_w": reduced_w,
                          **check_certificate(e, ["x", "y"])})
    for exponent in range(-3, 4):
        e = author.Elementary([author.R(2), "X" + power("y", exponent)])
        author.primitive_cleanup(e, 1, "y", "X")
        author.finish_xy(e)
        arbitrary.append({"pure_y_exponent": exponent, **check_certificate(e, ["x", "y"])})
    output["arbitrary_w_checks"] = arbitrary

    saved = json.loads((HERE / "ms_family_checks.json").read_text())
    saved_checks = []
    for record in saved["full_certificates"]:
        endpoint, peak = independent_replay(record["initial"], record["moves"])
        require(endpoint == record["endpoint"] == ["x", "y"], "stored endpoint")
        require(peak == record["peak"], "stored peak")
        require(len(record["moves"]) == record["move_count"], "stored move count")
        require(ac_words.replay(record["initial"], external_moves(record["moves"])) == ["x", "y"],
                "stored external replay")
        saved_checks.append({"parameters": record["parameters"], "move_count": len(record["moves"]),
                             "endpoint": endpoint})
    output["stored_certificate_replays"] = saved_checks
    scans = [independent_scan(HERE.parents[1] / "data/ms_unsolved_reps" / f"aca_124_{name}.csv")
             for name in ("initial", "best")]
    for scan in scans:
        old = next(s for s in saved["u124_scans"] if s["path"] == scan["path"])
        require(scan["sha256"] == old["sha256"], "input table hash mismatch")
        require(scan["rows_with_companion_shape"] == old["matched_ids"], "U124 scan mismatch")
    output["independent_u124_scans"] = scans
    for path, old_hash in hashes.items():
        require(hashlib.sha256((HERE / path).read_bytes()).hexdigest() == old_hash,
                "source changed during audit: " + path)
    output.update(cpu_seconds=time.process_time() - start_cpu,
                  wall_seconds=time.perf_counter() - start_wall)
    output["summary"] = {"identities": identities, "shift_certificates": len(shifts),
                         "normalization_certificates": len(normalizations), "terminal_certificates": len(terminal),
                         "boundary_certificates": len(boundary), "arbitrary_w_certificates": len(arbitrary),
                         "stored_certificates": len(saved_checks)}
    (HERE / "ms_independent_audit.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({"status": output["status"], "counts": output["summary"],
                      "cpu_seconds": output["cpu_seconds"], "wall_seconds": output["wall_seconds"]}, indent=2))


if __name__ == "__main__":
    main()
