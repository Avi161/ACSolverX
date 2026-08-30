"""Re-run ONE campaign row under a time-resolved memory observer.

Built for the ac19_23156 anomaly: a 43.5 GB peak that no inventory of the
engine's arrays reaches and no widen/grow line explains, after three
falsified mechanisms. The stopping rule after the third was measurement,
not a fourth hypothesis -- so this runs a single named row exactly the way
the campaign does (same loader, same ``plan_memory`` sizing, same spawned
``_RowProc`` isolation) while the parent samples the child's ``/proc``
every few seconds into a CSV:

    elapsed_s, vmrss_gb, vmhwm_gb, thp_gb

A STEP in that curve is a transient (its timestamp names the event; the
engine's widen/grow prints are now self-attributing via the worker's comm);
a smooth RAMP means the steady per-state model itself is wrong for this
search shape. The search is deterministic for a fixed (row, budget, mrl,
reservation), so one observed run settles what the campaign's single
end-of-row VmHWM number could not.

Never touches the campaign's jsonl: results go to ``rerun_<name>.jsonl``
and ``rerun_<name>_rss.csv`` in ``--out-dir``. Pass ``--reserve-states``
with the campaign's exact reservation (the grow lines print it) when
reproducing a campaign peak -- ``plan_memory`` recomputes from free RAM,
which on a differently-loaded box can clip differently.
"""
from __future__ import annotations

import argparse
import json
import os
import time

from experiments.search.run_leftovers_5m import (
    HAVE_HCOMPACT, MRL_5M, NODE_BUDGET_5M, _RowProc, load_rows_5m,
    plan_memory, resolve_campaign,
)


def _proc_gb(pid, path, keys):
    """Named fields of /proc/<pid>/<path> in GB, or Nones (racing a death
    or a kernel without the file must never kill the observer)."""
    out = {k: None for k in keys}
    try:
        with open(f"/proc/{pid}/{path}") as f:
            for line in f:
                for k in keys:
                    if line.startswith(k + ":"):
                        out[k] = round(int(line.split()[1]) / 2 ** 20, 3)
    except (OSError, ValueError, IndexError):
        pass
    return [out[k] for k in keys]


def find_row(name, arm="greedy", campaign="ac19", csv_path=None):
    ckey, _ = resolve_campaign(campaign)
    rows, used = load_rows_5m(arm, csv_path=csv_path, campaign=ckey)
    for r in rows:
        if r["name"] == name:
            return r
    raise SystemExit(
        f"row {name!r} is not in the {arm}/{ckey} list ({len(rows)} rows "
        f"from {used})")


def rerun(name, out_dir, arm="greedy", campaign="ac19", budget=NODE_BUDGET_5M,
          mrl=MRL_5M, reserve_states=None, mem_limit_bytes=None,
          sample_secs=5.0, heartbeat_secs=60, csv_path=None, log=print):
    if not HAVE_HCOMPACT:
        raise SystemExit("hcompact engine missing -- a python-fallback rerun "
                         "would measure the wrong program")
    row = find_row(name, arm, campaign, csv_path)
    if mem_limit_bytes is None or reserve_states is None:
        ml, rs = plan_memory(budget, mrl, log=log)
        mem_limit_bytes = ml if mem_limit_bytes is None else mem_limit_bytes
        reserve_states = rs if reserve_states is None else reserve_states
    os.makedirs(out_dir, exist_ok=True)
    csv_out = os.path.join(out_dir, f"rerun_{name}_rss.csv")
    rec_out = os.path.join(out_dir, f"rerun_{name}.jsonl")

    log(f"  row     : {name}  ({arm}/{campaign})")
    log(f"  budget  : {budget:,} nodes, cap {mrl}, "
        f"reserve {reserve_states:,} states")
    log(f"  observer: /proc sample every {sample_secs:g}s -> {csv_out}")

    proc = _RowProc(arm, row, budget, mrl, heartbeat_secs, mem_limit_bytes,
                    reserve_states, None, log)
    t0 = time.time()
    rec, last = None, 0.0
    with open(csv_out, "w") as csv:
        csv.write("elapsed_s,vmrss_gb,vmhwm_gb,thp_gb\n")
        while rec is None:
            rec = proc.poll(timeout=1.0)
            now = time.time()
            if now - last >= sample_secs:
                last = now
                rss, hwm = _proc_gb(proc.proc.pid, "status",
                                    ("VmRSS", "VmHWM"))
                thp, = _proc_gb(proc.proc.pid, "smaps_rollup",
                                ("AnonHugePages",))
                if rss is not None:
                    csv.write(f"{now - t0:.1f},{rss},{hwm},{thp}\n")
                    csv.flush()
    with open(rec_out, "w") as fh:
        fh.write(json.dumps(rec) + "\n")
    log(f"  done    : solved={rec.get('solved')} "
        f"nodes={rec.get('nodes_explored', 0):,} "
        f"peak_rss_gb={rec.get('peak_rss_gb')} "
        f"({time.time() - t0:,.0f}s)")
    log(f"  -> {rec_out}")
    return rec, csv_out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--row", required=True, help="row name, e.g. ac19_23156")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--arm", default="greedy")
    ap.add_argument("--campaign", default="ac19")
    ap.add_argument("--budget", type=int, default=NODE_BUDGET_5M)
    ap.add_argument("--mrl", type=int, default=MRL_5M)
    ap.add_argument("--reserve-states", type=int, default=None,
                    help="pin the campaign's exact reservation; default "
                         "recomputes via plan_memory on THIS machine")
    ap.add_argument("--sample-secs", type=float, default=5.0)
    ap.add_argument("--csv", dest="csv_path", default=None)
    a = ap.parse_args(argv)
    rerun(a.row, a.out_dir, arm=a.arm, campaign=a.campaign, budget=a.budget,
          mrl=a.mrl, reserve_states=a.reserve_states,
          sample_secs=a.sample_secs, csv_path=a.csv_path)


if __name__ == "__main__":
    main()
