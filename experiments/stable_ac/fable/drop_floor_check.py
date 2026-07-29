"""Decisive machine check of the DROP FLOOR (results/stable_ac/theory/fable/R7C_DROP_FLOOR.md).

REUSES the existing audited harness -- ``audit_r7_core.py`` (Dict0, spike_words,
spike_layout, all_spikes, restrict, gens_of) and ``audit_r7_checks.py`` (interpolate,
bases_reduced, canon_bases) -- and modifies neither. This module is new code only.

DROP FLOOR (as reduced in R7c). Write, for a base P, a spike (j,k,u) of P, and a
compatible rotation system C' of the spiked complex:

    d_post = defect(C')                      (Dict0(post).defect(op))
    d_pre  = defect(rho(C'))                 (Dict0(pre).defect(restrict(op, ...)))

A STRICT DROP is d_post == d_pre - 2. The claim is: every strict drop has d_pre >= 4.

R7c's own reduction (communicated by the orchestrator; re-derived here independently
via the interpolation walk in ``audit_r7_checks.interpolate``) shows:

    d_post - d_pre = -2*Xminus + 2*Xplus,   Xminus in {0,1}, Xplus in {0,1,2,3}

so a strict drop forces Xminus=1, Xplus=0, and since defect is even and >= 0 pointwise,
d_pre = 0 CANNOT support a strict drop (it would force d_post = -2). Consequently:

  * a strict drop with d_pre == 0 is IMPOSSIBLE a priori -- if this script finds one it
    is flagged as a BUG (most likely restrict() mapping to the wrong complex), never as
    a mathematical discovery;
  * the entire question reduces to whether a strict drop can occur AT d_pre == 2. The
    count of (base, spike, op) triples examined with d_pre == 2 is therefore reported as
    the primary strength-of-verdict number, separate from the raw triple count.

Also reports, per the master prompt: the joint (d_pre, d_post) histogram (with/without
degenerate length-1-relator bases); the histogram of d_pre among strict drops and its
minimum; for strict drops, the (Xminus, Xplus) histogram and the joint (d_pre,
delta_comp) histogram (delta_comp = whether the spike germ s and the corner germ X of
the base lie in the same link component -- computed exactly as check_fibration_and_master
does it); and, over every (base, spike) pair, 2*gamma_N(spike) vs 2*gamma_N(base), with
any pair where gamma_N(spike) == 0 < gamma_N(base) printed in full as a direct
counterexample to "spiked thickenable => reduced thickenable".

GUARDRAILS applied (see CLAUDE.md lessons):
  * no free/cyclic reduction is ever applied to spiked spellings -- audit_r7_core's
    helpers are already spike-safe and are used as-is.
  * RANK GATE: Dict0 is always constructed with the fixed generators ("x","y"); a base
    or spiked word list is processed only if gens_of(words) == {"x","y"} (i.e. BOTH
    letters actually occur), otherwise it is skipped and counted. This prevents a
    rank-1 word list from being silently scored as a smaller complex.
  * degenerate bases (a relator of length 1) are INCLUDED, not filtered, but every
    histogram is reported twice: with and without them. Triples are also broken down by
    len(words[j]) (the length of the relator actually being spiked), since a parallel
    audit found the S2 fibration failing specifically on length-1 relators.

Run directly: ``python3 drop_floor_check.py [--out PATH] [--cap N] [--max-total-len N]
[--time-budget SECONDS]``. Pure Python (itertools/collections only) -- no numpy, no
numba, no JAX. Not a move-search of any kind, so node_budget does not apply; the only
budgets here are the compatible-rotation-system census cap and a wall-clock cap.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import Counter

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_THIS_DIR, "..", "..", ".."))
sys.path.insert(0, _THIS_DIR)   # audit_r7_core / audit_r7_checks import each other as top-level modules
sys.path.insert(0, _REPO_ROOT)  # neuwirth_rank_n imports via "experiments.stable_ac.fable...."

from audit_r7_core import Dict0, all_spikes, gens_of, restrict, spike_layout, spike_words
from audit_r7_checks import bases_reduced, canon_bases, interpolate

GENERATORS = ("x", "y")


def full_rank(words):
    """RANK GATE: both generators must actually occur in the word list."""
    return set(gens_of(words)) == set(GENERATORS)


def is_degenerate_base(words):
    return any(len(w) == 1 for w in words)


def hkey(t):
    if isinstance(t, tuple):
        return ",".join(str(x) for x in t)
    return str(t)


def hist_to_dict(counter):
    return {hkey(k): v for k, v in sorted(counter.items(), key=lambda kv: str(kv[0]))}


def op_to_json(op):
    return {str(v): list(seq) for v, seq in sorted(op.items())}


def build_corpus(max_total_len, verbose=True):
    raw = []
    for total in range(2, max_total_len + 1):
        raw.extend(bases_reduced(total))
    t0 = time.time()
    canon = canon_bases(raw)
    if verbose:
        print(f"[corpus] total length 2..{max_total_len}: {len(raw)} raw pairs -> "
              f"{len(canon)} canonical bases ({time.time() - t0:.2f}s to canonicalize)",
              flush=True)
    return canon


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default="results/stable_ac/fable/drop_floor_check.json")
    ap.add_argument("--cap", type=int, default=6000,
                     help="max census_size() of the SPIKED complex to fully enumerate")
    ap.add_argument("--base-cap", type=int, default=2_000_000,
                     help="max census_size() of the BASE, for computing its own gamma_N")
    ap.add_argument("--max-total-len", type=int, default=8,
                     help="sweep bases_reduced(2..max-total-len), canon-deduped")
    ap.add_argument("--time-budget", type=float, default=1000.0,
                     help="soft wall-clock budget in seconds (script stops sweeping "
                          "new bases past this and reports exactly what it covered)")
    ap.add_argument("--progress-every", type=int, default=25)
    args = ap.parse_args()

    t_start = time.time()

    def elapsed():
        return time.time() - t_start

    bases = build_corpus(args.max_total_len)
    corpus_size = len(bases)

    # ---- counters -----------------------------------------------------------------
    joint_hist = Counter()
    joint_hist_nondeg = Counter()
    joint_hist_deg = Counter()

    strict_drop_dpre_hist = Counter()
    strict_drop_dpre_hist_nondeg = Counter()
    strict_drop_dpre_hist_deg = Counter()
    strict_drop_wj_len_hist = Counter()
    strict_drop_xminus_xplus_hist = Counter()
    strict_drop_dpre_deltacomp_hist = Counter()

    pair_gamma_hist = Counter()          # (gamma_pre, gamma_post) over (base,spike) pairs

    d_pre_eq_2_triples = 0
    d_pre_eq_2_by_wj_len = Counter()
    d_pre_eq_0_triples = 0

    min_dpre_strict_drop = None
    min_dpre_strict_drop_nondeg = None

    violations = []              # strict drop with d_pre == 2 : genuine DROP FLOOR test
    bug_impossible_zero = []     # strict drop with d_pre == 0 : a priori impossible -> bug
    bug_s2_incompatible = []     # restrict() landed outside the base's compatible orders
    bug_s4_mismatch = []         # interpolate() disagrees with direct defect()
    s2_incompatible_by_deg_relator = Counter()

    sr_counterexamples = []      # gamma_N(spike) == 0 < gamma_N(base)

    skipped_rank_bases = 0
    skipped_rank_spikes = 0
    skipped_cap_base = 0
    skipped_cap_post = 0

    bases_examined = 0
    bases_examined_degenerate = 0
    spikes_examined = 0
    triples_examined = 0

    time_up = False

    for bi, words in enumerate(bases):
        if elapsed() > args.time_budget:
            time_up = True
            break
        if not full_rank(words):
            skipped_rank_bases += 1
            continue
        pre = Dict0(words, GENERATORS)
        if pre.census_size() > args.base_cap:
            skipped_cap_base += 1
            continue
        pre_defects = [pre.defect(o) for o in pre.compatible_orders()]
        if not pre_defects:
            skipped_cap_base += 1
            continue
        gamma_pre = min(pre_defects) // 2
        deg_base = is_degenerate_base(words)
        bases_examined += 1
        if deg_base:
            bases_examined_degenerate += 1

        for (j, k, u) in all_spikes(words, GENERATORS):
            if elapsed() > args.time_budget:
                time_up = True
                break
            post_words = spike_words(words, j, k, u)
            if not full_rank(post_words):
                # a priori impossible (spikes only add letters) -- flag loudly if hit
                skipped_rank_spikes += 1
                bug_s2_incompatible.append(("RANK GATE: spike lost a generator -- bug",
                                             list(words), j, k, list(post_words)))
                continue
            post = Dict0(post_words, GENERATORS)
            if post.census_size() > args.cap:
                skipped_cap_post += 1
                continue
            deg_relator = len(words[j]) == 1
            lay = spike_layout(words, j, k, u)

            post_defects_all = []
            for op in post.compatible_orders():
                d_post = post.defect(op)
                post_defects_all.append(d_post)
                r = restrict(op, words, j, k, u)
                if not pre.is_compatible(r):
                    bug_s2_incompatible.append(dict(
                        words=list(words), j=j, k=k, u=u,
                        post_words=list(post_words), deg_relator=deg_relator,
                    ))
                    s2_incompatible_by_deg_relator[deg_relator] += 1
                    continue
                d_pre = pre.defect(r)
                triples_examined += 1
                joint_hist[(d_pre, d_post)] += 1
                (joint_hist_deg if deg_base else joint_hist_nondeg)[(d_pre, d_post)] += 1

                if d_pre == 2:
                    d_pre_eq_2_triples += 1
                    d_pre_eq_2_by_wj_len[len(words[j])] += 1
                elif d_pre == 0:
                    d_pre_eq_0_triples += 1

                if d_post == d_pre - 2:
                    # STRICT DROP
                    strict_drop_dpre_hist[d_pre] += 1
                    (strict_drop_dpre_hist_deg if deg_base
                     else strict_drop_dpre_hist_nondeg)[d_pre] += 1
                    strict_drop_wj_len_hist[len(words[j])] += 1
                    if min_dpre_strict_drop is None or d_pre < min_dpre_strict_drop:
                        min_dpre_strict_drop = d_pre
                    if not deg_base and (min_dpre_strict_drop_nondeg is None
                                          or d_pre < min_dpre_strict_drop_nondeg):
                        min_dpre_strict_drop_nondeg = d_pre

                    defs, deltas = interpolate(words, j, k, u, op)
                    if defs[0] != d_pre or defs[4] != d_post:
                        bug_s4_mismatch.append(dict(
                            words=list(words), j=j, k=k, u=u, d_pre=d_pre, d_post=d_post,
                            defs=defs,
                        ))
                    Xminus = 1 if deltas[0] == -2 else 0
                    Xplus = sum(1 for i in (1, 2, 3) if deltas[i] == 2)
                    delta_comp = (0 if pre.comp_of.get(lay["s"]) == pre.comp_of.get(lay["X"])
                                  else 1)
                    strict_drop_xminus_xplus_hist[(Xminus, Xplus)] += 1
                    strict_drop_dpre_deltacomp_hist[(d_pre, delta_comp)] += 1

                    witness = dict(
                        words=list(words), j=j, k=k, u=u, post_words=list(post_words),
                        op=op_to_json(op), d_pre=d_pre, d_post=d_post,
                        Xminus=Xminus, Xplus=Xplus, delta_comp=delta_comp,
                        deg_base=deg_base, deg_relator=deg_relator, len_wj=len(words[j]),
                        gamma_pre_of_base=gamma_pre,
                        rank_gate_words=full_rank(words),
                        rank_gate_post=full_rank(post_words),
                    )
                    if d_pre == 0:
                        bug_impossible_zero.append(witness)
                    elif d_pre <= 2:
                        violations.append(witness)

            if post_defects_all:
                gamma_post = min(post_defects_all) // 2
                pair_gamma_hist[(gamma_pre, gamma_post)] += 1
                if gamma_post == 0 and gamma_pre > 0:
                    sr_counterexamples.append(dict(
                        words=list(words), post_words=list(post_words),
                        j=j, k=k, u=u, gamma_pre=gamma_pre, gamma_post=gamma_post,
                        rank_gate_words=full_rank(words),
                        rank_gate_post=full_rank(post_words),
                    ))
            spikes_examined += 1

        if bi % args.progress_every == 0:
            print(f"[progress] base {bi + 1}/{corpus_size} elapsed={elapsed():.0f}s "
                  f"bases_examined={bases_examined} spikes_examined={spikes_examined} "
                  f"triples={triples_examined} d_pre=2 triples={d_pre_eq_2_triples} "
                  f"strict_drops={sum(strict_drop_dpre_hist.values())} "
                  f"min_dpre_strict_drop={min_dpre_strict_drop} "
                  f"violations={len(violations)} bugs(zero)={len(bug_impossible_zero)} "
                  f"bugs(s2)={len(bug_s2_incompatible)} sr_counterexamples="
                  f"{len(sr_counterexamples)}", flush=True)

    total_time = elapsed()

    n_strict_drops = sum(strict_drop_dpre_hist.values())
    drop_floor_status = "CONFIRMED"
    if bug_impossible_zero or bug_s2_incompatible or bug_s4_mismatch:
        drop_floor_status = "HARNESS BUG -- SEE bug_* FIELDS, NOT A MATH VERDICT"
    elif violations:
        drop_floor_status = "REFUTED"

    # The literal per-triple DROP FLOOR is a strictly stronger statement than the
    # global implication SR ("spiked thickenable => reduced thickenable"): a single
    # violation (strict drop at d_pre==2) only forces gamma_N(spike)==0 for that
    # (base,spike) pair; it becomes an SR counterexample only if that SAME base has NO
    # other rotation of defect 0, i.e. gamma_N(base) > 0. R7C's proof of
    # "DROP FLOOR => SR" is correct (violations==0 must force sr_counterexamples==0 --
    # that direction is a logical certainty, not merely empirical); its informal
    # "SR => DROP FLOOR" paragraph is NOT: a base can have gamma_N(base)==0 via one
    # rotation while some OTHER rotation of that same base still strict-drops from
    # d_pre==2, and that is consistent with SR, not a contradiction. The real invariant
    # implied by the (correct) DROP-FLOOR=>SR direction is therefore:
    #     any violation whose OWN base has gamma_N(base) > 0 must correspond to an
    #     SR counterexample, and conversely.
    violations_at_nonthickenable_base = [w for w in violations if w["gamma_pre_of_base"] > 0]
    violations_at_thickenable_base = [w for w in violations if w["gamma_pre_of_base"] == 0]
    true_equivalence_agrees = ((len(violations_at_nonthickenable_base) == 0)
                                == (len(sr_counterexamples) == 0))

    result = dict(
        meta=dict(
            script="experiments/stable_ac/fable/drop_floor_check.py",
            claim="DROP FLOOR: every strict drop (d_post = d_pre - 2) has d_pre >= 4; "
                  "reduces (R7c) to: no strict drop can occur at d_pre == 2, since "
                  "d_pre == 0 is a priori impossible for a strict drop.",
            args=vars(args),
            corpus_total_length_range=[2, args.max_total_len],
            corpus_size_canonical_bases=corpus_size,
            time_up_triggered=time_up,
            total_runtime_seconds=round(total_time, 2),
        ),
        counts=dict(
            bases_in_corpus=corpus_size,
            bases_skipped_rank_gate=skipped_rank_bases,
            bases_skipped_base_cap=skipped_cap_base,
            bases_examined=bases_examined,
            bases_examined_degenerate_length1_relator=bases_examined_degenerate,
            spikes_skipped_rank_gate=skipped_rank_spikes,
            spikes_skipped_post_census_cap=skipped_cap_post,
            spikes_examined=spikes_examined,
            triples_examined=triples_examined,
            triples_with_d_pre_eq_0=d_pre_eq_0_triples,
            triples_with_d_pre_eq_2=d_pre_eq_2_triples,
            triples_with_d_pre_eq_2_by_len_wj=hist_to_dict(d_pre_eq_2_by_wj_len),
            strict_drops_total=n_strict_drops,
            min_d_pre_over_strict_drops=min_dpre_strict_drop,
            min_d_pre_over_strict_drops_nondegenerate_base=min_dpre_strict_drop_nondeg,
        ),
        joint_d_pre_d_post_histogram=dict(
            all=hist_to_dict(joint_hist),
            nondegenerate_base_only=hist_to_dict(joint_hist_nondeg),
            degenerate_base_only=hist_to_dict(joint_hist_deg),
        ),
        strict_drop_d_pre_histogram=dict(
            all=hist_to_dict(strict_drop_dpre_hist),
            nondegenerate_base_only=hist_to_dict(strict_drop_dpre_hist_nondeg),
            degenerate_base_only=hist_to_dict(strict_drop_dpre_hist_deg),
            by_len_wj_spiked_relator=hist_to_dict(strict_drop_wj_len_hist),
        ),
        strict_drop_Xminus_Xplus_histogram=hist_to_dict(strict_drop_xminus_xplus_hist),
        strict_drop_d_pre_delta_comp_histogram=hist_to_dict(strict_drop_dpre_deltacomp_hist),
        pair_gamma_pre_gamma_post_histogram=hist_to_dict(pair_gamma_hist),
        drop_floor_violations_d_pre_le_2=violations,
        sr_direct_counterexamples=sr_counterexamples,
        bug_flags=dict(
            impossible_strict_drop_at_d_pre_0=bug_impossible_zero,
            s2_restrict_incompatible_with_base=bug_s2_incompatible,
            s2_incompatible_by_deg_relator=hist_to_dict(s2_incompatible_by_deg_relator),
            s4_interpolate_mismatch=bug_s4_mismatch,
        ),
        verdict=dict(
            drop_floor_status=drop_floor_status,
            note="The literal per-rotation DROP FLOOR and the global implication SR "
                 "are NOT equivalent as claimed in R7C_DROP_FLOOR.md's informal 'SR => "
                 "DROP FLOOR' paragraph: DROP FLOOR => SR is a logical certainty "
                 "(verified: see true_equivalence_agrees), but the converse fails -- a "
                 "base can satisfy SR (have its own gamma_N==0 via one rotation) while "
                 "a DIFFERENT rotation of the SAME base still strict-drops from d_pre==2. "
                 "See violations_at_thickenable_base_count vs "
                 "violations_at_nonthickenable_base_count.",
            n_drop_floor_violations=len(violations),
            violations_at_thickenable_base_count=len(violations_at_thickenable_base),
            violations_at_nonthickenable_base_count=len(violations_at_nonthickenable_base),
            n_sr_direct_counterexamples=len(sr_counterexamples),
            true_equivalence_agrees=true_equivalence_agrees,
            min_d_pre_over_strict_drops=min_dpre_strict_drop,
            triples_examined_at_d_pre_eq_2=d_pre_eq_2_triples,
            triples_examined_total=triples_examined,
        ),
    )

    out_path = args.out
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"[done] wrote {out_path} ({total_time:.1f}s wall clock)", flush=True)

    print("\n=== SUMMARY ===")
    print(f"corpus: {corpus_size} canonical bases, total length 2..{args.max_total_len}; "
          f"bases_examined={bases_examined} (degenerate={bases_examined_degenerate}), "
          f"time_up_triggered={time_up}")
    print(f"triples_examined={triples_examined}  (at d_pre==2: {d_pre_eq_2_triples}; "
          f"at d_pre==0: {d_pre_eq_0_triples})")
    print(f"strict_drops={n_strict_drops}  min_d_pre_over_strict_drops="
          f"{min_dpre_strict_drop}")
    print(f"drop_floor_violations(d_pre<=2)={len(violations)}  "
          f"[at thickenable base(gamma_pre=0)={len(violations_at_thickenable_base)}, "
          f"at NON-thickenable base(gamma_pre>0)={len(violations_at_nonthickenable_base)}]  "
          f"sr_direct_counterexamples={len(sr_counterexamples)}  "
          f"true_equivalence_agrees={true_equivalence_agrees}")
    print(f"bug flags: zero-strict-drop={len(bug_impossible_zero)} "
          f"s2-incompatible={len(bug_s2_incompatible)} "
          f"s4-mismatch={len(bug_s4_mismatch)}")
    print(f"VERDICT: {drop_floor_status}")


if __name__ == "__main__":
    main()
