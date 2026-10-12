"""One function per method: solve a presentation, verify the certificate on it, return a record.

Each function takes the row's presentation and the run config. A record is written only after its certificate
is verified on the row (``acx.verify.replay``; a CoV ``stable_cert`` by ``acx.cov.verify``). With ``path = false`` no
certificate is made where the method can skip it, and none is verified.
"""
from functools import lru_cache

from ..core.moves import encode_path
from ..verify.decode import decode_and_replay
from ..verify.pack import pack
from ..verify.replay import replay
from .caps import record_caps
from .config import method_config
from .output import keeps_path


def record(solved, kind=None, aut_assisted=False, cost=0, sub_moves=None, elem_moves=None, path=None,
           elementary=None, **extra):
    """One row's record; ``extra`` fields (cap counters, ``rank``, ``image``, ...) follow the common ones.

    ``kind``: ``ac_path``, ``stable_cert`` or None. ``aut_assisted``: an ``ac_path`` carried back to the row from
    another basis. ``cost``: pops, hybrid units or network evaluations. ``sub_moves``: substitution moves.
    ``elem_moves``: elementary AC moves on the row (None for a CoV ``stable_cert``). ``path``: the S-moves
    (``acx.core.moves.encode_path``). ``elementary``: the elementary moves (``acx.verify.decode.pack``).
    ``verified`` starts false; ``output.shape`` sets it for a solve whose path was kept, as each method replays it.
    """
    return dict(solved=solved, kind=kind, aut_assisted=aut_assisted, cost=cost, sub_moves=sub_moves,
                elem_moves=elem_moves, path=None if path is None else encode_path(path),
                elementary=None if elementary is None else pack(elementary), verified=False, **extra)


def decoded_length(pres, path, cfg):
    """Elementary length of an S-move path (``path`` and ``decode`` true, cyclic reduction on), else None."""
    if not (keeps_path(cfg) and cfg.get("decode", True) and cfg.get("search", {}).get("cyclic", True)):
        return None
    return len(decode_and_replay(pres.reduced(False), path)[0])


def length(moves):
    """The number of moves, None when there is no path."""
    return None if moves is None else len(moves)


def greedy(pres, cfg):
    """Plain best-first search (``acx.search``)."""
    from ..search import search
    config = method_config(cfg)
    res = search(pres, config)
    caps = record_caps(res.stats)
    if not res.solved:
        return record(False, cost=res.pops, **caps)
    if keeps_path(cfg):
        replay(pres, res.path, cyclic=config.cyclic, cap=config.cap)
    return record(True, "ac_path", cost=res.pops, sub_moves=res.path_length,
                  elem_moves=decoded_length(pres, res.path, cfg), path=res.path, **caps)


def cov(pres, cfg):
    """Change-of-variables search (``acx.cov``)."""
    from ..cov import run_cov, verify
    res = run_cov(pres, method_config(cfg))
    caps = record_caps(res.stats)
    found = res.ac_path or res.stable_cert
    if found is None:
        return record(False, cost=res.pops, **caps)
    if keeps_path(cfg):
        verify(pres, found)
    image = found.image and found.image.tag
    if found.kind == "stable_cert":
        return record(True, "stable_cert", cost=res.pops, sub_moves=len(found.path), path=found.path,
                      image=image, steps=list(found.image.steps), **caps)
    on_the_row = not (found.path and isinstance(found.path[0], dict))      # S-moves on the row itself
    if on_the_row:
        return record(True, "ac_path", cost=res.pops, sub_moves=len(found.path),
                      elem_moves=decoded_length(pres, found.path, cfg), path=found.path, image=image, **caps)
    # Otherwise the path is elementary moves on the row, and the S-moves are those of the image.
    return record(True, "ac_path", aut_assisted=True, cost=res.pops, sub_moves=len(found.result.path),
                  elem_moves=len(found.path), path=found.result.path, elementary=found.path, image=image, **caps)


def aut(pres, cfg):
    """Search on the Aut-minimal representative, carried back to the row (``acx.aut``)."""
    from ..aut import solve_via_aut_min
    config = method_config(cfg)
    res, moves = solve_via_aut_min(pres, config)
    caps = record_caps(res.stats)
    if not res.solved:
        return record(False, cost=res.pops, **caps)
    carried_back = res.start != pres.normal(config.cyclic)      # False: the row is its own Aut-minimal form
    if keeps_path(cfg):
        replay(pres, moves, normalize=False)
        if not carried_back and config.cyclic:
            # The S-moves replay on the row itself and may decode shorter than the transported path.
            moves = min(moves, decode_and_replay(pres.reduced(False), res.path)[0], key=len)
    return record(True, "ac_path", aut_assisted=carried_back, cost=res.pops, sub_moves=res.path_length,
                  elem_moves=length(moves), path=res.path, elementary=moves, rep=list(res.start.strs), **caps)


def hybrid(pres, cfg):
    """Hybrid solver (``acx.hybrid``)."""
    from ..core.moves import Move
    from ..hybrid import encode_steps, solve
    from ..hybrid.cascade import Aut
    res = solve(pres, method_config(cfg))
    caps = record_caps(res.stats)
    if not res.solved:
        return record(False, cost=res.units, **caps)
    if keeps_path(cfg):
        replay(pres, res.path, normalize=False)
    used_aut = res.kind == "ac_path" and any(isinstance(step, Aut) for step in res.steps)
    return record(True, res.kind, aut_assisted=used_aut, cost=res.units,
                  sub_moves=sum(isinstance(step, Move) for step in res.steps), elem_moves=length(res.path),
                  elementary=res.path, stage=res.stage, steps=encode_steps(res.steps), **caps)


def ngen(pres, cfg):
    """n-generator search, SAC then lift (``acx.ngen``)."""
    from ..ngen import solve, verify
    config = method_config(cfg)
    res = solve(pres, config)
    caps = record_caps(res.search.stats)
    if not res.solved:
        return record(False, cost=res.search.pops, rank=res.rank, **caps)
    if keeps_path(cfg):
        verify(pres, res, cyclic=config.search.cyclic)
    path, sub_moves = res.search.path, res.search.path_length
    if res.kind == "ac_path":
        return record(True, "ac_path", cost=res.search.pops, sub_moves=sub_moves,
                      elem_moves=decoded_length(pres, path, cfg), path=path, rank=res.rank, **caps)
    return record(True, "stable_cert", cost=res.search.pops, sub_moves=sub_moves, elem_moves=length(res.moves),
                  path=path, elementary=res.moves, rank=res.rank, **caps)


@lru_cache(maxsize=1)
def _policy():
    """The pretrained policy, loaded once per process."""
    from ..rl.policy import pretrained
    return pretrained()


def rl(pres, cfg):
    """Network-guided beam search (``acx.rl``, needs PyTorch)."""
    from ..rl.solve import solve
    res = solve(pres, _policy(), **method_config(cfg))
    caps = record_caps(res.stats)
    if not res.solved:
        skipped = {"skipped": res.stats["skipped"]} if "skipped" in res.stats else {}
        return record(False, cost=res.pops, **skipped, **caps)
    if keeps_path(cfg):
        replay(pres, res.path, cap=res.stats["cap"])
    return record(True, "ac_path", cost=res.pops, sub_moves=res.path_length,
                  elem_moves=decoded_length(pres, res.path, cfg), path=res.path, **caps)


# ``rankn`` is not here: it writes its own per-row files (``acx.ngen.sweep``).
SOLVERS = {"greedy": greedy, "cov": cov, "aut": aut, "hybrid": hybrid, "ngen": ngen, "rl": rl}
