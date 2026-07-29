from __future__ import annotations

from dataclasses import dataclass
from itertools import product
import json
from typing import Any, Iterable, Mapping, Sequence


TOKEN_COUNT = 84
THRESHOLD_STATES = (0, 1, 2, None)


@dataclass(frozen=True)
class Cell:
    cell_id: str
    names: tuple[str, ...]
    states: tuple[int | None, ...]
    base_values: tuple[int, ...]


@dataclass(frozen=True)
class HistogramBucket:
    key: tuple[Any, ...]
    count: int
    mask: int


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True)


def _state_label(name: str, state: int | None) -> str:
    if name == "a" and state is None:
        return "3"
    return "ge3" if state is None else str(state)


def _name_label(name: str) -> str:
    return "age" if name == "a" else name


def make_cells(names: Sequence[str]) -> tuple[Cell, ...]:
    field_names = tuple(names)
    cells = []
    for states in product(THRESHOLD_STATES, repeat=len(field_names)):
        cells.append(
            Cell(
                cell_id="_".join(
                    f"{_name_label(name)}{_state_label(name, state)}"
                    for name, state in zip(field_names, states)
                ),
                names=field_names,
                states=states,
                base_values=tuple(3 if state is None else state for state in states),
            )
        )
    return tuple(cells)


def p_domain_nonempty(cell: Cell) -> bool:
    a, h, r = cell.states
    if a is None:
        if h is None or r is None:
            return True
        return h + r >= 3
    if h is None or r is None:
        return True
    return h + r >= a


def bucketize_records(
    records: Iterable[Mapping[str, Any]], *, key_fields: Sequence[str]
) -> tuple[HistogramBucket, ...]:
    grouped: dict[str, tuple[tuple[Any, ...], int, int]] = {}
    seen_indices: set[int] = set()
    for record in records:
        token_index = record["token_index"]
        if isinstance(token_index, bool) or not isinstance(token_index, int):
            raise ValueError("token_index must be an integer")
        if not 0 <= token_index < TOKEN_COUNT:
            raise ValueError("token_index must be in 0..83")
        if token_index in seen_indices:
            raise ValueError(f"duplicate token_index: {token_index}")
        seen_indices.add(token_index)

        key = tuple(record[field] for field in key_fields)
        serialized_key = canonical_json(key)
        previous = grouped.get(serialized_key)
        if previous is None:
            grouped[serialized_key] = (key, 1, 1 << token_index)
        else:
            previous_key, count, mask = previous
            grouped[serialized_key] = (previous_key, count + 1, mask | (1 << token_index))

    if seen_indices != set(range(TOKEN_COUNT)):
        raise ValueError("token indices must cover 0..83 exactly")

    buckets = tuple(
        HistogramBucket(key=key, count=count, mask=mask)
        for _, (key, count, mask) in sorted(grouped.items())
    )
    union = 0
    for bucket in buckets:
        assert union & bucket.mask == 0
        union |= bucket.mask
    assert union == (1 << TOKEN_COUNT) - 1
    return buckets
