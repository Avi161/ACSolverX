"""Tests for the equivalence-class machinery.

Layered so a bug in one layer cannot hide a bug in another:

  * the move sets, against the baseline solver's own ``expand_node_nj``;
  * the Aut(F2) canonical form, against the *independent* ``experiments/analysis/whitehead.py``
    (same theory, separately written, and it computes no witness -- so agreement is real
    evidence, not a tautology);
  * the certificates, against pure string substitution and a Nielsen-reduction basis test that
    shares nothing with the Whitehead code that produced them;
  * the search, against facts established independently of it (the 2 merges the 1M-node sweep
    found, and the known 261 -> 168 Aut partition).

Run:  .venv/bin/python3 -m pytest experiments/equivalence_classes -q
"""
import csv
import json
import os
import random
import sys

import pytest

# The repo root, found by walking up rather than by counting directory levels. A
# dirname chain encodes this file's depth, so it silently repoints at the wrong
# directory the moment the file moves -- and every path below is then wrong.
def _repo_root():
    d = os.path.dirname(os.path.abspath(__file__))
    while d != os.path.dirname(d):
        if (os.path.isdir(os.path.join(d, "experiments"))
                and os.path.isdir(os.path.join(d, "data"))):
            return d
        d = os.path.dirname(d)
    raise RuntimeError("repo root (holding experiments/ and data/) not found")


ROOT = _repo_root()
sys.path.insert(0, ROOT)

from experiments.analysis import whitehead as wh  # noqa: E402
from experiments.equivalence_classes.lib.acmoves import canon, children  # noqa: E402
from experiments.equivalence_classes.search.aut_search import aut_key, aut_multi_search  # noqa: E402
from experiments.equivalence_classes.lib.autcanon import (  # noqa: E402
    aut_canon, check, compose, peak_reduce,
)
from experiments.equivalence_classes.verify.verify_certificates import is_basis  # noqa: E402
from experiments.equivalence_classes.lib.words import (  # noqa: E402
    SIGNED_PERMS, apply_pair, canon_pair, inv, ms_presentation, relabel_key, replay_move, rev,
)
from experiments.search.greedy_baseline import (  # noqa: E402
    canonical_pair_nj, expand_node_nj, reduce_relator_nj, str_to_arr,
)

CAP = 48
_CHR = {1: "X", 2: "Y", 3: "x", 4: "y"}


@pytest.fixture(scope="session")
def reps():
    p = os.path.join(ROOT, "data", "ms_unsolved_reps", "ms_reps_unsolved.csv")
    return {r["name"]: (r["r1"], r["r2"]) for r in csv.DictReader(open(p))}


@pytest.fixture(scope="session")
def sample(reps):
    return random.Random(0).sample(sorted(reps), 20)


def _baseline_children(r1s, r2s):
    a1 = reduce_relator_nj(str_to_arr(r1s), True)
    a2 = reduce_relator_nj(str_to_arr(r2s), True)
    c1, c2 = canonical_pair_nj(a1, a2)
    codes, lens, _, n = expand_node_nj(c1, c2, CAP, True)
    return {("".join(_CHR[c] for c in codes[i, :lens[i, 0]]),
             "".join(_CHR[c] for c in codes[i, lens[i, 0]:lens[i, 0] + lens[i, 1]]))
            for i in range(n)}


# --------------------------------------------------------------------- move sets
def test_seam_move_set_is_the_baseline(reps, sample):
    for n in sample:
        r1, r2 = reps[n]
        assert set(children(r1, r2, cap=CAP, seam_only=True)) == _baseline_children(r1, r2)


def test_full_move_set_strictly_contains_seam(reps, sample):
    for n in sample:
        r1, r2 = reps[n]
        assert set(children(r1, r2, cap=CAP, seam_only=True)) < \
            set(children(r1, r2, cap=CAP, seam_only=False))


def test_trivial_is_a_sink_under_seam_but_not_under_full():
    """The reason the enlarged move set exists at all."""
    assert children("x", "y", cap=CAP, seam_only=True) == {}
    assert children("x", "y", cap=CAP, seam_only=False) != {}


def test_moves_are_inverse_closed(reps, sample):
    """P must be recoverable from each of its children in one move -- otherwise a merge found
    by two balls meeting would not imply the roots are AC-equivalent."""
    for n in sample[:6]:
        P = canon(*reps[n])
        for c in list(children(*P, cap=CAP, seam_only=False))[:10]:
            assert P in children(*c, cap=CAP, seam_only=False)


def test_replay_move_matches_the_numba_expander(reps, sample):
    """The pure-Python replay the verifier trusts must agree with the search's numba moves."""
    for n in sample[:8]:
        P = canon(*reps[n])
        for child, mv in list(children(*P, cap=CAP, seam_only=False).items())[:12]:
            assert replay_move(P, mv) == child


# ------------------------------------------------------------------ Aut(F2) keys
def test_aut_canon_agrees_with_independent_whitehead(reps, sample):
    """Same partition as experiments/analysis/whitehead.py -- a separately written implementation."""
    for n in sample:
        p = canon(*reps[n])
        mine = aut_canon(p)
        theirs = wh.canonical_form(p)[0]
        assert mine[0] == theirs[0]          # same Aut-minimal total length


def test_aut_partition_of_the_261_is_exactly_168(reps):
    classes = {aut_canon(canon(*p))[1] for p in reps.values()}
    assert len(classes) == 168


def test_every_phi_is_an_automorphism_and_its_certificate_holds(reps, sample):
    for n in sample:
        p = canon(*reps[n])
        _, rep, phi = aut_canon(p)
        assert is_basis(phi["x"], phi["y"]), f"{n}: phi is not an automorphism"
        assert check(p, rep, phi), f"{n}: canon(phi(P)) != rep"


def test_peak_reduction_alone_is_not_a_valid_key(reps):
    """Guards the reason phase 2 cannot be dropped for speed: peak reduction is not confluent,
    so the peak-reduced form splits the 168 true classes into many more."""
    peak = {canon_pair(*peak_reduce(canon(*p))[1]) for p in reps.values()}
    assert len(peak) > 168


def test_compose_is_the_right_way_round():
    f = {"x": "xy", "y": "y"}
    g = {"x": "x", "y": "yx"}
    from experiments.equivalence_classes.lib.words import apply_hom
    h = compose(f, g)
    for w in ("x", "y", "xyX", "YxyX"):
        assert apply_hom(w, h) == apply_hom(apply_hom(w, g), f)


# ------------------------------------------------------- symmetries that are NOT new
def test_word_reversal_is_subsumed_by_the_signed_permutations(reps):
    """reverse(w) = sigma(w^-1) with sigma: x->X, y->Y, and relator inversion is already
    quotiented out -- so reversal is not an extra symmetry and merges nothing new."""
    sigma = {"x": "X", "y": "Y"}
    for r1, r2 in reps.values():
        assert canon_pair(rev(r1), rev(r2)) == apply_pair((r1, r2), sigma)
        assert relabel_key((rev(r1), rev(r2))) == relabel_key((r1, r2))


def test_there_are_exactly_eight_signed_permutations():
    assert len(SIGNED_PERMS) == 8


def test_inv_is_an_involution(reps):
    for r1, _ in list(reps.values())[:20]:
        assert inv(inv(r1)) == r1


# ---------------------------------------------------------- the Miller-Schupp family
def test_ms_convention_reproduces_the_1190_file():
    """MS(n, w) = <x, y | x^-1 y^n x y^-(n+1), x^-1 w>. Pins the parametrisation the whole
    provenance argument rests on."""
    import ast

    from experiments.equivalence_classes.lib.words import ints_to_word
    ms = set()
    with open(os.path.join(ROOT, "data", "1190MS.txt")) as f:
        for line in f:
            ints = ast.literal_eval(line.strip())
            h = len(ints) // 2
            ms.add(canon_pair(ints_to_word(ints[:h]), ints_to_word(ints[h:])))
    rows = list(csv.reader(
        open(os.path.join(ROOT, "data", "ms_unsolved_reps", "ms_solved_grid.csv"))))
    ws = [r[0] for r in rows[1:] if r[0]]
    rebuilt = {canon_pair(*ms_presentation(n, w)) for w in ws for n in range(1, 8)}
    assert rebuilt == ms and len(ms) == 1190


# ------------------------------------------------------------------------- the search
@pytest.mark.parametrize("a,b", [("19_52", "18_9"), ("19_46", "18_11")])
def test_search_rediscovers_the_two_known_merges(reps, a, b):
    """Both were found independently by the 1M-node greedy sweep. If the ACA search cannot
    reproduce them it is not measuring what it claims to."""
    dsu, merges, stats, _ = aut_multi_search(
        [(a, *reps[a]), (b, *reps[b])], nodes_per_source=2000, max_total=24,
        seam_only=True, stop_when_merged=True)
    assert dsu.find(0) == dsu.find(1)
    assert stats["popped"] < 100          # and it should be *cheap*, not a lucky deep dig


def test_search_seeds_reproduce_the_168_aut_classes(reps):
    """Seeding all 261 must collapse to 168 at seed time, with no search at all."""
    dsu, merges, stats, _ = aut_multi_search(
        [(n, *reps[n]) for n in reps], nodes_per_source=0, max_total=26, seam_only=True)
    assert len({dsu.find(i) for i in range(len(reps))}) == 168
    assert all(m["kind"] == "aut" for m in merges)


def test_verifier_rebuilds_the_partition_not_just_the_merges():
    """The count is a separate claim from the merges.

    Verifying every merge does NOT verify the class count: a union-find that over-merged would
    put a rep in a class it has no verified chain to, and every individual merge would still
    check out. The verifier must rebuild the partition from the verified merges alone and get
    the reported one back. This test pins that the shipped artifact does.
    """
    import subprocess
    art = os.path.join(ROOT, "results", "equivalence_classes", "sweep_seam_28_250.json")
    if not os.path.exists(art):
        pytest.skip("headline artifact not present")
    out = subprocess.run(
        [sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "verify", "verify_certificates.py"), art],
        capture_output=True, text=True, cwd=ROOT)
    assert out.returncode == 0, out.stdout + out.stderr
    assert "partition rebuilt from verified merges alone: 126 classes == the 126 reported" \
        in out.stdout, out.stdout


def test_a_merge_implies_equal_abelian_det(reps):
    """|det| of the exponent-sum matrix is an AC-invariant the search never computes, and a
    change of variables preserves it too. Any merge that violates it is simply wrong."""
    from experiments.equivalence_classes.lib.words import abelian_det
    names = sorted(reps)[:40]
    dsu, _, _, _ = aut_multi_search([(n, *reps[n]) for n in names], nodes_per_source=20,
                                    max_total=26, seam_only=True)
    comp = {}
    for i, n in enumerate(names):
        comp.setdefault(dsu.find(i), []).append(abs(abelian_det(*reps[n])))
    for v in comp.values():
        assert len(set(v)) == 1


# ------------------------------------------------------------------ Aut(F2) inverses
def test_invert_is_a_two_sided_inverse_of_every_phi_in_the_certificates():
    """`make_proof_book` states a change-of-variables merge as ONE substitution
    psi = phi_B^-1 . phi_A, which needs phi_B^-1. Pins that the Nielsen-tracking inverse is right
    on every phi the search actually produced, both ways round."""
    from experiments.equivalence_classes.lib.autinv import invert
    from experiments.equivalence_classes.lib.words import apply_hom
    d = json.load(open(os.path.join(ROOT, "results", "equivalence_classes",
                                    "sweep_seam_28_250.json")))
    for name, r in d["roots"].items():
        phi = r["phi"]
        psi = invert(phi)
        for g in ("x", "y"):
            assert apply_hom(psi[g], phi) == g, name
            assert apply_hom(phi[g], psi) == g, name


@pytest.mark.parametrize("bad", ["xx", "xyX", "", "y"])
def test_invert_rejects_a_non_automorphism(bad):
    from experiments.equivalence_classes.lib.autinv import invert
    with pytest.raises(ValueError):
        invert({"x": bad, "y": "y"})


# ------------------------------------------------------------- the verification pipeline
CERT = os.path.join(ROOT, "results", "equivalence_classes", "certificates.json")
VERIFY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "verify", "verify_proofs.py")


def _verify(path):
    import subprocess
    return subprocess.run([sys.executable, VERIFY, path], capture_output=True, text=True, cwd=ROOT)


def test_verify_proofs_passes_on_the_shipped_certificates():
    if not os.path.exists(CERT):
        pytest.skip("certificates.json not present -- run make_proof_book.py")
    out = _verify(CERT)
    assert out.returncode == 0, out.stdout + out.stderr
    # RESULT CHANGE 2026-07-14: the overnight ladder's two verified edges (21_3 == 21_29,
    # 21_7 == 21_28) took the shipped book from 126 classes / 135 edges to 124 / 137.
    assert "The 261 presentations are 124 distinct problems." in out.stdout, out.stdout


def _first(cert, kind):
    for c in cert["classes"]:
        for e in c["edges"]:
            if e["kind"] == kind:
                return c, e
    raise AssertionError(f"no {kind} edge")


def _tamper_subst(cert):
    """A change-of-variables edge whose psi does not actually carry A onto B."""
    _, e = _first(cert, "cv")
    e["subst"] = {"x": "xy", "y": "y"}


def _tamper_move(cert):
    """An AC move with a different rotation -- it will not land on the recorded state."""
    _, e = _first(cert, "ac")
    st = (e["side_a"]["steps"] or e["side_b"]["steps"])[0]
    st["move"][2] += 1


def _tamper_pres_id(cert):
    """The right words under the wrong row number."""
    cert["classes"][0]["members"][0]["pres_id"] += 1


def _tamper_phi(cert):
    """A substitution that is not an automorphism of F2 (x -> xx is not invertible)."""
    _, e = _first(cert, "cv")
    e["side_a"]["phi0"] = {"x": "xx", "y": "y"}


def _tamper_overmerge(cert):
    """Two classes fused in the member lists, with no edge to justify it -- exactly the failure
    that verifying edges one by one cannot see, and the partition rebuild must."""
    a, b = cert["classes"][0], cert["classes"][-1]
    a["members"] += b["members"]
    a["size"] += b["size"]
    cert["classes"].pop()
    cert["summary"]["classes"] -= 1


def _tamper_pure_flag(cert):
    """Claim a path is pure AC when a change of variables sits inside it."""
    for c in cert["classes"]:
        for e in c["edges"]:
            if e["kind"] == "ac" and not e["pure_ac_path"]:
                e["pure_ac_path"] = True
                return
    raise AssertionError("no impure ac edge")


def _tamper_meet(cert):
    """The two sides do not actually meet where the certificate says."""
    _, e = _first(cert, "ac")
    e["meet"][0] = e["meet"][0] + "x"


# The three below tamper with the *printed derivation* rather than the states. They are the ones
# that matter for a human reader: the book says "rotate by 3" and a person does exactly that with a
# pencil. If the printed step is wrong but the endpoints still agree, the states all check out and
# only the reader is misled -- so the witness must be replayed literally, not merely implied.
def _tamper_witness_rotate(cert):
    _, e = _first(cert, "cv")
    e["subst_witness"][0]["rotate"] += 1


def _tamper_witness_invert(cert):
    _, e = _first(cert, "cv")
    w = e["subst_witness"][0]
    w["inverted"] = not w["inverted"]


def _tamper_move_piece(cert):
    """The book prints the two rotated pieces so the reader can concatenate them. Corrupt one."""
    _, e = _first(cert, "ac")
    st = (e["side_a"]["steps"] or e["side_b"]["steps"])[0]
    st["detail"]["piece_i"] = st["detail"]["piece_i"] + "x"


@pytest.mark.parametrize("mutate", [
    _tamper_subst, _tamper_move, _tamper_pres_id, _tamper_phi,
    _tamper_overmerge, _tamper_pure_flag, _tamper_meet,
    _tamper_witness_rotate, _tamper_witness_invert, _tamper_move_piece,
])
def test_verify_proofs_catches_a_tampered_certificate(mutate, tmp_path):
    """A checker that has never failed is not evidence of anything. Each mutation is a way a
    certificate could be wrong; every one must be rejected with a non-zero exit."""
    if not os.path.exists(CERT):
        pytest.skip("certificates.json not present -- run make_proof_book.py")
    cert = json.load(open(CERT))
    mutate(cert)
    p = tmp_path / "tampered.json"
    json.dump(cert, open(p, "w"))
    out = _verify(str(p))
    assert out.returncode != 0, f"{mutate.__name__} was NOT caught:\n{out.stdout}"
    assert "FAILED" in out.stdout, out.stdout
