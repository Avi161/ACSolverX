"""W5.1 — certify: the MMS02 bridge is EQUIVALENT to one-stabilization
AC-triviality of the published rank-two descendant Q (hence, via the repo's
53-move Appendix-F replay, of AK(3)).

What is certified here, step by literal step:

  1. alpha in Aut(F3), alpha: x->x, y->y, z->Yxz, satisfies alpha(Xyz) = z,
     and is an automorphism (its inverse z->Xyz is exhibited and both
     composites are checked to be the identity on generators).
  2. alpha(Tpub) = (alpha A, alpha B, z).
  3. An explicit sequence of literal AC2 moves (multiply a row by a conjugate
     of the row z) carries (alpha A, alpha B, z) to (Q1, Q2, z), where
     (Q1,Q2) = (A,B) with z := Yx.  Every move is verified by
     ``check_ac2``; a deliberately corrupted move is verified to be REJECTED
     (adversarial control).
  4. The same for Txy with alpha': z->zxy, alpha'(zYX) = z, landing on the
     recorded U=xy pair.
  5. Both endpoint pairs are checked against the spellings recorded in
     .scratch/mms02_u_xy_bridge.md (independent-source control).

Run:
  python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- \
      python3 fable/proofs/checkers/bridge_reduction.py
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from w5_words import (  # noqa: E402
    A, B, K_PUB, K_XY, REC_PAIR_PUB, REC_PAIR_XY,
    apply_ac2, check_ac2, drop_gen, inv, mul, reduce_word, subst,
)

FAILS: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    print(f"{'PASS' if cond else 'FAIL'}  {name}" + (f"   {detail}" if detail else ""))
    if not cond:
        FAILS.append(name)


def is_automorphism(images: dict[str, str], inverse: dict[str, str]) -> bool:
    for g in "xyz":
        if subst(images[g], inverse) != g:
            return False
        if subst(inverse[g], images) != g:
            return False
    return True


def eliminate_z(state: tuple[str, str, str]) -> tuple[tuple[str, str, str], list]:
    """Delete every z-letter from rows 0,1 using literal AC2 moves against row 2 = z.

    If r = p z^e s then r * (s^-1 z^-e s) = p s, so w = s^-1 is the conjugator.
    Every step is verified as a legal AC2 move before it is taken.
    """
    moves = []
    cur = tuple(reduce_word(r) for r in state)
    assert cur[2] == "z"
    for i in (0, 1):
        while True:
            r = cur[i]
            pos = next((k for k, c in enumerate(r) if c.lower() == "z"), None)
            if pos is None:
                break
            e = 1 if r[pos] == "z" else -1
            s = r[pos + 1:]
            w = inv(s)
            nxt = apply_ac2(cur, i, 2, -e, w)
            assert check_ac2(cur, nxt, i, 2, -e, w), "illegal move constructed"
            moves.append({"row": i, "donor": 2, "exp": -e, "conj": w,
                          "before": cur[i], "after": nxt[i]})
            cur = nxt
    return cur, moves  # type: ignore[return-value]


def main() -> int:
    # ---- 1. the two changes of basis --------------------------------------
    alpha = {"x": "x", "y": "y", "z": "Yxz"}          # alpha(Xyz) = z
    alpha_inv = {"x": "x", "y": "y", "z": "Xyz"}
    beta = {"x": "x", "y": "y", "z": "zxy"}           # beta(zYX) = z
    beta_inv = {"x": "x", "y": "y", "z": "zYX"}

    check("alpha is an automorphism of F3", is_automorphism(alpha, alpha_inv))
    check("beta is an automorphism of F3", is_automorphism(beta, beta_inv))
    check("alpha(Xyz) = z", subst(K_PUB, alpha) == "z", subst(K_PUB, alpha))
    check("beta(zYX) = z", subst(K_XY, beta) == "z", subst(K_XY, beta))

    # ---- 2/3. Tpub -> (Q1,Q2,z) -------------------------------------------
    tpub_img = (subst(A, alpha), subst(B, alpha), subst(K_PUB, alpha))
    end_pub, moves_pub = eliminate_z(tpub_img)  # type: ignore[arg-type]
    q_direct = (reduce_word(subst(A, {"x": "x", "y": "y", "z": "Yx"})),
                reduce_word(subst(B, {"x": "x", "y": "y", "z": "Yx"})))
    check("Tpub: AC2 z-elimination lands on (A,B)|_{z=Yx}",
          end_pub[:2] == q_direct, f"{len(moves_pub)} moves")
    check("Tpub: endpoint row 2 is still z", end_pub[2] == "z")
    check("Tpub: (A,B)|_{z=Yx} equals the recorded published pair Q",
          q_direct == REC_PAIR_PUB, str(q_direct))

    # ---- 4. Txy -> (P1,P2,z) ----------------------------------------------
    txy_img = (subst(A, beta), subst(B, beta), subst(K_XY, beta))
    end_xy, moves_xy = eliminate_z(txy_img)  # type: ignore[arg-type]
    p_direct = (reduce_word(subst(A, {"x": "x", "y": "y", "z": "xy"})),
                reduce_word(subst(B, {"x": "x", "y": "y", "z": "xy"})))
    check("Txy: AC2 z-elimination lands on (A,B)|_{z=xy}",
          end_xy[:2] == p_direct, f"{len(moves_xy)} moves")
    check("Txy: (A,B)|_{z=xy} equals the recorded U=xy pair",
          p_direct == REC_PAIR_XY, str(p_direct))

    # ---- 5. dropping z agrees with substituting z:=1 -----------------------
    check("z-deletion = substitution z:=Yx on A",
          drop_gen(tpub_img[0], "z") == q_direct[0])
    check("z-deletion = substitution z:=xy on A",
          drop_gen(txy_img[0], "z") == p_direct[0])

    # ---- adversarial controls ---------------------------------------------
    m = moves_pub[0]
    before = tuple(reduce_word(r) for r in tpub_img)
    good = apply_ac2(before, m["row"], 2, m["exp"], m["conj"])
    check("control(+): the first recorded move verifies",
          check_ac2(before, good, m["row"], 2, m["exp"], m["conj"]))
    bad_conj = m["conj"] + "x"
    check("control(-): same move with a corrupted conjugator is REJECTED",
          not check_ac2(before, good, m["row"], 2, m["exp"], bad_conj))
    bad_state = (good[0], mul(good[1], "x"), good[2])
    check("control(-): a move that also perturbs a passive row is REJECTED",
          not check_ac2(before, bad_state, m["row"], 2, m["exp"], m["conj"]))
    check("control(-): wrong donor exponent is REJECTED",
          not check_ac2(before, good, m["row"], 2, -m["exp"], m["conj"]))

    # ---- Lemma 1 step: a transposition of two rows IS a word in AC1/AC2 -----
    # (u,v,w) -> (u,vu,w) -> (v^-1,vu,w) -> (v^-1,u,w) -> (v,u,w)
    rng = __import__("random").Random(5)
    trans_ok = True
    for _ in range(200):
        T = tuple(reduce_word("".join(rng.choice("xyzXYZ") for _ in range(rng.randint(1, 8))))
                  for _ in range(3))
        if any(t == "" for t in T):
            continue
        s = T
        seq = [(1, 0, 1, ""), (0, 1, -1, ""), (1, 0, 1, inv(T[0]))]
        for (i, j, e, cw) in seq:
            nxt = apply_ac2(s, i, j, e, cw)
            trans_ok &= check_ac2(s, nxt, i, j, e, cw)
            s = nxt
        s = (inv(s[0]), s[1], s[2])          # AC1 on row 0
        trans_ok &= (s == (reduce_word(T[1]), reduce_word(T[0]), reduce_word(T[2])))
    check("Lemma 1: row transposition realised by 3 AC2 moves + 1 AC1, on 200 "
          "random triples (so Nielsen transformations are AC moves)", trans_ok)

    # ---- provenance dump ---------------------------------------------------
    out = {
        "alpha": alpha, "beta": beta,
        "tpub_after_basis_change": list(tpub_img),
        "txy_after_basis_change": list(txy_img),
        "Q": list(q_direct), "P": list(p_direct),
        "n_moves_pub": len(moves_pub), "n_moves_xy": len(moves_xy),
        "moves_pub": moves_pub, "moves_xy": moves_xy,
    }
    dest = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "out", "w5_bridge_reduction.json")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w") as fh:
        json.dump(out, fh, indent=1)
    print(f"\nwrote {dest}")
    print(f"Q  = {q_direct}")
    print(f"P  = {p_direct}")
    print("\n" + ("ALL CHECKS PASS" if not FAILS else f"FAILURES: {FAILS}"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    raise SystemExit(main())
