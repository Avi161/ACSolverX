"""Optional RL extra (needs ``torch``): the Two-Hump PPO policy, step-1000 weights only, as a beam-search solver.

    moves.py    batched substitution move       policy.py   ``ActorCritic`` and ``pretrained()``
    beam.py     ``beam_search`` with cap counters   solve.py    ``solve(pres, cap=24)``: beam, S-move translation, replay
    env.py ppo.py   training (``VecEnv``, ``train``)      convert.py  one-time orbax -> torch ``state_dict``

    from acx.rl.solve import solve
    res = solve(Presentation.parse("YYXyx", "Yx"), width=256, steps=100)   # a Result; res.path replays

Install: ``pip install torch`` (CPU is enough; ``--index-url https://download.pytorch.org/whl/cpu`` for the small wheel).
"""

L = 24      # the policy's observation width: the longest relator it can see (torch-free, for config checks)
