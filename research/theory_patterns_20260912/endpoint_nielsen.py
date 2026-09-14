"""Bounded strict Nielsen descent of already certified theorem endpoints."""

import gzip
import json
from pathlib import Path
import time

from .ac_words import canon, inv, red, replay
from .complement_followup import candidates, decompressed_sha256
from .check_complement import sha256

HERE = Path(__file__).resolve().parent
MAPS = (("xy", "y"), ("xY", "y"), ("yx", "y"), ("Yx", "y"),
        ("x", "yx"), ("x", "yX"), ("x", "xy"), ("x", "Xy"))
INVERSES = (1, 0, 3, 2, 5, 4, 7, 6)


def image(word, images):
    mapping = dict(zip("xXyY", (images[0], inv(images[0]), images[1], inv(images[1]))))
    return red("".join(mapping[c] for c in word))


def pair_canon(pair):
    return tuple(sorted(canon(word) for word in pair))


def descend(pair, remaining):
    pair, path, charge = pair_canon(pair), [], 0
    while remaining - charge >= len(MAPS):
        choices = []
        for index, images in enumerate(MAPS):
            child = pair_canon(image(word, images) for word in pair)
            choices.append((sum(map(len, child)), child, index))
        charge += len(MAPS)
        length, child, index = min(choices)
        if length >= sum(map(len, pair)):
            return pair, path, charge, True
        path.append({"map": index, "images": MAPS[index], "inverse_images": MAPS[INVERSES[index]],
                     "before": pair, "after": child})
        pair = child
    return pair, path, charge, False


def checks():
    for index, images in enumerate(MAPS):
        inverse = MAPS[INVERSES[index]]
        for word in ("x", "y", "YxyXX", "xyxYYXXy", ""):
            assert image(image(word, images), inverse) == red(word)
            assert image(image(word, inverse), images) == red(word)
    for pair in (("xy", "y"), ("yx", "x"), ("xxY", "xY")):
        best, path, charges, complete = descend(pair, 1000)
        assert sum(map(len, best)) == 2 and complete
        assert 0 < charges <= 1000
    assert descend(("xy", "y"), 7)[2:] == (0, False)


def main():
    checks()
    paths = [HERE / "boundary_compiler_report.json", HERE / "prepared_frames_full124.jsonl.gz"]
    hashes = {paths[0].name: sha256(paths[0]),
              "prepared_frames_full124.jsonl": decompressed_sha256(paths[1])}
    hashes[Path(__file__).name] = sha256(Path(__file__))
    boundary = {row["name"]: {**row, "_record_index": i}
                for i, row in enumerate(json.loads(paths[0].read_text())["full_u124"]["records"])}
    started_wall, started_cpu = time.perf_counter(), time.process_time()
    records = []
    with gzip.open(paths[1], "rt") as source, (HERE / "endpoint_nielsen.jsonl").open("w") as output:
        for line in source:
            prepared = json.loads(line)
            name, original = prepared["name"], prepared["input"]
            cache, charges, states = {}, 0, []
            best_pair, best_witness = pair_canon(original), None
            selected = candidates(boundary[name], prepared, hashes)
            row_cpu, row_wall = time.process_time(), time.perf_counter()
            for candidate in selected:
                if 1000 - charges < len(MAPS):
                    break
                key = pair_canon(candidate["pair"])
                if key in cache:
                    continue
                best, trace, used, complete = descend(key, 1000 - charges)
                cache[key] = (best, trace, complete)
                charges += used
                record = {"pair": candidate["pair"], "canonical_pair": key,
                          "provenance": candidate["provenance"], "best_pair": best,
                          "best_length": sum(map(len, best)), "trace": trace,
                          "image_evaluations": used, "strict_descent_exhausted": complete}
                states.append(record)
                if record["best_length"] < sum(map(len, best_pair)):
                    assert replay(original, candidate["moves"]) == list(candidate["pair"])
                    record["ordinary_prefix_moves"] = candidate["moves"]
                    best_pair, best_witness = best, record
            records.append({"name": name, "input": original, "input_length": sum(map(len, original)),
                            "best_pair": best_pair, "best_length": sum(map(len, best_pair)),
                            "best_witness": best_witness, "states": states,
                            "candidate_count": len(selected), "normalized_candidate_count": len(cache),
                            "image_evaluations": charges, "cpu_seconds": time.process_time() - row_cpu,
                            "wall_seconds": time.perf_counter() - row_wall})
            output.write(json.dumps(records[-1], separators=(",", ":")) + "\n")
            output.flush()
            time.sleep(.05)
    assert len(records) == 124 and {row["name"] for row in records} == set(boundary)
    summary = {"status": "complete", "source_hashes": hashes,
               "algorithm": "Eight signed left/right Nielsen maps; accept only strict total cyclic length descent. Exact canonical starting-state cache. Shortest saved endpoints first.",
               "scope": "Additional endpoint screen capped at 1000 map evaluations per input; no heap nodes. This cost is additional to producing saved endpoints, not a combined 1k search claim.",
               "certificate_kind": "ordinary saved prefix followed by explicitly invertible ambient maps; finite stable AC realizability on these known trivial-group inputs, expansion not emitted",
               "improved": [r["name"] for r in records if r["best_length"] < r["input_length"]],
               "solved": [r["name"] for r in records if r["best_length"] == 2],
               "image_evaluations": sum(r["image_evaluations"] for r in records),
               "normalized_candidate_count": sum(r["normalized_candidate_count"] for r in records),
               "descent_steps": sum(len(s["trace"]) for r in records for s in r["states"]),
               "screen_cpu_seconds": sum(r["cpu_seconds"] for r in records),
               "screen_wall_seconds": sum(r["wall_seconds"] for r in records),
               "elapsed_cpu_seconds": time.process_time() - started_cpu,
               "elapsed_wall_seconds_including_cooling": time.perf_counter() - started_wall,
               "rows": [{k: v for k, v in row.items() if k not in ("states", "best_witness")} for row in records]}
    (HERE / "endpoint_nielsen.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "rows"}, indent=2))


if __name__ == "__main__":
    main()
