from runpy import run_path
from math import gcd


NODE_BUDGET = 100_000


def exponent_evaluator(dag):
    words = dag["WORDS"]
    memo = {}

    def word_vector(word):
        values = [0, 0, 0]
        for letter in word:
            values["xyz".index(letter.lower())] += 1 if letter.islower() else -1
        return tuple(values)

    def evaluate(expression, environment=()):
        key = (id(expression), tuple((name, id(image)) for name, image in environment))
        if key in memo:
            return memo[key]
        assert len(memo) < NODE_BUDGET
        if expression.kind == "lit":
            value = word_vector(expression.value)
        elif expression.kind == "leaf":
            source = expression.args[0]
            image = next((image for name, image in reversed(environment) if name == source), None)
            value = evaluate(image, tuple(pair for pair in environment if pair[0] != source)) if image else word_vector(words[source])
        elif expression.kind == "prod":
            value = tuple(sum(part[index] for part in (evaluate(child, environment) for child in expression.args)) for index in range(3))
        elif expression.kind == "inv":
            value = tuple(-entry for entry in evaluate(expression.args[0], environment))
        elif expression.kind == "conj":
            value = evaluate(expression.args[1], environment)
        elif expression.kind == "subst":
            item, source, image = expression.args
            value = evaluate(item, environment + ((source, image),))
        elif expression.kind == "subst-evidence":
            raise AssertionError("proof-only substitution evidence")
        else:
            raise AssertionError(expression.kind)
        memo[key] = value
        return value

    return evaluate, memo


def cyclic_weights(first, second):
    vector = (
        first[1] * second[2] - first[2] * second[1],
        first[2] * second[0] - first[0] * second[2],
        first[0] * second[1] - first[1] * second[0],
    )
    divisor = gcd(gcd(abs(vector[0]), abs(vector[1])), abs(vector[2]))
    assert divisor
    vector = tuple(entry // divisor for entry in vector)
    first_nonzero = next(entry for entry in vector if entry)
    return vector if first_nonzero > 0 else tuple(-entry for entry in vector)


def fox_evaluator(dag, laurent, weights):
    add, neg, mul, monomial = (laurent[name] for name in ("add", "neg", "mul", "monomial"))
    words = dag["WORDS"]
    memo = {}

    def shift(height, row):
        return tuple(mul(monomial(height), entry) for entry in row)

    def combine(first, second):
        weight, row = first
        other_weight, other_row = second
        return weight + other_weight, tuple(add(left, right) for left, right in zip(row, shift(weight, other_row)))

    def invert(value):
        weight, row = value
        return -weight, tuple(neg(entry) for entry in shift(-weight, row))

    def word_value(word):
        height, row = 0, ({}, {}, {})
        for letter in word:
            generator = "xyz".index(letter.lower())
            step = weights[letter.lower()]
            if letter.islower():
                row = tuple(add(entry, monomial(height) if index == generator else {}) for index, entry in enumerate(row))
                height += step
            else:
                row = tuple(add(entry, monomial(height - step, -1) if index == generator else {}) for index, entry in enumerate(row))
                height -= step
        return height, row

    def evaluate(expression, environment=()):
        key = (id(expression), tuple((name, id(image)) for name, image in environment))
        if key in memo:
            return memo[key]
        assert len(memo) < NODE_BUDGET
        if expression.kind == "lit":
            value = word_value(expression.value)
        elif expression.kind == "leaf":
            source = expression.args[0]
            image = next((image for name, image in reversed(environment) if name == source), None)
            value = evaluate(image, tuple(pair for pair in environment if pair[0] != source)) if image else word_value(words[source])
        elif expression.kind == "prod":
            value = (0, ({}, {}, {}))
            for child in expression.args:
                value = combine(value, evaluate(child, environment))
        elif expression.kind == "inv":
            value = invert(evaluate(expression.args[0], environment))
        elif expression.kind == "conj":
            coefficient, child = expression.args
            coefficient_value = (
                word_value(coefficient)
                if isinstance(coefficient, str)
                else evaluate(coefficient, ())
            )
            value = combine(combine(coefficient_value, evaluate(child, environment)), invert(coefficient_value))
        elif expression.kind == "subst":
            item, source, image = expression.args
            value = evaluate(item, environment + ((source, image),))
        elif expression.kind == "subst-evidence":
            raise AssertionError("endpoint row contains proof-only substitution evidence")
        else:
            raise AssertionError(expression.kind)
        memo[key] = value
        return value

    return evaluate, memo


def fundamental(laurent, row, weights):
    result = {}
    for generator, derivative in zip("xyz", row):
        coefficient = laurent["sub"](laurent["monomial"](weights[generator]), laurent["monomial"](0))
        result = laurent["add"](result, laurent["mul"](coefficient, derivative))
    return result


def expr_gate(dag, laurent, relators, target, weights):
    evaluate, memo = fox_evaluator(dag, laurent, weights)
    relator_values = tuple(evaluate(row) for row in relators)
    target_weight, target_row = evaluate(target)
    assert target_weight == 0 and all(weight == 0 for weight, _ in relator_values)
    for _, row in relator_values + ((target_weight, target_row),):
        assert fundamental(laurent, row, weights) == {}
    rows = tuple(row for _, row in relator_values)
    columns, divisor = laurent["choose_minor"](*rows)
    first, second = columns
    numerator_alpha = laurent["sub"](laurent["mul"](target_row[first], rows[1][second]), laurent["mul"](target_row[second], rows[1][first]))
    numerator_beta = laurent["sub"](laurent["mul"](rows[0][first], target_row[second]), laurent["mul"](rows[0][second], target_row[first]))
    alpha_quotient, alpha_remainder = laurent["divide"](
        numerator_alpha, divisor
    )
    beta_quotient, beta_remainder = laurent["divide"](numerator_beta, divisor)
    alpha = alpha_quotient if not alpha_remainder else None
    beta = beta_quotient if not beta_remainder else None
    other = ({0, 1, 2} - set(columns)).pop()
    discrepancy = None
    if alpha is not None and beta is not None:
        for column in columns:
            assert laurent["add"](laurent["mul"](alpha, rows[0][column]), laurent["mul"](beta, rows[1][column])) == target_row[column]
        discrepancy = laurent["sub"](laurent["add"](laurent["mul"](alpha, rows[0][other]), laurent["mul"](beta, rows[1][other])), target_row[other])
    return {
        "verdict": "necessary-filter pass" if alpha is not None and beta is not None and not alpha_remainder and not beta_remainder and not discrepancy else "nonmember",
        "columns": columns, "D": divisor, "Nalpha": numerator_alpha, "Nbeta": numerator_beta,
        "alpha": alpha, "beta": beta, "alpha_remainder": alpha_remainder,
        "alpha_quotient": alpha_quotient, "beta_quotient": beta_quotient,
        "beta_remainder": beta_remainder, "third_discrepancy": discrepancy,
        "unique_nodes": len(memo),
    }


def kill_first_results():
    dag = run_path("tests/stable_ac/test_ak3_mms02_relation_lift_certificate.py")
    laurent = run_path("tests/stable_ac/test_ak3_mms02_residual_alexander_gates.py")
    data = dag["relation_lift_data"]()
    inverse, leaf, prod = dag["inverse"], dag["leaf"], dag["prod"]
    ka2 = expr_gate(dag, laurent, (leaf("B"), leaf("v")), prod(data["e_a"], inverse(leaf("A"))), {"x": 1, "y": 1, "z": 0})
    kb2 = expr_gate(dag, laurent, (leaf("A"), leaf("v")), prod(data["e_b"], inverse(leaf("B"))), {"x": 1, "y": 0, "z": 1})
    exponent, exponent_memo = exponent_evaluator(dag)
    ka1_relators = (data["e_a"], leaf("B"))
    exponent_rows = tuple(exponent(row) for row in ka1_relators)
    weights_vector = cyclic_weights(*exponent_rows)
    weights = dict(zip("xyz", weights_vector))
    ka1_target = prod(data["h_a"], inverse(leaf("v")))
    target_exponent = exponent(ka1_target)
    if sum(weight * exponent for weight, exponent in zip(weights_vector, target_exponent)):
        ka1 = {"verdict": "abelianization nonmember"}
    else:
        ka1 = expr_gate(dag, laurent, ka1_relators, ka1_target, weights)
    ka1.update({"weights": weights, "exponent_rows": exponent_rows, "target_exponent": target_exponent, "unique_exponent_nodes": len(exponent_memo)})
    return {
        "KA1": ka1,
        "KA2": ka2,
        "KB2": kb2,
    }


def test_kill_first_alexander_gates():
    results = kill_first_results()
    assert set(results) == {"KA1", "KA2", "KB2"}
    assert results["KA1"]["verdict"] == "nonmember"
    assert results["KA2"]["verdict"] == "necessary-filter pass"
    assert results["KB2"]["verdict"] == "nonmember"
    assert results["KA1"]["alpha_remainder"] == {
        -6: 1,
        -5: -4,
        -4: 7,
        -3: -2,
        -2: -9,
        -1: 14,
        0: -5,
        2: 1,
    }
    assert results["KB2"]["alpha_remainder"] == {
        -33: -3664388358890479647198
    }
    assert results["KA2"]["D"] == {0: -1}
    assert results["KA2"]["third_discrepancy"] == {}
    for result in results.values():
        assert result["verdict"] in {"necessary-filter pass", "nonmember", "abelianization nonmember"}
        if result["verdict"] != "abelianization nonmember":
            assert result["D"] and result["unique_nodes"] < NODE_BUDGET
    assert results["KA1"]["unique_exponent_nodes"] < NODE_BUDGET
