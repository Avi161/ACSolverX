"""Decode every solved mixed certificate in a JSONL into elementary AC moves."""
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path

from experiments.search.ac_decode import decode_elementary, replay_elementary


def pack_move(move):
    op = move["op"]
    if op == "invert":
        return ["I", move["target"]]
    if op == "swap":
        return ["S"]
    if op == "conjugate":
        return ["C", move["target"], move["by"]]
    if op == "multiply":
        return ["M", move["target"], move["source"]]
    raise ValueError(f"unknown elementary AC operation: {op!r}")


def unpack_move(move):
    if not isinstance(move, list) or not move:
        raise ValueError(f"invalid packed elementary move: {move!r}")
    if move[0] == "I" and len(move) == 2:
        return {"op": "invert", "target": move[1]}
    if move[0] == "S" and len(move) == 1:
        return {"op": "swap"}
    if move[0] == "C" and len(move) == 3:
        return {"op": "conjugate", "target": move[1], "by": move[2]}
    if move[0] == "M" and len(move) == 3:
        return {"op": "multiply", "target": move[1], "source": move[2]}
    raise ValueError(f"invalid packed elementary move: {move!r}")


def replay_packed(pair, moves):
    return replay_elementary(pair, [unpack_move(move) for move in moves])


def certificate_from_record(row):
    if "states" in row and "steps" in row:
        return row["states"], row["steps"]
    if "path" in row and "path_moves" in row:
        return row["path"], [
            {"kind": "substitution", "move": move}
            for move in row["path_moves"]
        ]
    raise ValueError("solved record has neither states/steps nor path/path_moves")


def decode_file(source, output):
    source, output = Path(source), Path(output)
    if source.resolve() == output.resolve():
        raise ValueError("input and output JSONL paths must differ")
    source_bytes = source.read_bytes()
    source_sha256 = hashlib.sha256(source_bytes).hexdigest()
    rows = [json.loads(line) for line in source_bytes.decode().splitlines() if line.strip()]
    if not rows:
        raise ValueError(f"empty input JSONL: {source}")
    output.parent.mkdir(parents=True, exist_ok=True)
    decoded = 0
    seen = set()
    partial = None
    try:
        with tempfile.NamedTemporaryFile(
                mode="w", dir=output.parent, prefix=f".{output.name}.",
                suffix=".partial", delete=False) as stream:
            partial = Path(stream.name)
            for row in rows:
                row_id = row.get("pres_id", row.get("name"))
                if row_id is None or row_id in seen:
                    raise ValueError(f"missing or duplicate presentation id: {row_id!r}")
                seen.add(row_id)
                record = {
                    "schema": "elementary_ac_v1",
                    "source_sha256": source_sha256,
                    "pres_id": row_id,
                    "r1": row["r1"],
                    "r2": row["r2"],
                    "source_solved": bool(row.get("solved")),
                    "source_winner": row.get("winner"),
                }
                if row.get("solved"):
                    states, steps = certificate_from_record(row)
                    moves = decode_elementary(
                        (row["r1"], row["r2"]), states, steps)
                    final = replay_elementary((row["r1"], row["r2"]), moves)
                    packed = [pack_move(move) for move in moves]
                    if replay_packed((row["r1"], row["r2"]), packed) != final:
                        raise AssertionError(f"packed replay mismatch for {row_id!r}")
                    record.update(
                        decoded=True, elementary_move_count=len(moves),
                        move_encoding="I,target | S | C,target,letter | M,target,source",
                        elementary_moves=packed, final_state=final,
                        replay_verified=final == ["x", "y"])
                    decoded += 1
                else:
                    record.update(decoded=False, elementary_move_count=None,
                                  elementary_moves=[], final_state=None,
                                  replay_verified=None)
                stream.write(json.dumps(record, separators=(",", ":")) + "\n")
        partial.replace(output)
    except BaseException:
        if partial is not None:
            partial.unlink(missing_ok=True)
        raise
    return {"rows": len(rows), "solved": sum(bool(r.get("solved")) for r in rows),
            "decoded": decoded, "source_sha256": source_sha256,
            "output": str(output)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args(argv)
    print(json.dumps(decode_file(args.source, args.output), sort_keys=True))


if __name__ == "__main__":
    main()
