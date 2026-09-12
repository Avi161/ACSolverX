"""Atomic JSONL writer: same-directory partial file, then replace.

Rejects duplicate IDs when appending to an existing JSONL of objects that
carry an ``id`` field.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterable, Mapping


def _ids_in_path(path: Path) -> set[str]:
    seen: set[str] = set()
    if not path.exists():
        return seen
    with path.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if not isinstance(row, Mapping) or "id" not in row:
                raise ValueError(f"{path}:{line_no} missing id")
            key = str(row["id"])
            if key in seen:
                raise ValueError(f"{path}:{line_no} duplicate id {key!r}")
            seen.add(key)
    return seen


def write_jsonl_atomic(path: str | os.PathLike[str], rows: Iterable[Mapping]) -> int:
    """Write ``rows`` to ``path`` via ``path.partial``, replacing the target.

    Existing file IDs and new-row IDs must be disjoint. Returns the number of
    new rows written (the whole file is rewritten, including previous rows).
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    existing: list[dict] = []
    seen = set()
    if target.exists():
        with target.open(encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                key = str(row["id"])
                if key in seen:
                    raise ValueError(f"existing duplicate id {key!r} in {target}")
                seen.add(key)
                existing.append(row)
    new_rows = []
    for row in rows:
        key = str(row["id"])
        if key in seen:
            raise ValueError(f"duplicate id {key!r}")
        seen.add(key)
        new_rows.append(dict(row))
    partial = target.with_name(target.name + ".partial")
    with partial.open("w", encoding="utf-8") as handle:
        for row in existing + new_rows:
            handle.write(json.dumps(row, sort_keys=True, ensure_ascii=True) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
    os.replace(partial, target)
    return len(new_rows)
