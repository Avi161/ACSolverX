"""The hybrid solver: the "solve everything" mode for balanced two-generator presentations.

    from acx.hybrid import solve
    res = solve(Presentation.parse("YYXyx", "Yx"))       # HybridConfig() defaults
    res.solved, res.kind, res.units, len(res.path)       # res.path replays under acx.verify.replay

Pipeline (each module's docstring has the details):

* ``cascade``: stages A-C on the canonical pair (Nielsen descent, primitive
  deletion, pinch cascade) and the finishing gates;
* ``solver``: then a best-first search over rank two (S-moves, Nielsen maps,
  signed-permutation canonical form; ``frontier``, on backend ``spec`` or
  ``fast``) and higher rank (``dynrank``: products, digram definitions,
  eliminations, transvections), one budget of work units;
* ``capwatch``: the cap counters of its three limits (``r2_cap``, ``dyn_cap``, ``slack``): what each
  dropped and whether a dropped state would have been popped (``stats``: ``cap_*``, ``dyn_cap_*``,
  ``slack_*``; the fields of ``acx.core.capcount``);
* ``certify``: the certificate becomes elementary AC moves on the presentation
  itself (plus AC4/AC5 when higher rank was used) and is replayed by
  ``acx.verify.replay`` before ``solve`` returns it.

Results are typed: ``ac_path`` (rank two throughout) or ``stable_cert`` (the
path passes through higher rank, so it proves stable AC-triviality); both are
replayable. Measured with the defaults (budget 1,000 units, one core):
MS640 640/640 in about 2.4 s; AC19 Aut-minimal census 72,779/72,779, 188 of
them ``stable_cert`` (``tests/test_hybrid.py``).

Source: ``origin/claude/vigilant-babbage-nnbuj0:research/ac_hashfree_cascade_20260914/``
(``hfhybrid.py``, ``hfcascade.py``, ``hfunified.py``) and
``research/ac_dynamic_rank_20260913/dynrank.py``, commit 5ae1bd8e. The source
called it "hash-free"; it is not (each frontier has a visited set), so the name
is dropped. No backward-ball table.
"""
from .certify import certify
from .solver import HybridConfig, HybridResult, decode_steps, encode_steps, solve
