from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.stable_ac import depth4_period_two_phi_infinity_hessian_certificate as hessian
from experiments.stable_ac import depth4_period_two_tree_flow_factorization_certificate as tree


PINNED = {
    "experiments/stable_ac/depth4_period_two_binomial_forest_certificate.py": "147cde85f0596bbb31729a3a8fcbe3ed60e4b1a02b6f5ab8f25c70efe25b7105",
    "experiments/stable_ac/depth4_period_two_degree_two_escape_certificate.py": "c07a27211d94dcf24aaabac1e4d388dad17c270d5944a73da30341671a391134",
    "experiments/stable_ac/depth4_period_two_phi_infinity_hessian_certificate.py": "53fd6d7bffd317151786f02d94e6808da68b9a89cba666387512ca8167afd17f",
    "experiments/stable_ac/depth4_period_two_phi4_escape_certificate.py": "cde8ce3ed746e7d87b4b1a16d99ffc66d63012c95dd83f727a24633e8e2844ed",
    "experiments/stable_ac/depth4_period_two_remote_syzygy_certificate.py": "15d054d6b796aa4773379db9eaa26bcccfb2c736d917382a0267fdf3bc08e8bc",
    "experiments/stable_ac/depth4_period_two_source_flow_certificate.py": "4c91efba651f95ece531a205ac19f562f1ba6de82044c89b7161c858ca14a9ba",
    "experiments/stable_ac/depth4_period_two_subgroup_rewrite_certificate.py": "9d93d0fca1404027b56ec4ddef8210b4d7e16724afbe4906c307363655608185",
    "experiments/stable_ac/depth4_period_two_tree_flow_factorization_certificate.py": "bf354d949bbf21775d559e0a1058949ce8566630649ddbb00ce875e2c2857404",
    "experiments/stable_ac/depth4_period_two_lift_certificate.py": "ab5d428ed048d50bb5b4bb17196553af23982765d0e2c956178e41fb040af4b0",
}


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


for relative, expected in PINNED.items():
    actual = file_sha256(ROOT / relative)
    assert actual == expected, (relative, expected, actual)


lift = hessian.lift
H_WORDS = ((), (lift.C,))


def word_key(word: lift.Word) -> tuple[int, lift.Word]:
    return len(word), word


def double_coset_words(word: lift.Word) -> frozenset[lift.Word]:
    return frozenset(
        lift.quotient_multiply(left, word, right)
        for left in H_WORDS
        for right in H_WORDS
    )


def bucket_record(left: lift.Word, right: lift.Word) -> tuple[lift.Word, bool, int]:
    relative = lift.quotient_multiply(lift.quotient_inverse(left), right)
    direct = double_coset_words(relative)
    inverse = double_coset_words(lift.quotient_inverse(relative))
    direct_representative = min(direct, key=word_key)
    inverse_representative = min(inverse, key=word_key)
    if word_key(direct_representative) <= word_key(inverse_representative):
        return direct_representative, direct == inverse, 1
    return inverse_representative, direct == inverse, -1


left = tree.anchored_direction(lift.parse_quotient("TTT"))
right = tree.anchored_direction(lift.parse_quotient("cTTT"))
wedge = hessian.symbolic_mixed_wedge(left, right)
subtotals = hessian.anchored_hessian_subtotals(
    lift.parse_quotient("TTT"),
    lift.parse_quotient("cTTT"),
)

bucket_bits: dict[tuple[lift.Word, bool], int] = defaultdict(int)
bucket_integral_l1: dict[tuple[lift.Word, bool], int] = defaultdict(int)
oriented_integral: dict[lift.Word, int] = defaultdict(int)
for (first, second), coefficient in wedge.items():
    representative, self_inverse, orientation = bucket_record(first, second)
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
torsion_mod2_nonzero = tuple(row for row in mod2_nonzero if row["self_inverse"])
free_parity = len(free_odd) % 2
torsion_parity = len(torsion_mod2_nonzero) % 2
full_wedge_parity = sum(wedge.values()) % 2
free_integral_nonzero_count = sum(value != 0 for value in oriented_integral.values())

assert full_wedge_parity == hessian.beta_infinity(
    lift.parse_quotient("TTT"),
    lift.parse_quotient("cTTT"),
) == 1
assert (free_parity + torsion_parity) % 2 == full_wedge_parity
assert subtotals.total == full_wedge_parity
assert all(row["integral_coordinate"] % 2 for row in free_odd)

payload = {
    "schema": "ak3-anchored-relative-buckets-v1",
    "inputs": ["TTT", "cTTT"],
    "orientation_convention": "choose D+ by minimum (word length, integer-word tuple) across D and D^-1; HTH uses D+=HTH",
    "pinned_sha256": PINNED,
    "slot_support_sizes": {
        "left": [len(slot) for slot in left],
        "right": [len(slot) for slot in right],
    },
    "wedge_support": len(wedge),
    "wedge_l1": sum(abs(value) for value in wedge.values()),
    "kernel_subtotals": {
        "equality_terms": subtotals.equality_terms,
        "inversion_terms": subtotals.inversion_terms,
        "external": subtotals.external,
        "total": subtotals.total,
    },
    "mod2_nonzero_bucket_count": len(mod2_nonzero),
    "free_odd_count": len(free_odd),
    "torsion_mod2_nonzero_count": len(torsion_mod2_nonzero),
    "free_integral_nonzero_count": free_integral_nonzero_count,
    "free_parity": free_parity,
    "torsion_parity": torsion_parity,
    "full_wedge_parity": full_wedge_parity,
    "mod2_nonzero_buckets": mod2_nonzero,
}
payload["ledger_sha256"] = sha256(
    json.dumps(payload["mod2_nonzero_buckets"], sort_keys=True, separators=(",", ":")).encode()
).hexdigest()

assert payload["slot_support_sizes"] == {
    "left": [2, 0, 10, 11, 14],
    "right": [2, 0, 7, 11, 12],
}
assert payload["wedge_support"] == 505
assert payload["wedge_l1"] == 2353
assert subtotals.equality_terms == (1, 1, 0, 0)
assert subtotals.inversion_terms == (0, 0, 0, 0, 0, 1)
assert payload["mod2_nonzero_bucket_count"] == 51
assert payload["free_odd_count"] == 49
assert payload["torsion_mod2_nonzero_count"] == 2
assert payload["free_integral_nonzero_count"] == 238
assert payload["free_parity"] == 1
assert payload["torsion_parity"] == 0
assert payload["ledger_sha256"] == "87941b50f9d3b1fe8b6844a5235141a9f938550c186ff3160de295a43ddfeb90"
assert next(
    row for row in free_odd if row["representative"] == "T"
)["integral_coordinate"] == -1
assert tuple(row["representative"] for row in torsion_mod2_nonzero) == (
    "tttcTTT",
    "ttctcTcTT",
)
summary = {
    key: payload[key]
    for key in (
        "schema",
        "inputs",
        "orientation_convention",
        "slot_support_sizes",
        "wedge_support",
        "wedge_l1",
        "kernel_subtotals",
        "mod2_nonzero_bucket_count",
        "free_odd_count",
        "torsion_mod2_nonzero_count",
        "free_integral_nonzero_count",
        "free_parity",
        "torsion_parity",
        "full_wedge_parity",
        "ledger_sha256",
    )
}
summary["T_integral_coordinate"] = next(
    row for row in free_odd if row["representative"] == "T"
)["integral_coordinate"]
summary["torsion_representatives"] = tuple(
    row["representative"] for row in torsion_mod2_nonzero
)
print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
