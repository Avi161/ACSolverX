"""One-shot change of variables (z-family ``subnc2pxysb``): images, certificates, CoV-then-search.

    substitution.py   the word operations (put z for w, isolate a generator)
    family.py         which words w define z, and the tag's rules
    cov.py            ``CoVImage`` and ``enumerate_images``
    certificate.py    ``apply_steps`` / ``check_cert``, the independent checker
    run.py            ``run_cov``: the row and its images searched within one budget

The docstrings of ``enumerate_images`` and ``run_cov`` explain the transform and the typed outcomes
``stable_cert`` and ``ac_path``.
"""
from .certificate import ReplayError, apply_steps, check_cert
from .cov import CoVImage, enumerate_images
from .run import CoVConfig, CoVResult, Outcome, verify
from .run import run as run_cov
