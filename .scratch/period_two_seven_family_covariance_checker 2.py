"""Direct chronological replay for the seven-family covariance remainder."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.stable_ac import (
    depth4_period_two_phi_infinity_hessian_certificate as hessian,
)
from experiments.stable_ac import (
    depth4_period_two_tree_flow_factorization_certificate as tree,
)

lift = hessian.lift
Word = tuple[int, ...]
Direction = tuple[dict[Word, int], ...]
AGGREGATE_CHECKER_PATH = ROOT / ".scratch/period_two_new_new_aggregate_checker.py"
AGGREGATE_MANIFEST_PATH = ROOT / ".scratch/period_two_new_new_aggregate_manifest.json"
INVERSE_CHECKER_PATH = ROOT / ".scratch/period_two_inverse_q_companion_checker.py"
INVERSE_MANIFEST_PATH = ROOT / ".scratch/period_two_inverse_q_companion_manifest.json"
MANIFEST_PATH = ROOT / ".scratch/period_two_seven_family_covariance_manifest.json"


@dataclass(frozen=True)
class Token:
    token_id: str
    coordinate: tuple[Any, ...]
    leaf: int
    occurrence: int | None
    polarity: int | None
    module_vertex: Word | None
    raw_position: int | None
    label: Word
    raw_weight: int


def parse_raw(value: str) -> Word:
    alphabet = {"c": lift.C, "C": -lift.C, "t": lift.T, "T": -lift.T}
    return tuple(alphabet[letter] for letter in value)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


P = parse_raw("tc")
G = lift.quotient_reduce(parse_raw("ctcTTTct"))
GAMMA = lift.quotient_multiply(G, G, G)
GAMMA_INVERSE = lift.quotient_inverse(GAMMA)
U = lift.quotient_reduce(parse_raw("cTctttcTcTctttcTcTctttcT"))


def raw_parser_guard() -> tuple[str, str]:
    return lift.literal(P), lift.literal(lift.quotient_inverse(P))


def signed_quotient_power(word: Word, exponent: int) -> Word:
    if exponent < 0:
        return signed_quotient_power(lift.quotient_inverse(word), -exponent)
    value: Word = ()
    for _ in range(exponent):
        value = lift.quotient_multiply(value, word)
    return value


def y_vertex(i: int, j: int) -> Word:
    assert i >= 0 and j >= 0
    return lift.c_vertex(
        lift.quotient_multiply(
            lift.quotient_inverse(P),
            signed_quotient_power(GAMMA, i - j),
            (lift.C,),
            signed_quotient_power(GAMMA_INVERSE, i + 1),
            (lift.T,),
        )
    )


def anchored_direction(i: int, j: int) -> Direction:
    return tree.anchored_direction(y_vertex(i, j))


def add_directions(*values: Direction) -> Direction:
    return tree.add_directions(*values)


def negate(value: Direction) -> Direction:
    return tree.scale_direction(value, -1)


def formula_events(word: Word) -> tuple[tuple[Word, int], ...]:
    prefix: Word = ()
    events = []
    for letter in word:
        after = lift.quotient_append(prefix, letter)
        if letter == lift.C and prefix and abs(prefix[-1]) == lift.C:
            events.append((lift.c_vertex(after), 1))
        elif letter == -lift.C and not (prefix and abs(prefix[-1]) == lift.C):
            events.append((lift.c_vertex(after), -1))
        prefix = after
    return tuple(events)


def raw_weight(action: Word, vertex: Word) -> int:
    raw_word = lift.multiply(
        action,
        lift.relation_generator(vertex),
        lift.inverse(action),
    )
    events = formula_events(raw_word)
    assert len(events) % 2 == 1
    middle = len(events) // 2
    central = lift.c_vertex(lift.quotient_multiply(action, vertex))
    assert events[middle][0] == central
    assert tuple(label for label, _ in events[:middle]) == tuple(
        label for label, _ in reversed(events[middle + 1 :])
    )
    return sum(label != central for label, _ in events[:middle]) % 2


def fixed_tokens() -> tuple[Token, ...]:
    prefix: Word = ()
    tokens = []
    for leaf_index, leaf in enumerate(hessian._expand(hessian._residual_ast()), start=1):
        if leaf.literal is None:
            continue
        for raw_position, letter in enumerate(leaf.literal, start=1):
            after = lift.quotient_append(prefix, letter)
            label = None
            emits_positive = letter == lift.C and prefix and abs(prefix[-1]) == lift.C
            emits_negative = letter == -lift.C and not (
                prefix and abs(prefix[-1]) == lift.C
            )
            if emits_positive or emits_negative:
                label = lift.c_vertex(after)
            if label is not None:
                tokens.append(
                    Token(
                        token_id=f"fixed:L{leaf_index}:r{raw_position}",
                        coordinate=("fixed", leaf_index, raw_position),
                        leaf=leaf_index,
                        occurrence=None,
                        polarity=None,
                        module_vertex=None,
                        raw_position=raw_position,
                        label=label,
                        raw_weight=0,
                    )
                )
            prefix = after
    assert prefix == ()
    return tuple(tokens)


FIXED_TOKENS = fixed_tokens()


def correction_tokens(
    value: Direction,
    source: str,
    *,
    compute_raw: bool = True,
) -> tuple[Token, ...]:
    tokens = []
    prefix: Word = ()
    occurrence = 0
    for leaf_index, leaf in enumerate(hessian._expand(hessian._residual_ast()), start=1):
        if leaf.literal is not None:
            prefix = lift.quotient_multiply(prefix, lift.quotient_reduce(leaf.literal))
            continue
        assert leaf.slot is not None
        occurrence += 1
        vertices = sorted(
            (vertex for vertex, coefficient in value[leaf.slot].items() if coefficient % 2),
            key=lambda word: (len(word), word),
            reverse=leaf.polarity == -1,
        )
        for vertex in vertices:
            tokens.append(
                Token(
                    token_id=f"{source}:o{occurrence}:{lift.literal(vertex) or 'eps'}",
                    coordinate=("correction", occurrence, vertex),
                    leaf=leaf_index,
                    occurrence=occurrence,
                    polarity=leaf.polarity,
                    module_vertex=vertex,
                    raw_position=None,
                    label=lift.c_vertex(lift.quotient_multiply(prefix, vertex)),
                    raw_weight=raw_weight(prefix, vertex) if compute_raw else 0,
                )
            )
    assert occurrence == 16 and prefix == ()
    return tuple(tokens)


def chronological_less(left: Token, right: Token) -> bool:
    if left.leaf != right.leaf:
        return left.leaf < right.leaf
    if left.occurrence is None and right.occurrence is None:
        assert left.raw_position != right.raw_position
        return left.raw_position < right.raw_position
    assert left.occurrence == right.occurrence
    assert left.module_vertex is not None and right.module_vertex is not None
    assert left.module_vertex != right.module_vertex
    assert left.polarity == right.polarity
    left_key = (len(left.module_vertex), left.module_vertex)
    right_key = (len(right.module_vertex), right.module_vertex)
    return left_key < right_key if left.polarity == 1 else left_key > right_key


def kernel(left: Token, right: Token) -> int:
    if left.coordinate == right.coordinate:
        return 0
    earlier, later = (left, right) if chronological_less(left, right) else (right, left)
    return int((len(earlier.label), earlier.label) < (len(later.label), later.label))


def quadratic(tokens: tuple[Token, ...]) -> int:
    return sum(kernel(left, right) for left, right in combinations(tokens, 2)) % 2


def bilinear(left: tuple[Token, ...], right: tuple[Token, ...]) -> int:
    return sum(kernel(left_token, right_token) for left_token in left for right_token in right) % 2


def raw_linear(tokens: tuple[Token, ...]) -> int:
    return sum(token.raw_weight for token in tokens) % 2


def endpoint_tokens(
    direction: Direction,
    source: str,
    *,
    compute_raw: bool = True,
) -> tuple[Token, ...]:
    current = add_directions(hessian._base_variables(), direction)
    return (
        *FIXED_TOKENS,
        *correction_tokens(current, source, compute_raw=compute_raw),
    )


def endpoint_value(direction: Direction, source: str) -> dict[str, int]:
    tokens = endpoint_tokens(direction, source)
    raw = raw_linear(tokens)
    sort = quadratic(tokens)
    return {"raw": raw, "sort": sort, "phi": raw ^ sort}


def terminal_vertex(i: int, d: int) -> Word:
    assert i >= d >= 1
    return lift.c_vertex(
        lift.quotient_multiply(
            parse_raw("T"),
            signed_quotient_power(GAMMA, d - 1),
            signed_quotient_power(U, i + 1),
            parse_raw("ct"),
        )
    )


def seven_family_rectangle(i: int, j: int) -> dict[str, Any]:
    d = i - j
    assert i >= d >= 1 and j >= 0
    a00 = anchored_direction(i, j)
    a01 = anchored_direction(i, j + 1)
    a11 = anchored_direction(i + 1, j + 1)
    a12 = anchored_direction(i + 1, j + 2)
    b = add_directions(a01, negate(a00))
    f = add_directions(a11, negate(a00))
    g = add_directions(a12, negate(a11), negate(a01), a00)
    g_zero = tuple(g[slot] if slot == 0 else {} for slot in range(5))
    g_q = tuple({} if slot == 0 else g[slot] for slot in range(5))

    terminal = terminal_vertex(i, d)
    terminal_coordinates = {
        ("correction", 9, terminal),
        ("correction", 14, terminal),
    }
    old_tokens = endpoint_tokens(a00, "a", compute_raw=False)
    assert sum(token.coordinate in terminal_coordinates for token in old_tokens) == 2
    old_excised = tuple(
        token for token in old_tokens if token.coordinate not in terminal_coordinates
    )
    b_tokens = correction_tokens(b, "b", compute_raw=False)
    f_tokens = correction_tokens(f, "f", compute_raw=False)
    g_zero_tokens = correction_tokens(g_zero, "g0", compute_raw=False)
    g_q_tokens = correction_tokens(g_q, "gQ", compute_raw=False)
    values = [
        bilinear(old_excised, g_zero_tokens),
        bilinear(old_excised, g_q_tokens),
        bilinear(b_tokens, f_tokens),
        bilinear(b_tokens, g_zero_tokens),
        bilinear(b_tokens, g_q_tokens),
        bilinear(f_tokens, g_zero_tokens),
        bilinear(f_tokens, g_q_tokens),
    ]
    return {
        "i": i,
        "j": j,
        "d": d,
        "seven_values": values,
        "seven_xor": sum(values) % 2,
    }


def direct_rectangle(i: int, j: int) -> dict[str, Any]:
    corners = (
        anchored_direction(i, j),
        anchored_direction(i, j + 1),
        anchored_direction(i + 1, j + 1),
        anchored_direction(i + 1, j + 2),
    )
    a00, a01, a11, a12 = corners
    b = add_directions(a01, negate(a00))
    f = add_directions(a11, negate(a00))
    g = add_directions(a12, negate(a11), negate(a01), a00)
    a_tokens = endpoint_tokens(a00, "a")
    b_tokens = correction_tokens(b, "b")
    f_tokens = correction_tokens(f, "f")
    g_tokens = correction_tokens(g, "g")
    cochain = raw_linear(g_tokens) ^ bilinear(a_tokens, g_tokens) ^ quadratic(g_tokens)
    terms = (
        cochain,
        bilinear(b_tokens, f_tokens),
        bilinear(b_tokens, g_tokens),
        bilinear(f_tokens, g_tokens),
    )
    return {
        "token_counts": {
            "a": len(a_tokens),
            "b": len(b_tokens),
            "f": len(f_tokens),
            "g": len(g_tokens),
        },
        "endpoint_values": [
            endpoint_value(direction, f"corner{index}")
            for index, direction in enumerate(corners)
        ],
        "cochain_and_three_bilinears": list(terms),
        "defect": sum(terms) % 2,
    }


def separate_path_fibers(
    aggregate: Any,
    inverse: Any,
    generator: Any,
    templates: dict[tuple[str, str], Any],
    metadata: dict[str, dict[str, Any]],
    cell: Any,
    delta: int,
) -> tuple[list[dict[str, Any]], dict[str, int], int]:
    rows = []
    for row_key, row in sorted(
        metadata.items(), key=lambda item: (item[1]["nu"], item[1]["k"])
    ):
        rows.append(
            {
                "id": f"{row_key}:delta{delta}",
                "row_key": row_key,
                "slot": row["slot"],
                "coefficient": row["source_sign"]
                * row["incidence"]
                * (1 if delta == 0 else -1),
                "module_schema": f"partner:module:{row_key}:delta{delta}",
            }
        )
    assert len(rows) == 92

    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    equality_methods: Counter[str] = Counter()
    equality_checks = 0
    for left_index, left in enumerate(rows):
        left_template = templates[(left["module_schema"], cell.cell_id)]
        left_key = (left["slot"], inverse.canonical_blocks(left_template))
        grouped.setdefault(left_key, []).append(left)
        for right in rows[left_index + 1 :]:
            if left["slot"] != right["slot"]:
                continue
            right_template = templates[(right["module_schema"], cell.cell_id)]
            comparison = aggregate.compare_templates(
                inverse, generator, left_template, right_template
            )
            equality_checks += 1
            equality_methods[comparison["method"]] += 1
            right_key = (right["slot"], inverse.canonical_blocks(right_template))
            assert (comparison["order"] == 0) == (left_key == right_key)

    occurrences_by_slot = {2: (1, 6), 3: (9, 14), 4: (15, 16)}
    fibers = []
    for members in grouped.values():
        members.sort(key=lambda item: item["id"])
        representative = members[0]
        coefficient_sum = sum(member["coefficient"] for member in members)
        action_schemas = {}
        for occurrence in occurrences_by_slot[representative["slot"]]:
            representative_action = (
                f"partner:action:{representative['row_key']}:"
                f"delta{delta}:o{occurrence}"
            )
            for member in members[1:]:
                member_action = (
                    f"partner:action:{member['row_key']}:"
                    f"delta{delta}:o{occurrence}"
                )
                comparison = aggregate.compare_templates(
                    inverse,
                    generator,
                    templates[(representative_action, cell.cell_id)],
                    templates[(member_action, cell.cell_id)],
                )
                assert comparison["order"] == 0
            action_schemas[str(occurrence)] = representative_action
        fibers.append(
            {
                "slot": representative["slot"],
                "members": [member["id"] for member in members],
                "integral_coefficient_sum": coefficient_sum,
                "activity_parity": coefficient_sum % 2,
                "module_schema": representative["module_schema"],
                "action_schemas": action_schemas,
            }
        )
    fibers.sort(key=lambda item: (item["slot"], item["members"]))
    return fibers, dict(sorted(equality_methods.items())), equality_checks


def symbolic_b_tokens(
    cell: Any,
    delta: int,
    g_zero_templates: dict[tuple[str, str], Any],
    g_q_templates: dict[tuple[str, str], Any],
    fibers: list[dict[str, Any]],
    occurrences: dict[int, dict[str, Any]],
    inverse: Any,
) -> list[dict[str, Any]]:
    corners = ("00", "01") if delta == 0 else ("11", "12")
    tokens = []
    for corner in corners:
        module_schema = f"g0:{corner}:module"
        for occurrence in (3, 4, 7, 8, 11, 12):
            module_template = g_zero_templates[(module_schema, cell.cell_id)]
            tokens.append(
                {
                    "id": f"b{delta}:g0:{corner}:o{occurrence}",
                    "source": f"b{delta}",
                    "occurrence": occurrence,
                    "polarity": occurrences[occurrence]["polarity"],
                    "module_schema": module_schema,
                    "module_template": module_template,
                    "label_schema": f"g0:{corner}:action:o{occurrence}",
                    "label_template": g_zero_templates[
                        (f"g0:{corner}:action:o{occurrence}", cell.cell_id)
                    ],
                    "coordinate_key": (
                        occurrence,
                        inverse.canonical_blocks(module_template),
                    ),
                }
            )
    for fiber_index, fiber in enumerate(fibers):
        if not fiber["activity_parity"]:
            continue
        for occurrence, action_schema in sorted(
            fiber["action_schemas"].items(), key=lambda item: int(item[0])
        ):
            occurrence_number = int(occurrence)
            module_template = g_q_templates[
                (fiber["module_schema"], cell.cell_id)
            ]
            tokens.append(
                {
                    "id": f"b{delta}:path:f{fiber_index:03d}:o{occurrence}",
                    "source": f"b{delta}",
                    "occurrence": occurrence_number,
                    "polarity": occurrences[occurrence_number]["polarity"],
                    "module_schema": fiber["module_schema"],
                    "module_template": module_template,
                    "label_schema": action_schema,
                    "label_template": g_q_templates[
                        (action_schema, cell.cell_id)
                    ],
                    "coordinate_key": (
                        occurrence_number,
                        inverse.canonical_blocks(module_template),
                    ),
                }
            )
    tokens.sort(key=lambda token: token["id"])
    assert len(tokens) == 84
    assert len({token["coordinate_key"] for token in tokens}) == 84
    return tokens


def symbolic_quadratic_result(
    aggregate: Any,
    inverse: Any,
    generator: Any,
    tokens: list[dict[str, Any]],
) -> dict[str, Any]:
    digest = hashlib.sha256()
    semantic_digest = hashlib.sha256()
    one_count = 0
    chronology_counts: Counter[str] = Counter()
    label_methods: Counter[str] = Counter()
    module_methods: Counter[str] = Counter()
    pair_count = 0
    for left_index, left in enumerate(tokens):
        for right in tokens[left_index + 1 :]:
            record = aggregate.pair_record(inverse, generator, left, right)
            digest.update(aggregate.canonical_line(record))
            semantic_digest.update(
                aggregate.canonical_line(aggregate.semantic_record(record))
            )
            one_count += record["bit"]
            pair_count += 1
            chronology_counts[record["chronology"]] += 1
            label_methods[record["label_method"]] += 1
            if record["module_method"] is not None:
                module_methods[record["module_method"]] += 1
    assert pair_count == 84 * 83 // 2 == 3486
    return {
        "pair_count": pair_count,
        "one_count": one_count,
        "Q": one_count % 2,
        "ordered_pair_digest_sha256": digest.hexdigest(),
        "semantic_pair_digest_sha256": semantic_digest.hexdigest(),
        "chronology_counts": dict(sorted(chronology_counts.items())),
        "label_method_counts": dict(sorted(label_methods.items())),
        "module_method_counts": dict(sorted(module_methods.items())),
    }


def symbolic_cross_result(
    aggregate: Any,
    inverse: Any,
    generator: Any,
    left_tokens: list[dict[str, Any]],
    right_tokens: list[dict[str, Any]],
) -> dict[str, Any]:
    digest = hashlib.sha256()
    one_count = 0
    equal_coordinates = 0
    comparison_count = 0
    for left in left_tokens:
        for right in right_tokens:
            comparison_count += 1
            if left["coordinate_key"] == right["coordinate_key"]:
                equal_coordinates += 1
                record = {
                    "left": left["id"],
                    "right": right["id"],
                    "equal_coordinate": True,
                    "bit": 0,
                }
            else:
                record = aggregate.pair_record(inverse, generator, left, right)
                record["equal_coordinate"] = False
                one_count += record["bit"]
            digest.update(aggregate.canonical_line(record))
    assert comparison_count == 84 * 84
    return {
        "comparison_count": comparison_count,
        "equal_coordinates": equal_coordinates,
        "one_count": one_count,
        "B_b0_b1": one_count % 2,
        "ordered_comparison_digest_sha256": digest.hexdigest(),
    }


def direct_b_replay(a: int, n: int) -> dict[str, Any]:
    i = a + n + 1
    j = n
    a00 = anchored_direction(i, j)
    a01 = anchored_direction(i, j + 1)
    a11 = anchored_direction(i + 1, j + 1)
    a12 = anchored_direction(i + 1, j + 2)
    b0 = add_directions(a01, negate(a00))
    b1 = add_directions(a12, negate(a11))
    b0_tokens = correction_tokens(b0, "b0", compute_raw=False)
    b1_tokens = correction_tokens(b1, "b1", compute_raw=False)
    assert len(b0_tokens) == len(b1_tokens) == 84
    q0 = quadratic(b0_tokens)
    q1 = quadratic(b1_tokens)
    return {
        "a": a,
        "n": n,
        "i": i,
        "d": a + 1,
        "Q_b0": q0,
        "Q_b1": q1,
        "B_b_g": q0 ^ q1,
        "token_counts": {"b0": len(b0_tokens), "b1": len(b1_tokens)},
    }


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_manifest() -> dict[str, Any]:
    aggregate = load_module("seven_family_aggregate_checker", AGGREGATE_CHECKER_PATH)
    inverse = load_module("seven_family_inverse_checker", INVERSE_CHECKER_PATH)
    generator = inverse.load_raw_generator()
    g_q_schemas, metadata = inverse.schema_words(generator)
    g_q_templates = aggregate.build_templates(inverse, generator, g_q_schemas)
    g_zero_schemas = aggregate.g_zero_schemas(inverse, generator)
    g_zero_templates = aggregate.build_templates(
        inverse, generator, g_zero_schemas
    )
    occurrences = {item["order"]: item for item in generator.trace_ast()[1]}

    cells = []
    for cell in aggregate.CELLS:
        fibers0, methods0, checks0 = separate_path_fibers(
            aggregate,
            inverse,
            generator,
            g_q_templates,
            metadata,
            cell,
            0,
        )
        fibers1, methods1, checks1 = separate_path_fibers(
            aggregate,
            inverse,
            generator,
            g_q_templates,
            metadata,
            cell,
            1,
        )
        tokens0 = symbolic_b_tokens(
            cell,
            0,
            g_zero_templates,
            g_q_templates,
            fibers0,
            occurrences,
            inverse,
        )
        tokens1 = symbolic_b_tokens(
            cell,
            1,
            g_zero_templates,
            g_q_templates,
            fibers1,
            occurrences,
            inverse,
        )
        q0 = symbolic_quadratic_result(
            aggregate, inverse, generator, tokens0
        )
        q1 = symbolic_quadratic_result(
            aggregate, inverse, generator, tokens1
        )
        cross = symbolic_cross_result(
            aggregate, inverse, generator, tokens0, tokens1
        )
        assert q0["Q"] == q1["Q"]
        assert cross["B_b0_b1"] == 0
        cells.append(
            {
                "cell": cell.cell_id,
                "predicate": {
                    "a": cell.a_value if cell.a_value is not None else ">=3",
                    "n": cell.n_value if cell.n_value is not None else ">=3",
                },
                "path_fibers": {
                    "b0": {
                        "total": len(fibers0),
                        "active": sum(fiber["activity_parity"] for fiber in fibers0),
                        "equality_checks": checks0,
                        "equality_methods": methods0,
                    },
                    "b1": {
                        "total": len(fibers1),
                        "active": sum(fiber["activity_parity"] for fiber in fibers1),
                        "equality_checks": checks1,
                        "equality_methods": methods1,
                    },
                },
                "token_counts": {"b0": len(tokens0), "b1": len(tokens1)},
                "pair_counts": {
                    "b0": q0["pair_count"],
                    "b1": q1["pair_count"],
                },
                "Q_b0": q0["Q"],
                "Q_b1": q1["Q"],
                "B_b_g": q0["Q"] ^ q1["Q"],
                "quadratic_records": {"b0": q0, "b1": q1},
                "cross_records": cross,
            }
        )

    direct_replays = []
    for cell in aggregate.CELLS:
        replay = direct_b_replay(cell.base_a, cell.base_n)
        symbolic = next(item for item in cells if item["cell"] == cell.cell_id)
        assert replay["Q_b0"] == symbolic["Q_b0"]
        assert replay["Q_b1"] == symbolic["Q_b1"]
        replay["cell"] = cell.cell_id
        direct_replays.append(replay)

    return {
        "format": "period-two-seven-family-covariance-v1",
        "domain": "a=d-1>=0, n=i-d>=0",
        "status": "partial theorem: B(b,g)=0; complete seven-family xor remains open",
        "raw_parser_guard": {"p": raw_parser_guard()[0], "p_inverse": raw_parser_guard()[1]},
        "theorem": {
            "name": "diagonal invariance of the j-increment quadratic",
            "formula": "Q(b_(n+1,d))=Q(b_(n,d)), hence B(b,g)=0",
            "cell_values": {item["cell"]: item["B_b_g"] for item in cells},
        },
        "cells": cells,
        "direct_replays": direct_replays,
        "checks": {
            "cells": len(cells),
            "tokens_per_edge": 84,
            "pairs_per_edge": 3486,
            "pairs_all_cells": 2 * 16 * 3486,
            "cross_comparisons_all_cells": 16 * 84 * 84,
            "direct_replays": len(direct_replays),
            "coverage_failures": 0,
            "collision_failures": 0,
            "chronology_failures": 0,
            "quadratic_equality_failures": 0,
            "direct_replay_failures": 0,
        },
        "provenance": {
            "inputs": {
                str(AGGREGATE_CHECKER_PATH.relative_to(ROOT)): sha256_path(AGGREGATE_CHECKER_PATH),
                str(AGGREGATE_MANIFEST_PATH.relative_to(ROOT)): sha256_path(AGGREGATE_MANIFEST_PATH),
                str(INVERSE_CHECKER_PATH.relative_to(ROOT)): sha256_path(INVERSE_CHECKER_PATH),
                str(INVERSE_MANIFEST_PATH.relative_to(ROOT)): sha256_path(INVERSE_MANIFEST_PATH),
                ".scratch/period_two_new_new_aggregate.md": sha256_path(ROOT / ".scratch/period_two_new_new_aggregate.md"),
                ".scratch/period_two_residual_augmented_defect.md": sha256_path(ROOT / ".scratch/period_two_residual_augmented_defect.md"),
            },
            "checker_sha256": sha256_path(Path(__file__).resolve()),
        },
    }


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def write_manifest() -> dict[str, Any]:
    manifest = build_manifest()
    MANIFEST_PATH.write_bytes(canonical_json(manifest))
    return manifest


def check_manifest() -> dict[str, Any]:
    manifest = build_manifest()
    assert MANIFEST_PATH.read_bytes() == canonical_json(manifest)
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--summary", action="store_true")
    arguments = parser.parse_args()
    if arguments.write:
        output = write_manifest()
    elif arguments.check:
        output = check_manifest()
    else:
        output = build_manifest()
    print(
        json.dumps(
            {
                "status": "PASS",
                "theorem": output["theorem"],
                "checks": output["checks"],
            },
            indent=2,
            sort_keys=True,
        )
    )
