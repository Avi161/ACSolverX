from runpy import run_path


def free_reduce(word):
    stack = []
    for letter in word:
        if stack and stack[-1] == letter.swapcase():
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


def add(left, right):
    result = dict(left)
    for exponent, coefficient in right.items():
        result[exponent] = result.get(exponent, 0) + coefficient
        if not result[exponent]:
            del result[exponent]
    return result


def neg(poly):
    return {exponent: -coefficient for exponent, coefficient in poly.items()}


def sub(left, right):
    return add(left, neg(right))


def mul(left, right):
    result = {}
    for left_exponent, left_coefficient in left.items():
        for right_exponent, right_coefficient in right.items():
            exponent = left_exponent + right_exponent
            result[exponent] = result.get(exponent, 0) + left_coefficient * right_coefficient
    return {exponent: coefficient for exponent, coefficient in result.items() if coefficient}


def monomial(exponent, coefficient=1):
    return {} if not coefficient else {exponent: coefficient}


def divide(numerator, denominator):
    if not denominator:
        raise ZeroDivisionError
    if not numerator:
        return {}, {}
    numerator_min = min(numerator)
    denominator_min = min(denominator)
    normalized_numerator = {
        exponent - numerator_min: coefficient
        for exponent, coefficient in numerator.items()
    }
    normalized_denominator = {
        exponent - denominator_min: coefficient
        for exponent, coefficient in denominator.items()
    }
    remainder = dict(normalized_numerator)
    quotient = {}
    divisor_top = max(normalized_denominator)
    divisor_lead = normalized_denominator[divisor_top]
    while remainder and max(remainder) >= divisor_top:
        top = max(remainder)
        coefficient = remainder[top]
        if coefficient % divisor_lead:
            return None, remainder
        exponent = top - divisor_top
        term = monomial(exponent, coefficient // divisor_lead)
        quotient = add(quotient, term)
        remainder = sub(remainder, mul(term, normalized_denominator))
    quotient_shift = numerator_min - denominator_min
    shifted_quotient = {
        exponent + quotient_shift: coefficient
        for exponent, coefficient in quotient.items()
    }
    shifted_remainder = {
        exponent + numerator_min: coefficient
        for exponent, coefficient in remainder.items()
    }
    assert add(mul(shifted_quotient, denominator), shifted_remainder) == numerator
    return shifted_quotient, shifted_remainder


def ordinary_exponent(word):
    values = {"x": 0, "y": 0, "z": 0}
    for letter in word:
        values[letter.lower()] += 1 if letter.islower() else -1
    return values["x"], values["y"], values["z"]


def weighted_exponent(word, weights):
    return sum((1 if letter.islower() else -1) * weights[letter.lower()] for letter in word)


def fox_row(word, weights):
    height = 0
    row = {generator: {} for generator in "xyz"}
    for letter in word:
        generator = letter.lower()
        weight = weights[generator]
        if letter.islower():
            row[generator] = add(row[generator], monomial(height))
            height += weight
        else:
            row[generator] = add(row[generator], monomial(height - weight, -1))
            height -= weight
    assert height == 0
    return tuple(row[generator] for generator in "xyz")


def fundamental(row, weights):
    result = {}
    for generator, derivative in zip("xyz", row):
        result = add(result, mul(sub(monomial(weights[generator]), monomial(0)), derivative))
    return result


def determinant(left, right, columns):
    first, second = columns
    return sub(mul(left[first], right[second]), mul(left[second], right[first]))


def choose_minor(left, right):
    for columns in ((0, 1), (0, 2), (1, 2)):
        value = determinant(left, right, columns)
        if value:
            return columns, value
    raise AssertionError("Fox rows have rank below two")


def gate(relators, defect, weights):
    assert all(weighted_exponent(word, weights) == 0 for word in relators + (defect,))
    assert ordinary_exponent(defect) == (0, 0, 0)
    rows = tuple(fox_row(word, weights) for word in relators)
    target = fox_row(defect, weights)
    for row in rows + (target,):
        assert fundamental(row, weights) == {}
    columns, divisor = choose_minor(*rows)
    first, second = columns
    numerator_alpha = sub(mul(target[first], rows[1][second]), mul(target[second], rows[1][first]))
    numerator_beta = sub(mul(rows[0][first], target[second]), mul(rows[0][second], target[first]))
    alpha_quotient, alpha_remainder = divide(numerator_alpha, divisor)
    beta_quotient, beta_remainder = divide(numerator_beta, divisor)
    alpha = alpha_quotient if not alpha_remainder else None
    beta = beta_quotient if not beta_remainder else None
    other = ({0, 1, 2} - set(columns)).pop()
    reconstructed = {} if alpha is None or beta is None else add(mul(alpha, rows[0][other]), mul(beta, rows[1][other]))
    discrepancy = None if alpha is None or beta is None else sub(reconstructed, target[other])
    if alpha is not None and beta is not None:
        for column in columns:
            assert add(mul(alpha, rows[0][column]), mul(beta, rows[1][column])) == target[column]
    passed = alpha is not None and beta is not None and not alpha_remainder and not beta_remainder and not discrepancy
    return {
        "verdict": "necessary-filter pass" if passed else "nonmember",
        "columns": columns,
        "D": divisor,
        "Nalpha": numerator_alpha,
        "Nbeta": numerator_beta,
        "alpha": alpha,
        "beta": beta,
        "alpha_quotient": alpha_quotient,
        "beta_quotient": beta_quotient,
        "alpha_remainder": alpha_remainder,
        "beta_remainder": beta_remainder,
        "third_discrepancy": discrepancy,
    }


def gate_results():
    transcript = run_path(".scratch/mms02_u_xy_bridge_checker.py")
    _, steps = transcript["expand_path"](
        transcript["MISPRINTED_RANK_THREE"], transcript["RANK_THREE_MOVES"]
    )
    assert len(steps) == 134
    dag = run_path("tests/stable_ac/test_ak3_mms02_relation_lift_certificate.py")
    rows = dag["rank_three_rows"]()
    v_expression = dag["prod"](rows[2], dag["inverse"](rows[1]), dag["inverse"](rows[0]))
    h_expression = dag["project"](v_expression, {"u"})
    h = h_expression.value
    assert h is not None and len(h) == 337 and h_expression.support == {"u"}
    a, b, u = dag["A"], dag["B"], dag["U"]
    defect = free_reduce(u + h)
    return {
        "CA": gate((b, free_reduce(a + h)), defect, {"x": 2, "y": 2, "z": 3}),
        "CB": gate((a, free_reduce(b + h)), defect, {"x": 2, "y": 1, "z": 2}),
    }


def test_residual_alexander_gates():
    results = gate_results()
    assert set(results) == {"CA", "CB"}
    assert results["CA"]["verdict"] == "nonmember"
    assert results["CB"]["verdict"] == "nonmember"
    assert max(results["CA"]["Nalpha"]) - min(results["CA"]["Nalpha"]) < max(results["CA"]["D"]) - min(results["CA"]["D"])
    assert results["CB"]["alpha_remainder"] == {
        -14: 8,
        -13: 3,
        -12: -12,
        -11: -3,
        -10: 12,
        -9: 2,
        -8: 9,
        -7: 4,
        -6: -7,
        -5: 17,
        -4: 13,
    }
    for result in results.values():
        assert result["D"]
        assert result["columns"] in {(0, 1), (0, 2), (1, 2)}
        assert result["verdict"] in {"necessary-filter pass", "nonmember"}
        assert add(
            mul(result["alpha_quotient"], result["D"]),
            result["alpha_remainder"],
        ) == result["Nalpha"]
        assert add(
            mul(result["beta_quotient"], result["D"]),
            result["beta_remainder"],
        ) == result["Nbeta"]
