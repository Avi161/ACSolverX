"""Guarded wave-3 checks: C12 step-4 replay and primitivity aggregates."""

from __future__ import annotations

import sys
from pathlib import Path

CODE = Path(__file__).resolve().parent
if str(CODE) not in sys.path:
    sys.path.insert(0, str(CODE))

from c12_generator_deletion import main as deletion_main  # noqa: E402
from primitive_aggregates import main as aggregate_main  # noqa: E402


def main() -> None:
    print("=== C12 generator deletion replay ===")
    deletion_main()
    print("=== primitive product and depth-1 aggregates ===")
    aggregate_main()


if __name__ == "__main__":
    main()
