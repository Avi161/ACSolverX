"""Stage B for the relabel-deduped arms: ``cov_top3_run`` under a scoped rule registration.

``cov_top3_run.load_config`` validates ``--rule`` against
``cov_top3_manifest.RULES``, and ``cov_top3_run.main`` builds its ``--rule``
choices from the same dict when it is called — so the deduped name has to be in
that whitelist while the run is being configured. ``cov_top3_relabel.registered``
puts it there for exactly that long and takes it back out afterwards, including
on error.

Why not register at import: that dict is read at module scope elsewhere, so a
permanent entry would make behaviour depend on import order — five tests in
``tests/stable_ac/test_cov_top3.py`` parametrize on ``sorted(M.RULES)`` at
collection time, and ``cov_top3_manifest``'s no-argument CLI builds
``sorted(RULES)``, which would then overwrite the deduped manifests with
undeduped ones. The full reasoning is in ``cov_top3_relabel``'s docstring.

No searching, resume, chunking, heartbeat or summary logic is restated here.
The rule name is in the resume prefix (``abel_rdtop3_...``), so these arms
cannot resume into the shipped ``abeltop3_*`` / ``lentop3_*`` files.

Build the manifest first — :func:`preflight` refuses one that is missing, built
for another rule, or not actually deduped:

    .venv/bin/python3 -m experiments.stable_ac.cov.run.cov_top3_relabel abel_rd
    ACSOLVERX_ALLOW_BIG=1 .venv/bin/python3 \
        -m experiments.stable_ac.cov.run.cov_top3_relabel_run --rule abel_rd

Production budgets run on Colab. ``cov_top3_run.load_config`` still refuses a
budget above 1,000 without ``ACSOLVERX_ALLOW_BIG=1``, and that cap is not
relaxed here.
"""

import sys

from experiments.stable_ac.cov.run import cov_top3_relabel as rd
from experiments.stable_ac.cov.run import cov_top3_run


def preflight(rule, out_dir=None, root=rd.ROOT):
    """Fail before any search if the rule's manifest is missing or not deduped.

    Stage B's own check is the ``rule`` field, which an undeduped build to the
    deduped path would also satisfy — ``cov_top3_relabel.verify`` re-derives
    every relabel class from ``(r1, r2)`` instead of trusting a stored tag.
    """
    rd.check_rule(rule)
    path = rd.manifest_path(rule, out_dir or rd.manifest.OUT_DIR)
    return rd.verify(path, root=root, rule=rule)


def _rule_of(argv):
    for i, a in enumerate(argv):
        if a == "--rule" and i + 1 < len(argv):
            return argv[i + 1]
        if a.startswith("--rule="):
            return a.split("=", 1)[1]
    return None


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    rule = _rule_of(argv)
    if rule is None:
        raise SystemExit(
            f"--rule is required here; expected one of {sorted(rd.RULES)}. "
            f"The shipped arms run through cov_top3_run directly.")
    r = preflight(rule)
    print(f"[preflight] {r['path']}: no relabel repeats over "
          f"{r['n_pres']} presentations", flush=True)
    old = sys.argv
    try:
        sys.argv = [old[0]] + argv
        with rd.registered(rule):
            cov_top3_run.main()
    finally:
        sys.argv = old


if __name__ == "__main__":
    main()
