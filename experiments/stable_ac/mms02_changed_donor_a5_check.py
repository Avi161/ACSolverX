"""One finite A5 check of the changed-donor relation and residues."""

from itertools import permutations
import json

IDENTITY = (0, 1, 2, 3, 4)
A_REPRESENTATIVES = (IDENTITY, (1, 0, 3, 2, 4), (1, 2, 0, 3, 4), (1, 2, 3, 4, 0))
RAW_A = "xYxYXyyXYxyXy"
RAW_B = "XyyXYXyxYYxy"
PERIOD = 30


def even_permutations():
    return tuple(p for p in permutations(range(5))
                 if sum(p[i] > p[j] for i in range(5) for j in range(i + 1, 5)) % 2 == 0)


def multiply(p, q):
    return tuple(p[q[index]] for index in range(5))


def inverse(p):
    return tuple(p.index(index) for index in range(5))


def power(p, exponent):
    if exponent < 0:
        p, exponent = inverse(p), -exponent
    result = IDENTITY
    for _ in range(exponent):
        result = multiply(result, p)
    return result


def word_image(word, x, y):
    images = {"x": x, "X": inverse(x), "y": y, "Y": inverse(y)}
    result = IDENTITY
    for letter in word:
        result = multiply(result, images[letter])
    return result


def conjugate(p, by):
    return multiply(multiply(by, p), inverse(by))


def are_conjugate(p, q, group):
    return any(conjugate(p, by) == q for by in group)


def order(p):
    for exponent in range(1, PERIOD + 1):
        if power(p, exponent) == IDENTITY:
            return exponent
    raise AssertionError("permutation order exceeded the pinned A5 period")


def data():
    group = even_permutations()
    if len(group) != 60:
        raise AssertionError("the A5 inventory drifted")
    rows = []
    allowed_global = set(range(PERIOD))
    valid_count = nontrivial_count = noncommuting_count = a_nonidentity_count = 0
    for a in A_REPRESENTATIVES:
        for t in group:
            x = multiply(a, power(t, 2))
            image_a = word_image(RAW_A, x, t)
            image_b = word_image(RAW_B, x, t)
            image_r = multiply(image_a, image_b)
            valid = image_r == IDENTITY
            commuting = multiply(a, t) == multiply(t, a)
            allowed = None
            if valid:
                conjugacy_class = {conjugate(image_a, by) for by in group}
                allowed = [m for m in range(PERIOD) if multiply(power(a, m), t) in conjugacy_class]
                allowed_global.intersection_update(allowed)
                valid_count += 1
                nontrivial_count += a != IDENTITY or t != IDENTITY
                noncommuting_count += not commuting
                a_nonidentity_count += a != IDENTITY
            rows.append({"a": a, "t": t, "x": x, "image_A": image_a, "image_B": image_b,
                         "image_R": image_r, "valid_R_identity": valid, "allowed_residues": allowed,
                         "order_a": order(a), "base_rows_killed": image_a == image_b == IDENTITY,
                         "a_identity": a == IDENTITY, "commuting": commuting})
    if len(rows) != 240:
        raise AssertionError("the fixed representative table must contain 240 pairs")
    return {"group": "A5", "product_convention": "p composed with q", "period": PERIOD,
            "raw_A": RAW_A, "raw_B": RAW_B, "a_representatives": A_REPRESENTATIVES,
            "rows": rows, "counts": {"pairs": len(rows), "valid": valid_count,
                "nontrivial_valid_image": nontrivial_count, "noncommuting_valid": noncommuting_count,
                "a_nonidentity_valid": a_nonidentity_count},
            "allowed_global": sorted(allowed_global), "status": "one_finite_changed_donor_check_only"}


if __name__ == "__main__":
    print(json.dumps(data(), sort_keys=True))
