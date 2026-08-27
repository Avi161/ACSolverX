"""Independent four-corner replay for the anchored relative-bucket ledger.

This checker deliberately avoids ``symbolic_mixed_tensor``,
``symbolic_mixed_wedge``, and the existing relative-bucket checker.  It
builds the two anchored source-flow currents itself, then evaluates all four
raw residual coordinates through the production AST-coordinate interpreter.

Shared production helpers are limited to the quotient/module algebra, the
source-flow path construction, and the direct AST-coordinate evaluator.  In
particular, this does not use the occurrence expansion that produces the
symbolic mixed tensor, nor its wedge or double-coset postprocessing.
"""

from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.stable_ac import depth4_period_two_phi_infinity_hessian_certificate as hessian
from experiments.stable_ac import depth4_period_two_source_flow_certificate as source


PINNED = {
    "experiments/stable_ac/depth4_period_two_binomial_forest_certificate.py": "147cde85f0596bbb31729a3a8fcbe3ed60e4b1a02b6f5ab8f25c70efe25b7105",
    "experiments/stable_ac/depth4_period_two_degree_two_escape_certificate.py": "c07a27211d94dcf24aaabac1e4d388dad17c270d5944a73da30341671a391134",
    "experiments/stable_ac/depth4_period_two_lift_certificate.py": "ab5d428ed048d50bb5b4bb17196553af23982765d0e2c956178e41fb040af4b0",
    "experiments/stable_ac/depth4_period_two_phi4_escape_certificate.py": "cde8ce3ed746e7d87b4b1a16d99ffc66d63012c95dd83f727a24633e8e2844ed",
    "experiments/stable_ac/depth4_period_two_phi_infinity_hessian_certificate.py": "53fd6d7bffd317151786f02d94e6808da68b9a89cba666387512ca8167afd17f",
    "experiments/stable_ac/depth4_period_two_remote_syzygy_certificate.py": "15d054d6b796aa4773379db9eaa26bcccfb2c736d917382a0267fdf3bc08e8bc",
    "experiments/stable_ac/depth4_period_two_source_flow_certificate.py": "4c91efba651f95ece531a205ac19f562f1ba6de82044c89b7161c858ca14a9ba",
    "experiments/stable_ac/depth4_period_two_subgroup_rewrite_certificate.py": "9d93d0fca1404027b56ec4ddef8210b4d7e16724afbe4906c307363655608185",
}


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


for relative, expected in PINNED.items():
    actual = file_sha256(ROOT / relative)
    assert actual == expected, (relative, expected, actual)


lift = hessian.lift
escape = hessian.escape
H_WORDS = ((), (lift.C,))
ANCHOR = lift.parse_quotient("T")


def word_key(word: lift.Word) -> tuple[int, lift.Word]:
    return len(word), word


def clean_tensor(value: dict[tuple[lift.Word, lift.Word], int]) -> dict[tuple[lift.Word, lift.Word], int]:
    return {pair: coefficient for pair, coefficient in value.items() if coefficient}


def add_tensors(*values: dict[tuple[lift.Word, lift.Word], int]) -> dict[tuple[lift.Word, lift.Word], int]:
    result: dict[tuple[lift.Word, lift.Word], int] = defaultdict(int)
    for value in values:
        for pair, coefficient in value.items():
            result[pair] += coefficient
    return clean_tensor(result)


def scale_tensor(
    value: dict[tuple[lift.Word, lift.Word], int], coefficient: int,
) -> dict[tuple[lift.Word, lift.Word], int]:
    return clean_tensor({pair: coefficient * entry for pair, entry in value.items()})


def add_variables(*values: tuple[lift.ModuleVector, ...]) -> tuple[lift.ModuleVector, ...]:
    return tuple(lift.add_vectors(*(value[slot] for value in values)) for slot in range(5))


def anchored_direction(vertex: lift.Word) -> tuple[lift.ModuleVector, ...]:
    """Reconstruct H_0(vertex) without calling tree.anchored_direction."""
    _, _, _, _, operators = escape.recurrence_data()
    canonical_vertex = lift.c_vertex(vertex)
    boundary = lift.apply_operator(operators[0], {canonical_vertex: 1})
    first_orbit, second_orbit = source.orbit_sums(boundary)
    assert first_orbit + second_orbit == 0
    anchored_source = lift.add_vectors({canonical_vertex: 1}, {ANCHOR: -first_orbit})
    anchored_boundary = lift.apply_operator(operators[0], anchored_source)
    assert source.orbit_sums(anchored_boundary) == (0, 0)
    direction = source.build_l0_direction(anchored_source).variables
    assert len(direction) == 5
    assert not escape.correction_image(direction, operators)
    return direction


def direct_ast_coordinate(
    variables: tuple[lift.ModuleVector, ...],
) -> tuple[lift.ModuleVector, dict[tuple[lift.Word, lift.Word], int]]:
    """Evaluate the residual through the AST-coordinate path, not occurrences."""
    coordinate = hessian._evaluate_ast_coordinate(hessian._residual_ast(), variables)
    assert coordinate.quotient == ()
    return lift.add_vectors(coordinate.linear), clean_tensor(dict(coordinate.tensor))


def double_coset_words(word: lift.Word) -> frozenset[lift.Word]:
    return frozenset(
        lift.quotient_multiply(left, word, right)
        for left in H_WORDS
        for right in H_WORDS
    )


def canonical_bucket(
    left: lift.Word, right: lift.Word,
) -> tuple[lift.Word, bool, int]:
    """Canonicalize H\\Q/H independently, including D+/D- orientation."""
    relative = lift.quotient_multiply(lift.quotient_inverse(left), right)
    direct = double_coset_words(relative)
    inverse = double_coset_words(lift.quotient_inverse(relative))
    direct_representative = min(direct, key=word_key)
    inverse_representative = min(inverse, key=word_key)
    if word_key(direct_representative) <= word_key(inverse_representative):
        return direct_representative, direct == inverse, 1
    return inverse_representative, direct == inverse, -1


def tensor_to_wedge(
    tensor: dict[tuple[lift.Word, lift.Word], int],
) -> dict[tuple[lift.Word, lift.Word], int]:
    assert all(left != right for left, right in tensor), "mixed tensor diagonal is nonzero"
    for (left, right), coefficient in tensor.items():
        assert tensor.get((right, left), 0) == -coefficient, (
            "mixed tensor is not opposite-orientation antisymmetric"
        )
    return {
        (left, right): coefficient
        for (left, right), coefficient in tensor.items()
        if word_key(left) < word_key(right)
    }


base = escape.variables_from_entries(lift.CORRECTION)
F = anchored_direction(lift.parse_quotient("TTT"))
G = anchored_direction(lift.parse_quotient("cTTT"))

assert tuple(len(slot) for slot in F) == (2, 0, 10, 11, 14)
assert tuple(len(slot) for slot in G) == (2, 0, 7, 11, 12)

corners = tuple(
    direct_ast_coordinate(variables)
    for variables in (
        base,
        add_variables(base, F),
        add_variables(base, G),
        add_variables(base, F, G),
    )
)
(linear_00, raw_00), (linear_10, raw_10), (linear_01, raw_01), (linear_11, raw_11) = corners

mixed_linear = lift.add_vectors(
    linear_11,
    lift.scale_vector(linear_10, -1),
    lift.scale_vector(linear_01, -1),
    linear_00,
)
mixed_tensor = add_tensors(raw_11, scale_tensor(raw_10, -1), scale_tensor(raw_01, -1), raw_00)

assert not mixed_linear, "four-corner residual has nonzero linear coordinate"
wedge = tensor_to_wedge(mixed_tensor)

bucket_bits: dict[tuple[lift.Word, bool], int] = defaultdict(int)
bucket_integral_l1: dict[tuple[lift.Word, bool], int] = defaultdict(int)
oriented_integral: dict[lift.Word, int] = defaultdict(int)
for (first, second), coefficient in wedge.items():
    representative, self_inverse, orientation = canonical_bucket(first, second)
    key = representative, self_inverse
    bucket_bits[key] ^= coefficient & 1
    bucket_integral_l1[key] += abs(coefficient)
    if not self_inverse:
        oriented_integral[representative] += orientation * coefficient

mod2_nonzero = sorted(
    (
        {
            "representative": lift.literal(representative),
            "self_inverse": self_inverse,
            "integral_coordinate": None if self_inverse else oriented_integral[representative],
            "integral_l1_before_bucket_cancellation": bucket_integral_l1[(representative, self_inverse)],
        }
        for (representative, self_inverse), bit in bucket_bits.items()
        if bit
    ),
    key=lambda row: (row["self_inverse"], len(row["representative"]), row["representative"]),
)
free_odd = tuple(row for row in mod2_nonzero if not row["self_inverse"])
torsion_mod2 = tuple(row for row in mod2_nonzero if row["self_inverse"])
free_parity = len(free_odd) % 2
torsion_parity = len(torsion_mod2) % 2

payload = {
    "schema": "ak3-anchored-relative-buckets-independent-replay-v1",
    "inputs": ["TTT", "cTTT"],
    "shared_production_helpers": [
        "quotient/module algebra",
        "anchored source-flow path construction",
        "direct AST-coordinate evaluator",
    ],
    "excluded_helpers": [
        "symbolic_mixed_tensor",
        "symbolic_mixed_wedge",
        "period_two_anchored_relative_bucket_checker",
    ],
    "orientation_convention": "choose D+ by minimum (word length, integer-word tuple) across D and D^-1; HTH uses D+=HTH",
    "pinned_sha256": PINNED,
    "slot_support_sizes": {"F": [len(slot) for slot in F], "G": [len(slot) for slot in G]},
    "wedge_support": len(wedge),
    "wedge_l1": sum(abs(value) for value in wedge.values()),
    "mod2_nonzero_bucket_count": len(mod2_nonzero),
    "free_odd_count": len(free_odd),
    "torsion_mod2_nonzero_count": len(torsion_mod2),
    "free_parity": free_parity,
    "torsion_parity": torsion_parity,
    "mod2_nonzero_buckets": mod2_nonzero,
}
payload["ledger_sha256"] = sha256(
    json.dumps(payload["mod2_nonzero_buckets"], sort_keys=True, separators=(",", ":")).encode()
).hexdigest()

assert payload["wedge_support"] == 505
assert payload["wedge_l1"] == 2353
assert payload["mod2_nonzero_bucket_count"] == 51
assert payload["free_odd_count"] == 49
assert payload["torsion_mod2_nonzero_count"] == 2
assert payload["free_parity"] == 1
assert payload["torsion_parity"] == 0
assert payload["ledger_sha256"] == "87941b50f9d3b1fe8b6844a5235141a9f938550c186ff3160de295a43ddfeb90"
assert next(row for row in free_odd if row["representative"] == "T")["integral_coordinate"] == -1
assert tuple(row["representative"] for row in torsion_mod2) == ("tttcTTT", "ttctcTcTT")

summary = {
    key: payload[key]
    for key in (
        "schema",
        "inputs",
        "orientation_convention",
        "slot_support_sizes",
        "wedge_support",
        "wedge_l1",
        "mod2_nonzero_bucket_count",
        "free_odd_count",
        "torsion_mod2_nonzero_count",
        "free_parity",
        "torsion_parity",
        "ledger_sha256",
    )
}
summary["HTH_D_plus_integral_coordinate"] = next(
    row for row in free_odd if row["representative"] == "T"
)["integral_coordinate"]
summary["torsion_representatives"] = tuple(row["representative"] for row in torsion_mod2)
print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
