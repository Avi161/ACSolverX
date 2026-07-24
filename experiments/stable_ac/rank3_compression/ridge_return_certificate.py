"""Chained certificate for the five-orbit AK(3) ridge return."""

import argparse
import json
from pathlib import Path

from experiments.stable_ac.rank3_compression.post_compression_edge_certificate import (
    RESULT_PATH as UPSTREAM_PATH,
    build_certificate as build_edge_certificate,
    verify_certificate as verify_edge_certificate,
)


SCHEMA = "ak3-ridge-return-v1"
ORBIT2 = ("YYXXyx", "YYYxyXX")
ROOT = Path(__file__).resolve().parents[3]
RESULT_PATH = ROOT / "results/stable_ac/theory/ak3_ridge_return.json"


def extract_ridge_roots(
    path: Path = UPSTREAM_PATH,
) -> tuple[tuple[tuple[str, str], ...], int, str]:
    with path.open() as handle:
        data = json.load(handle)
    if data.get("schema") != "ak3-post-compression-edge-v1":
        raise ValueError("post-compression certificate has wrong schema")
    minimum = data.get("minimum_child_floor")
    if not isinstance(minimum, int):
        raise ValueError("post-compression certificate has no minimum")
    trace = data.get("trace_sha256")
    if not isinstance(trace, str) or len(trace) != 64:
        raise ValueError("post-compression certificate has invalid trace")
    aut_orbits = data.get("aut_orbits")
    if not isinstance(aut_orbits, list):
        raise ValueError("post-compression certificate has no Aut orbits")
    roots = {
        tuple(orbit.get("representative", ()))
        for orbit in aut_orbits
        if isinstance(orbit, dict)
        and orbit.get("minimum_total") == minimum
    }
    if any(len(root) != 2 for root in roots):
        raise ValueError("malformed minimum representative")
    return tuple(sorted(roots)), minimum, trace


def build_certificate() -> dict[str, object]:
    roots, upstream_minimum, upstream_trace = extract_ridge_roots()
    ridge = build_edge_certificate(
        roots=roots,
        upstream_trace=upstream_trace,
    )
    if ridge["distinct_root_child_count"] > 1000:
        raise RuntimeError("ridge image exceeds the 1,000-state local cap")

    minimum = ridge["minimum_child_floor"]
    minimum_orbits = [
        orbit
        for orbit in ridge["aut_orbits"]
        if orbit["minimum_total"] == minimum
    ]
    minimum_representatives = [
        orbit["representative"] for orbit in minimum_orbits
    ]
    minimum_child_count = sum(
        len(orbit["children"]) for orbit in minimum_orbits
    )
    return_proved = (
        minimum == 13
        and minimum_child_count == 1
        and minimum_representatives == [list(ORBIT2)]
    )
    return {
        "schema": SCHEMA,
        "claim": (
            "complete one-edge image of the minimum Aut orbits in the "
            "certified post-compression wall"
        ),
        "upstream_minimum_floor": upstream_minimum,
        "upstream_trace": upstream_trace,
        "ridge_roots": [list(root) for root in roots],
        "ridge": ridge,
        "minimum_child_count": minimum_child_count,
        "minimum_representatives": minimum_representatives,
        "floor12_candidate": (
            "PROVED" if minimum is not None and minimum <= 12 else "REFUTED"
        ),
        "return_proposition": "PROVED" if return_proved else "REFUTED",
    }


def verify_certificate(
    data: dict[str, object],
    verify_upstream: bool = True,
) -> None:
    errors: list[str] = []
    if data.get("schema") != SCHEMA:
        errors.append(f"wrong schema: {data.get('schema')!r}")
    ridge = data.get("ridge")
    if not isinstance(ridge, dict):
        errors.append("ridge must be an object")
        ridge = {}

    if verify_upstream:
        with UPSTREAM_PATH.open() as handle:
            upstream = json.load(handle)
        verify_edge_certificate(upstream)
        roots, minimum, trace = extract_ridge_roots()
        if data.get("ridge_roots") != [list(root) for root in roots]:
            errors.append("ridge roots differ from verified upstream minima")
        if data.get("upstream_minimum_floor") != minimum:
            errors.append("upstream minimum differs")
        if data.get("upstream_trace") != trace:
            errors.append("upstream trace differs")

    if ridge:
        try:
            verify_edge_certificate(ridge, verify_upstream=False)
        except AssertionError as exc:
            errors.append(f"ridge replay failed: {exc}")
        if ridge.get("distinct_root_child_count", 1001) > 1000:
            errors.append("ridge image exceeds the 1,000-state local cap")

    minimum = ridge.get("minimum_child_floor")
    aut_orbits = ridge.get("aut_orbits", [])
    if not isinstance(aut_orbits, list):
        errors.append("ridge aut_orbits must be a list")
        aut_orbits = []
    minimum_orbits = [
        orbit
        for orbit in aut_orbits
        if isinstance(orbit, dict)
        and orbit.get("minimum_total") == minimum
    ]
    minimum_representatives = [
        orbit.get("representative") for orbit in minimum_orbits
    ]
    minimum_child_count = sum(
        len(orbit.get("children", [])) for orbit in minimum_orbits
    )
    if data.get("minimum_child_count") != minimum_child_count:
        errors.append("minimum child count mismatch")
    if data.get("minimum_representatives") != minimum_representatives:
        errors.append("minimum representatives mismatch")
    return_proved = (
        minimum == 13
        and minimum_child_count == 1
        and minimum_representatives == [list(ORBIT2)]
    )
    if data.get("return_proposition") != (
        "PROVED" if return_proved else "REFUTED"
    ):
        errors.append("return proposition verdict mismatch")
    if data.get("floor12_candidate") != (
        "PROVED" if isinstance(minimum, int) and minimum <= 12 else "REFUTED"
    ):
        errors.append("floor-12 verdict mismatch")

    if errors:
        raise AssertionError("\n".join(errors))

    expected = build_certificate()
    if data != expected:
        differing = sorted(
            key
            for key in set(data) | set(expected)
            if data.get(key) != expected.get(key)
        )
        raise AssertionError(
            "certificate differs from complete replay in keys: "
            + ", ".join(differing)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--output", type=Path, default=RESULT_PATH)
    args = parser.parse_args()
    if args.verify:
        with args.output.open() as handle:
            data = json.load(handle)
        verify_certificate(data)
        ridge = data["ridge"]
        print(
            "CERTIFICATE VERIFIES: "
            f"{ridge['root_count']} ridge roots, "
            f"{ridge['distinct_root_child_count']} edges, "
            f"minimum {ridge['minimum_child_floor']}, "
            f"return {data['return_proposition']}"
        )
        return
    data = build_certificate()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    ridge = data["ridge"]
    print(
        "CERTIFICATE WRITTEN: "
        f"{ridge['root_count']} ridge roots, "
        f"{ridge['distinct_root_child_count']} edges, "
        f"minimum {ridge['minimum_child_floor']}, "
        f"return {data['return_proposition']} -> {args.output}"
    )


if __name__ == "__main__":
    main()
