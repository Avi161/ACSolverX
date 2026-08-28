from dataclasses import dataclass
from runpy import run_path
import sys


sys.setrecursionlimit(100_000)


A, B, U, V = "xzYXyxZXYxyZ", "XyxZXYXyxzXYxy", "zYX", "Xyz"
M0, M1, R, S = "xYxYXyyXYxyXy", "XyyXYXyxYYxy", "xxxYYYY", "xyxYXY"
WORDS = {"A": A, "B": B, "u": U, "v": V, "M0": M0, "M1": M1, "R": R, "S": S}
VALUE_LIMIT = 100_000
NODE_BUDGET = 100_000


def inv(word):
    return "".join(letter.swapcase() for letter in reversed(word))


def red(word):
    stack = []
    for letter in word:
        if stack and stack[-1] == letter.swapcase():
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


@dataclass(frozen=True)
class Expr:
    kind: str
    args: tuple
    value: str | None
    support: frozenset[str]


def lit(word):
    return Expr("lit", (), word, frozenset())


def leaf(source):
    return Expr("leaf", (source,), WORDS[source], frozenset((source,)))


def is_empty(item):
    return item.kind == "lit" and item.value == ""


def shallow(item):
    return item.kind, item.value, item.support, len(item.args)


def prod(*items):
    items = tuple(item for item in items if not is_empty(item))
    if not items:
        return lit("")
    if len(items) == 1:
        return items[0]
    raw = None if any(item.value is None for item in items) else "".join(item.value for item in items)
    value = red(raw) if raw is not None and len(raw) <= VALUE_LIMIT else None
    return Expr("prod", items, value, frozenset().union(*(item.support for item in items)))


def inverse(item):
    return Expr("inv", (item,), None if item.value is None else inv(item.value), item.support)


def conj(word, item):
    coefficient = word.value if isinstance(word, Expr) else word
    raw = None if coefficient is None or item.value is None else coefficient + item.value + inv(coefficient)
    return Expr("conj", (word, item), red(raw) if raw is not None and len(raw) <= VALUE_LIMIT else None, item.support)


def subst(item, source, image):
    return Expr("subst", (item, source, image), None, (item.support - {source}) | image.support)


def subst_evidence(item, source, equality):
    return Expr("subst-evidence", (item, source, equality.evidence), None, equality.support)


def nodes(item):
    seen, stack = set(), [item]
    while stack:
        node = stack.pop()
        if id(node) in seen:
            continue
        seen.add(id(node))
        assert len(seen) < NODE_BUDGET
        stack.extend(arg for arg in node.args if isinstance(arg, Expr))
    return len(seen)


@dataclass(frozen=True)
class Proof:
    left: Expr
    right: Expr
    evidence: Expr
    support: frozenset[str]
    rule: str
    children: tuple = ()


def same(left, right):
    return left is right or (left.value is not None and left.value == right.value)


def refl(item):
    return Proof(item, item, lit(""), frozenset(), "refl")


def sym(proof):
    return Proof(proof.right, proof.left, inverse(proof.evidence), proof.support, "sym", (proof,))


def trans(first, second):
    assert same(first.right, second.left)
    return Proof(first.left, second.right, prod(first.evidence, second.evidence), first.support | second.support, "trans", (first, second))


def pprod(first, second):
    return Proof(prod(first.left, second.left), prod(first.right, second.right), prod(first.evidence, conj(first.right, second.evidence)), first.support | second.support, "prod", (first, second))


def pinv(proof):
    return Proof(inverse(proof.left), inverse(proof.right), conj(inverse(proof.left), inverse(proof.evidence)), proof.support, "inv", (proof,))


def pconj(word, proof):
    return Proof(conj(word, proof.left), conj(word, proof.right), conj(word, proof.evidence), proof.support, "conj", (proof,))


def psubst(item, source, equality):
    assert equality.right.kind == "leaf" and equality.right.args[0] == source
    return Proof(subst(item, source, equality.left), item, subst_evidence(item, source, equality), equality.support, "subst", (equality,))


def verify(proof):
    seen, stack = set(), [proof]
    while stack:
        proof = stack.pop()
        if id(proof) in seen:
            continue
        seen.add(id(proof))
        assert len(seen) < NODE_BUDGET
        if proof.rule == "refl":
            assert proof.left is proof.right and not proof.support
        elif proof.rule == "sym":
            assert proof.left is proof.children[0].right
        elif proof.rule == "trans":
            assert same(proof.children[0].right, proof.children[1].left)
        elif proof.rule == "prod":
            left, right = proof.children
            assert shallow(proof.left) == shallow(prod(left.left, right.left))
            assert shallow(proof.right) == shallow(prod(left.right, right.right))
        elif proof.rule == "inv":
            child = proof.children[0]
            assert shallow(proof.left) == shallow(inverse(child.left))
            assert shallow(proof.right) == shallow(inverse(child.right))
        elif proof.rule == "conj":
            child = proof.children[0]
            assert proof.left.kind == "conj" and shallow(proof.right) == shallow(conj(proof.left.args[0], child.right))
        elif proof.rule == "drop":
            assert proof.left.kind == "leaf" and is_empty(proof.right)
        elif proof.rule == "free":
            assert is_empty(proof.evidence) and same(proof.left, proof.right)
        elif proof.rule == "checked":
            assert proof.left.value is not None and proof.right.value is not None
        elif proof.rule == "subst":
            child = proof.children[0]
            assert proof.left.kind == "subst" and proof.right is proof.left.args[0]
            assert proof.left.args[1] == child.right.args[0]
            assert proof.left.args[2] is child.left and proof.evidence.kind == "subst-evidence"
            assert proof.support == child.support
        else:
            raise AssertionError(proof.rule)
        assert proof.evidence.support <= proof.support
        if proof.evidence.value is not None and proof.left.value is not None and proof.right.value is not None:
            assert proof.evidence.value == red(proof.left.value + inv(proof.right.value))
        stack.extend(proof.children)


def project(item, keep):
    memo = {}
    def visit(node):
        key = id(node)
        if key in memo:
            return memo[key]
        assert len(memo) < NODE_BUDGET
        if node.kind == "leaf": result = node if node.args[0] in keep else lit("")
        elif node.kind == "lit": result = node
        elif node.kind == "prod": result = prod(*(visit(arg) for arg in node.args))
        elif node.kind == "inv": result = inverse(visit(node.args[0]))
        elif node.kind == "subst": result = subst(visit(node.args[0]), node.args[1], node.args[2])
        else: result = conj(node.args[0], visit(node.args[1]))
        memo[key] = result
        return result
    return visit(item)


def project_proof(item, keep):
    memo = {}
    def visit(node):
        key = id(node)
        if key in memo: return memo[key]
        assert len(memo) < NODE_BUDGET
        if node.kind == "leaf": result = refl(node) if node.args[0] in keep else Proof(node, lit(""), node, frozenset((node.args[0],)), "drop")
        elif node.kind == "lit": result = refl(node)
        elif node.kind == "prod":
            result = refl(lit(""))
            for arg in node.args: result = pprod(result, visit(arg))
        elif node.kind == "inv": result = pinv(visit(node.args[0]))
        elif node.kind == "subst": result = psubst(node.args[0], node.args[1], node.args[2])
        else: result = pconj(node.args[0], visit(node.args[1]))
        memo[key] = result
        return result
    return visit(item)


def replace(item, source, image):
    memo = {}
    def visit(node):
        key = id(node)
        if key in memo: return memo[key]
        assert len(memo) < NODE_BUDGET
        if node.kind == "leaf": result = image if node.args[0] == source else node
        elif node.kind == "lit": result = node
        elif node.kind == "prod": result = prod(*(visit(arg) for arg in node.args))
        elif node.kind == "inv": result = inverse(visit(node.args[0]))
        elif node.kind == "subst": result = subst(visit(node.args[0]), node.args[1], node.args[2])
        else: result = conj(node.args[0], visit(node.args[1]))
        memo[key] = result
        return result
    return visit(item)


def replace_proof(item, source, equality):
    memo = {}
    def visit(node):
        key = id(node)
        if key in memo: return memo[key]
        assert len(memo) < NODE_BUDGET
        if node.kind == "leaf": result = equality if node.args[0] == source else refl(node)
        elif node.kind == "lit": result = refl(node)
        elif node.kind == "prod":
            result = refl(lit(""))
            for arg in node.args: result = pprod(result, visit(arg))
        elif node.kind == "inv": result = pinv(visit(node.args[0]))
        elif node.kind == "subst": result = psubst(node.args[0], node.args[1], node.args[2])
        else: result = pconj(node.args[0], visit(node.args[1]))
        memo[key] = result
        return result
    return visit(item)


def rank_three_rows():
    code = run_path(".scratch/mms02_u_xy_bridge_checker.py")
    states, steps = code["expand_path"](code["MISPRINTED_RANK_THREE"], code["RANK_THREE_MOVES"])
    assert len(code["RANK_THREE_MOVES"]) == 11 and len(steps) == 134
    rows = [leaf("A"), leaf("B"), leaf("u")]
    for step in steps:
        if step.kind == "AC1":
            rows[step.target] = prod(rows[step.target], rows[step.operand])
        elif step.kind == "AC2":
            rows[step.target] = inverse(rows[step.target])
        else:
            rows[step.target] = conj(step.operand, rows[step.target])
        assert rows[step.target].value == step.after[step.target]
    assert tuple(row.value for row in rows) == states[-1] == ("Z", "Y", "X")
    return tuple(rows)


def h_step(words, rows, move):
    first, second = words
    left, right = rows
    if move == 1:
        return (first, red(second + first)), (left, prod(right, left))
    if move == 2:
        return (red(first + inv(second)), second), (prod(left, inverse(right)), right)
    if move == 3:
        return (first, red(second + inv(first))), (left, prod(right, inverse(left)))
    if move == 4:
        return (red(first + second), second), (prod(left, right), right)
    table = {5: (1, "X"), 6: (0, "Y"), 7: (1, "Y"), 8: (0, "x"), 9: (1, "x"), 10: (0, "y"), 11: (1, "y"), 12: (0, "X")}
    target, word = table[move]
    new_words, new_rows = [first, second], [left, right]
    new_words[target] = red(word + new_words[target] + inv(word))
    new_rows[target] = conj(word, new_rows[target])
    return tuple(new_words), tuple(new_rows)


def two_row_rows():
    code = run_path(".scratch/mms02_wirtinger_repair_attack_checker.py")
    words, rows = (M0, M1), (leaf("M0"), leaf("M1"))
    words, rows = (inv(words[0]), words[1]), (inverse(rows[0]), rows[1])
    word = words[0][-1]
    words, rows = (red(word + words[0] + inv(word)), words[1]), (conj(word, rows[0]), rows[1])
    words, rows = (words[0], inv(words[1])), (rows[0], inverse(rows[1]))
    assert words == code["PUBLISHED_P"] and tuple(row.value for row in rows) == words
    assert len(code["MISPRINTED_TO_AK3"]) == 53
    for move in code["MISPRINTED_TO_AK3"]:
        words, rows = h_step(words, rows, move)
        assert tuple(row.value for row in rows) == words
    assert words == (R, S)
    return rows


def ak3_expr(cert, row_r, row_s):
    rows = {"R": row_r, "S": row_s}
    terms = []
    for factor in cert.factors:
        row = rows[factor.relator]
        terms.append(conj(factor.conjugator, row if factor.sign == 1 else inverse(row)))
    return prod(*terms)


def z_sub(source, target):
    result = refl(lit(""))
    for letter in source:
        if letter == "z":
            step = Proof(lit("z"), lit("Yx"), conj("z", leaf("v")), frozenset(("v",)), "checked")
        elif letter == "Z":
            step = Proof(lit("Z"), lit("Xy"), inverse(leaf("v")), frozenset(("v",)), "checked")
        else:
            step = refl(lit(letter))
        result = pprod(result, step)
    assert result.left.value == source and result.right.value == target
    return result


def free_proof(left, right):
    assert same(left, right)
    return Proof(left, right, lit(""), frozenset(), "free")


def relation_lift_data():
    rows = rank_three_rows()
    v_expr = prod(rows[2], inverse(rows[1]), inverse(rows[0]))
    assert v_expr.value == V
    h = project(v_expr, {"u"})
    h_eq_v = sym(project_proof(v_expr, {"u"}))
    verify(h_eq_v)
    assert same(h_eq_v.left, h) and h_eq_v.support <= {"A", "B"}

    row_r, row_s = two_row_rows()
    ak3 = run_path("tests/stable_ac/test_ak3_normal_closure_certificate.py")["certificate"]()
    x_m, y_m = ak3_expr(ak3["x_one"], row_r, row_s), ak3_expr(ak3["y_one"], row_r, row_s)
    assert x_m.value == "x" and y_m.value == "y"

    a_m0, b_m1 = z_sub(A, M0), z_sub(B, M1)
    verify(a_m0)
    verify(b_m1)
    m0_a, m1_b = sym(a_m0), sym(b_m1)
    m0_abv = prod(m0_a.evidence, leaf("A"))
    m1_abv = prod(m1_b.evidence, leaf("B"))
    assert m0_abv.value == M0 and m1_abv.value == M1
    x_abv = replace(replace(x_m, "M0", m0_abv), "M1", m1_abv)
    y_abv = replace(replace(y_m, "M0", m0_abv), "M1", m1_abv)
    assert x_abv.value == "x" and y_abv.value == "y"

    u_inverse = lit("xyZ")
    u_to_xyxy = z_sub("xyZ", "xyXy")
    x_one = Proof(lit("x"), lit(""), x_abv, x_abv.support, "checked")
    y_one = Proof(lit("y"), lit(""), y_abv, y_abv.support, "checked")
    xyxy_one = pprod(pprod(pprod(x_one, y_one), pinv(x_one)), y_one)
    u_inverse_one = trans(u_to_xyxy, xyxy_one)
    verify(u_inverse_one)
    evidence_projection = project_proof(u_inverse_one.evidence, {"v"})
    k = evidence_projection.right
    k_eq_u_inverse = sym(trans(free_proof(u_inverse, u_inverse_one.evidence), evidence_projection))
    verify(k_eq_u_inverse)

    h_a, h_b = prod(leaf("A"), h), prod(leaf("B"), h)
    h_a_eq_v = trans(pprod(Proof(leaf("A"), lit(""), leaf("A"), frozenset(("A",)), "drop"), h_eq_v), free_proof(h_eq_v.right, leaf("v")))
    h_b_eq_v = trans(pprod(Proof(leaf("B"), lit(""), leaf("B"), frozenset(("B",)), "drop"), h_eq_v), free_proof(h_eq_v.right, leaf("v")))
    verify(h_a_eq_v)
    verify(h_b_eq_v)

    k_a, k_b = subst(k, "v", h_a), subst(k, "v", h_b)
    k_eq_k_a = sym(psubst(k, "v", h_a_eq_v))
    k_eq_k_b = sym(psubst(k, "v", h_b_eq_v))
    k_a_eq_u_inverse = trans(sym(k_eq_k_a), k_eq_u_inverse)
    k_b_eq_u_inverse = trans(sym(k_eq_k_b), k_eq_u_inverse)
    e_a, e_b = prod(leaf("u"), k_a), prod(leaf("u"), k_b)
    e_a_eq_one = trans(pprod(refl(leaf("u")), k_a_eq_u_inverse), free_proof(prod(leaf("u"), u_inverse), lit("")))
    e_b_eq_one = trans(pprod(refl(leaf("u")), k_b_eq_u_inverse), free_proof(prod(leaf("u"), u_inverse), lit("")))
    verify(e_a_eq_one)
    verify(e_b_eq_one)
    assert (e_a, leaf("B"), h_a)[1].value == B
    assert (leaf("A"), e_b, h_b)[0].value == A
    return {
        "h": h,
        "k": k,
        "h_a": h_a,
        "h_b": h_b,
        "e_a": e_a,
        "e_b": e_b,
        "h_a_eq_v": h_a_eq_v,
        "h_b_eq_v": h_b_eq_v,
        "e_a_eq_one": e_a_eq_one,
        "e_b_eq_one": e_b_eq_one,
    }


def test_mms02_relation_lift_certificate_dag():
    data = relation_lift_data()
    assert data["e_a_eq_one"].support <= {"A", "B"}
    assert data["h_a_eq_v"].support <= {"A", "B"}
    assert data["e_b_eq_one"].support <= {"A", "B"}
    assert data["h_b_eq_v"].support <= {"A", "B"}
    assert nodes(data["e_a"]) < 25_000 and nodes(data["e_b"]) < 25_000
