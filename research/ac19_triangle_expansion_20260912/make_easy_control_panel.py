"""Freeze the deterministic easy-control panel used by this experiment."""
import glob
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
EXPECTED = [
    'ac19_41', 'ac19_42', 'ac19_43', 'ac19_44', 'ac19_45', 'ac19_46',
    'ac19_47', 'ac19_48', 'ac19_50', 'ac19_51', 'ac19_52', 'ac19_54',
]


def main():
    selected = []
    pattern = ROOT / 'results/heuristic_search/ac19_final_policy_full_1k/rows_*.jsonl'
    for path in sorted(glob.glob(str(pattern))):
        for line in Path(path).read_text().splitlines():
            row = json.loads(line)
            if (row['solved'] and 5 <= row['nodes_explored'] <= 50
                    and min(map(len, row['pair'])) >= 6):
                selected.append(row)
                if len(selected) == len(EXPECTED):
                    break
        if len(selected) == len(EXPECTED):
            break
    if [row['name'] for row in selected] != EXPECTED:
        raise AssertionError('deterministic control panel changed')
    if not all(row['elementary_verified'] for row in selected):
        raise AssertionError('control panel contains an unverified rank-two solve')
    output = HERE / 'easy_control_panel.jsonl'
    if output.exists():
        raise ValueError('refusing to overwrite control panel')
    output.write_text(''.join(json.dumps(row, separators=(',', ':')) + '\n'
                              for row in selected))
    print([(row['name'], row['nodes_explored']) for row in selected])


if __name__ == '__main__':
    main()
