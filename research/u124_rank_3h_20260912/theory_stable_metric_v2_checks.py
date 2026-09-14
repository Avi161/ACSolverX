"""Replay stable-spelling controls and verify exact parameter cost balls."""
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import theory_stable_metric_v2 as metric
import theory_stable_metric_checks as inherited
import theory_corridor as corridor


def run():
    inherited.metric = metric
    result = inherited.run()
    balls = pairs = 0
    for exponent in (2, -3, 7):
        root = corridor.Root(-1, 3, 2, exponent, [])
        model = {'m': 4, 'n': 5}
        for ceiling in range(4):
            values, used, complete = metric._coin_ball(root, ceiling, 1000)
            assert complete and used == 2 * ceiling * ceiling + 2 * ceiling + 1
            expected = {e: len(corridor.shortest_power(e, root))
                        for e in range(-abs(exponent) * ceiling, abs(exponent) * ceiling + 1)
                        if len(corridor.shortest_power(e, root)) <= ceiling}
            assert values == expected
            generated = list(metric._parameters(root, model, values, ceiling))
            expected_pairs = {(p, q) for p in values for q in values
                              if (p, q) != (0, 0) and values[p] + values[q] <= ceiling}
            assert len(generated) == len(set(generated)) and set(generated) == expected_pairs
            balls += 1
            pairs += len(generated)
    result.update({'exact_coin_balls_checked': balls, 'admissible_parameter_pairs_checked': pairs})
    return result


if __name__ == '__main__':
    result = run()
    Path(__file__).with_suffix('.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
