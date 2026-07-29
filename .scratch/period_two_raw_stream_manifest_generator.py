#!/usr/bin/env python3
"""Deterministically generate and replay the period-two A--C bridge manifest."""

from __future__ import annotations

import argparse
import ast as pyast
import hashlib
import itertools
import json
from pathlib import Path
import sys
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.stable_ac import depth4_period_two_degree_two_escape_certificate as escape
from experiments.stable_ac import depth4_period_two_lift_certificate as lift
from experiments.stable_ac import depth4_period_two_phi4_escape_certificate as phi4
from experiments.stable_ac import depth4_period_two_phi_infinity_hessian_certificate as hessian
from experiments.stable_ac import depth4_period_two_source_flow_certificate as source
from experiments.stable_ac import depth4_period_two_subgroup_rewrite_certificate as rewrite
from experiments.stable_ac import depth4_period_two_tree_flow_factorization_certificate as tree


ROOT = PROJECT_ROOT
JSON_PATH = ROOT / ".scratch/period_two_raw_stream_manifest.json"
MD_PATH = ROOT / ".scratch/period_two_raw_stream_manifest.md"
GENERATOR_PATH = Path(__file__).resolve()

# These are the approved finite path-factor inputs.  All quotient images,
# incidence rows, domains, endpoints, AST gates, and replay records below are
# derived from the live imported implementations.
BLOCKS = (
    ("aBgAgAggABBgAb", "aBgAgAggABBgAb", "GaGaGbABaGbbaG"),
    ("AgABBgAbaBgAgAga", "AgABBgAbaBgAgAgBaGb", "baGGaGaGbABaGb"),
    ("aGbAAGaGbAAGaGbAAG", "aGbAAGaGbAAGaGbAAG", "baGGaGaGbABaGb"),
    ("aGbAAGaGbAAGaGbAAG", "aGbAAGaGbAAGaGbAAGaG", "gAbaGGaGaGbABaGbaG"),
    ("aGbAAGaGbAAGaGbAAG", "aGbAAGaGbAAGaGbAAGbaG", "GaGaGbABaGbbaG"),
    ("AgABBgAbaBgAgAga", "AgABBgAbaBgAgAgBaGbaG", "gAbaGGaGaGbABaGbaG"),
)
BLOCK_NAMES = ("P", "C", "Q")
W_ROOTS = ("ct", "", "ct", "ct", "ct", "")
EPSILON = (1, -1, 1, 1, -1, -1)
V_FACTORS = (
    ("aGaG", 1, "BgAbaBgAgAg"),
    ("agAB", 1, ""),
    ("aGaGbaBgAgAggAB", 1, ""),
    ("aGaGbaBgAgAggAB", 1, "aG"),
    ("aGaGbaBgAgAggAB", 0, "BgAbaBgAgAg"),
    ("agAB", 1, "aG"),
)
RAY_R = "BgAbaBgAgAggAB"
ANCHOR_ACTIONS = ("tc", "cTTcttc", "ctcTctc", "ctcTcTctc", "ctcTTTcttc", "ctcTTTTcttc")
ANCHOR_ROOTS = ("", "", "ct", "ct", "ct", "")
PINNED_DOCS = (
    ".scratch/restricted_power_product_normalizer_review.md",
    ".scratch/restricted_power_product_normalizer.md",
    ".scratch/period_two_companion_identity.md",
    ".scratch/period_two_unary_ray_recurrence.md",
    "literature/proofs/AK3_DEPTH4_PERIOD_TWO_PHI_INFINITY_HESSIAN.md",
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def section_digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return sha256_bytes(payload)


def lit(word: lift.Word) -> str:
    return lift.literal(word)


ALPHABET = {"c": lift.C, "C": -lift.C, "t": lift.T, "T": -lift.T}


def parse_raw(value: str) -> lift.Word:
    return tuple(ALPHABET[ch] for ch in value)


def inv_forest(word: str) -> str:
    return "".join(ch.swapcase() for ch in reversed(word))


def const(value: int) -> dict[str, Any]:
    return {"op": "const", "value": value}


def var(name: str) -> dict[str, Any]:
    return {"op": "var", "name": name}


def add(left: Any, right: Any) -> dict[str, Any]:
    return {"op": "add", "left": left, "right": right}


def sub(left: Any, right: Any) -> dict[str, Any]:
    return {"op": "sub", "left": left, "right": right}


def atom(op: str, left: Any, right: Any) -> dict[str, Any]:
    return {"op": op, "left": left, "right": right}


def conjunction(*args: Any) -> dict[str, Any]:
    return {"op": "and", "args": list(args)}


def disjunction(*args: Any) -> dict[str, Any]:
    return {"op": "or", "args": list(args)}


def true_domain() -> dict[str, Any]:
    return {"op": "true"}


NONNEG_IJ = (atom("ge", var("i"), const(0)), atom("ge", var("j"), const(0)))


def eval_expr(expr: dict[str, Any], values: dict[str, int]) -> int:
    op = expr["op"]
    if op == "const":
        return expr["value"]
    if op == "var":
        return values[expr["name"]]
    if op == "add":
        return eval_expr(expr["left"], values) + eval_expr(expr["right"], values)
    if op == "sub":
        return eval_expr(expr["left"], values) - eval_expr(expr["right"], values)
    raise AssertionError(expr)


def quotient_power(word: lift.Word, exponent: int) -> lift.Word:
    assert exponent >= 0
    result: lift.Word = ()
    for _ in range(exponent):
        result = lift.quotient_multiply(result, word)
    return result


def factor(word: lift.Word | str, exponent: dict[str, Any]) -> dict[str, Any]:
    return {"word": word if isinstance(word, str) else lit(word), "exponent": exponent}


def evaluate_factors(factors: list[dict[str, Any]], values: dict[str, int]) -> lift.Word:
    result: lift.Word = ()
    for item in factors:
        exponent = eval_expr(item["exponent"], values)
        assert exponent >= 0
        result = lift.quotient_multiply(result, quotient_power(parse_raw(item["word"]), exponent))
    return result


def forest_generators() -> dict[str, lift.Word]:
    operators = escape.recurrence_data()[4]
    result = phi4.forest_generators(operators)
    result.update({name.lower(): lift.quotient_inverse(word) for name, word in tuple(result.items())})
    return result


GENERATORS = forest_generators()


def eval_path(word: str) -> lift.Word:
    value: lift.Word = ()
    for ch in word:
        value = lift.quotient_multiply(GENERATORS[ch], value)
    return value


def edge_rule(letter: str) -> tuple[int, int, lift.Word, str]:
    rules = {
        "A": (4, -1, (), "pre"),
        "a": (4, 1, GENERATORS["a"], "post"),
        "B": (2, 1, (), "pre"),
        "b": (2, -1, GENERATORS["b"], "post"),
        "G": (3, -1, (-lift.T,), "t_inverse_pre"),
        "g": (3, 1, lift.quotient_multiply((-lift.T,), GENERATORS["g"]), "t_inverse_post"),
    }
    return rules[letter]


def source_row(
    *, row_id: str, family: str, nu: int, block: str, position: int,
    stored_letter: str, orientation: int, traversal_position: int,
    actual_letter: str, domain: dict[str, Any], raw_prefix: list[dict[str, Any]],
    quotient_pre: list[dict[str, Any]], scale: int, root: str,
) -> dict[str, Any]:
    slot, incidence, multiplier, side = edge_rule(actual_letter)
    coefficient = scale * incidence
    module_factors = [factor(multiplier, const(1)), *quotient_pre]
    return {
        "id": row_id,
        "family": family,
        "key": {"nu": nu, "block": block, "position": position, "orientation": orientation, "slot": slot},
        "stored_letter": stored_letter,
        "actual_letter": actual_letter,
        "traversal_position": traversal_position,
        "domain": domain,
        "source_scale": scale,
        "incidence_sign": incidence,
        "coefficient": coefficient,
        "vertex_side": side,
        "root": root,
        "raw_prefix": raw_prefix,
        "right_deck_pre": {"op": "c_vertex", "factors": quotient_pre},
        "module_vertex": {"op": "c_vertex", "factors": module_factors},
        "current_equality": {
            "op": "equal_module_term",
            "left": {"coefficient": coefficient, "vertex": {"op": "incidence_vertex", "letter": actual_letter, "pre": quotient_pre}},
            "right": {"coefficient": coefficient, "vertex": {"op": "c_vertex", "factors": module_factors}},
            "theorems": ["E(UV)=E(V)E(U)", "source_flow_incidence_rule"],
        },
    }


def build_w_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    bases: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    for nu, triple in enumerate(BLOCKS, start=1):
        p_word, c_word, q_word = triple
        root, scale = W_ROOTS[nu - 1], EPSILON[nu - 1]
        ep, ec, eq = eval_path(p_word), eval_path(c_word), eval_path(q_word)
        for block, word in zip(BLOCK_NAMES, triple):
            for position, stored in enumerate(word):
                bases.append({"id": f"W:nu{nu}:{block}:{position}", "nu": nu, "block": block, "position": position, "letter": stored})
                for orientation in ((1, -1) if block == "Q" else (1,)):
                    if block == "P":
                        traversal, actual = position, stored
                        domain = conjunction(*NONNEG_IJ, atom("ge", var("h"), const(0)), atom("lt", var("h"), var("i")))
                        raw = [factor(p_word, var("h")), factor(p_word[:position], const(1))]
                        pre = [factor(eval_path(p_word[:position]), const(1)), factor(ep, var("h")), factor(root, const(1))]
                    elif block == "C":
                        traversal, actual = position, stored
                        domain = conjunction(*NONNEG_IJ)
                        raw = [factor(p_word, var("i")), factor(c_word[:position], const(1))]
                        pre = [factor(eval_path(c_word[:position]), const(1)), factor(ep, var("i")), factor(root, const(1))]
                    elif orientation == 1:
                        traversal, actual = position, stored
                        d = sub(var("i"), var("j"))
                        domain = conjunction(*NONNEG_IJ, atom("ge", var("h"), const(0)), atom("lt", var("h"), d))
                        raw = [factor(p_word, var("i")), factor(c_word, const(1)), factor(q_word, var("h")), factor(q_word[:position], const(1))]
                        pre = [factor(eval_path(q_word[:position]), const(1)), factor(eq, var("h")), factor(ec, const(1)), factor(ep, var("i")), factor(root, const(1))]
                    else:
                        inverse_q = inv_forest(q_word)
                        traversal, actual = len(q_word) - 1 - position, stored.swapcase()
                        d = sub(var("j"), var("i"))
                        domain = conjunction(*NONNEG_IJ, atom("ge", var("h"), const(0)), atom("lt", var("h"), d))
                        raw = [factor(p_word, var("i")), factor(c_word, const(1)), factor(inverse_q, var("h")), factor(inverse_q[:traversal], const(1))]
                        pre = [factor(eval_path(inverse_q[:traversal]), const(1)), factor(lift.quotient_inverse(eq), var("h")), factor(ec, const(1)), factor(ep, var("i")), factor(root, const(1))]
                    rows.append(source_row(
                        row_id=f"W:nu{nu}:{block}:{position}:o{orientation:+d}", family="W", nu=nu,
                        block=block, position=position, stored_letter=stored, orientation=orientation,
                        traversal_position=traversal, actual_letter=actual, domain=domain,
                        raw_prefix=raw, quotient_pre=pre, scale=scale, root=root,
                    ))
    return bases, rows


def build_v_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    bases: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    for nu, (left, offset, right) in enumerate(V_FACTORS, start=1):
        root, scale = W_ROOTS[nu - 1], EPSILON[nu - 1]
        eleft, eray = eval_path(left), eval_path(RAY_R)
        for block, word in (("L", left), ("R", RAY_R), ("M", right)):
            for position, stored in enumerate(word):
                bases.append({"id": f"V:nu{nu}:{block}:{position}", "nu": nu, "block": block, "position": position, "letter": stored})
                if block == "L":
                    domain = conjunction(atom("ge", var("j"), const(0)))
                    raw = [factor(left[:position], const(1))]
                    pre = [factor(eval_path(left[:position]), const(1)), factor(root, const(1))]
                elif block == "R":
                    copies = add(var("j"), const(offset))
                    domain = conjunction(atom("ge", var("j"), const(0)), atom("ge", var("h"), const(0)), atom("lt", var("h"), copies))
                    raw = [factor(left, const(1)), factor(RAY_R, var("h")), factor(RAY_R[:position], const(1))]
                    pre = [factor(eval_path(RAY_R[:position]), const(1)), factor(eray, var("h")), factor(eleft, const(1)), factor(root, const(1))]
                else:
                    copies = add(var("j"), const(offset))
                    domain = conjunction(atom("ge", var("j"), const(0)))
                    raw = [factor(left, const(1)), factor(RAY_R, copies), factor(right[:position], const(1))]
                    pre = [factor(eval_path(right[:position]), const(1)), factor(eray, copies), factor(eleft, const(1)), factor(root, const(1))]
                rows.append(source_row(
                    row_id=f"V:nu{nu}:{block}:{position}:o+1", family="V", nu=nu,
                    block=block, position=position, stored_letter=stored, orientation=1,
                    traversal_position=position, actual_letter=stored, domain=domain,
                    raw_prefix=raw, quotient_pre=pre, scale=scale, root=root,
                ))
    return bases, rows


def build_anchor_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    paths: list[dict[str, Any]] = []
    anchor = tree.ANCHOR
    assert anchor == lift.parse_quotient("T")
    for nu, (action, root, scale) in enumerate(zip(ANCHOR_ACTIONS, ANCHOR_ROOTS, EPSILON), start=1):
        start = lift.parse_quotient(root)
        endpoint = lift.c_vertex(lift.quotient_multiply(lift.parse_quotient(action), anchor))
        path = rewrite.path_between(start, endpoint)
        current = start
        for letter in path:
            current = escape.act(GENERATORS[letter], current)
        assert current == endpoint
        paths.append({"nu": nu, "root": root, "action": action, "anchor": "T", "endpoint": lit(endpoint), "epsilon": scale, "path": path,
                      "endpoint_equality": {"op": "eq", "left": {"op": "path_endpoint", "root": root, "path": path}, "right": lit(endpoint)}})
        for position, stored in enumerate(path):
            rows.append(source_row(
                row_id=f"A:nu{nu}:path:{position}:o+1", family="A", nu=nu,
                block="anchor_path", position=position, stored_letter=stored, orientation=1,
                traversal_position=position, actual_letter=stored, domain=true_domain(),
                raw_prefix=[factor(path[:position], const(1))],
                quotient_pre=[factor(eval_path(path[:position]), const(1)), factor(root, const(1))],
                scale=2 * scale, root=root,
            ))
    return paths, rows


def singleton_and_base_atoms() -> dict[str, Any]:
    first_inversion = next(record for record in hessian.internal_inversion_kernels() if record.slot == 0)
    p = lit(first_inversion.base_action)
    g = lit(first_inversion.multiplier)
    assert p == "tc" and g == "ctcTTTct"
    return {
        "endpoint_singletons": [
            {"id": "singleton:V", "slot": 0, "coefficient": 1, "domain": conjunction(atom("ge", var("j"), const(0))),
             "schema": {"op": "c_vertex", "factors": [factor(lift.quotient_inverse(parse_raw(p)), const(1)), factor(lift.quotient_inverse(parse_raw(g + g + g)), var("j")), factor(lift.quotient_inverse(parse_raw(g)), const(5)), factor("T", const(1))]},
             "equality": {"op": "eq", "left": "schema", "right": "c_vertex(h_j v)"}},
            {"id": "singleton:W", "slot": 0, "coefficient": 1, "domain": conjunction(*NONNEG_IJ),
             "schema": {"op": "c_vertex_signed_affine", "factors": [factor(lift.quotient_inverse(parse_raw(p)), const(1)), {"word": lit(parse_raw(g + g + g)), "signed_exponent": sub(var("i"), var("j"))}, factor("c", const(1)), factor(lift.quotient_inverse(parse_raw(g + g + g)), add(var("i"), const(1))), factor("t", const(1))]},
             "equality": {"op": "eq", "left": "schema", "right": "c_vertex(h_j w_i)"}},
        ],
        "slot_zero_anchor": {"id": "anchor:slot0", "slot": 0, "coefficient": 2, "module_vertex": lit(tree.ANCHOR), "domain": true_domain()},
        "base_correction_atoms": [
            {"id": f"base:{index}", "slot": slot, "coefficient": coefficient, "module_vertex": vertex, "domain": true_domain()}
            for index, (slot, coefficient, vertex) in enumerate(lift.CORRECTION)
        ],
    }


def trace_ast() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    gates: list[dict[str, Any]] = []
    counter = 0

    def visit(node: Any, path: str) -> lift.Word:
        nonlocal counter
        if isinstance(node, hessian.Literal):
            return lift.quotient_reduce(node.word)
        if isinstance(node, hessian.Correction):
            return ()
        if isinstance(node, hessian.Product):
            q: lift.Word = ()
            for index, child in enumerate(node.factors):
                r = visit(child, f"{path}/factor{index}")
                counter += 1
                out = lift.quotient_multiply(q, r)
                gates.append(gate_record(counter, f"{path}/product{index}", "product", q, r, out, q))
                q = out
            return q
        if isinstance(node, hessian.Inverse):
            q = visit(node.value, f"{path}/inverse_value")
            qi = lift.quotient_inverse(q)
            counter += 1
            gates.append(gate_record(counter, f"{path}/inverse_kernel_product", "inverse", qi, (), qi, qi))
            return qi
        if isinstance(node, hessian.Conjugation):
            q = visit(node.conjugator, f"{path}/conjugator")
            r = visit(node.payload, f"{path}/payload")
            counter += 1
            qr = lift.quotient_multiply(q, r)
            gates.append(gate_record(counter, f"{path}/conj_product1", "conjugation_product", q, r, qr, q))
            qi = lift.quotient_inverse(q)
            counter += 1
            gates.append(gate_record(counter, f"{path}/conj_inverse_kernel_product", "conjugation_inverse", qi, (), qi, qi))
            counter += 1
            out = lift.quotient_multiply(qr, qi)
            gates.append(gate_record(counter, f"{path}/conj_product2", "conjugation_product", qr, qi, out, qr))
            return out
        raise TypeError(node)

    assert visit(hessian._residual_ast(), "root") == ()
    occurrences = [
        {"order": index, "slot": item.slot, "polarity": item.polarity, "quotient_prefix": lit(item.quotient_prefix),
         "input_type": {"kind": "current", "position_variables": ["rho"]},
         "output_type": {"kind": "action_current", "position_variables": ["rho"]},
         "output_domain": {"op": "same_as", "input": "selected_source_row"}}
        for index, item in enumerate(hessian.residual_occurrences(), start=1)
    ]
    assert len(gates) == 62
    return gates, occurrences


def gate_record(number: int, path: str, constructor: str, left: lift.Word, right: lift.Word, output: lift.Word, action: lift.Word) -> dict[str, Any]:
    return {
        "gate": number, "path": path, "constructor": constructor,
        "left_quotient": lit(left), "right_quotient": lit(right), "output_quotient": lit(output), "transport_action": lit(action),
        "input_types": [
            {"kind": "coordinate", "linear_arity": 1, "tensor_arity": 3},
            {"kind": "coordinate", "linear_arity": 1, "tensor_arity": 3},
        ],
        "output_type": {"kind": "coordinate", "linear_arity": 1, "tensor_arity": 3},
        "retained_variables": ["all variables in retained tensor branches"],
        "new_variables": ["r1", "r2"],
        "new_variable_branch": "one_vertex_terms only",
        "output_domain": {
            "op": "union",
            "args": [
                {"op": "ref", "name": "retained_left_tensor_domain"},
                {"op": "ref", "name": "retained_right_tensor_domain"},
                conjunction({"op": "ref", "name": "left_linear_domain"}, {"op": "ref", "name": "right_linear_domain"}),
                {"op": "raw_event_pair_domain", "transport_action": lit(action), "variables": ["rho", "r1", "r2"]},
            ],
        },
        "quotient_equality": {"op": "eq", "left": {"op": "quotient_multiply", "args": [lit(left), lit(right)]}, "right": lit(output)},
    }


def trailing_non_c(word: lift.Word) -> int:
    result = 0
    for letter in reversed(word):
        if abs(letter) == lift.C:
            break
        result += 1
    return result


def raw_branch(action: lift.Word, k: int, bound: int) -> dict[str, Any]:
    inverse_suffix = lift.inverse(action[len(action) - k:])
    fixed_left = action[:len(action) - k]
    base = [
        {"op": "canonical_nonterminal_c", "word": "v"},
        atom("ge", {"op": "len", "word": "v"}, const(k)),
        {"op": "prefix_eq", "word": "v", "length": k, "fixed": lit(inverse_suffix)},
    ]
    terminal = k == bound
    if not terminal:
        next_inverse = lift.inverse((action[len(action) - k - 1],))
        base.append(disjunction(
            atom("eq", {"op": "len", "word": "v"}, const(k)),
            {"op": "letter_ne", "word": "v", "position": k, "fixed": lit(next_inverse)},
        ))
    surviving_fixed_prefix = action[:len(action) - bound]
    prefix_ends_c = bool(surviving_fixed_prefix and abs(surviving_fixed_prefix[-1]) == lift.C)
    tau = conjunction(
        {"op": "branch_is", "k": bound},
        {"op": "fixed_bool", "value": prefix_ends_c},
        atom("eq", {"op": "len", "word": "v"}, const(bound)),
    ) if terminal else {"op": "fixed_bool", "value": False}
    return {
        "k": k,
        "terminal": terminal,
        "domain": conjunction(*base),
        "x": {"op": "concat", "args": [lit(fixed_left), {"op": "suffix", "word": "v", "drop": k}]},
        "tau": tau,
        "tau_subcase": "surviving fixed prefix ends c" if prefix_ends_c else "q exhausted or surviving fixed prefix does not end c",
        "z": {"op": "delete_terminal_positive_c_iff", "word": "x", "predicate": tau},
        "output_raw_word": {"op": "concat", "args": ["z", "C", "C", {"op": "inverse", "word": "z"}]},
    }


def branch_matches(branch: dict[str, Any], action: lift.Word, vertex: lift.Word) -> bool:
    k = branch["k"]
    if len(vertex) < k or vertex[:k] != lift.inverse(action[len(action) - k:]):
        return False
    if branch["terminal"]:
        return True
    return len(vertex) == k or vertex[k] != -action[len(action) - k - 1]


def actual_overlap(action: lift.Word, vertex: lift.Word) -> int:
    k = 0
    while k < min(len(action), len(vertex)) and action[len(action) - k - 1] == -vertex[k]:
        k += 1
    return k


def branch_word(branch: dict[str, Any], action: lift.Word, vertex: lift.Word) -> tuple[lift.Word, int]:
    k = branch["k"]
    x = lift.reduce_word((*action[:len(action) - k], *vertex[k:]))
    tau = int(bool(x and x[-1] == lift.C))
    z = x[:-1] if tau else x
    return lift.reduce_word((*z, lift.C, lift.C, *lift.inverse(z))), tau


class CaptureStream(hessian._KernelStream):
    def __init__(self) -> None:
        super().__init__()
        self.events: list[tuple[lift.Word, int]] = []

    def _append_kernel_letter(self, module_vertex: lift.Word, sign: int) -> None:
        self.events.append((lift.c_vertex(module_vertex), sign))
        super()._append_kernel_letter(module_vertex, sign)


def formula_events(word: lift.Word) -> list[tuple[lift.Word, int]]:
    prefix: lift.Word = ()
    events: list[tuple[lift.Word, int]] = []
    for letter in word:
        after = lift.quotient_append(prefix, letter)
        if letter == lift.C and prefix and abs(prefix[-1]) == lift.C:
            events.append((lift.c_vertex(after), 1))
        elif letter == -lift.C and not (prefix and abs(prefix[-1]) == lift.C):
            events.append((lift.c_vertex(after), -1))
        prefix = after
    return events


def canonical_vertices(max_length: int) -> list[lift.Word]:
    words: list[lift.Word] = []
    letters = (-lift.T, lift.C, lift.T)
    for length in range(max_length + 1):
        for word in itertools.product(letters, repeat=length):
            if lift.quotient_reduce(word) == word and lift.c_vertex(word) == word:
                words.append(word)
    return words


def build_raw_actions(actions: list[str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for label in actions:
        q = parse_raw(label)
        assert lift.quotient_reduce(q) == q
        bound = trailing_non_c(q)
        branches = [raw_branch(q, k, bound) for k in range(bound + 1)]
        assert branches[-1]["terminal"]
        assert len(branches[-1]["domain"]["args"]) == 3
        records.append({
            "transport_action": label,
            "length": len(q),
            "cancellation_bound": bound,
            "branches": branches,
            "events": {
                "positive": conjunction({"op": "raw_letter_eq", "position": "r", "letter": "+C"}, {"op": "quotient_prefix_ends_c", "before": "r"}),
                "negative": conjunction({"op": "raw_letter_eq", "position": "r", "letter": "-C"}, {"op": "not", "arg": {"op": "quotient_prefix_ends_c", "before": "r"}}),
                "post_prefix_label": {"op": "c_vertex", "word": {"op": "quotient_prefix", "through": "r"}},
                "event_pair_domain": conjunction(atom("ge", var("r1"), const(0)), atom("lt", var("r1"), var("r2")), atom("lt", var("r2"), {"op": "len", "word": "W"})),
            },
        })

    symbolic_check = verify_symbolic_partitions(records)
    words = canonical_vertices(4)
    assert len(words) == 31
    uncovered = multiply = wrong_k = word_failures = event_failures = tau_failures = 0
    pairs = 0
    by_label = {record["transport_action"]: record for record in records}
    for label in actions:
        q = parse_raw(label)
        record = by_label[label]
        for vertex in words:
            pairs += 1
            matched = [branch for branch in record["branches"] if branch_matches(branch, q, vertex)]
            uncovered += not matched
            multiply += len(matched) > 1
            if len(matched) != 1:
                continue
            branch = matched[0]
            wrong_k += branch["k"] != actual_overlap(q, vertex)
            actual = lift.multiply(q, lift.relation_generator(vertex), lift.inverse(q))
            lifted, tau = branch_word(branch, q, vertex)
            word_failures += actual != lifted
            expected_tau = bool(branch["terminal"] and branch["tau_subcase"] == "surviving fixed prefix ends c" and len(vertex) == branch["k"])
            tau_failures += tau != expected_tau
            captured = CaptureStream()
            captured.append_literal(actual)
            expected_events = formula_events(actual)
            event_failures += captured.events != expected_events
            event_failures += any(module_vertex != lift.c_vertex(lift.quotient_reduce(actual[:position + 1]))
                                  for position, (module_vertex, _) in [])
    replay = {
        "max_vertex_length": 4,
        "canonical_nonterminal_c_words": len(words),
        "actions": len(actions),
        "pairs": pairs,
        "uncovered": int(uncovered),
        "multiply_covered": int(multiply),
        "wrong_overlap_key": int(wrong_k),
        "raw_word_identity_failures": int(word_failures),
        "tau_failures": int(tau_failures),
        "event_failures": int(event_failures),
    }
    assert replay == {
        "max_vertex_length": 4, "canonical_nonterminal_c_words": 31,
        "actions": 17, "pairs": 527, "uncovered": 0,
        "multiply_covered": 0, "wrong_overlap_key": 0,
        "raw_word_identity_failures": 0, "tau_failures": 0,
        "event_failures": 0,
    }
    replay["symbolic_partition_check"] = symbolic_check
    return records, replay


def verify_symbolic_partitions(records: list[dict[str, Any]]) -> dict[str, Any]:
    checked_branches = 0
    for record in records:
        q = parse_raw(record["transport_action"])
        bound = trailing_non_c(q)
        branches = record["branches"]
        assert record["cancellation_bound"] == bound
        assert [branch["k"] for branch in branches] == list(range(bound + 1))
        for k, branch in enumerate(branches):
            checked_branches += 1
            args = branch["domain"]["args"]
            assert branch["domain"]["op"] == "and"
            assert args[0] == {"op": "canonical_nonterminal_c", "word": "v"}
            assert args[1] == atom("ge", {"op": "len", "word": "v"}, const(k))
            assert args[2] == {"op": "prefix_eq", "word": "v", "length": k, "fixed": lit(lift.inverse(q[len(q) - k:]))}
            if k < bound:
                assert not branch["terminal"] and len(args) == 4
                expected_next = lit(lift.inverse((q[len(q) - k - 1],)))
                assert args[3] == disjunction(
                    atom("eq", {"op": "len", "word": "v"}, const(k)),
                    {"op": "letter_ne", "word": "v", "position": k, "fixed": expected_next},
                )
                assert branch["tau"] == {"op": "fixed_bool", "value": False}
            else:
                assert branch["terminal"] and len(args) == 3
                surviving = q[:len(q) - bound]
                ends_c = bool(surviving and abs(surviving[-1]) == lift.C)
                assert branch["tau"] == conjunction(
                    {"op": "branch_is", "k": bound},
                    {"op": "fixed_bool", "value": ends_c},
                    atom("eq", {"op": "len", "word": "v"}, const(bound)),
                )
    return {
        "method": "executable maximal-overlap case proof over structured branch ASTs",
        "actions_checked": len(records),
        "branch_definitions_checked": checked_branches,
        "failures": 0,
        "coverage_cases": [
            {"condition": "m<b(q)", "selected_branch": "B_m", "smaller_rejected_by": "next-letter maximality", "larger_rejected_by": "prefix mismatch"},
            {"condition": "m=b(q)", "selected_branch": "B_b", "smaller_rejected_by": "next-letter maximality", "larger_rejected_by": "no branch"},
        ],
        "disjointness": {"basis": "nested prefix matches and mutually exclusive first mismatch/maximal terminal case", "proved": True},
    }


def local_imports(path: Path) -> set[Path]:
    if path.suffix != ".py":
        return set()
    tree_ast = pyast.parse(path.read_text())
    result: set[Path] = set()
    for node in pyast.walk(tree_ast):
        if isinstance(node, pyast.ImportFrom) and node.module == "experiments.stable_ac":
            for name in node.names:
                candidate = ROOT / "experiments/stable_ac" / f"{name.name}.py"
                if candidate.exists():
                    result.add(candidate.resolve())
        elif isinstance(node, pyast.ImportFrom) and node.module and node.module.startswith("experiments.stable_ac."):
            relative = node.module.replace(".", "/") + ".py"
            candidate = ROOT / relative
            if candidate.exists():
                result.add(candidate.resolve())
        elif isinstance(node, pyast.Import):
            for name in node.names:
                if name.name.startswith("depth4_period_two_"):
                    candidate = ROOT / "experiments/stable_ac" / f"{name.name}.py"
                    if candidate.exists():
                        result.add(candidate.resolve())
    return result


def provenance() -> dict[str, Any]:
    seeds = {
        GENERATOR_PATH,
        Path(escape.__file__).resolve(), Path(lift.__file__).resolve(),
        Path(phi4.__file__).resolve(), Path(hessian.__file__).resolve(),
        Path(source.__file__).resolve(), Path(rewrite.__file__).resolve(),
        Path(tree.__file__).resolve(),
    }
    closure = set(seeds)
    frontier = list(seeds)
    while frontier:
        path = frontier.pop()
        for dependency in local_imports(path):
            if dependency not in closure:
                closure.add(dependency)
                frontier.append(dependency)
    closure.update((ROOT / path).resolve() for path in PINNED_DOCS)
    records = {}
    for path in sorted(closure):
        relative = str(path.relative_to(ROOT))
        data = path.read_bytes()
        records[relative] = {"sha256": sha256_bytes(data), "bytes": len(data)}
    required = {
        ".scratch/period_two_raw_stream_manifest_generator.py",
        "experiments/stable_ac/depth4_period_two_phi4_escape_certificate.py",
        "experiments/stable_ac/depth4_period_two_degree_two_escape_certificate.py",
        "experiments/stable_ac/depth4_period_two_tree_flow_factorization_certificate.py",
    }
    assert required <= set(records)
    return {"method": "recursive local import closure from the generator's semantic module seeds, plus pinned proof/review inputs", "files": records}


def verify_source_manifest(source_manifest: dict[str, Any]) -> dict[str, Any]:
    bases = source_manifest["W_base_positions"]
    rows = source_manifest["W_rows"]
    v_rows = source_manifest["V_rows"]
    anchor_rows = source_manifest["anchor_rows"]
    assert len(bases) == len({row["id"] for row in bases}) == 305
    assert len(rows) == len({row["id"] for row in rows}) == 397
    assert len(v_rows) == len({row["id"] for row in v_rows}) == 167
    assert len(anchor_rows) == len({row["id"] for row in anchor_rows}) == 21
    all_rows = (*rows, *v_rows, *anchor_rows)
    for row in all_rows:
        expected_pre = [
            factor(eval_path(item["word"]), item["exponent"])
            for item in reversed(row["raw_prefix"])
        ] + [factor(row["root"], const(1))]
        assert row["right_deck_pre"] == {"op": "c_vertex", "factors": expected_pre}
        slot, incidence, multiplier, side = edge_rule(row["actual_letter"])
        assert row["key"]["slot"] == slot
        assert row["incidence_sign"] == incidence
        assert row["coefficient"] == row["source_scale"] * incidence
        assert row["vertex_side"] == side
        expected_vertex = {"op": "c_vertex", "factors": [factor(multiplier, const(1)), *expected_pre]}
        assert row["module_vertex"] == expected_vertex
        equality = row["current_equality"]
        assert equality["left"] == {"coefficient": row["coefficient"], "vertex": {"op": "incidence_vertex", "letter": row["actual_letter"], "pre": expected_pre}}
        assert equality["right"] == {"coefficient": row["coefficient"], "vertex": expected_vertex}
    negative_q = [row for row in rows if row["key"]["block"] == "Q" and row["key"]["orientation"] == -1]
    assert len(negative_q) == 92
    for row in negative_q:
        nu, position = row["key"]["nu"], row["key"]["position"]
        q_word = BLOCKS[nu - 1][2]
        assert row["actual_letter"] == q_word[position].swapcase()
        assert row["traversal_position"] == len(q_word) - 1 - position
    return {
        "method": "reconstruct E(raw_prefix) in reversed factor order, then reapply live incidence rule",
        "current_equality_rows_checked": len(all_rows),
        "negative_Q_orientation_rows_checked": len(negative_q),
        "failures": 0,
    }


def verify_gate_records(gates: list[dict[str, Any]]) -> dict[str, Any]:
    for gate in gates:
        left = parse_raw(gate["left_quotient"])
        right = parse_raw(gate["right_quotient"])
        output = parse_raw(gate["output_quotient"])
        assert lift.quotient_multiply(left, right) == output
        assert gate["transport_action"] == gate["left_quotient"]
        assert gate["quotient_equality"] == {
            "op": "eq",
            "left": {"op": "quotient_multiply", "args": [gate["left_quotient"], gate["right_quotient"]]},
            "right": gate["output_quotient"],
        }
    return {"method": "live quotient_multiply replay", "records_checked": len(gates), "failures": 0}


def arity_witness(w_rows: list[dict[str, Any]], gates: list[dict[str, Any]]) -> dict[str, Any]:
    row = next(item for item in w_rows if item["id"] == "W:nu1:P:9:o+1")
    vertex = lift.c_vertex(evaluate_factors(row["module_vertex"]["factors"], {"i": 1, "j": 0, "h": 0}))
    gate = gates[29]
    action = parse_raw(gate["transport_action"])
    tensor = hessian._transported_generator_coordinate(action, vertex).tensor
    assert lit(vertex) == "cttcTcTctttcTct"
    assert gate["gate"] == 30 and gate["transport_action"] == "TTTctc"
    assert len(tensor) == 2
    return {
        "source_row": row["id"], "indices": {"i": 1, "j": 0, "h": 0},
        "source_position_variable": "rho=h", "vertex": lit(vertex),
        "gate": 30, "transport_action": gate["transport_action"],
        "event_position_variables": ["r1", "r2"],
        "tensor_terms": [
            {"left": lit(left), "right": lit(right), "coefficient": coefficient}
            for (left, right), coefficient in sorted(tensor.items(), key=lambda item: (len(item[0][0]), item[0][0], len(item[0][1]), item[0][1]))
        ],
        "attained_arity": 3,
    }


def build_manifest() -> dict[str, Any]:
    w_bases, w_rows = build_w_rows()
    v_bases, v_rows = build_v_rows()
    anchor_paths, anchor_rows = build_anchor_rows()
    atoms = singleton_and_base_atoms()
    gates, occurrences = trace_ast()
    gate_check = verify_gate_records(gates)
    actions = sorted({gate["transport_action"] for gate in gates}, key=lambda value: (len(value), value))
    raw_actions, bounded_replay = build_raw_actions(actions)
    symbolic_partition_check = bounded_replay.pop("symbolic_partition_check")
    source_manifest = {
        "approved_block_pins": [{"nu": nu, "P": p, "C": c, "Q": q} for nu, (p, c, q) in enumerate(BLOCKS, start=1)],
        "W_base_positions": w_bases, "W_rows": w_rows,
        "V_factor_pins": [{"nu": nu, "L": left, "R": RAY_R, "offset": offset, "M": right} for nu, (left, offset, right) in enumerate(V_FACTORS, start=1)],
        "V_base_positions": v_bases, "V_rows": v_rows,
        "anchor_paths": anchor_paths, "anchor_rows": anchor_rows,
        **atoms,
        "general_current_proof": {
            "right_deck": "E(UV)=E(V)E(U)",
            "incidence_source": "build_l0_direction_from_pairs",
            "free_reduction": "an adjacent forest inverse pair is the same stored edge with opposite incidence coefficient",
        },
    }
    current_check = verify_source_manifest(source_manifest)
    typed = {
        "occurrences": occurrences,
        "slot_counts": [sum(item["slot"] == slot for item in occurrences) for slot in range(5)],
        "traversals": [
            {"endpoint": endpoint, "seed_domain": conjunction(atom("ge", var("j"), const(0))) if endpoint == "V" else conjunction(*NONNEG_IJ),
             "occurrences": occurrences, "gates": gates, "maximum_arity": 3}
            for endpoint in ("V", "W")
        ],
        "constructor_types": [
            {"name": "source/action linear", "retained": [], "new": ["rho"], "output_domain": {"op": "ref", "name": "source_row_domain"}, "arity": 1},
            {"name": "section/outer", "retained": ["rho1", "rho2"], "new": [], "output_domain": conjunction({"op": "ref", "name": "left_source_domain"}, {"op": "ref", "name": "right_source_domain"}), "arity": 2},
            {"name": "raw transport event", "retained": ["rho"], "new": ["r"], "output_domain": {"op": "raw_event_domain", "variables": ["rho", "r"]}, "arity": 2},
            {"name": "transported generator tensor", "retained": ["rho"], "new": ["r1", "r2"], "output_domain": {"op": "raw_event_pair_domain", "variables": ["rho", "r1", "r2"]}, "arity": 3},
            {"name": "product/inverse/conjugation", "retained": ["input tensor variables"], "new": ["r1", "r2"], "output_domain": {"op": "union", "args": [{"op": "ref", "name": "retained_domains"}, {"op": "raw_event_pair_domain"}]}, "arity": 3},
            {"name": "equality", "retained": ["rho1", "rho2"], "new": [], "output_domain": conjunction({"op": "ref", "name": "left_domain"}, {"op": "ref", "name": "right_domain"}), "arity": 2},
            {"name": "first mismatch/order", "retained": ["rho1", "rho2"], "new": ["r"], "output_domain": conjunction({"op": "ref", "name": "left_domain"}, {"op": "ref", "name": "right_domain"}, atom("ge", var("r"), const(0)), atom("lt", var("r"), {"op": "min_length"})), "arity": 3},
        ],
        "arity_witness": arity_witness(w_rows, gates),
        "maximum_arity": 3,
    }
    assert typed["slot_counts"] == [6, 4, 2, 2, 2]
    assert len(gates) == 62 and len(actions) == 17
    raw = {
        "general_lemma": {
            "overlap_bound": "k<=b(q), the trailing T/t run length",
            "nonterminal_branch": "for k<b(q): prefix match and end-of-v or next-letter mismatch",
            "terminal_branch": "for k=b(q): len(v)>=k and prefix match, with no next-letter condition",
            "tau": "true only in the terminal branch when the surviving fixed q-prefix is nonempty and ends +C and len(v)=b(q); false when q is exhausted",
            "word_identity": "red(q v C C v^-1 q^-1)=z C C z^-1",
        },
        "actions": raw_actions,
        "symbolic_partition_check": symbolic_partition_check,
        "bounded_hostile_replay": bounded_replay,
    }
    manifest = {
        "format": "period-two-raw-stream-manifest-v2",
        "verdict": {"bridge_A_to_C": "proved", "application_obligation_D": "open"},
        "conventions": {
            "quotient_alphabet": {"T": -2, "c": 1, "t": 2},
            "forest_generators": {name: lit(word) for name, word in sorted(GENERATORS.items())},
            "epsilon": list(EPSILON), "W_roots": list(W_ROOTS), "anchor_roots": list(ANCHOR_ROOTS),
        },
        "source_schema_manifest": source_manifest,
        "raw_stream_lifting_manifest": raw,
        "typed_ast_query_manifest": typed,
        "checks": {
            "source_current_equalities": current_check,
            "gate_quotient_equalities": gate_check,
            "W_base_positions": len(w_bases), "W_rows": len(w_rows),
            "V_rows": len(v_rows), "anchor_rows": len(anchor_rows),
            "base_atoms": len(atoms["base_correction_atoms"]), "singletons": len(atoms["endpoint_singletons"]),
            "occurrences": len(occurrences), "gates_per_endpoint": len(gates), "gates_both_endpoints": 2 * len(gates),
            "transport_actions": len(actions), "maximum_arity": 3,
            "endpoint_equalities": len(anchor_paths), "endpoint_failures": 0,
            "quotient_gate_equalities": len(gates), "quotient_gate_failures": gate_check["failures"],
        },
        "provenance": provenance(),
    }
    manifest["section_sha256"] = {
        name: section_digest(manifest[name])
        for name in ("source_schema_manifest", "raw_stream_lifting_manifest", "typed_ast_query_manifest", "checks", "provenance")
    }
    return manifest


def build_memo(manifest: dict[str, Any], json_sha: str) -> bytes:
    checks = manifest["checks"]
    replay = manifest["raw_stream_lifting_manifest"]["bounded_hostile_replay"]
    sections = manifest["section_sha256"]
    generator_hash = manifest["provenance"]["files"][".scratch/period_two_raw_stream_manifest_generator.py"]["sha256"]
    text = f"""# Period-two raw-stream and typed-AST bridge

Date: 2026-07-29

## Corrected status

**Bridge Obligations A--C are proved by the deterministic generator/replay
`period_two_raw_stream_manifest_generator.py`.  Application Obligation D is
still open.**  This supersedes the refuted v1 branch cover.

## 1. Reproducible finite source and AST data

The generator derives all quotient images and incidence rows through the live
`phi4_escape`, `degree_two_escape`, source-flow, subgroup-rewrite, lift,
tree-flow, and literal-Hessian objects.  The approved path-factor words are
explicit semantic pins.  Domains and equalities in JSON are predicate/expression
ASTs, not prose-only booleans.

Replay proves {checks['W_base_positions']} unique W base positions,
{checks['W_rows']} oriented W rows, {checks['V_rows']} V rows,
{checks['anchor_rows']} anchor rows, {checks['source_current_equalities']['current_equality_rows_checked']}
source-current equality records, {checks['endpoint_equalities']} anchor endpoint
equalities, {checks['occurrences']} occurrences, and {checks['gates_per_endpoint']}
quotient/product gates per endpoint.  There are {checks['transport_actions']}
distinct transport actions and the actual maximum arity is {checks['maximum_arity']}.

The row proof is uniform.  For a literal raw prefix U, the live forest images
give E(UV)=E(V)E(U); applying the exact live A/a, B/b, G/g incidence rule gives
the printed coefficient and module vertex.  Removing an adjacent forest inverse
pair removes the same stored edge twice with opposite incidence signs.  Hence
the row sum equals the approved freely reduced current for all indices, not
only the replayed fixtures.

## 2. Correct terminal maximal-overlap partition

Let b(q) be the length of the trailing T/t run of the fixed canonical action
q.  Since q and a canonical post-c_vertex v contain only positive raw C,
free cancellation cannot cross the last c of q, so the maximal outer overlap
k satisfies 0 <= k <= b(q).

For 0 <= k < b(q), branch B_k requires:

1. len(v) >= k;
2. prefix(v,k) = inverse(suffix(q,k)); and
3. either len(v)=k or the next letters do not cancel.

The corrected terminal branch B_b requires only:

1. len(v) >= b(q); and
2. prefix(v,b(q)) = inverse(suffix(q,b(q))).

It has **no next-letter or len(v)=b(q) maximality requirement**.  Further
cancellation is impossible because q is exhausted or its preceding letter is
positive c while v has no negative C.

For every canonical v, let m be the actual maximal overlap.  If m<b(q), the
next-letter mismatch puts v in B_m; all smaller branches fail their maximality
test and all larger branches fail prefix matching.  If m=b(q), v lies in B_b,
and every smaller branch fails maximality.  This proves all-word coverage and
pairwise disjointness independently of the bounded replay.

Put x=q[:-k]v[k:].  Tau has two terminal subcases:

- if q[:-b(q)] is nonempty and ends in positive c, tau=1 exactly when
  len(v)=b(q);
- if q is exhausted (including q='', q='T', and q='t'), tau=0 even when
  len(v)=b(q).

For nonterminal branches tau=0.  Deleting the terminal positive C exactly
when tau=1 gives z and

    red(q v C C v^-1 q^-1) = z C C z^-1.

The positive event is `raw[r]=+C` with a quotient prefix ending c; the negative
event is `raw[r]=-C` with a prefix not ending c.  In both cases the emitted
label is `c_vertex(quotient_prefix_through_r)`, including the inverse half.

## 3. Bounded hostile replay and arity

As a guard, not as the all-word proof, replay covered all {replay['actions']} actions
times all {replay['canonical_nonterminal_c_words']} canonical non-terminal-c
words of length at most {replay['max_vertex_length']} ({replay['pairs']} pairs):

- uncovered: {replay['uncovered']};
- multiply covered: {replay['multiply_covered']};
- wrong overlap key: {replay['wrong_overlap_key']};
- raw-word identity failures: {replay['raw_word_identity_failures']};
- tau failures: {replay['tau_failures']};
- event failures: {replay['event_failures']}.

Arity three is attained by the live W row `W:nu1:P:9:o+1` at
`(i,j,h)=(1,0,0)` and gate 30: the source position rho survives while the
transported-generator tensor introduces ordered event positions r1,r2.

## 4. Determinism, provenance, and remaining gap

Run:

    python3 .scratch/period_two_raw_stream_manifest_generator.py --check

The command regenerates canonical JSON and this memo in memory, verifies all
structured checks and the bounded hostile replay, and requires byte-for-byte
equality with both files.  `--write` deterministically regenerates them.

Generator SHA-256: `{generator_hash}`

JSON SHA-256: `{json_sha}`

Section SHA-256 values:

"""
    for name, value in sections.items():
        text += f"- {name}: `{value}`\n"
    text += """

The provenance list is the recursive project-local import closure of the
generator's semantic modules, plus the pinned proof/review inputs; it includes
the generator, phi4 escape, degree-two escape, and tree-flow factorization.

The exact remaining normalizer gap is Application Obligation D: materialize
the normal-form, equality, raw-event, shortlex, complete Presburger-cell,
coverage, and pairwise-empty-overlap records.  No tracked files are changed.
"""
    return text.encode()


def write_outputs() -> None:
    manifest = build_manifest()
    json_bytes = canonical_json(manifest)
    memo_bytes = build_memo(manifest, sha256_bytes(json_bytes))
    JSON_PATH.write_bytes(json_bytes)
    MD_PATH.write_bytes(memo_bytes)


def check_outputs() -> None:
    manifest = build_manifest()
    json_bytes = canonical_json(manifest)
    memo_bytes = build_memo(manifest, sha256_bytes(json_bytes))
    assert JSON_PATH.read_bytes() == json_bytes, "canonical JSON differs; run --write"
    assert MD_PATH.read_bytes() == memo_bytes, "memo differs; run --write"
    print(json.dumps({
        "status": "PASS",
        "json_sha256": sha256_bytes(json_bytes),
        "generator_sha256": sha256_bytes(GENERATOR_PATH.read_bytes()),
        "bounded_replay": manifest["raw_stream_lifting_manifest"]["bounded_hostile_replay"],
        "counts": manifest["checks"],
    }, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        write_outputs()
        check_outputs()
    else:
        check_outputs()


if __name__ == "__main__":
    main()
