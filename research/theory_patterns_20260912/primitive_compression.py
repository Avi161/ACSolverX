"""Bounded primitive-single stable compression with exact macro witnesses."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from functools import lru_cache
import math
import sys
import time

sys.dont_write_bytecode = True
from coupled_power_word_compression import decompositions


BASIS = "xyz"
ALPHABET = "xXyYzZ"


def inverse(word):
    return word.swapcase()[::-1]


def reduce_word(word):
    stack = []
    for letter in word:
        if letter not in ALPHABET:
            raise ValueError("word outside F(x,y,z)")
        if stack and stack[-1] == letter.swapcase():
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


def expand(word, images):
    return reduce_word("".join(images[c.lower()] if c.islower()
                               else inverse(images[c.lower()]) for c in word))


def cyclic(word):
    word = reduce_word(word)
    start, stop = 0, len(word)
    while stop - start > 1 and word[start] == word[stop - 1].swapcase():
        start += 1
        stop -= 1
    return word[start:stop], word[:start]


def canonical_witness(word):
    core, prefix = cyclic(word)
    if not core:
        return "", {"sign": 1, "conjugator": ""}
    options = [(base[k:] + base[:k], sign, reduce_word(prefix + base[:k]))
               for sign, base in ((1, core), (-1, inverse(core)))
               for k in range(len(core))]
    result, sign, conjugator = min(options)
    return result, {"sign": sign, "conjugator": conjugator}


def normalize_tuple(words):
    normalized = [canonical_witness(w) for w in words]
    return [x[0] for x in normalized], [x[1] for x in normalized]


@lru_cache(None)
def whitehead_maps(basis=BASIS):
    signed = tuple(c for g in basis for c in (g, g.upper()))
    unique = {}
    for multiplier in signed:
        others = [c for c in signed if c.lower() != multiplier.lower()]
        for mask in range(1 << len(others)):
            chosen = {multiplier} | {c for k, c in enumerate(others) if mask & (1 << k)}
            images = {}
            for g in basis:
                if g == multiplier.lower():
                    images[g] = g
                else:
                    left = multiplier.swapcase() if g.upper() in chosen else ""
                    right = multiplier if g in chosen else ""
                    images[g] = left + g + right
            key = tuple(images[g] for g in basis)
            unique[key] = images
    unique.pop(tuple(basis), None)
    maps = tuple(unique[k] for k in sorted(unique))
    expected = 90 if len(basis) == 3 else 12
    if len(maps) != expected:
        raise ValueError("incomplete Whitehead inventory")
    return maps


@lru_cache(None)
def map_inverses(basis=BASIS):
    maps = whitehead_maps(basis)
    inverses = {}
    for images in maps:
        for candidate in maps:
            if all(expand(images[g], candidate) == g
                   and expand(candidate[g], images) == g for g in basis):
                inverses[tuple(images[g] for g in basis)] = candidate
                break
        else:
            raise ValueError("Whitehead map has no verified inverse in inventory")
    return inverses


@dataclass
class Meter:
    limit: int = 1000
    counts: Counter = field(default_factory=Counter)

    def __post_init__(self):
        if type(self.limit) is not int or not 0 <= self.limit <= 1000:
            raise ValueError("limit must be an integer between 0 and 1000")

    @property
    def used(self):
        return sum(self.counts.values())

    def charge(self, kind, amount):
        if self.used + amount > self.limit:
            return False
        self.counts[kind] += amount
        return True


def boundary(label, words):
    return {"label": label, "relators": list(words), "rank": len(words),
            "relator_lengths": list(map(len, words)), "total_length": sum(map(len, words))}


def eligible_isolator(word):
    word = canonical_witness(word)[0]
    counts = Counter(word.lower())
    if "z" not in counts or any(n < 2 for n in counts.values()):
        return False
    exponents = [word.count(g) - word.count(g.upper()) for g in BASIS]
    return math.gcd(*exponents) == 1


def candidate_templates(pair, maximum=64, max_defining=6):
    if type(maximum) is not int or not 1 <= maximum <= 64:
        raise ValueError("at most 64 decompositions may be retained")
    if type(max_defining) is not int or not 2 <= max_defining <= 6:
        raise ValueError("defining lengths must lie between 2 and 6")
    found = {}
    stats = Counter()
    for source in (0, 1):
        core, prefix = cyclic(pair[source])
        defining_words = sorted({(core + core)[i:i + n]
                                 for n in range(2, min(len(core), max_defining) + 1)
                                 for i in range(len(core))}, key=lambda w: (len(w), w))
        for defining in defining_words:
            stats["defining_words"] += 1
            companions = decompositions(pair[1 - source], defining, None, maximum=maximum)[:2]
            for sign, base in ((1, core), (-1, inverse(core))):
                for cut in range(len(base)):
                    oriented = base[cut:] + base[:cut]
                    stats["decomposition_calls"] += 1
                    templates = decompositions(oriented, defining, None, maximum=maximum)
                    for raw in templates:
                        compressed = reduce_word(raw)
                        stats["templates_examined"] += 1
                        if not eligible_isolator(compressed):
                            continue
                        stats["eligible_occurrences"] += 1
                        for companion in companions:
                            candidate = {"source": source, "source_sign": sign,
                                         "source_conjugator": reduce_word(prefix + base[:cut]),
                                         "oriented_source": oriented,
                                         "defining_word": defining,
                                         "isolator": compressed,
                                         "companion_template": reduce_word(companion)}
                            key = (canonical_witness(compressed)[0], defining,
                                   canonical_witness(companion)[0], source)
                            found.setdefault(key, candidate)
    ordered = sorted(found.values(), key=lambda c: (len(c["isolator"]),
                     len(c["defining_word"]), len(c["companion_template"]),
                     c["isolator"], c["defining_word"], c["source"],
                     c["oriented_source"], c["companion_template"]))
    stats["distinct_eligible_candidates"] = len(ordered)
    stats["retained_candidates"] = min(64, len(ordered))
    return ordered[:64], dict(stats)


def rank2_nielsen(pair, meter):
    maps = ({"x": x, "y": y} for x, y in
            (("xy", "y"), ("xY", "y"), ("yx", "y"), ("Yx", "y"),
             ("x", "yx"), ("x", "yX"), ("x", "xy"), ("x", "Xy")))
    maps = tuple(maps)
    current, witnesses = normalize_tuple(pair)
    trace = []
    initial = {"before": list(pair), "after": current, "canonical_witnesses": witnesses}
    stopped = "no_strict_nielsen_descent"
    while True:
        if not meter.charge("rank2_candidate_images", 16):
            stopped = "image_budget"
            break
        options = []
        for images in maps:
            raw = [expand(w, images) for w in current]
            child, canonical = normalize_tuple(raw)
            options.append((sum(map(len, child)), tuple(child), tuple(images.values()),
                            images, raw, canonical))
        option = min(options)
        if option[0] >= sum(map(len, current)):
            break
        _, child, _, images, raw, canonical = option
        inverse_images = next(candidate for candidate in maps
                              if all(expand(images[g], candidate) == g
                                     and expand(candidate[g], images) == g for g in "xy"))
        trace.append({"before": current, "images": images, "inverse_images": inverse_images,
                      "raw_image": raw, "canonical_witnesses": canonical, "after": list(child)})
        current = list(child)
    return {"initial_normalization": initial, "steps": trace,
            "endpoint": current, "stop": stopped}


def compile_candidate(pair, candidate, meter):
    pair = [reduce_word(w) for w in pair]
    source = candidate["source"]
    if (len(pair) != 2 or type(source) is not int or source not in (0, 1)
            or type(candidate["source_sign"]) is not int or candidate["source_sign"] not in (-1, 1)
            or not eligible_isolator(candidate["isolator"])):
        raise ValueError("not a nonliteral compressed isolator candidate")
    defining, isolator, companion = (candidate[k] for k in
                                      ("defining_word", "isolator", "companion_template"))
    if len(defining) > 6 or "z" in defining.lower():
        raise ValueError("invalid defining word")
    substitution = {"x": "x", "y": "y", "z": defining}
    oriented = reduce_word(inverse(candidate["source_conjugator"])
                           + (pair[source] if candidate["source_sign"] == 1 else inverse(pair[source]))
                           + candidate["source_conjugator"])
    if oriented != candidate["oriented_source"] or expand(isolator, substitution) != oriented:
        raise ValueError("isolator does not expand exactly to the oriented source")
    if expand(companion, substitution) != pair[1 - source]:
        raise ValueError("companion does not expand exactly")
    donor = reduce_word("Z" + defining)
    initial = [donor, isolator, companion]
    current, witnesses = normalize_tuple(initial)
    record = {"candidate": candidate, "input": pair,
              "status": "unknown", "initial_rank3": initial,
              "initial_normalization": {"before": initial, "after": current,
                                        "canonical_witnesses": witnesses},
              "boundaries": [boundary("input_rank2", pair),
                             boundary("defining_relator_added", [donor, oriented, pair[1-source]]),
                             boundary("compressed_rank3", initial),
                             boundary("canonical_rank3", current)],
              "whitehead_steps": []}
    start_charge = meter.used
    start_counts = meter.counts.copy()
    while len(current[1]) > 1:
        if meter.limit - meter.used < 93:
            record["status"] = "image_budget_before_full_whitehead_round"
            break
        meter.charge("rank3_candidate_images", 90)
        options = []
        for images in whitehead_maps():
            image, _ = canonical_witness(expand(current[1], images))
            if len(image) < len(current[1]):
                options.append((len(image), image, tuple(images[g] for g in BASIS), images))
        if not options:
            record["status"] = "nonprimitive_whitehead_minimum"
            break
        images = min(options)[3]
        meter.charge("selected_whole_rank3_images", 3)
        raw = [expand(w, images) for w in current]
        child, witnesses = normalize_tuple(raw)
        step = {"before": current, "images": images,
                "inverse_images": map_inverses()[tuple(images[g] for g in BASIS)],
                "raw_image": raw, "canonical_witnesses": witnesses, "after": child}
        record["whitehead_steps"].append(step)
        record["boundaries"].extend((boundary("whole_rank3_image", raw),
                                     boundary("canonical_rank3_image", child)))
        current = child
    record["rank3_endpoint"] = current
    if len(current[1]) == 1:
        axis = current[1].lower()
        images = {g: "" if g == axis else g for g in BASIS}
        remaining = [expand(current[i], images) for i in (0, 2)]
        normalized_isolator = axis
        record["deletion"] = {"axis": axis, "isolator_sign": 1 if current[1] == axis else -1,
                              "before": current, "after_substitution": [remaining[0], normalized_isolator, remaining[1]],
                              "surviving_words": remaining}
        record["boundaries"].append(boundary("before_strict_destabilization",
                                              [remaining[0], normalized_isolator, remaining[1]]))
        survivors = [g for g in BASIS if g != axis]
        relabel = {survivors[0]: "x", survivors[1]: "y"}
        rank2 = [expand(w, relabel) for w in remaining]
        record["relabel"] = relabel
        record["raw_rank2_endpoint"] = rank2
        record["boundaries"].append(boundary("rank2_after_deletion", rank2))
        record["rank2_nielsen"] = rank2_nielsen(rank2, meter)
        record["endpoint"] = record["rank2_nielsen"]["endpoint"]
        record["endpoint_length"] = sum(map(len, record["endpoint"]))
        record["strict_length_gain"] = record["endpoint_length"] < sum(map(len, pair))
        record["status"] = "primitive_with_replayed_rank2_macro_endpoint"
    record["image_evaluations"] = meter.used - start_charge
    record["image_evaluation_counts"] = dict(meter.counts - start_counts)
    record["recorded_rank3_boundary_max_total_length"] = max(
        (b["total_length"] for b in record["boundaries"] if b["rank"] == 3), default=0)
    return record


def row_probe(row, image_limit=1000):
    started_wall, started_cpu = time.perf_counter(), time.process_time()
    pair = [row["r1"], row["r2"]]
    candidates, generation = candidate_templates(pair)
    meter = Meter(image_limit)
    attempts = []
    for candidate in candidates:
        if meter.limit - meter.used < 93:
            break
        attempts.append(compile_candidate(pair, candidate, meter))
    endpoints = [a for a in attempts if "endpoint" in a]
    best = min(endpoints, key=lambda a: (a["endpoint_length"], a["endpoint"])) if endpoints else None
    return {"name": row["name"], "input": pair, "input_length": sum(map(len, pair)),
            "candidate_generation": generation, "attempts": attempts,
            "image_evaluations": meter.used, "image_evaluation_counts": dict(meter.counts),
            "image_limit": image_limit,
            "candidates_unattempted": len(candidates) - len(attempts),
            "primitive_candidates": len(endpoints),
            "best_endpoint": best["endpoint"] if best else None,
            "best_endpoint_length": best["endpoint_length"] if best else None,
            "strict_length_gain": bool(best and best["strict_length_gain"]),
            "runtime_seconds": {"wall": time.perf_counter() - started_wall,
                                "cpu": time.process_time() - started_cpu}}
