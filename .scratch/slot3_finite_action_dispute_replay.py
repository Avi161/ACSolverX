from __future__ import annotations

from experiments.stable_ac import (
    depth4_period_two_eleven_direction_obstruction_certificate as eleven,
    depth4_period_two_lift_certificate as lift,
    depth4_period_two_phi_infinity_hessian_certificate as hessian,
    depth4_period_two_remote_syzygy_certificate as remote,
)


CORE = "cTctttcT"
PREFIXES = {
    "a": "TctcTctcT",
    "b": "TctctcT",
    "c": "TctttcT",
    "d": "TcttcTcTctttcT",
    "g": "ttcT",
    "h": "TctcTTctttcT",
    "j": "ttcTcTctttcT",
}
REVERSALS = (
    ("g", "b"),
    ("g", "c"),
    ("g", "a"),
    ("g", "d"),
    ("b", "c"),
    ("b", "d"),
    ("a", "d"),
    ("h", "d"),
    ("j", "d"),
)
PERIODS = (2, 4, 1, 1, 2, 4, 4, 1, 4, 1, 5, 5, 4, 4)


def protected_word(family: str, level: int) -> lift.Word:
    assert level >= 1
    return lift.parse_quotient(PREFIXES[family] + CORE * (3 * level) + "ct")


def level_bits(level: int) -> tuple[int, ...]:
    wedge = {
        (protected_word(left, level), protected_word(right, level)): 1
        for left, right in REVERSALS
    }
    assert len(wedge) == 9
    return hessian._direct_fourteen_bits(wedge)


def residue_row(coordinate: int, period: int) -> str:
    # Residues are printed in the order 0,1,...,r-1, using positive levels.
    return "".join(str(level_bits(period if residue == 0 else residue)[coordinate]) for residue in range(period))


def source_row(coordinate: int, period: int) -> str:
    return "".join(
        str(level_bits(index + 1)[coordinate] ^ level_bits(index + 2)[coordinate])
        for index in range(period)
    )


def main() -> None:
    c_image, t_image = eleven.NEW_ACTION
    state_rows = {
        family: tuple(
            remote.point_image(protected_word(family, level), 0, c_image, t_image)
            for level in range(4, 8)
        )
        for family in PREFIXES
    }
    prefix_actions = {
        family: tuple(
            remote.point_image(lift.parse_quotient(prefix), point, c_image, t_image)
            for point in range(4)
        )
        for family, prefix in PREFIXES.items()
    }
    print("NEW_ACTION prefix permutations:")
    for family, action in prefix_actions.items():
        literal = lift.literal(lift.parse_quotient(PREFIXES[family]))
        print(f"  {family}: {action} from {literal}")
    print("NEW_ACTION states by n mod 4:")
    for family, states in state_rows.items():
        print(f"  {family}: {states}")
    print(
        "NEW_ACTION distinct W edges: "
        + "".join(
            str(
                sum(
                    state_rows[left][residue] != state_rows[right][residue]
                    for left, right in REVERSALS
                )
            )
            for residue in range(4)
        )
    )
    for coordinate, period in enumerate(PERIODS):
        print(
            f"k={coordinate + 1:02d} r={period} "
            f"C={residue_row(coordinate, period)} "
            f"S={source_row(coordinate, period)}"
        )


if __name__ == "__main__":
    main()
