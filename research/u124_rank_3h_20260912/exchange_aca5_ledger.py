"""Extract the three ordinary donor factors between the two saved aca5 aliases."""
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'rank_unbounded_20260912'))

import rank3_low_length as word_check
import lemma11
import verify


def main():
    source = Path(__file__).with_name('exchange_aca5_worked_path.json')
    data = json.loads(source.read_text())
    short = data['fixed_definition_alias_comparison'][0]['events'][0]
    longer = data['fixed_definition_alias_comparison'][1]['events'][0]
    before = tuple(tuple(w) for w in short['after'])
    expected = tuple(tuple(w) for w in longer['after'])
    helper = short['helpers'][0]
    defining = tuple(short['defining_words'][0])
    donor = (-helper,) + defining
    target = word_check.inverse(tuple(longer['rows'][1]['template']))
    original = before[2]
    assert before[0] == donor

    def expand(word):
        return word_check.free(t for x in word for t in
                               (defining if x == helper else word_check.inverse(defining)
                                if x == -helper else (x,)))

    assert expand(target) == original
    expanded_prefix, factors, derivation = (), [], []
    for position, letter in enumerate(target):
        if abs(letter) == helper:
            left = word_check.free(expanded_prefix + defining) if letter > 0 else expanded_prefix
            sign = -1 if letter > 0 else 1
            right = word_check.free(word_check.inverse(left) + original)
            factors.append({'donor_index': 0, 'sign': sign, 'conjugator': right})
            derivation.append({'position': position, 'letter': letter,
                               'expanded_prefix': expanded_prefix, 'left_conjugator': left,
                               'right_conjugator': right, 'donor_sign': sign})
        expanded_prefix = word_check.free(expanded_prefix + expand((letter,)))
    current, intermediates = original, [original]
    for factor in factors:
        signed = donor if factor['sign'] > 0 else word_check.inverse(donor)
        q = factor['conjugator']
        current = word_check.free(current + word_check.inverse(q) + signed + q)
        intermediates.append(current)
    assert current == target
    raw_after = before[:2] + (target,)
    after, normalization = lemma11.normalize_witness(raw_after)
    assert after == expected
    event = {'kind': 'normal_product_substitution', 'before': before, 'target': 2,
             'factors': factors, 'raw_target_after': target, 'after': after,
             'certificate_kind': 'ordinary_AC_normal_product',
             'defining_donor_retained': donor, 'normalization': normalization}
    assert verify.verify_event(event, known_trivial=True) == after
    record = {'source': source.name, 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'before': before, 'after': after, 'event': event, 'factor_derivation': derivation,
              'target_intermediates': intermediates,
              'frame_alignment': {'original_row': 1, 'both_orientation_signs': -1,
                                  'both_orientation_conjugators': (),
                                  'short_raw_template': short['rows'][1]['template'],
                                  'long_raw_template': longer['rows'][1]['template'],
                                  'initial_canonical_target_is_inverse_short_template': True,
                                  'raw_target_is_inverse_long_template': True},
              'verification': 'independent normal-product dispatcher and separate word routine pass',
              'scope': 'ordinary AC once the defining helper exists; no stable removal lemma used by this bridge'}
    target_path = source.with_name('exchange_aca5_ordinary_ledger.json')
    target_path.write_text(json.dumps(record, indent=2) + '\n')
    print({'factors': factors, 'target_lengths': list(map(len, intermediates)),
           'tuple_lengths': [sum(map(len, before)), sum(map(len, after))]})


if __name__ == '__main__':
    main()
