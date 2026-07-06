"""Probe: (1) reproduce the paper's corrected 3-generator family via our Lemma-11
cascade and compare with the printed formula (Section 9.2.2, [a,b]=aba^-1b^-1);
(2) eliminate z via w to get the corrected P25 analog ("P25corr"); (3) verify the whole
chain's certificate; (4) compare P25corr against P25/AK3."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from hmoves import AK3, P25
from presentation import (
    abelianization_det, canonical_state_key, canonical_word, relabel_canonical_key,
    total_length, word_bytes,
)
from verify_certificate import verify
from wirtinger import Cascade, eliminate_final_via_w, paper_family


def word(*chunks):
    out = []
    for c in chunks:
        out.extend(c)
    return out


# printed corrected family, [a,b] = a b a^-1 b^-1 (MMS02's stated convention)
C_yx = [-2, -1, 2, 1]       # [y^-1, x^-1]
C_yX = [-2, 1, 2, -1]       # [y^-1, x]
C_xy = [-1, -2, 1, 2]       # [x^-1, y^-1]
R1_PRINTED = word(C_yx, [2], [-1], [-3], [1], [-2], [-1], C_yX, [3], [1],
                  C_yx, [2], [-1], [3], [1], [-2], [-1])
R2_PRINTED = word(C_yX, [-3], [1], C_yx, [2], [-1], [3], [1], [-2], C_xy,
                  [1], [2], [-1], [-3], [1], [-2], C_xy, [-1], [3], [1], [-2], [-1])


def cyc_eq(a, b):
    return word_bytes(canonical_word(list(a))) == word_bytes(canonical_word(list(b)))


def main():
    c = paper_family()                      # delete r6, eliminate 11 gens, rename
    state = c._state()
    print(f"cascade result: n_gen={c.n_gen}, relators sorted by len:")
    rels = sorted(state, key=len)
    for r in rels:
        print(f"  len={len(r)}: {r}")
    w_rel = rels[0]
    others = rels[1:]
    print(f"\nprinted r1 len={len(R1_PRINTED)}, r2 len={len(R2_PRINTED)}")
    for tag, printed in (("r1", R1_PRINTED), ("r2", R2_PRINTED)):
        hit = [i for i, r in enumerate(others) if cyc_eq(r, printed)]
        print(f"  printed {tag} matches cascade relator (up to rot/inv): {hit}")
    print(f"  w-relator: {w_rel}  (expect x^-1 y z ~ [-1,2,3])")
    print(f"  w matches [-1,2,3]: {cyc_eq(w_rel, [-1, 2, 3])}")

    ok = eliminate_final_via_w(c)
    print(f"\neliminate z via w: {ok}; now n_gen={c.n_gen}")
    p25corr = c._state()
    print(f"P25corr: total_len={total_length(p25corr)}")
    for r in p25corr:
        print(f"  len={len(r)}: {r}")
    print(f"|det| = {abs(abelianization_det(p25corr, 2))}")
    cert = c.certificate("wirtinger_P25corr", "End = P25corr (2 generators).")
    okv, errs = verify(cert)
    print(f"certificate verifies: {okv} {errs[:3] if errs else ''}")

    print(f"\nP25corr == P25 (relabel-canonical): "
          f"{relabel_canonical_key(p25corr, 2) == relabel_canonical_key(P25, 2)}")
    print(f"P25corr == AK3 (relabel-canonical): "
          f"{relabel_canonical_key(p25corr, 2) == relabel_canonical_key(AK3, 2)}")
    print(f"P25 (for reference): total_len={total_length(P25)}")


if __name__ == "__main__":
    main()
