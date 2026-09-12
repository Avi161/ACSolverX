"""Independent integer-word audit of theorem-backed stable composites."""

from __future__ import annotations

import csv
import hashlib
import json
import time
from pathlib import Path

import coupled_power_general_compression as general
import coupled_power_stable_probe as special
import coupled_power_word_compression as literal

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ENC = {"x": 1, "X": -1, "y": 2, "Y": -2, "z": 3, "Z": -3}
DEC = {v: k for k, v in ENC.items()}
INVERSES = {("xy", "y"): ("xY", "y"), ("xY", "y"): ("xy", "y"),
            ("yx", "y"): ("Yx", "y"), ("Yx", "y"): ("yx", "y"),
            ("x", "yx"): ("x", "yX"), ("x", "yX"): ("x", "yx"),
            ("x", "xy"): ("x", "Xy"), ("x", "Xy"): ("x", "xy")}


def require(value, message):
    if not value:
        raise AssertionError(message)


def reduced(values):
    stack = []
    for value in values:
        if stack and stack[-1] == -value:
            stack.pop()
        else:
            stack.append(value)
    return tuple(stack)


def red(word):
    return "".join(DEC[v] for v in reduced(ENC[c] for c in word))


def inv(word):
    return "".join(DEC[-ENC[c]] for c in reversed(word))


def power(word, exponent):
    return red((word if exponent >= 0 else inv(word)) * abs(exponent))


def expand(word, images):
    return red("".join(images[c.lower()] if c.islower() else inv(images[c.lower()]) for c in word))


def cyclic(word):
    word = red(word)
    start, stop = 0, len(word)
    while stop - start > 1 and word[start] == inv(word[stop - 1]):
        start += 1
        stop -= 1
    return word[start:stop], word[:start]


def canon(word):
    core, _ = cyclic(word)
    return min((w[k:] + w[:k] for w in (core, inv(core)) for k in range(len(w))), default="")


def cpair(pair):
    return tuple(sorted(canon(w) for w in pair))


def check_descent(raw, best, trace):
    state = cpair(raw)
    for step in trace:
        require(tuple(step["before"]) == state, "Nielsen before")
        images = tuple(step["images"])
        require(images in INVERSES, "undeclared ambient map")
        inverse = INVERSES[images]
        for first, second in ((images, inverse), (inverse, images)):
            require(tuple(expand(w, dict(zip("xy", second))) for w in first) == ("x", "y"),
                    "ambient inverse composition")
        after = cpair(expand(w, dict(zip("xy", images))) for w in state)
        require(after == tuple(step["after"]), "Nielsen after")
        require(sum(map(len, after)) < sum(map(len, state)), "non-strict descent")
        state = after
    require(state == tuple(best), "final ambient endpoint")


def orientation(source, prefix, cut, expected):
    core, actual_prefix = cyclic(source)
    require(actual_prefix == prefix, "cyclic prefix")
    require(red(inv(prefix) + source + prefix) == core, "cyclic conjugation")
    require(0 <= cut < len(core), "cyclic cut")
    require(core[cut:] + core[:cut] == expected, "oriented source")


def isolate(isolator, axis, sign, recovered):
    require(red(isolator) == isolator, "unreduced isolator")
    positions = [i for i, c in enumerate(isolator) if c.lower() == axis]
    require(len(positions) == 1, "not a unique-occurrence isolator")
    position = positions[0]
    require(sign == (1 if isolator[position].islower() else -1), "isolator sign")
    tail = red(isolator[position + 1:] + isolator[:position])
    expected = inv(tail) if sign == 1 else tail
    require(recovered == expected and axis not in recovered.lower(), "recovered generator")
    images = {"x": "x", "y": "y", "z": "z", axis: recovered}
    require(expand(isolator, images) == "", "isolator does not vanish under substitution")
    return images


def word_witness(pair, witness):
    source = witness["source"]
    orientation(pair[source], witness["cyclic_prefix"], witness["cut"], witness["oriented_source"])
    defining, isolator, companion = witness["defining_word"], witness["isolator"], witness["companion_template"]
    require(defining and red(defining) == defining, "defining word")
    defining_images = {"x": "x", "y": "y", "z": defining}
    require(expand(isolator, defining_images) == witness["oriented_source"], "isolator expansion")
    require(expand(companion, defining_images) == red(pair[1 - source]), "companion expansion")
    axis = witness["eliminated_axis"]
    images = isolate(isolator, axis, witness["unique_sign"], witness["recovered_word"])
    donor = red("Z" + defining)
    dprime, sprime = expand(donor, images), expand(companion, images)
    survivor = "y" if axis == "x" else "x"
    labels = {survivor: "y", "z": "x"}
    endpoint = [expand(dprime, labels), expand(sprime, labels)]
    require(endpoint == witness["raw_rank2_endpoint"], "rank-two endpoint")
    boundaries = [[*map(red, pair), donor], [isolator, red(companion), donor], [isolator, sprime, dprime]]
    lengths = [sum(len(red(w)) for w in state) for state in boundaries]
    require(witness["recorded_rank3_boundary_max_total_length"] == max(lengths), "rank-three total")
    check_descent(endpoint, witness["best_pair"], witness["nielsen_trace"])
    require(sum(map(len, witness["best_pair"])) == witness["best_length"], "stored endpoint length")
    return {"rank3_boundary_lengths": lengths, "rank3_boundary_words": boundaries,
            "raw_endpoint": endpoint, "final_length": witness["best_length"]}


def run_companion(word, d, choices):
    selected = {c["offset"]: c for c in choices}
    out, i, count = "", 0, 0
    while i < len(word):
        if word[i].lower() == "y":
            out += word[i]
            i += 1
            continue
        j = i + 1
        while j < len(word) and word[j] == word[i]:
            j += 1
        exponent = (j - i) * (1 if word[i] == "x" else -1)
        choice = selected[i]
        q, r, side = choice["quotient"], choice["remainder"], choice["side"]
        require(choice["exponent"] == exponent and exponent == d * q + r, "power-run arithmetic")
        require(side in (0, 1), "power-run side")
        block = power("z", q) + power("x", r) if side == 0 else power("x", r) + power("z", q)
        require(expand(block, {"x": "x", "z": "x" * d}) == word[i:j], "power-run expansion")
        out += block
        i, count = j, count + 1
    require(count == len(choices), "extra run choices")
    return red(out)


def power_witness(pair, candidate, special_case=False):
    if special_case:
        w = candidate["orientation"]
        mapping = {w["a"].lower(): "x" if w["a"].islower() else "X",
                   w["t"].lower(): "y" if w["t"].islower() else "Y"}
        normalized = [expand(z, mapping) for z in pair]
        src = normalized[w["source"]]
        src = src if w["sign"] == 1 else inv(src)
        oriented = src[w["cut"]:] + src[:w["cut"]]
        d, m = candidate["power"], w["m"]
        require(oriented == "Y" + "x" * (m + 1) + "y" + "X" * m, "special BS orientation")
        require(d in (m, m + 1), "special power")
        isolator = "YxzyZ" if d == m else "YzyZx"
        sign, recovered = 1, candidate["recovered_a"].translate(str.maketrans("xX", "zZ"))
        companion = w["companion"]
    else:
        w = candidate["witness"]
        normalized = list(pair) if w["axis"] == "x" else [expand(z, {"x": "y", "y": "x"}) for z in pair]
        orientation(normalized[w["source"]], w["cyclic_prefix"], w["cut"], w["oriented_source"])
        oriented, d, isolator, sign = w["oriented_source"], w["power"], w["isolator"], w["unique_sign"]
        recovered = w["recovered_a"].translate(str.maketrans("xX", "zZ"))
        companion = w["companion"]
    require(companion == normalized[1 - w["source"]], "normalized companion")
    require(expand(isolator, {"x": "x", "y": "y", "z": "x" * d}) == oriented,
            "power isolator expansion")
    images = isolate(isolator, "x", sign, recovered)
    compressed = run_companion(companion, d, candidate["block_choices"])
    require(expand(compressed, {"x": "x", "y": "y", "z": "x" * d}) == companion,
            "power companion expansion")
    recovered2 = recovered.translate(str.maketrans("zZ", "xX"))
    for choice in candidate["block_choices"]:
        q, r = choice["quotient"], choice["remainder"]
        replacement = power("x", q) + power(recovered2, r) if choice["side"] == 0 else power(recovered2, r) + power("x", q)
        require(red(replacement) == choice["replacement"], "stored individual run replacement")
    donor = "Z" + "x" * d
    dprime, sprime = expand(donor, images), expand(compressed, images)
    labels = {"z": "x", "y": "y"}
    endpoint = [expand(dprime, labels), expand(sprime, labels)]
    require(endpoint == candidate["raw_endpoint"], "power raw endpoint")
    check_descent(endpoint, candidate["best_pair"], candidate["nielsen_trace"])
    require(candidate["best_length"] == sum(map(len, candidate["best_pair"])), "power length")
    lengths = [sum(map(len, normalized)) + len(donor), len(isolator) + len(compressed) + len(donor),
               len(isolator) + len(dprime) + len(sprime)]
    return {"rank3_boundary_lengths": lengths, "raw_endpoint": endpoint, "final_length": candidate["best_length"]}


def all_literal_endpoints(row, saved, maximum):
    pair, seen, entries = row["input"], set(), []
    for source in (0, 1):
        core, prefix = cyclic(pair[source])
        for defining in literal.source_words(core, maximum):
            companions = literal.decompositions(pair[1 - source], defining, None)
            for cut in range(len(core)):
                oriented = core[cut:] + core[:cut]
                for axis in ("x", "y"):
                    for original in literal.decompositions(oriented, defining, axis):
                        if "z" not in original.lower():
                            continue
                        isolator = red(original)
                        if sum(c.lower() == axis for c in isolator) != 1:
                            continue
                        position = next(i for i, c in enumerate(isolator) if c.lower() == axis)
                        sign = 1 if isolator[position].islower() else -1
                        tail = red(isolator[position + 1:] + isolator[:position])
                        recovered = inv(tail) if sign == 1 else tail
                        images = {"x": "x", "y": "y", "z": "z", axis: recovered}
                        donor = red("Z" + defining)
                        dprime = expand(donor, images)
                        labels = {"y" if axis == "x" else "x": "y", "z": "x"}
                        for companion in companions:
                            sprime = expand(companion, images)
                            endpoint = [expand(dprime, labels), expand(sprime, labels)]
                            key = cpair(endpoint)
                            if key in seen:
                                continue
                            seen.add(key)
                            best, trace = special.nielsen_descent(endpoint)
                            w = {"source": source, "cyclic_prefix": prefix, "cut": cut,
                                 "oriented_source": oriented, "defining_word": defining, "isolator": isolator,
                                 "eliminated_axis": axis, "unique_sign": sign, "recovered_word": recovered,
                                 "companion_template": companion, "raw_rank2_endpoint": endpoint,
                                 "best_pair": best, "best_length": sum(map(len, best)), "nielsen_trace": trace,
                                 "recorded_rank3_boundary_max_total_length": max(
                                     sum(map(len, pair)) + len(donor),
                                     len(isolator) + len(red(companion)) + len(donor),
                                     len(isolator) + len(sprime) + len(dprime))}
                            checked = word_witness(pair, w)
                            entries.append({"raw": endpoint, "best": best, "rank3": checked["rank3_boundary_lengths"]})
    require(len(entries) == saved["attempted_endpoints"], (row["name"], "endpoint enumeration count"))
    require(not saved["limit_hit"], "row limit changed")
    best_length = min(sum(map(len, e["best"])) for e in entries)
    require(best_length == saved["best"]["best_length"], "enumerated best length")
    return {"name": row["name"], "checked_endpoints": len(entries), "best_length": best_length,
            "endpoint_records_sha256": hashlib.sha256(json.dumps(entries, sort_keys=True).encode()).hexdigest(),
            "strict_gains": sum(sum(map(len, e["best"])) < row["input_length"] for e in entries)}


def product_normal(word, order):
    syllables = []
    for c in word:
        generator = c.lower()
        modulus = 2 if generator == "x" else order
        value = 1 if c.islower() else -1
        if syllables and syllables[-1][0] == generator:
            value += syllables.pop()[1]
        value %= modulus
        if value:
            syllables.append((generator, value))
    while len(syllables) > 1 and syllables[0][0] == syllables[-1][0]:
        generator, first = syllables.pop(0)
        value = (first + syllables.pop()[1]) % (2 if generator == "x" else order)
        if value:
            syllables.insert(0, (generator, value))
    return min((tuple(syllables[k:] + syllables[:k]) for k in range(len(syllables))), default=())


def all_power_endpoints(row, kind):
    pair, count, gains, best_length = row["input"], 0, 0, None
    templates = special.orientations(pair) if kind == "special" else general.templates(pair)
    for witness in templates:
        choices = ((witness["m"], "yxYX"), (witness["m"] + 1, "xYXy")) if kind == "special" else (
            (witness["power"], witness["recovered_a"]),)
        for d, recovered in choices:
            companion, blocks = special.run_substitute(witness["companion"], d, recovered)
            raw = [red("X" + power(recovered, d)), companion]
            best, trace = special.nielsen_descent(raw)
            candidate = {"orientation" if kind == "special" else "witness": witness,
                         "power": d, "recovered_a": recovered, "block_choices": blocks,
                         "raw_endpoint": raw, "best_pair": best, "best_length": sum(map(len, best)),
                         "nielsen_trace": trace}
            power_witness(pair, candidate, special_case=kind == "special")
            count += 1
            gains += candidate["best_length"] < row["input_length"]
            best_length = candidate["best_length"] if best_length is None else min(best_length, candidate["best_length"])
    require(count == row["candidate_count"], (row["name"], kind, "power endpoint count"))
    require(best_length == (row["best"]["best_length"] if row["best"] else None), "power enumerated best")
    return {"name": row["name"], "checked_endpoints": count, "strict_gains": gains, "best_length": best_length}


def torus_checks(records):
    checked = []
    for item in records:
        m, k, order = item["m"], item["k"], item["torus_order"]
        require(order == 2 * k + 1, "torus order")
        original_r = "Y" + "x" * (m + 1) + "y" + "X" * m
        original_s = "Y" * (k + 1) + "x" + "y" * k + "x"
        images = {"x": "x" + "Y" * k, "y": "y"}
        mapped_r, mapped_s = expand(original_r, images), expand(original_s, images)
        require(mapped_r == item["mapped_r"] and mapped_s == item["mapped_s"], "torus map")
        require(red("y" * (k + 1) + mapped_s + "Y" * (k + 1)) == "xx" + "Y" * order,
                "torus defining equation")
        normal = product_normal(mapped_r, order)
        require(normal == tuple(map(tuple, item["cyclic_normal"])), "torus normal form")
        require(sum(g == "x" for g, e in normal) == 2 * m + 1, "torus stable syllables")
        runs = [-k] * m + [1] + [-(k + 1)] * (m - 1) + [-(order + 1)]
        require(runs == item["run_exponents"], "torus run exponents")
        require(product_normal("".join("x" + power("y", e) for e in runs), order) == normal,
                "torus run word")
        for candidate in item["candidate_primitives"]:
            h, j = candidate["t_exponent"], candidate["u_exponent"]
            require(2 * h + order * j == 1 and abs(j) == 2 * m + 1, "primitive exponent necessity")
            a, b = abs(h), abs(j)
            christoffel = "".join(("x" if j > 0 else "X") + power("y", (1 if h > 0 else -1) *
                                (((i + 1) * a // b) - (i * a // b))) for i in range(b))
            require(christoffel == candidate["word"], "Christoffel word")
            hit = product_normal(christoffel, order) == normal
            require(hit == candidate["same_free_product_conjugacy_class"], "primitive quotient comparison")
        require(any(c["same_free_product_conjugacy_class"] for c in item["candidate_primitives"]) == (m == k == 1),
                "torus boundary exception")
        checked.append({"m": m, "k": k, "projection_hit": m == k == 1})
    return checked


def main():
    start_cpu, start_wall = time.process_time(), time.perf_counter()
    names = ["STABLE_CERTIFICATE_CONVENTIONS.md", "coupled_power_theory.md", "coupled_power_stable_probe.py",
             "coupled_power_stable_probe.json", "coupled_power_general_compression.py", "coupled_power_general_compression.json",
             "coupled_power_word_compression.py", "coupled_power_word_compression_all124.json", "coupled_power_probe.py",
             "coupled_power_checks.json", "check_stable_independent.py"]
    hashes = {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in names}
    inputs = ROOT / "data/ms_unsolved_reps/aca_124_best.csv"
    input_hash = hashlib.sha256(inputs.read_bytes()).hexdigest()
    rows = {r["name"]: (r["r1"], r["r2"]) for r in csv.DictReader(inputs.open())}
    output = {"status": "PASS", "certificate_scope": "theorem_backed_stable_composites_not_expanded_elementary",
              "source_sha256": hashes, "input_sha256": input_hash, "heap_search_nodes": 0, "jit": False}
    for filename, kind in (("coupled_power_stable_probe.json", "special"),
                           ("coupled_power_general_compression.json", "general"),
                           ("coupled_power_word_compression_all124.json", "literal")):
        data = json.loads((HERE / filename).read_text())
        require(data["source_sha256"] == input_hash, "saved input hash")
        checked = []
        for row in data["rows"]:
            require(tuple(row["input"]) == rows[row["name"]], "exact input row")
            require(row["input_length"] == sum(map(len, row["input"])), "input length")
            if row["best"]:
                result = word_witness(row["input"], row["best"]) if kind == "literal" else power_witness(
                    row["input"], row["best"], special_case=kind == "special")
                checked.append({"name": row["name"], **result})
        output[kind + "_stored_witnesses"] = checked
        if kind == "literal":
            output["all_literal_endpoint_checks"] = [all_literal_endpoints(row, row, data["max_defining_length"])
                                                      for row in data["rows"]]
        else:
            output["all_" + kind + "_endpoint_checks"] = [all_power_endpoints(row, kind) for row in data["rows"]]
    ordinary = json.loads((HERE / "coupled_power_checks.json").read_text())
    output["torus_projection_checks"] = torus_checks(ordinary["torus_cases"])
    for name, expected in hashes.items():
        require(hashlib.sha256((HERE / name).read_bytes()).hexdigest() == expected, "source changed during audit: " + name)
    output["summary"] = {"special_stored_witnesses": len(output["special_stored_witnesses"]),
                         "general_stored_witnesses": len(output["general_stored_witnesses"]),
                         "literal_stored_witnesses": len(output["literal_stored_witnesses"]),
                         "all_special_endpoints": sum(r["checked_endpoints"] for r in output["all_special_endpoint_checks"]),
                         "all_general_endpoints": sum(r["checked_endpoints"] for r in output["all_general_endpoint_checks"]),
                         "all_literal_endpoints": sum(r["checked_endpoints"] for r in output["all_literal_endpoint_checks"]),
                         "strict_literal_gains": sum(r["strict_gains"] for r in output["all_literal_endpoint_checks"]),
                         "torus_projection_cases": len(output["torus_projection_checks"])}
    output.update(cpu_seconds=time.process_time() - start_cpu, wall_seconds=time.perf_counter() - start_wall)
    (HERE / "stable_independent_audit.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({"status": output["status"], "summary": output["summary"], "cpu_seconds": output["cpu_seconds"]}, indent=2))


if __name__ == "__main__":
    main()
