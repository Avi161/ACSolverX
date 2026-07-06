"""Certified-descendant catalog: randomized Lemma-11 cascades from the corrected
Wirtinger W down to 2-generator presentations. Every leaf is stably AC-trivial by
construction (Prop 12 + Lemma 11) and ships a verifying certificate.

Search dimensions: deleted relator k (1..14), the added word w (bank over the original
14 generators, exponent sum +-1), the elimination order (random permutations; at each
step any generator with an exactly-once relator may go), and which generator the final
w-elimination removes. Leaves are deduped by relabel-canonical key; we keep the
shortest N (they feed the MITM search lanes).

Run:  .venv/bin/python3 experiments/stable_ac/ak3_stable_proof/catalog.py \
          --iters 20000 --seed 0 --out results/stable_ac/ak3_stable_proof/catalog
Resumable/append-only: leaves stream to catalog_leaves.jsonl (dedup on resume);
certificates for the best leaves are written separately by --emit_certs.
"""
import argparse
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)

from presentation import (  # noqa: E402
    abelianization_det, relabel_canonical_key, total_length,
)
from stable_moves import LengthCapExceeded, occurrences  # noqa: E402
from verify_certificate import verify  # noqa: E402
from wirtinger import Cascade, N_W  # noqa: E402


def w_bank(rng, n_words=None):
    """Words over the original 14 generators with exponent sum +-1. Deterministic core
    bank + optional random extras."""
    bank = []
    for i in range(1, N_W + 1):
        bank.append((-i % (N_W + 1) or 1,))  # placeholder replaced below
    bank = [(i,) for i in range(1, N_W + 1)]                      # w = x_i
    for i in (6, 10, 14):
        for j in (6, 10, 14):
            for k in (6, 10, 14):
                if len({i, j, k}) >= 2:
                    bank.append((-i, j, k))                        # x_i^-1 x_j x_k
    bank.append((-10, 14, 6))                                      # the paper-analog w
    seen, out = set(), []
    for w in bank:
        if sum(1 if a > 0 else -1 for a in w) in (1, -1) and w not in seen:
            seen.add(w)
            out.append(w)
    return out


def random_cascade(rng, delete_k, w, l_cap=64, target_ngen=2):
    """Eliminate randomly-chosen eliminable generators until target_ngen remain.
    Returns the Cascade or None (dead end / cap exceeded)."""
    c = Cascade(delete_k=delete_k, w=list(w), l_cap=l_cap)
    while c.n_gen > target_ngen:
        cands = []
        for og in c.alive():
            g = c.cur[og]
            for i, (tag, r) in enumerate(c.rels):
                if len(occurrences(r, g)) == 1:
                    cands.append((og, tag))
        if not cands:
            return None
        og, tag = cands[rng.randrange(len(cands))]
        try:
            c.eliminate_gen(og, prefer_tag=tag)
        except LengthCapExceeded:
            return None
    return c


def leaf_record(c, seed_info):
    state = c._state()
    key = relabel_canonical_key(state, 2)
    return {
        "key": key.hex(),
        "total_len": total_length(state),
        "relators": [list(r) for r in state],
        "abel_det": abelianization_det(state, 2),
        "delete_k": c.delete_k,
        "w_original": c.w_original,
        "elim_seq": [(s["orig_gen"], s["via_tag"]) for s in c.steps
                     if s["type"] == "eliminate"],
        "seed_info": seed_info,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iters", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--l_cap", type=int, default=64)
    ap.add_argument("--out", default=os.path.join(ROOT, "results", "stable_ac",
                                                  "ak3_stable_proof", "catalog"))
    ap.add_argument("--emit_certs", type=int, default=0,
                    help="write verified certificates for the N shortest leaves")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    leaves_path = os.path.join(args.out, "catalog_leaves.jsonl")

    seen = set()
    if os.path.exists(leaves_path):
        with open(leaves_path) as f:
            for line in f:
                try:
                    seen.add(json.loads(line)["key"])
                except Exception:
                    pass
    print(f"resuming with {len(seen)} known leaves")

    rng = random.Random(args.seed)
    bank = w_bank(rng)
    n_new, n_dead = 0, 0
    best = []
    with open(leaves_path, "a") as f:
        for it in range(args.iters):
            delete_k = rng.randrange(1, N_W + 1)
            w = bank[rng.randrange(len(bank))]
            c = random_cascade(rng, delete_k, w, l_cap=args.l_cap)
            if c is None:
                n_dead += 1
                continue
            state = c._state()
            d = abelianization_det(state, 2)
            if d is None or abs(d) != 1:
                raise AssertionError(f"leaf with |det|={d}: {state}")
            rec = leaf_record(c, {"seed": args.seed, "iter": it})
            if rec["key"] in seen:
                continue
            seen.add(rec["key"])
            n_new += 1
            f.write(json.dumps(rec) + "\n")
            f.flush()
            best.append((rec["total_len"], rec["key"]))
    best.sort()
    print(f"iters={args.iters} new_leaves={n_new} dead_ends={n_dead} "
          f"total_known={len(seen)}")
    if best:
        print("shortest new leaves:", best[:10])

    if args.emit_certs:
        # re-derive + verify certificates for the N shortest leaves overall
        with open(leaves_path) as f:
            recs = [json.loads(line) for line in f]
        recs.sort(key=lambda r: r["total_len"])
        certs_dir = os.path.join(args.out, "certs")
        os.makedirs(certs_dir, exist_ok=True)
        n_ok = 0
        for rec in recs[:args.emit_certs]:
            c = Cascade(delete_k=rec["delete_k"], w=rec["w_original"], l_cap=args.l_cap)
            try:
                for og, tag in rec["elim_seq"]:
                    c.eliminate_gen(og, prefer_tag=tag)
            except (LengthCapExceeded, ValueError):
                print(f"  cert re-derivation failed for {rec['key'][:16]}")
                continue
            state = c._state()
            if relabel_canonical_key(state, 2).hex() != rec["key"]:
                print(f"  cert mismatch for {rec['key'][:16]}")
                continue
            cert = c.certificate(f"wirtinger_leaf_{rec['key'][:16]}",
                                 f"End: 2-generator, total length {rec['total_len']}.")
            ok, errs = verify(cert)
            if not ok:
                print(f"  cert verify FAILED for {rec['key'][:16]}: {errs[:2]}")
                continue
            with open(os.path.join(certs_dir, f"{rec['key'][:16]}.json"), "w") as g:
                json.dump(cert, g)
            n_ok += 1
        print(f"emitted {n_ok}/{min(args.emit_certs, len(recs))} verified certificates")


if __name__ == "__main__":
    main()
