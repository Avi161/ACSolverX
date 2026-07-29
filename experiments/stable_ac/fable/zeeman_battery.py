"""R10 / Zeeman route: anchor audit, POWER CALIBRATION ladder, and the AK targets.

NEW FILE.  Pure CPU, standard library only (no numpy, no numba, no JAX).  Single
process, single output file, incremental flush -- a partial run is usable.

This is the driver for ``zeeman_collapse.py``.  It exists because the instrument it
drives is **one-sided**: a collapse of ``K x I`` is a replayable certificate, while a
failure to find one is silence.  Silence is worth exactly the measured detection rate
of the search that produced it, so the ladder in phase B is not optional decoration --
it is the only thing that gives phase C's null any content at all.

Phases
------
``anchors``  every engine claim checked against a complex whose answer is known
             independently (including Bing's house and the dunce hat, which are the
             two anchors that a broken collapse engine gets wrong).
``ladder``   POSITIVE POWER.  Complexes whose ``K x I`` *is* collapsible, of growing
             size, run through the same blind search that phase C uses.  Reports a
             hit RATE per restart, not a yes/no.
``targets``  AK(2) (the requested positive control) and AK(3) (the question), over
             several triangulations, plus a graded discrete-Morse near-miss measure.

Usage::

    python3 -m experiments.stable_ac.fable.zeeman_battery --phase all \\
        --out results/stable_ac/fable/zeeman_collapse.json
"""

from __future__ import annotations

import argparse
import json
import os
import random
import time
from typing import Dict, List, Optional, Sequence, Tuple

from experiments.stable_ac.fable.zeeman_collapse import (
    AK2_WORDS,
    AK3_WORDS,
    Complex,
    Face,
    build_target,
    cylinder_collapse_sequence,
    homology,
    partial_cylinder_prefix,
    pi1_presentation,
    presentation_complex,
    prism,
    prism_level_score,
    random_discrete_morse,
    run_collapse,
    search_collapse,
    tietze_simplify,
    verify_collapse_sequence,
)

BEST_STRATEGIES = ("uniform-lifo", "top-lifo")
BEST_SCORE = "copy"


# =====================================================================================
# result bookkeeping (single writer, incremental flush)
# =====================================================================================


class Sink:
    """The one and only writer of the output json."""

    def __init__(self, path: str):
        self.path = path
        self.data: Dict[str, object] = {
            "kind": "R10_zeeman_collapse_battery",
            "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "anchors": [],
            "ladder": [],
            "targets": [],
            "certificates": [],
            "notes": [],
        }
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self.flush()

    def add(self, section: str, row: Dict[str, object]) -> None:
        self.data[section].append(row)  # type: ignore[union-attr]
        self.flush()

    def note(self, text: str) -> None:
        self.data["notes"].append(text)  # type: ignore[union-attr]
        self.flush()

    def flush(self) -> None:
        self.data["updated_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        tmp = self.path + ".tmp"
        with open(tmp, "w") as fh:
            json.dump(self.data, fh, indent=1)
        os.replace(tmp, self.path)


def _jsonable(seq) -> List[List[List[int]]]:
    return [[list(t), list(s)] for (t, s) in seq]


def dump_certificate(dirpath: str, label: str, work: Complex,
                     seq: Sequence[Tuple[Face, Face]], target: str,
                     protected=None) -> Dict[str, object]:
    """Verify a sequence with the INDEPENDENT replay verifier and write it to disk."""
    rep = verify_collapse_sequence(sorted(work.faces), seq, target=target,
                                   protected=protected)
    os.makedirs(dirpath, exist_ok=True)
    path = os.path.join(dirpath, f"zeeman_cert_{label}.json")
    payload = {
        "label": label,
        "target": target,
        "replay_report": rep,
        "n_faces": work.n_faces(),
        "f_vector": work.f_vector(),
        "facets": [list(f) for f in sorted(work.faces)],
        "sequence": _jsonable(seq),
    }
    if protected is not None:
        payload["protected"] = [list(f) for f in sorted(protected)]
    with open(path, "w") as fh:
        json.dump(payload, fh)
    return {"path": path, "replay_ok": rep["ok"], "replay": rep, "n_steps": len(seq)}


# =====================================================================================
# phase A -- anchors
# =====================================================================================

# (name, contractible?, base collapsible?, K x I collapsible?)  -- the independently
# known answers this engine is being audited against.
ANCHOR_EXPECT = {
    "ball3":   ("yes", "yes", "yes"),
    "disc":    ("yes", "yes", "yes"),
    "trivial": ("yes", "yes", "yes"),
    "s2":      ("no",  "no",  "no"),
    "rp2":     ("no",  "no",  "no"),
    "dunce":   ("yes", "no",  "yes"),
    "bing":    ("yes", "no",  "yes-expected"),
}


def phase_anchors(sink: Sink, per_target_s: float, certdir: str) -> None:
    for name in ("ball3", "disc", "trivial", "s2", "rp2", "dunce", "bing"):
        t0 = time.time()
        cx, _info = build_target(name, 3)
        h = homology(cx)
        row: Dict[str, object] = {
            "target": name,
            "f_vector": cx.f_vector(),
            "n_faces": cx.n_faces(),
            "euler": cx.euler_characteristic(),
            "downward_closed": cx.is_closed(),
            "n_free_faces": len(cx.free_faces()),
            "homology": {str(d): {"betti": v["betti"], "torsion": v["torsion"]}
                         for d, v in h.items()},
            "expected": ANCHOR_EXPECT[name],
        }
        # pi_1 for the complexes that do not arrive as presentation complexes
        if name == "bing":
            gens, rels = pi1_presentation(cx)
            ng, rel = tietze_simplify(len(gens), rels, rounds=5000)
            row["pi1_tietze"] = {"gens_before": len(gens), "rels_before": len(rels),
                                 "gens_after": ng, "rels_after": len(rel)}
            row["pi1_trivial_certified"] = (ng == 0 and len(rel) == 0)

        # base: is K itself collapsible?
        rb = search_collapse(cx, restarts=200, seed=3, strategies=BEST_STRATEGIES,
                             time_budget=per_target_s / 3)
        row["base_collapsible_found"] = bool(rb["success"])

        # K x I: deterministic collapse onto the bottom copy (leg (a))
        work, bottom = prism(cx, 1)
        det = cylinder_collapse_sequence(cx, 1)
        cert = dump_certificate(certdir, f"anchor_{name}_onto_bottom", work, det,
                                "subcomplex", bottom)
        row["prism_f_vector"] = work.f_vector()
        row["prism_n_faces"] = work.n_faces()
        row["onto_bottom_deterministic"] = {"n_steps": len(det),
                                            "replay_ok": cert["replay_ok"]}

        # K x I -> point (blind search, the phase-C instrument)
        score = prism_level_score(work.stride, work.layers, BEST_SCORE)
        rp = search_collapse(work, restarts=100000, seed=5,
                             strategies=BEST_STRATEGIES,
                             time_budget=per_target_s, score=score)
        row["prism_to_point_found"] = bool(rp["success"])
        row["prism_to_point_restarts"] = rp["restarts_used"]
        if rp["success"]:
            c = dump_certificate(certdir, f"anchor_{name}_prism_to_point", work,
                                 rp["sequence"], "point")
            row["prism_to_point_cert"] = {k: c[k] for k in ("path", "replay_ok",
                                                            "n_steps")}
        else:
            row["prism_to_point_best_left"] = rp.get("best_faces_left")
        row["elapsed_s"] = round(time.time() - t0, 1)
        print(f"[anchor] {name}: {row['expected']} -> base={row['base_collapsible_found']} "
              f"prismpt={row['prism_to_point_found']} "
              f"bottom_ok={row['onto_bottom_deterministic']['replay_ok']}", flush=True)
        sink.add("anchors", row)


# =====================================================================================
# phase B -- the positive-power ladder
# =====================================================================================


def dunce_subcomplex(cx: Complex, info: Dict[str, object]) -> Complex:
    """The induced subcomplex of a padded complex on the dunce-hat part."""
    labels: List[str] = info["labels"]        # type: ignore[assignment]
    keep = {i for i, s in enumerate(labels)
            if s == "v" or s.startswith("x") or s.startswith("u0_") or s == "c0"}
    return Complex([f for f in cx.faces if set(f) <= keep], "dunce_part")


def padded_dunce(pad: int, subdivision: int = 3):
    """``<x, a, b, ... | xxX, a, b, ...>``: a dunce hat wedged with ``pad`` discs.

    The padding relators are single letters, so each padding disc is glued along a
    loop that occurs in no other relator; every edge of that loop lies in exactly one
    triangle of the disc, so the padding collapses away and ``K`` collapses onto the
    dunce hat.  Hence ``K x I`` is collapsible **iff** the dunce prism is (up to the
    triangulation of the padding), which phase A certifies directly -- so this is a
    size ladder whose positives are guaranteed by construction, not assumed.
    """
    pads = [c for c in "abdefghijklmnopqrstuvwz"][:pad]
    words = ("xxX",) + tuple(pads)
    gens = ("x",) + tuple(pads)
    return presentation_complex(words, gens, subdivision, f"dunce+{pad}pad")


def hit_rate(work: Complex, score, strategies: Sequence[str], seed: int,
             time_budget: float, max_runs: int = 10 ** 9,
             prefix=()) -> Dict[str, object]:
    """Blind restarted search; returns hits/runs plus the first certificate found."""
    faces = work.faces
    t0 = time.time()
    hits = 0
    runs = 0
    first = None
    while runs < max_runs and time.time() - t0 < time_budget:
        st = strategies[runs % len(strategies)]
        rng = random.Random((seed * 7_919 + runs * 2_654_435_761) & 0xFFFFFFFF)
        seq, res = run_collapse(faces, rng, st, (), 0.0, score, prefix)
        runs += 1
        if len(res) == 1 and len(next(iter(res))) == 1:
            hits += 1
            if first is None:
                first = (seq, runs, st)
    return {"hits": hits, "runs": runs, "rate": (hits / runs) if runs else None,
            "elapsed_s": round(time.time() - t0, 1), "first": first}


def phase_ladder(sink: Sink, per_unit_s: float, certdir: str) -> None:
    units: List[Tuple[str, Complex, Dict[str, object], int]] = []
    for sub in (3, 4, 5, 6):
        cx, info = build_target("dunce", sub)
        units.append((f"dunce_s{sub}", cx, info, 1))
        if sub == 3:
            units.append((f"dunce_s{sub}", cx, info, 2))
    for pad in (2, 4, 6, 8, 10):
        cx, info = padded_dunce(pad, 3)
        units.append((f"dunce+{pad}pad", cx, info, 1))
    cxb, infob = build_target("bing", 3)
    units.append(("bing", cxb, infob, 1))
    units.append(("bing", cxb, infob, 2))

    for label, cx, info, layers in units:
        t0 = time.time()
        work, _bottom = prism(cx, layers)
        score = prism_level_score(work.stride, work.layers, BEST_SCORE)
        r = hit_rate(work, score, BEST_STRATEGIES, seed=17 + layers,
                     time_budget=per_unit_s)
        row: Dict[str, object] = {
            "label": f"{label}_L{layers}",
            "base_f_vector": cx.f_vector(),
            "base_n_faces": cx.n_faces(),
            "base_free_faces": len(cx.free_faces()),
            "layers": layers,
            "prism_n_faces": work.n_faces(),
            "prism_f_vector": work.f_vector(),
            "hits": r["hits"], "runs": r["runs"], "rate": r["rate"],
            "elapsed_s": r["elapsed_s"],
            "positive_guaranteed": label.startswith("dunce"),
        }
        if r["first"] is not None:
            seq, at, st = r["first"]
            c = dump_certificate(certdir, f"ladder_{label}_L{layers}", work, seq,
                                 "point")
            row["cert"] = {k: c[k] for k in ("path", "replay_ok", "n_steps")}
            row["first_hit_run"] = at
            row["first_hit_strategy"] = st
        print(f"[ladder] {row['label']:16s} faces={work.n_faces():6d} "
              f"hits={r['hits']}/{r['runs']} rate={r['rate']}", flush=True)
        row["wall_s"] = round(time.time() - t0, 1)
        sink.add("ladder", row)


# =====================================================================================
# phase C -- AK(2) control and AK(3) question
# =====================================================================================


def phase_targets(sink: Sink, per_unit_s: float, certdir: str,
                  morse_s: float, subdivisions: Sequence[int] = (3, 4),
                  layer_list: Sequence[int] = (1, 2)) -> None:
    for name, words in (("ak2", AK2_WORDS), ("ak3", AK3_WORDS)):
        for sub in subdivisions:
            for layers in layer_list:
                t0 = time.time()
                cx, info = build_target(name, sub)
                work, bottom = prism(cx, layers)
                score = prism_level_score(work.stride, work.layers, BEST_SCORE)
                row: Dict[str, object] = {
                    "target": name, "words": list(words),
                    "subdivision": sub, "layers": layers,
                    "base_f_vector": cx.f_vector(),
                    "base_free_faces": len(cx.free_faces()),
                    "prism_n_faces": work.n_faces(),
                    "prism_f_vector": work.f_vector(),
                }
                # leg (a): deterministic, no search
                det = cylinder_collapse_sequence(cx, layers)
                c = dump_certificate(certdir, f"{name}_s{sub}_L{layers}_onto_bottom",
                                     work, det, "subcomplex", bottom)
                row["onto_bottom"] = {"n_steps": len(det), "replay_ok": c["replay_ok"],
                                      "path": c["path"]}
                # leg (b): blind search
                r = hit_rate(work, score, BEST_STRATEGIES, seed=101 + sub * 10 + layers,
                             time_budget=per_unit_s)
                row.update({"hits": r["hits"], "runs": r["runs"], "rate": r["rate"],
                            "search_elapsed_s": r["elapsed_s"]})
                if r["first"] is not None:
                    seq, at, st = r["first"]
                    cc = dump_certificate(certdir, f"{name}_s{sub}_L{layers}_to_point",
                                          work, seq, "point")
                    row["cert"] = {k: cc[k] for k in ("path", "replay_ok", "n_steps")}
                    row["first_hit_run"] = at
                # guided opening: spend the prism over k random 2-cells first
                tris = [f for f in cx.faces if len(f) == 3]
                grow = {"hits": 0, "runs": 0}
                gt0 = time.time()
                rr = random.Random(7 * sub + layers)
                while time.time() - gt0 < per_unit_s / 2:
                    k = rr.randint(1, max(1, len(tris) // 8))
                    pre = partial_cylinder_prefix(cx, rr.sample(tris, k), layers)
                    g = hit_rate(work, score, BEST_STRATEGIES,
                                 seed=rr.randrange(10 ** 9), time_budget=1.0,
                                 prefix=pre)
                    grow["hits"] += g["hits"]
                    grow["runs"] += g["runs"]
                    if g["first"] is not None:
                        seq, _at, _st = g["first"]
                        cc = dump_certificate(
                            certdir, f"{name}_s{sub}_L{layers}_guided_to_point",
                            work, seq, "point")
                        grow["cert"] = {k: cc[k] for k in ("path", "replay_ok",
                                                           "n_steps")}
                        break
                row["guided"] = grow
                # graded near-miss: minimal discrete Morse vector seen
                best = None
                mt0 = time.time()
                sweeps = 0
                while time.time() - mt0 < morse_s:
                    rng = random.Random(sweeps * 6_364_136 + sub * 31 + layers)
                    m = random_discrete_morse(work.faces, rng, "uniform-lifo", score)
                    sweeps += 1
                    key = (m["total_critical"], m["morse"])
                    if best is None or key < best[0]:
                        best = (key, m)
                row["morse"] = {"sweeps": sweeps,
                                "best_vector": None if best is None else best[1]["morse"],
                                "best_total": None if best is None else
                                best[1]["total_critical"],
                                "euler_check": None if best is None else
                                best[1]["euler_check"]}
                row["wall_s"] = round(time.time() - t0, 1)
                print(f"[target] {name} s={sub} L={layers} faces={work.n_faces()} "
                      f"blind={r['hits']}/{r['runs']} guided={grow['hits']}/{grow['runs']} "
                      f"morse={row['morse']['best_vector']}", flush=True)
                sink.add("targets", row)


# =====================================================================================
# CLI
# =====================================================================================


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="R10 Zeeman collapse battery")
    ap.add_argument("--out", default="results/stable_ac/fable/zeeman_collapse.json")
    ap.add_argument("--certdir", default="results/stable_ac/fable/zeeman_certs")
    ap.add_argument("--phase", default="all",
                    choices=("all", "anchors", "ladder", "targets"))
    ap.add_argument("--anchor-seconds", type=float, default=8.0)
    ap.add_argument("--ladder-seconds", type=float, default=25.0)
    ap.add_argument("--target-seconds", type=float, default=120.0)
    ap.add_argument("--morse-seconds", type=float, default=45.0)
    ap.add_argument("--subdivisions", type=int, nargs="*", default=[3, 4])
    ap.add_argument("--layers", type=int, nargs="*", default=[1, 2])
    args = ap.parse_args(argv)

    sink = Sink(args.out)
    sink.note("One-sided instrument: a collapse is a replayable certificate, a failure "
              "is silence. Read phase C only against phase B's measured hit rates.")
    if args.phase in ("all", "anchors"):
        phase_anchors(sink, args.anchor_seconds, args.certdir)
    if args.phase in ("all", "ladder"):
        phase_ladder(sink, args.ladder_seconds, args.certdir)
    if args.phase in ("all", "targets"):
        phase_targets(sink, args.target_seconds, args.certdir, args.morse_seconds,
                      args.subdivisions, args.layers)
    print(f"[done] wrote {args.out}", flush=True)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
