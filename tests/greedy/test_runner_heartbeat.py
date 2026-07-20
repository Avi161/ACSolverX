"""The heartbeat, driven by a fake clock at the production interval.

Every phase bug this code has had was invisible at the 2-second interval used
while developing it and only appeared at the real 90 seconds. So the clock is
faked and the interval is the real one:

* the first emission is a separate design decision from the steady-state period
  -- a long startup silence is indistinguishable from a hang; and
* a tick that prints nothing must not advance ``last_print``, or the next block
  is delayed by a whole further period.
"""

import multiprocessing as mp

import pytest

import experiments.run_baseline as rb
from experiments.run_baseline import (
    _auto_workers, _fmt_hb, _Heartbeat, _HbPrinter, _iter_with_heartbeat,
)

INTERVAL = 90.0     # the interval the real runs use


class FakeClock:
    """Stands in for the ``time`` module inside ``run_baseline`` only.

    Patching ``rb.time`` rather than ``time.time`` keeps the fake out of pytest's
    and numba's clocks.
    """

    def __init__(self, t=1000.0):
        self.t = t

    def time(self):
        return self.t

    def advance(self, dt):
        self.t += dt


@pytest.fixture
def clock(monkeypatch):
    c = FakeClock()
    monkeypatch.setattr(rb, "time", c)
    return c


# -- _Heartbeat --------------------------------------------------------------


def test_the_first_sample_arrives_after_first_after_not_a_full_interval(clock):
    out = []
    hb = _Heartbeat(3, 1_000_000, INTERVAL, out.append, first_after=10.0)

    clock.advance(9.0)
    hb(1024)
    assert out == [], "must not emit before first_after"

    clock.advance(1.5)
    hb(2048)
    assert len(out) == 1, "must emit at first_after, not at interval"
    assert out[0][0] == 3 and out[0][1] == 2048


def test_first_after_is_capped_by_the_interval(clock):
    out = []
    hb = _Heartbeat(0, 100, 2.0, out.append, first_after=10.0)
    clock.advance(2.5)
    hb(1024)
    assert len(out) == 1


def test_steady_state_cadence_is_the_interval(clock):
    out = []
    hb = _Heartbeat(0, 1_000_000, INTERVAL, out.append, first_after=10.0)
    clock.advance(10.0)
    hb(1024)
    assert len(out) == 1

    clock.advance(INTERVAL - 1)
    hb(2048)
    assert len(out) == 1, "early call must be ignored"

    clock.advance(2.0)
    hb(4096)
    assert len(out) == 2


def test_debug_mode_emits_on_the_very_first_tick(clock):
    out = []
    hb = _Heartbeat(0, 100, INTERVAL, out.append, first_after=0.0)
    hb(1024)
    assert len(out) == 1


def test_the_reported_rate_uses_the_delta_since_the_previous_sample(clock):
    out = []
    hb = _Heartbeat(0, 100_000, 10.0, out.append, first_after=10.0)
    clock.advance(10.0)
    hb(1000)                     # 1000 nodes in 10s
    clock.advance(10.0)
    hb(3000)                     # +2000 nodes in 10s
    assert out[0][4] == pytest.approx(100.0)
    assert out[1][4] == pytest.approx(200.0)


def test_fmt_hb_renders_a_sample():
    txt = _fmt_hb((7, 500, 1000, 10.0, 50.0))
    assert "pres 7" in txt and "500/1,000" in txt and "50%" in txt


# -- _HbPrinter --------------------------------------------------------------


class FakeQueue:
    def __init__(self, msgs):
        self.msgs = list(msgs)

    def get_nowait(self):
        import queue

        if not self.msgs:
            raise queue.Empty
        return self.msgs.pop(0)

    def qsize(self):
        return len(self.msgs)


def test_an_empty_tick_does_not_advance_last_print(clock, capsys):
    """Otherwise the first real block is delayed by a whole extra period."""
    p = _HbPrinter(INTERVAL)
    clock.advance(INTERVAL + 1)
    p.drain(FakeQueue([]))
    assert p.last_print == 0.0

    p.drain(FakeQueue([("sample", 1, 2048, 10000, 5.0, 400.0)]))
    assert p.last_print == clock.t
    assert "1 solving" in capsys.readouterr().out


def test_the_first_arriving_sample_prints_immediately(clock, capsys):
    p = _HbPrinter(INTERVAL)
    p.drain(FakeQueue([("sample", 4, 1024, 5000, 2.0, 500.0)]))
    out = capsys.readouterr().out
    assert "1 solving" in out and "pres 4" in out


def test_the_done_sentinel_is_tag_first_and_stops_the_rate_counting(clock, capsys):
    p = _HbPrinter(INTERVAL)
    p.drain(FakeQueue([("sample", 1, 1024, 5000, 1.0, 100.0),
                       ("sample", 2, 1024, 5000, 1.0, 200.0)]))
    assert set(p.live) == {1, 2}
    assert "agg 300 nodes/s" in capsys.readouterr().out

    clock.advance(INTERVAL + 1)
    p.drain(FakeQueue([("done", 1)]))
    assert set(p.live) == {2}
    assert "agg 200 nodes/s" in capsys.readouterr().out


def test_a_start_message_prints_liveness_before_any_sample(clock, capsys):
    p = _HbPrinter(INTERVAL)
    p.drain(FakeQueue([("start", 9, 4242)]))
    out = capsys.readouterr().out
    assert "pres 9 started" in out and "4242" in out
    assert p.live == {}


def test_a_dead_worker_is_dropped_after_two_intervals(clock, capsys):
    p = _HbPrinter(INTERVAL)
    p.drain(FakeQueue([("sample", 1, 1024, 5000, 1.0, 100.0)]))
    capsys.readouterr()
    clock.advance(2 * INTERVAL + 1)
    p.drain(FakeQueue([]))
    assert p.live == {}, "a worker that never sent 'done' must not inflate agg forever"


def test_debug_mode_warns_when_workers_start_but_never_tick(clock, capsys):
    p = _HbPrinter(INTERVAL, debug=True)
    p.drain(FakeQueue([("start", 1, 100)]))
    capsys.readouterr()
    clock.advance(51)
    p.drain(FakeQueue([]))
    out = capsys.readouterr().out
    assert "blocked inside greedy_search" in out


# -- _iter_with_heartbeat ----------------------------------------------------


def test_iter_with_heartbeat_is_a_passthrough_when_there_is_no_queue():
    assert list(_iter_with_heartbeat(iter([1, 2, 3]), None, 90)) == [1, 2, 3]


def test_iter_with_heartbeat_drains_between_results(clock, capsys):
    class It:
        def __init__(self):
            self.n = 0

        def next(self, timeout=None):
            self.n += 1
            if self.n == 1:
                raise mp.TimeoutError
            if self.n > 3:
                raise StopIteration
            return self.n

    q = FakeQueue([("sample", 1, 1024, 5000, 1.0, 123.0)])
    got = list(_iter_with_heartbeat(It(), q, INTERVAL))
    assert got == [2, 3]
    assert "123 nodes/s" in capsys.readouterr().out


# -- worker sizing -----------------------------------------------------------
#
# ``_auto_workers(cfg, node_budget)`` is bounded by usable cores AND by memory.
# ``GB_PER_PRES`` defaults to "auto": the per-search footprint is estimated from
# the node budget rather than assumed constant, because one constant is wrong at
# both ends (9.0 GB starves a 50k run of workers and under-provisions a 1M one).
# These tests pin the *shape* of that estimate, not its calibration constants.


def test_auto_workers_honours_an_explicit_setting():
    assert _auto_workers({"N_WORKERS": 7}, 1000) == 7


def test_auto_workers_is_bounded_by_memory_then_cores(monkeypatch):
    monkeypatch.setattr(rb, "_usable_cores", lambda: 16)
    monkeypatch.setattr(rb, "_avail_ram_gb", lambda: 50.0)
    # An explicit GB_PER_PRES wins over the estimate: 50 * 0.90 // 9 = 5.
    assert _auto_workers({"N_WORKERS": 0, "GB_PER_PRES": 9.0}, 1000) == 5
    # A smaller footprint lets more workers run, capped by the core count.
    assert _auto_workers({"N_WORKERS": 0, "GB_PER_PRES": 0.5}, 1000) == 16


def test_auto_workers_never_returns_zero(monkeypatch):
    """Under-provisioning cores wastes time; under-provisioning memory OOMs.

    So the floor is one worker, never zero, even when a search cannot fit.
    """
    monkeypatch.setattr(rb, "_usable_cores", lambda: 4)
    monkeypatch.setattr(rb, "_avail_ram_gb", lambda: 1.0)
    assert _auto_workers({"N_WORKERS": 0, "GB_PER_PRES": 9.0}, 1000) == 1


def test_auto_workers_survives_an_unreadable_ram_size(monkeypatch):
    monkeypatch.setattr(rb, "_usable_cores", lambda: 8)
    monkeypatch.setattr(rb, "_avail_ram_gb", lambda: 0.0)
    assert _auto_workers({"N_WORKERS": 0}, 1000) == 1


@pytest.mark.parametrize("solver", ["heavy", "compact"])
def test_the_auto_estimate_grows_with_the_node_budget(monkeypatch, solver):
    """The whole point of "auto": a 1k search must not be sized like a 1M one."""
    cfg = {"N_WORKERS": 0, "GB_PER_PRES": "auto", "SOLVER": solver}
    small = rb._est_gb_per_pres(cfg, 1_000)
    large = rb._est_gb_per_pres(cfg, 1_000_000)
    assert small < large
    assert small < 1.0, "a 1k-node search must not be provisioned in gigabytes"

    monkeypatch.setattr(rb, "_usable_cores", lambda: 16)
    monkeypatch.setattr(rb, "_avail_ram_gb", lambda: 50.0)
    assert _auto_workers(cfg, 1_000) >= _auto_workers(cfg, 1_000_000)


def test_the_1m_estimate_is_solver_specific():
    """The old fixed 9.0 was too LOW for the heavy solver at its own calibration
    point (1M x ~64 states x 220 B ~ 14 GB). The compact solver genuinely needs
    less than 9 -- that is not the old bug returning, it is the fix."""
    auto = {"N_WORKERS": 0, "GB_PER_PRES": "auto"}
    heavy = rb._est_gb_per_pres({**auto, "SOLVER": "heavy"}, 1_000_000)
    compact = rb._est_gb_per_pres({**auto, "SOLVER": "compact"}, 1_000_000)
    assert heavy > 9.0
    assert 4.0 < compact < 9.0
    assert compact < heavy


def test_an_explicit_gb_per_pres_overrides_the_estimate():
    cfg_auto = {"GB_PER_PRES": "auto"}
    cfg_fixed = {"GB_PER_PRES": 4.0}
    assert rb._est_gb_per_pres(cfg_fixed, 1_000_000) == 4.0
    assert rb._est_gb_per_pres(cfg_auto, 1_000_000) != 4.0


@pytest.mark.parametrize("falsy", ["auto", 0, None, False])
def test_a_falsy_gb_per_pres_falls_back_to_the_estimate(falsy):
    """0/None/False must not divide-by-zero or be read as "0 GB per search"."""
    est = rb._est_gb_per_pres({"GB_PER_PRES": falsy}, 10_000)
    assert est > 0
