"""Bounded structural probes for Q_{n,delta} and selected U124 MS floors.

This is deliberately not an AC graph search.  In particular, the corridor
enumerator's expensive ``aut_canon`` post-processing is temporarily replaced
with its phase-1-only ``aut_min_len`` calculation.  The resulting report does
not contain Aut(F_2) representatives or witnesses, only the requested cheap
minimum-length diagnostic for each accepted corridor.
"""

from __future__ import annotations

import csv
import json
import os
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.equivalence_classes.lib.autcanon import aut_min_len  # noqa: E402
from experiments.equivalence_classes.lib.words import free_reduce  # noqa: E402
from experiments.stable_ac.rank3_compression import corridors  # noqa: E402

DATA = ROOT / "data" / "ms_unsolved_reps" / "aca_124_best.csv"
OUTPUT = ROOT / "research" / "u124_stable_20260912" / "tables" / "q_residue_scan.json"

Q_BOUNDS = (2, 4)
FALLBACK_BOUNDS = (1, 3)
SOFT_TOTAL_LIMIT_SECONDS = 110.0
SLOW_PAIR_SECONDS = 10.0
U124_NAMES = (
    "aca_120",
    "aca_34",
    "aca_58",
    "aca_81",
    "aca_97",
    "aca_121",
    "aca_122",
    "aca_123",
    "aca_85",
    "aca_98",
)


def q_pair(n: int, delta: int) -> tuple[str, str]:
    xd = "x" if delta == 1 else "X"
    return ("XYxyxxy" + xd + "YXX", "Yxxy" + xd * n + "YXX")


def matching_floor_parameters(pair: tuple[str, str]) -> dict[str, int | str] | None:
    """Return the documented MS-floor parameter when a selected row has it."""
    r1, r2 = pair
    for donor, target in ((r1, r2), (r2, r1)):
        if donor == "YXXyxYx" and target.startswith("Y") and target.endswith("Xyyxx"):
            n = len(target) - 5
            if n >= 2 and target == "Y" * n + "Xyyxx":
                return {"shape": "upper", "n": n, "delta": -1}
        if donor == "YXyXYxx" and target.startswith("Y") and target.endswith("XXYYx"):
            n = len(target) - 5
            if n >= 2 and target == "Y" * n + "XXYYx":
                return {"shape": "lower", "n": n, "delta": 1}
    return None


def common_subwords(pair: tuple[str, str]) -> list[dict[str, int | str]]:
    """List direct, contiguous freely reduced common words of length 2 through 4."""
    left, right = (free_reduce(word) for word in pair)
    common: set[str] = set()
    for length in range(2, 5):
        left_words = {left[index:index + length] for index in range(len(left) - length + 1)}
        right_words = {right[index:index + length] for index in range(len(right) - length + 1)}
        common.update(left_words & right_words)
    return [
        {"word": word, "length": len(word)}
        for word in sorted(common, key=lambda word: (len(word), word))
    ]


@contextmanager
def cheap_corridor_enumeration() -> Iterator[None]:
    """Suppress the corridor module's Aut(F_2) level-set search for this probe."""
    original = corridors.aut_canon

    def phase_one_only(pair: tuple[str, str]) -> tuple[int, tuple[str, str], dict[str, str]]:
        # enumerate_short_corridors stores this internally, but this script
        # independently records aut_min_len per accepted output below.
        return aut_min_len(pair), pair, {"x": "x", "y": "y"}

    corridors.aut_canon = phase_one_only
    try:
        yield
    finally:
        corridors.aut_canon = original


def scan_corridors(
    pair: tuple[str, str],
    n: int,
    bounds: tuple[int, int],
) -> tuple[dict[str, object], float]:
    """Run one finite corridor census and annotate each accepted output."""
    started = time.perf_counter()
    with cheap_corridor_enumeration():
        census = corridors.enumerate_short_corridors(
            pair,
            max_word_length=bounds[0],
            max_template_length=bounds[1],
        )
    wall_seconds = time.perf_counter() - started
    input_total = sum(map(len, pair))
    accepted = []
    for row in census.accepted:
        output_total = sum(map(len, row.output))
        try:
            minimum = aut_min_len(row.output)
        except Exception as exc:  # Preserve scan evidence even if a cheap probe fails.
            minimum = None
            minimum_error: str | None = f"{type(exc).__name__}: {exc}"
        else:
            minimum_error = None
        accepted.append({
            **row.to_json(),
            "output_total_length": output_total,
            "aut_min_len": minimum,
            "aut_min_len_error": minimum_error,
            "strictly_below_n_plus_12": output_total < n + 12,
            "strictly_below_input_total": output_total < input_total,
        })
    return {
        "bounds_used": {
            "max_word_length": bounds[0],
            "max_template_length": bounds[1],
        },
        "wall_time_seconds": wall_seconds,
        "enumerated_templates": census.enumerated_templates,
        "accepted_count": census.accepted_count,
        "trace_sha256": census.trace_sha256,
        "accepted": accepted,
    }, wall_seconds


def choose_bounds(elapsed: float, completed: int, total: int, slow_seen: bool) -> tuple[int, int]:
    """Shrink only future scans when observed primary cost threatens the cap."""
    if slow_seen or elapsed >= SOFT_TOTAL_LIMIT_SECONDS:
        return FALLBACK_BOUNDS
    if completed:
        projected = elapsed / completed * total
        if projected >= SOFT_TOTAL_LIMIT_SECONDS:
            return FALLBACK_BOUNDS
    return Q_BOUNDS


def atomic_write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name + ".partial")
    with partial.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(partial, path)


def load_u124_pairs() -> dict[str, tuple[str, str]]:
    with DATA.open(newline="", encoding="utf-8") as handle:
        rows = {row["name"]: (row["r1"], row["r2"]) for row in csv.DictReader(handle)}
    missing = set(U124_NAMES) - set(rows)
    if missing:
        raise ValueError(f"named U124 rows absent from {DATA}: {sorted(missing)}")
    return rows


def main() -> None:
    all_jobs: list[dict[str, object]] = [
        {
            "id": f"Q_{n}_{delta:+d}",
            "kind": "Q",
            "n": n,
            "delta": delta,
            "pair": q_pair(n, delta),
        }
        for n in range(2, 8)
        for delta in (-1, 1)
    ]
    best = load_u124_pairs()
    for name in U124_NAMES:
        pair = best[name]
        parameters = matching_floor_parameters(pair)
        if parameters is None:
            raise ValueError(f"{name} does not match an expected U124 floor form")
        all_jobs.append({"id": name, "kind": "U124_best_floor", "pair": pair, **parameters})

    started = time.perf_counter()
    slow_seen = False
    scans = []
    for index, job in enumerate(all_jobs):
        bounds = choose_bounds(time.perf_counter() - started, index, len(all_jobs), slow_seen)
        pair = job["pair"]
        assert isinstance(pair, tuple)
        n = job["n"]
        assert isinstance(n, int)
        corridor_scan, wall_seconds = scan_corridors(pair, n, bounds)
        slow_seen = slow_seen or (bounds == Q_BOUNDS and wall_seconds > SLOW_PAIR_SECONDS)
        scans.append({
            **job,
            "input_pair": list(pair),
            "input_total_length": sum(map(len, pair)),
            "common_freely_reduced_subwords_length_2_to_4": common_subwords(pair),
            "corridor_scan": corridor_scan,
        })

    total_wall = time.perf_counter() - started
    payload = {
        "method": {
            "scope": "finite structural scan only; no AC heap search and no budgeted nodes",
            "corridor_enumerator": "experiments.stable_ac.rank3_compression.corridors.enumerate_short_corridors",
            "aut_minimum": "experiments.equivalence_classes.lib.autcanon.aut_min_len",
            "aut_canon_level_set_search": "disabled during corridor enumeration",
            "primary_bounds": {
                "max_word_length": Q_BOUNDS[0],
                "max_template_length": Q_BOUNDS[1],
            },
            "fallback_bounds": {
                "max_word_length": FALLBACK_BOUNDS[0],
                "max_template_length": FALLBACK_BOUNDS[1],
            },
            "soft_total_scan_limit_seconds": SOFT_TOTAL_LIMIT_SECONDS,
            "cyclic_complement_heuristic": "not implemented",
        },
        "source": {
            "u124_best_table": str(DATA.relative_to(ROOT)),
            "u124_names": list(U124_NAMES),
        },
        "wall_time_seconds": total_wall,
        "pair_count": len(scans),
        "pairs": scans,
    }
    atomic_write_json(OUTPUT, payload)
    print(f"wrote {OUTPUT.relative_to(ROOT)} ({len(scans)} pairs, {total_wall:.3f}s)")


if __name__ == "__main__":
    main()
