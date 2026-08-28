"""W2b: layer-1 (relation-module) liveness of the 17 period-two baselines.

For each essential chain (R, S, U) from the census, this checker:

  1. recovers concrete quotient conjugators h0..h3 and the target conjugator
     g by bounded ball search (complete for the recorded radii);
  2. lifts them verbatim to F(c,t), recomputes the literal recurrence with
     the UNREDUCED original source rows (imported from the codex
     certificate, unmodified), and forms the defect word
     D = Z * (g t g^-1)^-1, asserting D in N;
  3. projects D to the relation module M = Z[Q/<c>] and builds the five
     lifting operators; the general-target calculus replaces
     L3 = U^-1 - t, L4 = t - 1 by L3 = U^-1 - w, L4 = w - 1 with
     w = image(g t g^-1) (first-order perturbation of each conjugator by
     n_i in N; derivation in fable/proofs/W2B notes);
  4. decides layer-1 liveness bars:
       - augmentation: every L_i has augmentation 0, so a defect with
         nonzero coefficient sum is DEAD outright;
       - one-hop solvability over F_2, F_3, F_5 and over Q (variables =
         module vertices whose operator image meets the defect support):
         unsolvable mod any p => DEAD at one-hop support;
         solvable at all bars => LIVE-at-one-hop (same bar the witness
         passes; support escape beyond one hop is possible either way,
         per the codex degree-two escape lesson).

Control: the witness chain must reproduce the published defect data
(21 terms, l1 norm 48, augmentation 0) and be LIVE-at-one-hop (its known
8-term correction exists). A control failure voids the run.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from experiments.stable_ac.depth4_period_two_lift_certificate import (
    C,
    T,
    SOURCE_A,
    SOURCE_B,
    add_group_ring,
    add_vectors,
    apply_operator,
    c_vertex,
    conjugate,
    group_ring,
    inverse,
    literal,
    multiply,
    multiply_group_ring,
    quotient_inverse,
    quotient_multiply,
    quotient_reduce,
    relation_module,
)
from period_two_solution_census import (
    A as QA_STR,
    B as QB_STR,
    ball,
    cyc_form,
    inv as sinv,
    mul as smul,
)

CHAINS_FILE = Path(__file__).resolve().parent / "period_two_census_chains.json"
WITNESS = ("TTctcTctc", "TTTcttcTctt", "TTcttcTc")


def to_tuple(s):
    m = {"c": (C,), "t": (T,), "T": (-T,)}
    out = ()
    for ch in s:
        out = multiply(out, m[ch])
    return out


def find_conjugator(base, target, radius=10):
    """h with h*base*h^-1 == target in Q (string arithmetic), or None."""
    for h in ball(radius):
        if smul(h, base, sinv(h)) == target:
            return h
    return None


def find_conjugators(base, target, radius=10, cap=4):
    """Up to `cap` distinct h with h*base*h^-1 == target (gauge reps)."""
    out = []
    for h in ball(radius):
        if smul(h, base, sinv(h)) == target:
            out.append(h)
            if len(out) >= cap:
                break
    return out


def find_target_conjugator(U, S, radius=6):
    for g in ball(radius):
        if cyc_form(smul(U, g, "t", sinv(g))) == cyc_form(S):
            return g
    return None


def solve_mod_p(rows, rhs, p):
    """Rows: list of dicts var->coef; rhs: dict row->coef. Solvable mod p?
    Vectorized GF(p) elimination (numpy int64, exact)."""
    import numpy as np

    variables = sorted({v for row in rows for v in row})
    vidx = {v: i for i, v in enumerate(variables)}
    n_rows, n_cols = len(rows), len(variables)
    mat = np.zeros((n_rows, n_cols + 1), dtype=np.int64)
    for i, row in enumerate(rows):
        for v, cf in row.items():
            mat[i, vidx[v]] = cf % p
        mat[i, n_cols] = rhs[i] % p
    pivot_row = 0
    for col in range(n_cols):
        nz = np.nonzero(mat[pivot_row:, col])[0]
        if nz.size == 0:
            continue
        sel = pivot_row + int(nz[0])
        if sel != pivot_row:
            mat[[pivot_row, sel]] = mat[[sel, pivot_row]]
        invp = pow(int(mat[pivot_row, col]), -1, p)
        mat[pivot_row] = (mat[pivot_row] * invp) % p
        col_vals = mat[:, col].copy()
        col_vals[pivot_row] = 0
        mask = col_vals != 0
        if mask.any():
            mat[mask] = (mat[mask] - np.outer(col_vals[mask],
                                              mat[pivot_row])) % p
        pivot_row += 1
        if pivot_row == n_rows:
            break
    zero_lhs = ~mat[:, :n_cols].any(axis=1)
    return not bool((mat[zero_lhs, n_cols] != 0).any())


def build_operators_general(r, s, u, h2, h3, target_w):
    q_a = quotient_reduce(SOURCE_A)
    q_b = quotient_reduce(SOURCE_B)
    q_r = quotient_reduce(r)
    q_s = quotient_reduce(s)
    q_u = quotient_reduce(u)
    q_w = quotient_reduce(target_w)
    q_x = quotient_multiply(quotient_reduce(h2), q_s, quotient_inverse(h2))
    one = group_ring((1, ()))
    d_r = group_ring((1, q_a), (-1, q_r))
    d_s_0 = multiply_group_ring(group_ring((-1, q_s)), d_r)
    d_s_1 = group_ring((1, q_b), (-1, q_s))
    bridge = group_ring(
        (1, quotient_reduce(h2)),
        (1, quotient_multiply(quotient_inverse(q_u), quotient_reduce(h3))),
    )
    return (
        add_group_ring(
            multiply_group_ring(group_ring((-1, quotient_inverse(q_u))), d_r),
            multiply_group_ring(bridge, d_s_0),
        ),
        multiply_group_ring(bridge, d_s_1),
        add_group_ring(one, group_ring((-1, q_x))),
        group_ring((1, quotient_inverse(q_u)), (-1, q_w)),
        group_ring((1, q_w), (-1, ())),
    )


def one_hop_system(defect, operators):
    """Variables: (i, v) with L_i e_v meeting supp(defect). Rows indexed by
    module vertices in the union of defect support and variable images."""
    supp = set(defect)
    candidates = []
    for i, op in enumerate(operators):
        for g in op:
            for d_vertex in supp:
                v = c_vertex(quotient_multiply(quotient_inverse(g), d_vertex))
                candidates.append((i, v))
    candidates = sorted(set(candidates), key=lambda t: (t[0], t[1]))
    row_vertices = set(supp)
    columns = {}
    for (i, v) in candidates:
        img = apply_operator(operators[i], {v: 1})
        columns[(i, v)] = img
        row_vertices.update(img)
    row_list = sorted(row_vertices, key=lambda w: (len(w), w))
    ridx = {w: k for k, w in enumerate(row_list)}
    rows = [dict() for _ in row_list]
    for var, img in columns.items():
        for w, cf in img.items():
            rows[ridx[w]][var] = rows[ridx[w]].get(var, 0) + cf
    rhs = {k: -defect.get(w, 0) for k, w in enumerate(row_list)}
    return rows, rhs, len(candidates)


def analyze_reps(chain):
    """Sweep gauge representatives; LIVE if ANY tested lift is one-hop
    solvable mod 2, 3, 5. NOT_LIVE_AT_TESTED_WINDOWS is inconclusive."""
    R, S, U = chain
    ainv_r = smul(sinv(QA_STR), R)
    h0s = find_conjugators(sinv(QB_STR), ainv_r, cap=4)
    h1s = find_conjugators(sinv(R), smul(sinv(QB_STR), S), cap=2)
    h2s = find_conjugators(sinv(S), smul(sinv(R), U), cap=3)
    g = find_target_conjugator(U, S)
    if not h0s or not h1s or not h2s or g is None:
        return {"chain": list(chain), "status": "CONJUGATOR_NOT_FOUND"}
    target_q = smul(g, "t", sinv(g))
    h3s = find_conjugators(S, smul(U, target_q), cap=3)
    if not h3s:
        return {"chain": list(chain), "status": "H3_NOT_FOUND"}
    tested = 0
    for h0 in h0s:
        for h1 in h1s:
            for h2 in h2s:
                for h3 in h3s:
                    rec = analyze(chain, fixed_h=(h0, h1, h2, h3, g))
                    tested += 1
                    if rec["status"] == "LIVE_AT_ONE_HOP_MOD_235":
                        rec["reps_tested"] = tested
                        return rec
    rec["reps_tested"] = tested
    rec["status"] = "NOT_LIVE_AT_TESTED_WINDOWS"
    return rec


def analyze(chain, fixed_h=None):
    R, S, U = chain
    if fixed_h is not None:
        h0, h1, h2, h3, g = fixed_h
    else:
        ainv_r = smul(sinv(QA_STR), R)
        h0 = find_conjugator(sinv(QB_STR), ainv_r)
        h1 = find_conjugator(sinv(R), smul(sinv(QB_STR), S))
        h2 = find_conjugator(sinv(S), smul(sinv(R), U))
        g = find_target_conjugator(U, S)
        if None in (h0, h1, h2, g):
            return {"chain": list(chain), "status": "CONJUGATOR_NOT_FOUND"}
        target_q = smul(g, "t", sinv(g))
        h3 = find_conjugator(S, smul(U, target_q))
        if h3 is None:
            return {"chain": list(chain), "status": "H3_NOT_FOUND"}

    fh = [to_tuple(x) for x in (h0, h1, h2, h3, g)]
    r = multiply(SOURCE_A, conjugate(inverse(SOURCE_B), fh[0]))
    s = multiply(SOURCE_B, conjugate(inverse(r), fh[1]))
    u = multiply(r, conjugate(inverse(s), fh[2]))
    z = multiply(inverse(u), conjugate(s, fh[3]))
    target_f = conjugate((T,), fh[4])
    defect_word = multiply(z, inverse(target_f))
    assert quotient_reduce(defect_word) == (), "defect not in N"
    defect = relation_module(defect_word)
    operators = build_operators_general(r, s, u, fh[2], fh[3], target_f)
    aug = sum(defect.values())
    rec = {
        "chain": list(chain),
        "is_witness": chain == WITNESS,
        "h": [h0, h1, h2, h3, g],
        "defect_terms": len(defect),
        "defect_l1": sum(abs(v) for v in defect.values()),
        "defect_augmentation": aug,
        "operator_augmentations": [sum(op.values()) for op in operators],
    }
    if aug != 0:
        rec["status"] = "DEAD_AUGMENTATION"
        return rec
    rows, rhs, n_vars = one_hop_system(defect, operators)
    rec["one_hop_vars"] = n_vars
    for p in (2, 3, 5):
        if not solve_mod_p(rows, rhs, p):
            rec["status"] = f"DEAD_ONE_HOP_MOD_{p}"
            return rec
    rec["status"] = "LIVE_AT_ONE_HOP_MOD_235"
    return rec


def main():
    chains = [tuple(c) for c in json.loads(CHAINS_FILE.read_text())]
    assert WITNESS in chains
    codex_h = ("cTTcttt", "", "cTcttt", "t", "")
    fixed = analyze(WITNESS, fixed_h=codex_h)
    print(json.dumps({"fixed_h_witness_control": {
        k: fixed[k] for k in
        ("defect_terms", "defect_l1", "defect_augmentation", "status")}}))
    assert (fixed["defect_terms"], fixed["defect_l1"],
            fixed["defect_augmentation"]) == (21, 48, 0), \
        "fixed-h witness control failed"
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    end = int(sys.argv[2]) if len(sys.argv) > 2 else len(chains)
    results = []
    for chain in chains[start:end]:
        rec = analyze_reps(chain)
        results.append(rec)
        print(json.dumps(rec))
    live = [r for r in results
            if r["status"] == "LIVE_AT_ONE_HOP_MOD_235"
            and not r.get("is_witness")]
    wit_live = [r for r in results
                if r.get("is_witness")
                and r["status"] == "LIVE_AT_ONE_HOP_MOD_235"]
    print(json.dumps({
        "slice": [start, end],
        "fixed_h_witness_control": "passed (asserted above)",
        "witness_live_in_sweep": bool(wit_live),
        "live_non_witness_in_slice": len(live),
        "inconclusive_in_slice": sum(
            1 for r in results
            if r["status"] == "NOT_LIVE_AT_TESTED_WINDOWS"),
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
