"""Single guarded entry point for wave-2 structural checks."""

from __future__ import annotations

import sys
from pathlib import Path

CODE = Path(__file__).resolve().parent
if str(CODE) not in sys.path:
    sys.path.insert(0, str(CODE))

from elementary_ac2_scan import main as ac2_main  # noqa: E402
from primitive_relator_census import main as primitive_main  # noqa: E402
from q_peel import main as peel_main  # noqa: E402


def main() -> None:
    print("=== Q peel identities ===")
    peel_main()
    print("=== primitive relator census ===")
    primitive_main()
    print("=== depth-1 AC2 scan ===")
    ac2_main()


if __name__ == "__main__":
    main()
