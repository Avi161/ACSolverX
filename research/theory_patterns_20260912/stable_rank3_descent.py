"""Bounded total-length Whitehead descent after audited stable prefixes."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from primitive_compression import expand, whitehead_maps, map_inverses, normalize_tuple


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def descend(words, limit=1000):
    if type(limit) is not int or not 0 <= limit <= 1000:
        raise ValueError("invalid image budget")
    current, witnesses = normalize_tuple(words)
    initial = {"before": list(words), "after": current, "canonical_witnesses": witnesses}
    maps, inverses = whitehead_maps(), map_inverses()
    steps, used = [], 0
    while used + 3 * len(maps) <= limit:
        options = []
        for images in maps:
            raw = [expand(word, images) for word in current]
            child, canonical = normalize_tuple(raw)
            options.append((sum(map(len, child)), tuple(child), tuple(images.values()),
                            images, raw, canonical))
        used += 3 * len(maps)
        length, child, key, images, raw, canonical = min(options)
        if length >= sum(map(len, current)):
            stop = "no_strict_total_length_whitehead_descent"
            break
        steps.append({"before": current, "images": images,
                      "inverse_images": inverses[key], "raw_image": raw,
                      "canonical_witnesses": canonical, "after": list(child),
                      "rank": 3, "total_length": length})
        current = list(child)
    else:
        stop = "word_image_budget"
    return {"initial_normalization": initial, "steps": steps, "endpoint": current,
            "rank": 3, "total_length": sum(map(len, current)), "word_images": used,
            "stop": stop}


def main():
    source_path = HERE / "stable_dictionary_compression_report.json"
    source = json.loads(source_path.read_text())
    cpu, wall = time.process_time(), time.perf_counter()
    rows = []
    for row in source["rows"]:
        if row["best"] is None:
            continue
        result = descend(row["best"]["relators"])
        rows.append({"name": row["name"], "input": row["input"],
                     "source_witness": row["best"], "result": result,
                     "improves_prefix": result["total_length"] < row["best"]["total_length"]})
        time.sleep(0.05)
    report = {"status": "author_verified_pending_independent_replay",
              "source_report_sha256": digest(source_path), "script_sha256": digest(Path(__file__)),
              "rows": rows, "rows_examined": len(rows),
              "prefix_improvement_ids": [r["name"] for r in rows if r["improves_prefix"]],
              "starting_prefix_total": sum(r["source_witness"]["total_length"] for r in rows),
              "endpoint_total": sum(r["result"]["total_length"] for r in rows),
              "word_images": sum(r["result"]["word_images"] for r in rows),
              "maximum_word_images_per_row": max(r["result"]["word_images"] for r in rows),
              "strict_whitehead_steps": sum(len(r["result"]["steps"]) for r in rows),
              "cpu_seconds": time.process_time() - cpu,
              "wall_seconds_including_cooling": time.perf_counter() - wall,
              "scope": "All rank3 relators transformed simultaneously. Stable AC follows from the audited prefix and permitted ambient automorphisms; no rank2 endpoint or solve inferred. Budget counts individual word images, not elementary stable proof expansion."}
    (HERE / "stable_rank3_descent_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "rows"}, indent=2))


if __name__ == "__main__":
    main()
