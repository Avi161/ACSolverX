from itertools import permutations
import json
from pathlib import Path

from experiments.stable_ac.mms02_changed_donor_a5_check import (
    A_REPRESENTATIVES, IDENTITY, PERIOD, RAW_A, RAW_B, are_conjugate,
    even_permutations, inverse, multiply, power, word_image,
)


def pointwise_word(word, images):
    result = []
    for point in range(5):
        image = point
        for letter in reversed(word):
            permutation = images[letter.lower()]
            image = permutation.index(image) if letter.isupper() else permutation[image]
        result.append(image)
    return tuple(result)


def independent_group():
    result = []
    for permutation in permutations(range(5)):
        visited, cycles = set(), 0
        for point in range(5):
            if point in visited:
                continue
            cycles += 1
            while point not in visited:
                visited.add(point)
                point = permutation[point]
        if (5 - cycles) % 2 == 0:
            result.append(permutation)
    return tuple(result)


def test_a5_inventory_composition_and_inverse_controls():
    group = independent_group()
    assert group == even_permutations() and len(group) == 60
    inventory = set(group)
    for p in group:
        assert inverse(p) == pointwise_word("A", {"a": p})
        assert multiply(p, inverse(p)) == IDENTITY
        for q in group:
            expected = pointwise_word("ab", {"a": p, "b": q})
            assert multiply(p, q) == expected and expected in inventory


def test_split_five_cycle_conjugacy_and_period_controls():
    group = independent_group()
    cycle = (1, 2, 3, 4, 0)
    square = pointwise_word("aa", {"a": cycle})
    assert not are_conjugate(cycle, square, group)
    independent_class = {pointwise_word("baB", {"a": cycle, "b": by}) for by in group}
    assert square not in independent_class
    by = (1, 2, 0, 3, 4)
    conjugated = pointwise_word("baB", {"a": cycle, "b": by})
    assert conjugated in independent_class and are_conjugate(cycle, conjugated, group)
    assert not are_conjugate(IDENTITY, cycle, group)
    assert PERIOD == 30
    for a in A_REPRESENTATIVES:
        assert pointwise_word("a" * PERIOD, {"a": a}) == IDENTITY
        for m in (0, 1, 7, 29):
            images = {"a": a, "t": by}
            assert pointwise_word("a" * m + "t", images) == pointwise_word("a" * (m + PERIOD) + "t", images)
            assert power(a, m) == pointwise_word("a" * m, images)
    assert pointwise_word("a" * 5, {"a": cycle}) == pointwise_word("a" * 5, {"a": square}) == IDENTITY


def test_raw_relation_can_fail_and_pointwise_evaluator_agrees():
    assert RAW_A == "xYxYXyyXYxyXy" and RAW_B == "XyyXYXyxYYxy"
    a = (1, 0, 3, 2, 4)
    t = IDENTITY
    x = pointwise_word("att", {"a": a, "t": t})
    images = {"x": x, "y": t}
    assert pointwise_word(RAW_A + RAW_B, images) == pointwise_word("A", {"a": a}) != IDENTITY
    for word in (RAW_A, RAW_B, RAW_A + RAW_B):
        assert word_image(word, x, t) == pointwise_word(word, images)


def test_saved_a5_table_has_independent_complete_replay_and_d10_controls():
    path = Path(__file__).resolve().parents[2] / "results/stable_ac/theory/mms02_changed_donor_a5_check_20260906.json"
    artifact = json.loads(path.read_text(encoding="utf-8"))
    identity = (0, 1, 2, 3, 4)
    representatives = (identity, (1, 0, 3, 2, 4), (1, 2, 0, 3, 4), (1, 2, 3, 4, 0))
    group = independent_group()
    assert artifact["group"] == "A5" and artifact["period"] == 30
    assert artifact["product_convention"] == "p composed with q"
    assert artifact["raw_A"] == "xYxYXyyXYxyXy" and artifact["raw_B"] == "XyyXYXyxYYxy"
    assert tuple(map(tuple, artifact["a_representatives"])) == representatives
    rows = artifact["rows"]
    assert [(tuple(row["a"]), tuple(row["t"])) for row in rows] == [(a, t) for a in representatives for t in group]
    counts = {"pairs": len(rows), "valid": 0, "nontrivial_valid_image": 0,
              "noncommuting_valid": 0, "a_nonidentity_valid": 0}
    allowed_global = set(range(30))
    cyclic_count = d10_count = killed_count = 0
    for row in rows:
        a, t = tuple(row["a"]), tuple(row["t"])
        images = {"a": a, "t": t}
        x = pointwise_word("att", images)
        raw_images = {"x": x, "y": t}
        image_a = pointwise_word(artifact["raw_A"], raw_images)
        image_b = pointwise_word(artifact["raw_B"], raw_images)
        image_r = pointwise_word(artifact["raw_A"] + artifact["raw_B"], raw_images)
        assert tuple(row["x"]) == x
        assert tuple(row["image_A"]) == image_a and tuple(row["image_B"]) == image_b
        assert tuple(row["image_R"]) == image_r
        valid = image_r == identity
        commuting = pointwise_word("at", images) == pointwise_word("ta", images)
        killed = image_a == image_b == identity
        assert row["valid_R_identity"] == valid and row["commuting"] == commuting
        assert row["a_identity"] == (a == identity) and row["base_rows_killed"] == killed
        assert killed == (a == t == identity)
        killed_count += killed
        assert row["order_a"] == next(n for n in range(1, 31) if pointwise_word("a" * n, images) == identity)
        if not valid:
            assert row["allowed_residues"] is None
            continue
        counts["valid"] += 1
        counts["nontrivial_valid_image"] += a != identity or t != identity
        counts["noncommuting_valid"] += not commuting
        counts["a_nonidentity_valid"] += a != identity
        conjugacy_class = {pointwise_word("caC", {"c": by, "a": image_a}) for by in group}
        targets = [pointwise_word("a" * m + "t", images) for m in range(30)]
        allowed = [m for m, target in enumerate(targets) if target in conjugacy_class]
        assert row["allowed_residues"] == allowed == list(range(30))
        allowed_global.intersection_update(allowed)
        if a == identity:
            cyclic_count += 1
            assert commuting and image_a == t and image_b == pointwise_word("T", images)
        else:
            d10_count += 1
            assert row["order_a"] == 5 and not commuting
            assert pointwise_word("tt", images) == identity
            assert pointwise_word("taT", images) == pointwise_word("A", images)
            assert image_a == image_b == pointwise_word("at", images)
            subgroup = {pointwise_word("a" * i + suffix, images) for i in range(5) for suffix in ("", "t")}
            assert len(subgroup) == 10 and identity in subgroup and a in subgroup and t in subgroup
            for left in subgroup:
                assert pointwise_word("L", {"l": left}) in subgroup
                for right in subgroup:
                    assert pointwise_word("lr", {"l": left, "r": right}) in subgroup
            for m, target in enumerate(targets):
                k = next(k for k in range(5) if (2 * k + 1 - m) % 5 == 0)
                assert pointwise_word("a" * k + "at" + "A" * k, images) == target
                assert target != identity and pointwise_word("pp", {"p": target}) == identity
                assert target in conjugacy_class
                assert all(pointwise_word("ciC", {"c": by, "i": identity}) != target for by in group)
    assert counts == artifact["counts"] == {"pairs": 240, "valid": 65, "nontrivial_valid_image": 64,
                                             "noncommuting_valid": 5, "a_nonidentity_valid": 5}
    assert cyclic_count == 60 and d10_count == 5 and killed_count == 1
    assert sorted(allowed_global) == artifact["allowed_global"] == list(range(30))
