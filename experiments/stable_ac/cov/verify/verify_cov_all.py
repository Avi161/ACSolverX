"""Verify a ``run_cov_all`` jsonl: provenance, dedup, counts and stored paths.

For every row:
  * provenance — re-derive the start from ``r1_orig``/``r2_orig`` and the row's
    recorded transform alone (z word, chosen occurrences, isolating relator,
    eliminated generator) and require it to equal ``r1``/``r2``; check the z
    word belongs to the ``suballpxyb8`` family and every chosen window really is
    w or w⁻¹; check ``|det|`` of the exponent-sum matrix is 1 before and after;
  * dedup — ``class_key`` recomputed from ``r1``/``r2`` equals the stored one,
    no two rows of a presentation share it, and none equals the control's;
  * counts — per presentation, the number of CoV rows and one-pattern rows
    equals a fresh ``enumerate_classes`` (``--counts``, slower);
  * certificates — every row carrying ``path_moves`` is replayed through
    ``experiments.stable_ac.verify_results.verify_solved_row`` (spec only, never
    a solver) and must end at the trivial presentation within the row's cap.

CLI (repo root, ``PYTHONPATH=.``):
    python3 -m experiments.stable_ac.cov.verify.verify_cov_all FILE.jsonl \
        [--counts] [--dataset data/ms640_solved.txt] [--path-sample P]
"""

import argparse
import json
import sys
from collections import defaultdict

from experiments.greedy_tests.spec.words import inverse, reduce_word, str_to_word
from experiments.greedy_tests.spec.words import word_to_str
from experiments.stable_ac.cov import cov, cov_all
from experiments.stable_ac.cov.run import run_cov_all
from experiments.stable_ac.verify_results import CertificateError, verify_solved_row


def _s(word):
    return word_to_str(tuple(word))


def _det(r1, r2):
    def sums(w):
        return (sum((g == 1) - (g == -1) for g in w),
                sum((g == 2) - (g == -2) for g in w))
    a, b = sums(r1)
    c, d = sums(r2)
    return abs(a * d - b * c)


def check_provenance(row):
    r1o, r2o = str_to_word(row["r1_orig"]), str_to_word(row["r2_orig"])
    if _det(r1o, r2o) != 1:
        raise CertificateError("original |det| != 1")
    if row["is_control"]:
        if (row["r1"], row["r2"]) != (row["r1_orig"], row["r2_orig"]):
            raise CertificateError("control row is not the original pair")
        return
    c1 = reduce_word(r1o, cyclic=True)
    c2 = reduce_word(r2o, cyclic=True)
    w = str_to_word(row["z_word"])
    if max(w, inverse(w)) not in set(cov_all.subwords(c1, c2)):
        raise CertificateError(f"z word {row['z_word']} not in the family")
    L = len(w)
    ch1, ch2 = (tuple(tuple(o) for o in p) for p in row["pattern"])
    if not ch1 and not ch2:
        raise CertificateError("empty pattern")
    for cyc, ch in ((c1, ch1), (c2, ch2)):
        used = set()
        for start, sign in ch:
            win = tuple((cyc + cyc)[start:start + L])
            if win != (w if sign == 1 else inverse(w)):
                raise CertificateError(f"window at {start} is not w^{sign}")
            span = {(start + j) % len(cyc) for j in range(L)}
            if used & span:
                raise CertificateError("overlapping occurrences")
            used |= span
    r1s = cov_all.substitute_pattern(c1, ch1, L)
    r2s = cov_all.substitute_pattern(c2, ch2, L)
    if [list(r1s), list(r2s)] != [row["r1_substituted"], row["r2_substituted"]]:
        raise CertificateError("substituted pair does not match the pattern")
    r_def = cov.defining_relator(w)
    if list(r_def) != row["defining_relator"]:
        raise CertificateError("defining relator mismatch")
    gen = cov.X_GEN if row["iso_gen"] == "x" else cov.Y_GEN
    r_iso, keep = (r1s, r2s) if row["iso_index"] == 0 else (r2s, r1s)
    ok, expr = cov.isolate(r_iso, x=gen)
    if not ok or list(expr) != row["iso_expr"]:
        raise CertificateError("isolation does not reproduce iso_expr")
    o1 = cov.relabel(cov.substitute_generator(keep, gen, expr), row["iso_gen"])
    o2 = cov.relabel(cov.substitute_generator(r_def, gen, expr), row["iso_gen"])
    if (str_to_word(row["r1"]), str_to_word(row["r2"])) != (o1, o2):
        raise CertificateError("re-derived start differs from r1/r2")
    if _det(o1, o2) != 1:
        raise CertificateError("start |det| != 1")


def check_outcome(row, ident, path_frac):
    for k, v in ident.items():
        if row.get(k) != v:
            raise CertificateError(f"{k}={row.get(k)!r}, file has {v!r}")
    want = cov.DEFAULT_CAP if row["is_control"] else max(
        cov.DEFAULT_CAP, max(len(row["r1"]), len(row["r2"])) + cov.CAP_HEADROOM)
    if row["max_relator_length_cap"] != want:
        raise CertificateError(f"cap {row['max_relator_length_cap']} != {want}")
    if not 0 < row["nodes_explored"] <= row["node_budget"]:
        raise CertificateError("nodes_explored outside (0, node_budget]")
    if (row["path_length"] is None) == bool(row["solved"]):
        raise CertificateError("path_length must be set exactly when solved")
    if not row["is_control"] and row["n_subs"] != sum(len(p) for p in row["pattern"]):
        raise CertificateError("n_subs != number of chosen occurrences")
    if row["solved"] and path_frac is not None and run_cov_all._sampled(
            row["pres_id"], tuple(row["class_key"]), path_frac) \
            and row.get("path_moves") is None:
        raise CertificateError("sampled solved row carries no path_moves")
    if not row["solved"] and row.get("path_moves") is not None:
        raise CertificateError("unsolved row carries a path")


def verify(path, counts=False, dataset=None, path_frac=None):
    rows = [json.loads(ln) for ln in open(path) if ln.strip()]
    fails, n_paths = [], 0
    by_pres = defaultdict(list)
    ident = {k: rows[0][k] for k in ("node_budget", "family_tag", "source")} if rows else {}
    for row in rows:
        by_pres[row["pres_id"]].append(row)
        try:
            check_outcome(row, ident, path_frac)
            check_provenance(row)
            key = cov_all.class_key(str_to_word(row["r1"]), str_to_word(row["r2"]))
            if list(key) != row["class_key"]:
                raise CertificateError("class_key does not match r1/r2")
            if row.get("path_moves") is not None:
                verify_solved_row(row, row["path_moves"])
                n_paths += 1
        except Exception as e:  # any defect in one row is a failure, not a crash
            fails.append((row.get("pres_id"), row.get("z_word"),
                          f"{type(e).__name__}: {e}"))
    if dataset:
        orig = {p: (_s(r1), _s(r2)) for p, r1, r2 in run_cov_all.load_ms640(dataset)}
        for pid in sorted(set(orig) - set(by_pres)):
            fails.append((pid, None, "presentation missing from the file"))
        for pid, rs in by_pres.items():
            if pid not in orig or any((r["r1_orig"], r["r2_orig"]) != orig[pid] for r in rs):
                fails.append((pid, None, "r1_orig/r2_orig differ from the dataset"))
    for pid, rs in by_pres.items():
        keys = [tuple(r["class_key"]) for r in rs]
        if len(keys) != len(set(keys)):
            fails.append((pid, None, "duplicate class_key"))
        if sum(r["is_control"] for r in rs) != 1:
            fails.append((pid, None, "not exactly one control row"))
        if counts:
            r0 = rs[0]
            r1, r2 = str_to_word(r0["r1_orig"]), str_to_word(r0["r2_orig"])
            cls = cov_all.enumerate_classes(r1, r2)
            fam = cov_all.subwords(r1, r2)
            one = {cov_all.class_key(o.r1, o.r2)
                   for o in cov.enumerate_cov(r1, r2, family=fam)}
            want_keys = {tuple(c.meta["class_key"]) for c in cls}
            want_one = {tuple(c.meta["class_key"]) for c in cls if c.meta["class_key"] in one}
            got = [r for r in rs if not r["is_control"]]
            if {tuple(r["class_key"]) for r in got} != want_keys or len(got) != len(cls):
                fails.append((pid, None, f"class set differs ({len(got)} vs {len(cls)})"))
            if {tuple(r["class_key"]) for r in got if r["is_one_pattern"]} != want_one:
                fails.append((pid, None, "is_one_pattern flags differ"))
    n_cov = sum(not r["is_control"] for r in rows)
    print(f"{path}: {len(rows)} rows ({len(by_pres)} presentations, {n_cov} cov, "
          f"{sum(r['is_one_pattern'] is True for r in rows)} one-pattern), "
          f"{sum(r['solved'] for r in rows)} solved, {n_paths} paths replayed, "
          f"{len(fails)} failures")
    for f in fails[:20]:
        print("  FAIL", f)
    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--counts", action="store_true")
    ap.add_argument("--dataset", default=None,
                    help="require every presentation of this dataset, with matching relators")
    ap.add_argument("--path-sample", type=float, default=None,
                    help="the run's --path-sample: require path_moves on every sampled solve")
    a = ap.parse_args()
    bad = sum(len(verify(p, a.counts, a.dataset, a.path_sample)) for p in a.files)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
