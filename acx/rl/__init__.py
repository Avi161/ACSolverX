"""Optional RL extra: the Two-Hump PPO policy as a beam-search solver (needs ``torch``).

Source: ``origin/experiments/ppo:experiments/ppo`` (tip c73b11f2), the PyTorch port of the JAX PPO stack
(``origin/main:ppo_ac_s.py``, ``network.py``, ``envs/ac_moves.py``). Only the step-1000 weights of the
610model run ship (``checkpoint/610model_1000.pt``, 0.6 MB); there is no shaped-reward arm.

    moves.py    batched substitution move, bug for bug (0 mismatches on 7,500 legal transitions vs JAX)
    policy.py   ``ActorCritic`` (2 layers, 4 heads, ring attention) and ``pretrained()``; 2.7e-5 vs JAX
    beam.py     ``beam_search``: width x steps decode, 64-bit visited set, illegal actions dead, cap counters
    solve.py    ``solve(pres, cap=24)``: beam, translation to ``acx`` S-moves, ``acx.verify.replay``
    env.py ppo.py   training: ``VecEnv`` and ``train(states, updates)``
    convert.py  one-time orbax -> torch ``state_dict`` (needs jax + orbax-checkpoint)

    from acx.rl.solve import solve
    res = solve(Presentation.parse("YYXyx", "Yx"), width=256, steps=100)   # a Result; res.path replays

Install: ``pip install torch`` (CPU is enough; ``--index-url https://download.pytorch.org/whl/cpu`` for the small wheel).
"""

L = 24      # the policy's observation width: the longest relator it can see (torch-free, for config checks)
