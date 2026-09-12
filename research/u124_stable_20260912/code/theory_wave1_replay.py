"""Independent coordinator replay of theory_wave1 C16–C18.

Rebuilds the claimed identities from the repo word helpers rather than by
executing the inventor's embedded script. This is an identity check, not a
U124 solve and not an elementary certificate: C16 and C18 each use C0 twice.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from math import gcd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.equivalence_classes.lib.autcanon import aut_canon, check  # noqa: E402
from experiments.equivalence_classes.lib.words import (  # noqa: E402
    apply_hom,
    canon_pair,
    cyc_reduce,
    exp_sums,
    free_reduce,
    inv,
)

CODE = Path(__file__).resolve().parent
if str(CODE) not in sys.path:
    sys.path.insert(0, str(CODE))

from ms_template_identities import claimed_q, parametric_p  # noqa: E402

OUT = ROOT / "research" / "u124_stable_20260912" / "tables"
DATA = ROOT / "data" / "ms_unsolved_reps"

XI = "Yxy"  # ξ = y^{-1} x y
AUT_Y_TO_XINV2_Y = {"x": "x", "y": "XXy"}


def pw(letter: str, k: int) -> str:
    if k >= 0:
        return letter * k
    return letter.swapcase() * (-k)


def subst(word: str, img: dict[str, str]) -> str:
    """Free substitution on any alphabet; missing letters are left unchanged."""
    out = []
    for char in word:
        image = img.get(char.lower())
        if image is None:
            out.append(char)
        else:
            out.append(image if char.islower() else inv(image))
    return free_reduce("".join(out))


def same_cyclic(a: str, b: str) -> bool:
    a, b = cyc_reduce(a), cyc_reduce(b)
    if not a and not b:
        return True
    if len(a) != len(b):
        return False
    return b in {a[i:] + a[:i] for i in range(len(a))}


def rotations_and_inverses(word: str) -> list[str]:
    reduced = cyc_reduce(word)
    out = []
    seen = set()
    for spelling in (reduced, inv(reduced)):
        spelling = cyc_reduce(spelling)
        for i in range(len(spelling) or 1):
            rot = spelling[i:] + spelling[:i] if spelling else ""
            if rot not in seen:
                seen.add(rot)
                out.append(rot)
    return out


def magnus(word: str) -> tuple[list[tuple[int, int]], int]:
    """Magnus blocks (index i, exponent e) for ξ_i = y^{-i} x y^i, plus total y-exponent."""
    height = 0
    blocks: list[tuple[int, int]] = []
    for char in word:
        if char in "yY":
            height += 1 if char == "y" else -1
            continue
        exponent = 1 if char == "x" else -1
        index = -height
        if blocks and blocks[-1][0] == index:
            blocks[-1] = (index, blocks[-1][1] + exponent)
        else:
            blocks.append((index, exponent))
    blocks = [b for b in blocks if b[1] != 0]
    return blocks, height


def rebuild_magnus(blocks: list[tuple[int, int]], total: int) -> str:
    body = "".join(pw("y", -index) + pw("x", exponent) + pw("y", index) for index, exponent in blocks)
    return free_reduce(body + pw("y", total))


def q_prime(n: int, delta: int) -> tuple[str, str]:
    return (
        free_reduce("XYxyy" + pw("x", delta) + "Y"),
        free_reduce("Yxxy" + pw("x", n * delta) + "Y"),
    )


def p_pair(n: int, delta: int) -> tuple[str, str]:
    return parametric_p(n, delta)


def s_pair(n: int, delta: int, tag: str = "u") -> tuple[str, str]:
    m = n * delta
    return (
        free_reduce("X" + tag * 3 + pw("x", delta) + tag.upper() * 2),
        free_reduce(
            tag.upper()
            + pw("x", -m)
            + tag.upper() * 2
            + "x"
            + tag * 2
            + pw("x", m)
        ),
    )


def eval_ab(template: str) -> str:
    """Evaluate a word in {x, ξ} written with u standing for ξ."""
    return subst(template, {"x": "x", "u": XI})


def construct_rs(a_tmpl: str, b_tmpl: str, p: int, b: int, c: int) -> tuple[str, str]:
    a_xi = eval_ab(a_tmpl)
    b_xi = eval_ab(b_tmpl)
    r = free_reduce(a_xi + "y" + pw("x", b) + "Y" + b_xi)
    s = free_reduce(pw_word(XI, p) + pw("x", c) + "Y")
    return r, s


def pw_word(word: str, k: int) -> str:
    if k >= 0:
        return free_reduce(word * k)
    return free_reduce(inv(word) * (-k))


def h2_isolator(blocks: list[tuple[int, int]], height: int) -> bool:
    return height == -1 and len(blocks) == 2 and blocks[0][0] == 1 and blocks[1][0] == 0 and blocks[0][1] != 0


def h3_companion(blocks: list[tuple[int, int]], height: int) -> bool:
    if height != 0:
        return False
    support = {index for index, _ in blocks}
    if not support.issubset({0, 1, -1}):
        return False
    minus = [exponent for index, exponent in blocks if index == -1]
    return len(minus) == 1


def check_q_to_q_prime() -> dict:
    rows = []
    for delta in (-1, 1):
        for n in range(2, 9):
            q = claimed_q(n, delta)
            image = (apply_hom(q[0], AUT_Y_TO_XINV2_Y), apply_hom(q[1], AUT_Y_TO_XINV2_Y))
            claimed = q_prime(n, delta)
            freely_equal = image == claimed
            cyclically_equal = same_cyclic(image[0], claimed[0]) and same_cyclic(image[1], claimed[1])
            rows.append(
                {
                    "n": n,
                    "delta": delta,
                    "Q": list(q),
                    "apply_hom_y_to_xinv2_y": list(image),
                    "claimed_Q_prime": list(claimed),
                    "freely_equal": freely_equal,
                    "cyclically_equal": cyclically_equal,
                    "cyc_total_Q_prime": len(cyc_reduce(claimed[0])) + len(cyc_reduce(claimed[1])),
                }
            )
    return {
        "n_checked": len(rows),
        "all_freely_equal": all(r["freely_equal"] for r in rows),
        "all_cyclically_equal": all(r["cyclically_equal"] for r in rows),
        "rows": rows,
    }


def check_c16_u124_instance() -> dict:
    records = []
    for delta in (-1, 1):
        for n in range(2, 8):
            m = n * delta
            r, s = q_prime(n, delta)
            b_r, h_r = magnus(r)
            b_s, h_s = magnus(s)
            assert rebuild_magnus(b_r, h_r) == r
            assert rebuild_magnus(b_s, h_s) == s
            h2 = h2_isolator(b_s, h_s)
            h3 = h3_companion(b_r, h_r)
            i_r = free_reduce("X" + "u" + "y" + pw("x", delta) + "Y")
            i_s = free_reduce("uu" + pw("x", m) + "Y")
            d_row = free_reduce("U" + XI)
            faithful_r = subst(i_r, {"u": XI}) == r
            faithful_s = subst(i_s, {"u": XI}) == s
            isolator_y = sum(ch in "yY" for ch in i_s) == 1
            e = free_reduce("uu" + pw("x", m))
            a_hat = subst(i_r, {"y": e})
            b_hat = subst(d_row, {"y": e})
            claimed_a = free_reduce("Xuuu" + pw("x", delta) + "UU")
            claimed_b = free_reduce("U" + pw("x", -m) + "UUx" + "uu" + pw("x", m))
            c_free = subst(i_r, {"y": free_reduce("uu" + pw("x", m + 11))}) == a_hat
            rho = free_reduce("X" + pw("u", -3) + "xuu")
            legal = same_cyclic(rho, inv(a_hat))
            loop = None
            illegal_shorten = None
            if legal:
                out = free_reduce(b_hat + inv(free_reduce(pw("x", -m) + rho + pw("x", m))))
                pr = (
                    subst(p_pair(n, 1)[0], {"x": "u", "y": "x"}),
                    subst(p_pair(n, 1)[1], {"x": "u", "y": "x"}),
                )
                loop = same_cyclic(a_hat, inv(pr[0])) and same_cyclic(out, inv(pr[1]))
            else:
                # The δ=-1 rotation does not exist. Multiplying by ρ anyway is illegal.
                fake = free_reduce(b_hat + inv(free_reduce(pw("x", -m) + rho + pw("x", m))))
                illegal_shorten = {
                    "rho_is_rotation_of_Ahat_inv": False,
                    "illegal_product": fake,
                    "illegal_cyc_total": len(cyc_reduce(a_hat)) + len(cyc_reduce(fake)),
                    "legal_S_cyc_total": len(cyc_reduce(a_hat)) + len(cyc_reduce(b_hat)),
                }
            records.append(
                {
                    "n": n,
                    "delta": delta,
                    "Q_prime": [r, s],
                    "magnus_R": {"blocks": b_r, "height": h_r},
                    "magnus_S": {"blocks": b_s, "height": h_s},
                    "H2": h2,
                    "H3": h3,
                    "H2_exact_U124": b_s == [(1, 2), (0, m)] and h_s == -1,
                    "H3_exact_U124": b_r == [(0, -1), (1, 1), (-1, delta)] and h_r == 0,
                    "faithful_R": faithful_r,
                    "faithful_S": faithful_s,
                    "isolator_one_y_after_gate1": isolator_y,
                    "Ahat": a_hat,
                    "Bhat": b_hat,
                    "Ahat_matches_S_row1": a_hat == claimed_a,
                    "Bhat_matches_S_row2": b_hat == claimed_b,
                    "Ahat_c_free": c_free,
                    "C16_1_rotation_legal": legal,
                    "C16_1_loop": loop,
                    "illegal_rho_on_minus": illegal_shorten,
                    "S_x_exponent_row1": exp_sums(a_hat)[0],
                }
            )
    plus_loops = [r for r in records if r["delta"] == 1]
    minus_rows = [r for r in records if r["delta"] == -1]
    return {
        "n_checked": len(records),
        "all_H2_H3": all(r["H2"] and r["H3"] for r in records),
        "all_faithful": all(r["faithful_R"] and r["faithful_S"] for r in records),
        "all_c_free": all(r["Ahat_c_free"] for r in records),
        "all_plus_loops": all(r["C16_1_loop"] for r in plus_loops),
        "all_minus_rotation_absent": all(r["C16_1_rotation_legal"] is False for r in minus_rows),
        "minus_row1_x_exponent": sorted({r["S_x_exponent_row1"] for r in minus_rows}),
        "plus_row1_x_exponent": sorted({r["S_x_exponent_row1"] for r in plus_rows(records)}),
        "records": records,
    }


def plus_rows(records: list[dict]) -> list[dict]:
    return [r for r in records if r["delta"] == 1]


def check_c16_parameter_sweep() -> dict:
    a_tmpls = ["Xu", "uu", "x", "", "Xuu", "uX"]
    b_tmpls = ["", "x", "uX"]
    ps = [1, 2, 3, -2]
    bs = [-1, 1, 2]
    cs = [-5, -2, 0, 3, 7]
    n_ok = 0
    n_fail = 0
    failures = []
    for a_tmpl in a_tmpls:
        for b_tmpl in b_tmpls:
            for p in ps:
                for b in bs:
                    for c in cs:
                        r, s = construct_rs(a_tmpl, b_tmpl, p, b, c)
                        i_r = subst(a_tmpl, {"u": "u"}) + "y" + pw("x", b) + "Y" + subst(b_tmpl, {"u": "u"})
                        i_r = free_reduce(i_r)
                        i_s = free_reduce(pw("u", p) + pw("x", c) + "Y")
                        d_row = free_reduce("U" + XI)
                        faithful = subst(i_r, {"u": XI}) == r and subst(i_s, {"u": XI}) == s
                        isolator = sum(ch in "yY" for ch in i_s) == 1
                        e = free_reduce(pw("u", p) + pw("x", c))
                        a_hat = subst(i_r, {"y": e})
                        claimed_a = free_reduce(
                            subst(a_tmpl, {"u": "u"}) + pw("u", p) + pw("x", b) + pw("u", -p) + subst(b_tmpl, {"u": "u"})
                        )
                        c_free = subst(i_r, {"y": free_reduce(pw("u", p) + pw("x", c + 11))}) == a_hat
                        b_hat = subst(d_row, {"y": e})
                        claimed_b = free_reduce("U" + pw("x", -c) + pw("u", -p) + "x" + pw("u", p) + pw("x", c))
                        ok = (
                            faithful
                            and isolator
                            and a_hat == claimed_a
                            and b_hat == claimed_b
                            and c_free
                        )
                        if ok:
                            n_ok += 1
                        else:
                            n_fail += 1
                            if len(failures) < 8:
                                failures.append(
                                    {
                                        "A": a_tmpl,
                                        "B": b_tmpl,
                                        "p": p,
                                        "b": b,
                                        "c": c,
                                        "faithful": faithful,
                                        "isolator": isolator,
                                        "c_free": c_free,
                                        "Ahat_ok": a_hat == claimed_a,
                                        "Bhat_ok": b_hat == claimed_b,
                                    }
                                )
    return {
        "n_checked": n_ok + n_fail,
        "n_ok": n_ok,
        "n_fail": n_fail,
        "failures": failures,
    }


def E(c: int, e: int) -> str:
    return free_reduce("U" + pw("x", -c) + pw("u", -e) + "x" + pw("u", e) + pw("x", c))


def D_bs(m: int, n: int) -> str:
    return free_reduce("X" + pw("u", m) + "x" + pw("u", -n))


def shear_down_word(c: int, e: int, m: int, n: int) -> tuple[str, tuple[int, int]]:
    if e % m != 0:
        raise ValueError("M does not divide e")
    f = n * e // m
    # Replace each displayed u^{±e} by the BS rewriting u^e = x u^{Ne/M} x^{-1}.
    inner_neg = free_reduce("x" + pw("u", -f) + "X")
    inner_pos = free_reduce("x" + pw("u", f) + "X")
    word = free_reduce("U" + pw("x", -c) + inner_neg + "x" + inner_pos + pw("x", c))
    return word, (c - 1, f)


def shear_up_word(c: int, e: int, m: int, n: int) -> tuple[str, tuple[int, int]]:
    if e % n != 0:
        raise ValueError("N does not divide e")
    f = m * e // n
    inner_neg = free_reduce("X" + pw("u", -f) + "x")
    inner_pos = free_reduce("X" + pw("u", f) + "x")
    word = free_reduce("U" + pw("x", -c) + inner_neg + "x" + inner_pos + pw("x", c))
    return word, (c + 1, f)


def shear_orbit(c0: int, e0: int, m: int, n: int, cap: int = 4000) -> list[tuple[int, int]]:
    seen: set[tuple[int, int]] = set()
    stack = [(c0, e0)]
    while stack and len(seen) < cap:
        state = stack.pop()
        if state in seen:
            continue
        seen.add(state)
        c, e = state
        if e % m == 0:
            stack.append((c - 1, n * e // m))
        if e % n == 0:
            stack.append((c + 1, m * e // n))
    return sorted(seen)


def check_c17() -> dict:
    identities = []
    n_id_ok = 0
    for m, n in ((2, 1), (3, 2), (4, 3), (5, 4)):
        for c in (-3, 0, 2, 5):
            for e in (n, 2 * n, m * n, m * m * n):
                down = up = None
                if e % m == 0:
                    word, st = shear_down_word(c, e, m, n)
                    down = word == E(*st)
                    if down:
                        n_id_ok += 1
                if e % n == 0:
                    word, st = shear_up_word(c, e, m, n)
                    up = word == E(*st)
                    if up:
                        n_id_ok += 1
                identities.append({"M": m, "N": n, "c": c, "e": e, "down_ok": down, "up_ok": up})
    instances = []
    for delta in (-1, 1):
        for n in range(2, 9):
            s1, s2 = s_pair(n, delta)
            is_bs = s1 == D_bs(3, 2)
            is_e = s2 == E(n * delta, 2)
            instances.append(
                {
                    "n": n,
                    "delta": delta,
                    "S_row1": s1,
                    "S_row2": s2,
                    "row1_is_BS32": is_bs,
                    "row2_is_E": is_e,
                    "row1_x_exp": exp_sums(s1)[0],
                    "H3_3_pow_n_divides_2": (3 ** abs(n * delta)) % 2 == 0 or 2 % (3 ** abs(n * delta)) == 0,
                }
            )
    # 3^{|n|} | 2 is false for |n|>=1; record the exact predicate used by C17.
    for rec in instances:
        rec["H3"] = (2 % (3 ** abs(rec["n"]))) == 0 if rec["delta"] == 1 else False
    orbits = {
        "u124_c7_e2": shear_orbit(7, 2, 3, 2),
        "no_div_c1_e4": shear_orbit(1, 4, 3, 2),
        "positive_c2_e9": shear_orbit(2, 9, 3, 2),
        "smallest_c1_e3": shear_orbit(1, 3, 3, 2),
    }
    w, st = shear_down_word(2, 9, 3, 2)
    pos1 = w == E(*st) == E(1, 6)
    w, st = shear_down_word(*st, 3, 2)
    pos0 = w == E(*st) == E(0, 4)
    terminal = E(0, 4)
    return {
        "identity_rows": len(identities),
        "identity_ok_count": n_id_ok,
        "all_defined_shears_literal": all(
            (row["down_ok"] in (True, None)) and (row["up_ok"] in (True, None)) and (row["down_ok"] or row["up_ok"])
            for row in identities
        ),
        "positive_control_2_9_to_0_4": pos1 and pos0,
        "terminal_one_x": sum(ch in "xX" for ch in terminal) == 1,
        "terminal": terminal,
        "orbits": {k: [list(p) for p in v] for k, v in orbits.items()},
        "orbit_u124_flank_never_drops": orbits["u124_c7_e2"] == [(7, 2), (8, 3)],
        "S_plus_is_BS32_and_E": all(r["row1_is_BS32"] and r["row2_is_E"] for r in instances if r["delta"] == 1),
        "S_minus_not_BS": all((not r["row1_is_BS32"]) and r["row1_x_exp"] == -2 for r in instances if r["delta"] == -1),
        "S_plus_H3_fails": all(r["H3"] is False for r in instances if r["delta"] == 1),
        "instances": instances,
        "identities": identities,
    }


def x_runs(word: str, generator: str) -> int:
    return len(re.findall(f"[{generator}{generator.upper()}]+", word))


def is_h1_two_block(word: str, generator: str) -> bool:
    if x_runs(word, generator) != 1:
        return False
    return re.search(f"[{generator}{generator.upper()}]+$", word) is not None


def check_c18() -> dict:
    c0 = "Yuu"
    euclid_ok = True
    euclid_rows = []
    for m in (2, 3, 5, 7):
        for k in (m + 1, 2 * m + 1, 3 * m + 1):
            q = (k - 1) // m
            word = free_reduce("T" + pw("x", k))
            for i in range(q):
                word = cyc_reduce(free_reduce(word + pw("x", -m) + inv(c0)))
                want = cyc_reduce(free_reduce(pw_word(inv(c0), i + 1) + "T" + pw("x", k - (i + 1) * m)))
                match = same_cyclic(word, want)
                euclid_ok = euclid_ok and match
                word = want
            isolator = sum(ch in "xX" for ch in word) == 1
            back = subst(free_reduce(pw_word(inv(c0), q) + "Tx"), {"x": free_reduce("t" + pw_word(c0, q))})
            euclid_rows.append(
                {
                    "m": m,
                    "k": k,
                    "gcd": gcd(k, m),
                    "isolator": isolator,
                    "back_sub_empty": back == "",
                }
            )
            euclid_ok = euclid_ok and isolator and back == ""

    gcd_neg = []
    for k, m in ((6, 4), (4, 2), (9, 6)):
        gcd_neg.append({"k": k, "m": m, "gcd": gcd(k, m), "x_not_recoverable": gcd(k, m) > 1})

    let = "xabcdefghijklmnopqrstuvw"
    radix = []
    radix_ok = True
    for m in (1, 2, 3, 4, 5, 7, 8, 12, 15, 16, 31, 64, 100, 255, 1000, 4096):
        bits, r = [], m
        while r:
            bits.append(r & 1)
            r >>= 1
        j = len(bits) - 1
        word = "".join(let[i] for i, bit in enumerate(bits) if bit)
        defs = [let[i + 1].upper() + let[i] * 2 for i in range(j)]
        images = {let[i]: pw("x", 2 ** i) for i in range(j + 1)}
        word_ok = subst(word, images) == pw("x", m) and all(subst(defn, images) == "" for defn in defs)
        moves, cur = 0, m
        while cur >= 2:
            moves += cur // 2
            cur //= 2
        radix.append(
            {
                "m": m,
                "compressed": word,
                "n_extra_rows": j,
                "moves_theta_m": moves,
                "ok": word_ok,
            }
        )
        radix_ok = radix_ok and word_ok

    tested = hits = 0
    families = {
        "Q": lambda n, d: claimed_q(n, d),
        "Qp": q_prime,
        "S": lambda n, d: s_pair(n, d, tag="u"),
    }
    gens = {"Q": "xy", "Qp": "xy", "S": "xu"}
    for name, fn in families.items():
        for delta in (-1, 1):
            for n in range(2, 9):
                for row in fn(n, delta):
                    w = cyc_reduce(row)
                    for cand in rotations_and_inverses(w):
                        tested += 1
                        for g in gens[name]:
                            if is_h1_two_block(cand, g):
                                hits += 1
    # The inventor counted every rotation of the cyclically reduced word and
    # of its inverse separately, including duplicate cyclic reductions.
    tested_raw = hits_raw = 0
    for name, fn in families.items():
        for delta in (-1, 1):
            for n in range(2, 9):
                for row in fn(n, delta):
                    w = cyc_reduce(row)
                    cands = [w[i:] + w[:i] for i in range(len(w))]
                    cands += [inv(w)[i:] + inv(w)[:i] for i in range(len(w))]
                    for cand in cands:
                        tested_raw += 1
                        for g in gens[name]:
                            if is_h1_two_block(cand, g):
                                hits_raw += 1
    return {
        "euclid_ok": euclid_ok,
        "euclid_rows": euclid_rows,
        "gcd_negatives": gcd_neg,
        "radix_ok": radix_ok,
        "radix": radix,
        "radix_m1000_moves": next(r["moves_theta_m"] for r in radix if r["m"] == 1000),
        "h1_unique_orientations": {"tested": tested, "hits": hits},
        "h1_raw_rotations_matching_inventor": {"tested": tested_raw, "hits": hits_raw},
    }


def load_pairs(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def c16_shape_on_pair(r1: str, r2: str) -> dict:
    h2_hits = []
    h3_hits = []
    for label, word in (("r1", r1), ("r2", r2)):
        for spelling in rotations_and_inverses(word):
            blocks, height = magnus(spelling)
            rec = {"row": label, "spelling": spelling, "blocks": blocks, "height": height}
            if h2_isolator(blocks, height):
                h2_hits.append(rec)
            if h3_companion(blocks, height):
                h3_hits.append(rec)
    fires = bool(h2_hits) and bool(h3_hits)
    return {
        "fires": fires,
        "n_h2": len(h2_hits),
        "n_h3": len(h3_hits),
        "h2_sample": h2_hits[:2],
        "h3_sample": h3_hits[:2],
    }


def u_word_from_magnus_blocks(blocks: list[tuple[int, int]]) -> str:
    """Translate Magnus blocks in {ξ_0=x, ξ_1=u} into a rank-3 spelling."""
    parts = []
    for index, exponent in blocks:
        if index == 0:
            parts.append(pw("x", exponent))
        elif index == 1:
            parts.append(pw("u", exponent))
        else:
            raise ValueError(f"block index {index} is not a word in x,ξ")
    return free_reduce("".join(parts))


def verify_c16_spellings(companion: str, isolator: str) -> dict:
    """Replay Gate 1/2 substitutions on a candidate (H3, H2) spelling pair."""
    b_r, h_r = magnus(companion)
    b_s, h_s = magnus(isolator)
    idx = next(i for i, (index, _) in enumerate(b_r) if index == -1)
    a_blocks = b_r[:idx]
    _, b = b_r[idx]
    b_blocks = b_r[idx + 1 :]
    p, c = b_s[0][1], b_s[1][1]
    a_u = u_word_from_magnus_blocks(a_blocks)
    b_u = u_word_from_magnus_blocks(b_blocks)
    i_r = free_reduce(a_u + "y" + pw("x", b) + "Y" + b_u)
    i_s = free_reduce(pw("u", p) + pw("x", c) + "Y")
    e = free_reduce(pw("u", p) + pw("x", c))
    a_hat = subst(i_r, {"y": e})
    b_hat = subst(free_reduce("U" + XI), {"y": e})
    claimed_a = free_reduce(a_u + pw("u", p) + pw("x", b) + pw("u", -p) + b_u)
    claimed_b = free_reduce("U" + pw("x", -c) + pw("u", -p) + "x" + pw("u", p) + pw("x", c))
    rho = free_reduce("X" + pw("u", -3) + "xuu")
    out = {
        "rebuild_ok": rebuild_magnus(b_r, h_r) == companion and rebuild_magnus(b_s, h_s) == isolator,
        "H2": h2_isolator(b_s, h_s),
        "H3": h3_companion(b_r, h_r),
        "p": p,
        "b": b,
        "c": c,
        "A_u": a_u,
        "B_u": b_u,
        "faithful": subst(i_r, {"u": XI}) == companion and subst(i_s, {"u": XI}) == isolator,
        "isolator_one_y": sum(ch in "yY" for ch in i_s) == 1,
        "Ahat": a_hat,
        "Bhat": b_hat,
        "Ahat_ok": a_hat == claimed_a,
        "Bhat_ok": b_hat == claimed_b,
        "c_free": subst(i_r, {"y": free_reduce(pw("u", p) + pw("x", c + 11))}) == a_hat,
        "Ahat_x_exp": exp_sums(a_hat)[0],
        "in_cyc_total": len(cyc_reduce(companion)) + len(cyc_reduce(isolator)),
        "out_cyc_total": len(cyc_reduce(a_hat)) + len(cyc_reduce(b_hat)),
        "C16_1_rho_legal": same_cyclic(rho, inv(a_hat)),
    }
    ok = all(
        [
            out["rebuild_ok"],
            out["H2"],
            out["H3"],
            out["faithful"],
            out["isolator_one_y"],
            out["Ahat_ok"],
            out["Bhat_ok"],
            out["c_free"],
        ]
    )
    out["instance_ok"] = ok
    return out


def check_u124_c16_recognizer() -> dict:
    tables = {}
    for fname in ("aca_124_best.csv", "aca_124_initial.csv"):
        hits = []
        n_h2 = n_h3 = 0
        for row in load_pairs(DATA / fname):
            info = c16_shape_on_pair(row["r1"], row["r2"])
            if info["n_h2"]:
                n_h2 += 1
            if info["n_h3"]:
                n_h3 += 1
            if info["fires"]:
                h2 = info["h2_sample"][0]
                h3 = info["h3_sample"][0]
                verified = verify_c16_spellings(h3["spelling"], h2["spelling"])
                hits.append({"name": row["name"], **info, "verified": verified})
        tables[fname] = {
            "n_pairs": 124,
            "pairs_with_H2_orientation": n_h2,
            "pairs_with_H3_orientation": n_h3,
            "pairs_firing_C16": len(hits),
            "all_hits_instance_ok": all(h["verified"]["instance_ok"] for h in hits),
            "hits": hits,
        }
    controls = []
    for delta in (-1, 1):
        for n in range(2, 8):
            qp = q_prime(n, delta)
            s = s_pair(n, delta, tag="y")
            p = p_pair(n, delta)
            controls.append(
                {
                    "n": n,
                    "delta": delta,
                    "Q_prime_fires": c16_shape_on_pair(*qp)["fires"],
                    "S_fires": c16_shape_on_pair(*s)["fires"],
                    "P_fires": c16_shape_on_pair(*p)["fires"],
                    "aut_min_Q_prime_fires": None,
                }
            )
    # Aut-minimal spelling of Q' is what the best table stores for the MS family.
    aut_min_hits = 0
    for delta in (-1, 1):
        for n in (2, 3):
            t, rep, phi = aut_canon(q_prime(n, delta))
            fires = c16_shape_on_pair(*rep)["fires"]
            if fires:
                aut_min_hits += 1
            for rec in controls:
                if rec["n"] == n and rec["delta"] == delta:
                    rec["aut_min_Q_prime_fires"] = fires
                    rec["aut_min_len"] = t
                    rec["aut_min_rep"] = list(rep)
                    rec["aut_min_check"] = check(q_prime(n, delta), rep, phi)
    return {"tables": tables, "controls": controls, "aut_min_Q_prime_fires_n2_n3": aut_min_hits}


def check_mu_and_orbits() -> dict:
    rows = []
    distinct = []
    claimed_aut_s_hits = 0
    for delta in (-1, 1):
        for n in range(2, 7):
            s = s_pair(n, delta, tag="y")
            families = {
                "P": (p_pair(n, delta), 2 * n + 10),
                "Qp": (q_prime(n, delta), n + 12),
                "S": (s, 2 * n + 13),
            }
            keys = []
            for label, (pr, want) in families.items():
                total, rep, phi = aut_canon(pr)
                ok = total == want and check(pr, rep, phi)
                rows.append(
                    {
                        "label": label,
                        "n": n,
                        "delta": delta,
                        "mu": total,
                        "want": want,
                        "ok": ok,
                        "rep": list(rep),
                    }
                )
                keys.append(rep[0] + "|" + rep[1])
            distinct.append(len(set(keys)) == 3)
            claimed_s = (
                free_reduce("YXXX" + pw("y", delta) + "xx"),
                free_reduce(pw("y", -n) + "XXYxx" + pw("y", n) + pw("x", delta)),
            )
            _, s_rep, s_phi = aut_canon(s)
            if check(s, s_rep, s_phi) and canon_pair(*claimed_s) == s_rep:
                claimed_aut_s_hits += 1
    return {
        "n_rows": len(rows),
        "all_mu_ok": all(r["ok"] for r in rows),
        "all_three_orbits_distinct": all(distinct),
        "claimed_aut_S_matches": claimed_aut_s_hits,
        "claimed_aut_S_n_checked": 10,
        "rows": rows,
    }


def main() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    report = {
        "q_to_q_prime": check_q_to_q_prime(),
        "c16_u124": check_c16_u124_instance(),
        "c16_parameter_sweep": check_c16_parameter_sweep(),
        "c17": check_c17(),
        "c18": check_c18(),
        "u124_c16_recognizer": check_u124_c16_recognizer(),
        "mu_orbits": check_mu_and_orbits(),
        "solved_u124": 0,
        "notes": [
            "C16/C18 use C0 twice; identities here are not elementary certificates.",
            "C16.1 generator shift (x,y)->(u,x) is a relabel (Nielsen); stable transport is C1.",
            "C17 shear is Lemma-11-free; the C4 tail is not certified.",
            "C18 radix compresses state length, not move count.",
            "No U124 row is solved.",
        ],
    }
    q = report["q_to_q_prime"]
    c16 = report["c16_u124"]
    sweep = report["c16_parameter_sweep"]
    c17 = report["c17"]
    c18 = report["c18"]
    rec = report["u124_c16_recognizer"]
    mu = report["mu_orbits"]
    report["summary"] = {
        "Q_to_Q_prime_free": q["all_freely_equal"],
        "C16_U124_identities": c16["all_H2_H3"] and c16["all_faithful"] and c16["all_c_free"],
        "C16_1_plus_loop": c16["all_plus_loops"],
        "C16_1_minus_no_rotation": c16["all_minus_rotation_absent"],
        "C16_parameter_sweep_fail": sweep["n_fail"],
        "C17_shears_literal": c17["all_defined_shears_literal"] and c17["positive_control_2_9_to_0_4"],
        "C17_U124_H3_fails": c17["S_plus_H3_fails"],
        "C17_minus_not_BS": c17["S_minus_not_BS"],
        "C18_euclid": c18["euclid_ok"],
        "C18_radix": c18["radix_ok"],
        "C18_H1_raw": c18["h1_raw_rotations_matching_inventor"],
        "U124_best_C16_fires": rec["tables"]["aca_124_best.csv"]["pairs_firing_C16"],
        "U124_best_C16_verified": rec["tables"]["aca_124_best.csv"]["all_hits_instance_ok"],
        "U124_initial_C16_fires": rec["tables"]["aca_124_initial.csv"]["pairs_firing_C16"],
        "U124_initial_C16_verified": rec["tables"]["aca_124_initial.csv"]["all_hits_instance_ok"],
        "U124_best_C16_ids": [h["name"] for h in rec["tables"]["aca_124_best.csv"]["hits"]],
        "U124_best_C16_1_rho": [
            {"name": h["name"], "rho_legal": h["verified"]["C16_1_rho_legal"]}
            for h in rec["tables"]["aca_124_best.csv"]["hits"]
        ],
        "mu_ok": mu["all_mu_ok"],
        "three_orbits": mu["all_three_orbits_distinct"],
        "aut_S_form": mu["claimed_aut_S_matches"],
    }
    path = OUT / "theory_wave1_replay.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("theory_wave1 independent replay")
    print(json.dumps(report["summary"], indent=2))
    print(f"wrote {path}")
    return report


if __name__ == "__main__":
    main()
