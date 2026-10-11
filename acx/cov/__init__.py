"""One-shot change of variables (z-family ``subnc2pxysb``): images, certificates, CoV-then-search.

``enumerate_images`` / ``check_cert`` (module ``cov``) and ``run_cov`` (= ``run.run``), whose
docstrings explain the transform and the typed outcomes ``stable_cert`` and ``ac_path``.
"""
from .cov import CoVImage, ReplayError, apply_steps, check_cert, enumerate_images
from .run import CoVConfig, CoVResult, Outcome, verify
from .run import run as run_cov
