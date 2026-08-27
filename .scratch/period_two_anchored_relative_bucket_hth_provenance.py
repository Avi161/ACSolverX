"""Report complete signed production provenance for the free HTH bucket.

The output isolates every canonically ordered wedge pair whose H\\Q/H
representative is ``T`` (the HTH double coset), including its signed wedge
coefficient, D+/D- orientation, and each production mixed-tensor subtotal.
``MixedTensorSubtotals`` aggregates occurrence-level terms, so the emitted
categories are complete subtotal provenance but cannot identify a unique
individual AST occurrence for a surviving ordered pair.
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
from experiments.stable_ac import depth4_period_two_tree_flow_factorization_certificate as tree


# Full local import closure of the two production modules above.
PINNED = {
    "experiments/stable_ac/depth4_period_two_binomial_forest_certificate.py": "147cde85f0596bbb31729a3a8fcbe3ed60e4b1a02b6f5ab8f25c70efe25b7105",
    "experiments/stable_ac/depth4_period_two_cyclic_degree_two_obstruction_certificate.py": "96b145bb312f9c18a277d13bd6fe5edc2b46dac2873f4fbdc69eb52964fae1a4",
    "experiments/stable_ac/depth4_period_two_degree_two_escape_certificate.py": "c07a27211d94dcf24aaabac1e4d388dad17c270d5944a73da30341671a391134",
    "experiments/stable_ac/depth4_period_two_depth6_l0_census_certificate.py": "705deadd0833736801f85563a39f77aa54e081115c0f778dfa641f0ea5d5db77",
    "experiments/stable_ac/depth4_period_two_eight_direction_obstruction_certificate.py": "bc5973c30e9bf92a1ae6433750325b95ae663298ae74547d1085358f5b32fda5",
    "experiments/stable_ac/depth4_period_two_eleven_direction_obstruction_certificate.py": "75faaef89bfccc2b1dabddb836c5cd685cf15aed295fae5dea3e35f39cdd8967",
    "experiments/stable_ac/depth4_period_two_five_direction_obstruction_certificate.py": "7010369819167b9132d799d5dc7644cc7c4d3381b616177970b77184eaab2f12",
    "experiments/stable_ac/depth4_period_two_lift_certificate.py": "ab5d428ed048d50bb5b4bb17196553af23982765d0e2c956178e41fb040af4b0",
    "experiments/stable_ac/depth4_period_two_mod3_escape_obstruction_certificate.py": "7923962dda69be1cfddc2ae68f0590c32927d8aeaff835bfcaafdb46740704ed",
    "experiments/stable_ac/depth4_period_two_nine_direction_obstruction_certificate.py": "0f4f4bfad11adb5e3cefaaa17120c51e84dd9d0902082eaebb46caf523fac292",
    "experiments/stable_ac/depth4_period_two_phi4_escape_certificate.py": "cde8ce3ed746e7d87b4b1a16d99ffc66d63012c95dd83f727a24633e8e2844ed",
    "experiments/stable_ac/depth4_period_two_phi_infinity_hessian_certificate.py": "53fd6d7bffd317151786f02d94e6808da68b9a89cba666387512ca8167afd17f",
    "experiments/stable_ac/depth4_period_two_remote_syzygy_certificate.py": "15d054d6b796aa4773379db9eaa26bcccfb2c736d917382a0267fdf3bc08e8bc",
    "experiments/stable_ac/depth4_period_two_seven_direction_obstruction_certificate.py": "4ca96f93716ec52fe6bcded41dba873e3e85e3dae73926c00c7383893ec9daae",
    "experiments/stable_ac/depth4_period_two_six_direction_obstruction_certificate.py": "8e1234a3f5a7b7ef01fa22016c23e36a4ccf9f45415a9baa69b772f7d257a3fc",
    "experiments/stable_ac/depth4_period_two_source_flow_certificate.py": "4c91efba651f95ece531a205ac19f562f1ba6de82044c89b7161c858ca14a9ba",
    "experiments/stable_ac/depth4_period_two_subgroup_rewrite_certificate.py": "9d93d0fca1404027b56ec4ddef8210b4d7e16724afbe4906c307363655608185",
    "experiments/stable_ac/depth4_period_two_ten_direction_obstruction_certificate.py": "b16a73bfb7f00d35db6d92b052c9d359c16b3032037cfe81b1c4f3c060888091",
    "experiments/stable_ac/depth4_period_two_tree_flow_factorization_certificate.py": "bf354d949bbf21775d559e0a1058949ce8566630649ddbb00ce875e2c2857404",
}


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


for relative, expected in PINNED.items():
    actual = file_sha256(ROOT / relative)
    assert actual == expected, (relative, expected, actual)


lift = hessian.lift
H_WORDS = ((), (lift.C,))
HTH_REPRESENTATIVE = lift.parse_quotient("T")


def word_key(word: lift.Word) -> tuple[int, lift.Word]:
    return len(word), word


def double_coset_words(word: lift.Word) -> frozenset[lift.Word]:
    return frozenset(
        lift.quotient_multiply(left, word, right)
        for left in H_WORDS
        for right in H_WORDS
    )


def bucket_record(left: lift.Word, right: lift.Word) -> tuple[lift.Word, bool, int]:
    """Return the canonical H\\Q/H representative, torsion flag, and sign."""
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
subtotals = hessian.symbolic_mixed_subtotals(left, right)
category_tensors = {
    "positive_internal": subtotals.positive_internal,
    "negative_internal": subtotals.negative_internal,
    "external": subtotals.external,
    "propagated_diagonal": subtotals.propagated_diagonal,
}
wedge = hessian.symbolic_mixed_wedge(left, right)

# Replay the production external loop term-for-term, retaining the literal
# occurrence positions that ``MixedTensorSubtotals.external`` intentionally
# aggregates away.
occurrences = hessian.residual_occurrences()
external_replay: dict[tuple[lift.Word, lift.Word], int] = defaultdict(int)
hth_external_terms = []
for left_index, left_occurrence in enumerate(occurrences):
    left_F = hessian._action(left_occurrence.quotient_prefix, left[left_occurrence.slot])
    left_G = hessian._action(left_occurrence.quotient_prefix, right[left_occurrence.slot])
    for right_index, right_occurrence in enumerate(occurrences[left_index + 1:], left_index + 1):
        right_F = hessian._action(right_occurrence.quotient_prefix, left[right_occurrence.slot])
        right_G = hessian._action(right_occurrence.quotient_prefix, right[right_occurrence.slot])
        occurrence_sign = left_occurrence.polarity * right_occurrence.polarity
        legs = (
            ("F_at_left__G_at_right", "F", left_F, "G", right_G),
            ("G_at_left__F_at_right", "G", left_G, "F", right_F),
        )
        for leg_name, first_direction, first_vector, second_direction, second_vector in legs:
            term = hessian._scale_tensor(
                hessian._outer(first_vector, second_vector), occurrence_sign,
            )
            for pair, contribution in term.items():
                external_replay[pair] += contribution
                first, second = pair
                # The production wedge retains precisely this canonical order.
                if word_key(first) >= word_key(second):
                    continue
                representative, self_inverse, orientation = bucket_record(first, second)
                if representative != HTH_REPRESENTATIVE or self_inverse:
                    continue
                hth_external_terms.append({
                    "ordered_wedge_pair": [lift.literal(first), lift.literal(second)],
                    "left_occurrence": {
                        "index": left_index,
                        "slot": left_occurrence.slot,
                        "polarity": left_occurrence.polarity,
                        "quotient_prefix": lift.literal(left_occurrence.quotient_prefix),
                    },
                    "right_occurrence": {
                        "index": right_index,
                        "slot": right_occurrence.slot,
                        "polarity": right_occurrence.polarity,
                        "quotient_prefix": lift.literal(right_occurrence.quotient_prefix),
                    },
                    "leg_assignment": leg_name,
                    "first_leg_direction": first_direction,
                    "second_leg_direction": second_direction,
                    "occurrence_sign": occurrence_sign,
                    "signed_wedge_contribution": contribution,
                    "bucket_orientation": orientation,
                    "signed_oriented_bucket_contribution": orientation * contribution,
                })

external_replay = {pair: coefficient for pair, coefficient in external_replay.items() if coefficient}
assert external_replay == subtotals.external
assert sum(abs(coefficient) for coefficient in external_replay.values()) == sum(
    abs(coefficient) for coefficient in subtotals.external.values()
)

external_hth_by_pair: dict[tuple[lift.Word, lift.Word], int] = defaultdict(int)
for term in hth_external_terms:
    first_label, second_label = term["ordered_wedge_pair"]
    pair = lift.parse_quotient(first_label), lift.parse_quotient(second_label)
    external_hth_by_pair[pair] += term["signed_wedge_contribution"]
for pair, coefficient in external_hth_by_pair.items():
    assert coefficient == subtotals.external.get(pair, 0), (pair, coefficient, subtotals.external.get(pair, 0))

rows = []
category_oriented_totals: dict[str, int] = defaultdict(int)
for (first, second), coefficient in sorted(wedge.items(), key=lambda item: (word_key(item[0][0]), word_key(item[0][1]))):
    representative, self_inverse, orientation = bucket_record(first, second)
    if representative != HTH_REPRESENTATIVE or self_inverse:
        continue
    category_coefficients = {
        category: tensor.get((first, second), 0)
        for category, tensor in category_tensors.items()
    }
    assert sum(category_coefficients.values()) == coefficient
    category_oriented = {
        category: orientation * entry
        for category, entry in category_coefficients.items()
    }
    for category, entry in category_oriented.items():
        category_oriented_totals[category] += entry
    rows.append({
        "ordered_pair": [lift.literal(first), lift.literal(second)],
        "wedge_coefficient": coefficient,
        "canonical_representative": lift.literal(representative),
        "bucket_orientation": orientation,
        "oriented_bucket_contribution": orientation * coefficient,
        "production_subtotal_coefficients": category_coefficients,
        "production_subtotal_oriented_contributions": category_oriented,
        "individual_occurrence": None,
        "occurrence_caveat": (
            "MixedTensorSubtotals is aggregate provenance; the production API "
            "does not retain an individual AST occurrence for this pair."
        ),
    })

assert rows, "the HTH free bucket has no wedge provenance"
hth_coordinate = sum(row["oriented_bucket_contribution"] for row in rows)
assert hth_coordinate == -1
assert sum(category_oriented_totals.values()) == hth_coordinate

odd_hth_wedge_pairs = [row for row in rows if row["wedge_coefficient"] % 2]
assert len(odd_hth_wedge_pairs) == 1
assert odd_hth_wedge_pairs[0]["ordered_pair"] == ["TT", "TTT"]
odd_pair_external_terms = [
    term for term in hth_external_terms
    if term["ordered_wedge_pair"] == ["TT", "TTT"]
]

kernel = hessian.anchored_hessian_subtotals(
    lift.parse_quotient("TTT"), lift.parse_quotient("cTTT"),
)
payload = {
    "schema": "ak3-anchored-relative-bucket-hth-provenance-v1",
    "inputs": ["TTT", "cTTT"],
    "bucket": {
        "double_coset": "HTH",
        "canonical_representative": "T",
        "orientation_convention": "D+ is the least representative across D and D^-1 by (word length, integer-word tuple)",
        "integral_coordinate": hth_coordinate,
    },
    "provenance_rows": rows,
    "production_subtotal_oriented_totals": dict(sorted(category_oriented_totals.items())),
    "external_loop_provenance": {
        "term_count": len(hth_external_terms),
        "hth_terms": hth_external_terms,
        "per_wedge_pair_coefficients": {
            f"{lift.literal(first)}|{lift.literal(second)}": coefficient
            for (first, second), coefficient in sorted(
                external_hth_by_pair.items(), key=lambda item: (word_key(item[0][0]), word_key(item[0][1])),
            )
        },
        "focused_unique_mod_two_odd_pair": {
            "ordered_wedge_pair": ["TT", "TTT"],
            "all_external_terms": odd_pair_external_terms,
        },
    },
    "anchored_kernel_mod_two_subtotals": {
        "equality_terms": kernel.equality_terms,
        "inversion_terms": kernel.inversion_terms,
        "external_terms": kernel.external_terms,
        "total": kernel.total,
        "caveat": "These kernel records certify only the final mod-two scalar; they are not indexed by a wedge ordered pair.",
    },
    "pinned_sha256": PINNED,
}
payload["provenance_sha256"] = sha256(
    json.dumps(payload["provenance_rows"], sort_keys=True, separators=(",", ":")).encode()
).hexdigest()
print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
