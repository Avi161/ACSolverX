"""Flatten saved U124 lineages into replayable stable-composite certificates.

This is certificate reconstruction only: no presentation search, template
optimization, Whitehead descent or normal-closure enumeration is invoked.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import verify

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OLD = HERE.parent / 'theory_patterns_20260912'
PRIOR = HERE.parent / 'rank_unbounded_20260912'
OUT = HERE / 'verification/export'
need = verify.require
word, words = verify.word, verify.words
free, inv, image = verify.free, verify.invert, verify.image
decode = verify.parse_saved_strings
LETTERS = {c: i + 1 for i, c in enumerate('xyzuvw')}


def digest(value):
    return hashlib.sha256(value).hexdigest()


def cyclic_frame(value):
    value = free(value)
    left, right = 0, len(value)
    while right - left > 1 and value[left] == -value[right - 1]:
        left += 1
        right -= 1
    return value[left:right], value[:left]


def equivalence_witness(before, after):
    core, prefix = cyclic_frame(before)
    target, frame = cyclic_frame(after)
    if len(core) != len(target):
        return None
    for sign in (1, -1):
        signed = core if sign == 1 else inv(core)
        for cut in range(max(1, len(signed))):
            if signed[cut:] + signed[:cut] == target:
                c = free(prefix + signed[:cut] + inv(frame))
                if free(inv(c) + (before if sign == 1 else inv(before)) + c) == after:
                    return sign, c
    return None


def replay_event(event):
    before, after = words(event['before']), words(event['after'])
    kind = event['kind']
    if kind == 'export_relator_equivalence':
        rows = event['rows']
        need(len(rows) == len(before) == len(after), 'export equivalence row count differs')
        need(sorted(r['input_index'] for r in rows) == list(range(len(before))), 'export equivalence omits or duplicates a row')
        for row, target in zip(rows, after):
            old = before[row['input_index']]
            sign, c = row['sign'], word(row['conjugator'])
            need(type(sign) is int and sign in (-1, 1), 'export equivalence sign invalid')
            need(all(abs(x) in {abs(t) for w in before for t in w} for x in c), 'export equivalence conjugator uses foreign generator')
            need(free(inv(c) + (old if sign == 1 else inv(old)) + c) == target, 'export equivalence identity fails')
    elif kind == 'export_defining_template_composite':
        basis = {abs(x) for w in before for x in w}
        helper, defining = event['helper'], word(event['defining_word'])
        need(type(helper) is int and helper > 0 and helper not in basis, 'export definition helper is not fresh')
        need(free(defining) == defining and all(abs(x) in basis for x in defining), 'export definition uses foreign old generator')
        rows = event['rows']
        need([r['input_index'] for r in rows] == list(range(len(before))), 'export template omits an old row')
        mapping = {g: (g,) for g in basis} | {helper: defining}
        templates = []
        for row, old in zip(rows, before):
            template, c, sign = word(row['template']), word(row['conjugator']), row['sign']
            need(type(sign) is int and sign in (-1, 1), 'export template sign invalid')
            need(all(abs(x) in basis for x in c), 'export template conjugator uses foreign generator')
            need(all(abs(x) in mapping for x in template), 'export template uses undefined helper')
            oriented = free(inv(c) + (old if sign == 1 else inv(old)) + c)
            need(word(row['oriented']) == oriented == image(template, mapping), 'export template exact expansion fails')
            templates.append(template)
        need(after == ((-helper,) + defining,) + tuple(templates), 'export template drops defining or old relator')
        if 'literal_cuts' in event:
            need(len(event['literal_cuts']) == len(before), 'export literal cut count differs')
            for old, template, cut in zip(before, templates, event['literal_cuts']):
                need(type(cut) is int and 0 <= cut < max(1, len(old)), 'export literal cut invalid')
                expanded = tuple(x for token in template for x in (mapping[abs(token)] if token > 0 else inv(mapping[abs(token)])))
                need(expanded == old[cut:] + old[:cut], 'export literal expansion or exact rotation differs')
        need(event['required_hypothesis'] == 'known balanced presentation of the trivial group', 'export definition stable premise missing')
    elif kind == 'export_basis_map_composite':
        forward, backward = verify.basis_images(event['images']), verify.basis_images(event['inverse_images'])
        old_basis = {abs(x) for w in before for x in w}
        new_basis = {abs(x) for w in after for x in w}
        need(set(forward) == old_basis and set(backward) == new_basis and len(before) == len(after), 'export basis map domains differ')
        for g in old_basis:
            need(image(forward[g], backward) == (g,) and image(inv(forward[g]), backward) == (-g,), 'export basis map inverse fails')
        for g in new_basis:
            need(image(backward[g], forward) == (g,), 'export basis map reverse inverse fails')
        need(tuple(image(w, forward) for w in before) == after, 'export basis map does not retain every image')
        need(event['required_hypothesis'] == 'known balanced presentation of the trivial group', 'export basis stable premise missing')
    elif kind == 'export_ordinary_elementary':
        move = event['move']
        target = move['target']
        need(type(target) is int and 0 <= target < len(before), 'export elementary target invalid')
        raw = list(before)
        if move['op'] == 'AC1':
            raw[target] = inv(raw[target])
        elif move['op'] == 'AC2':
            donor = move['donor']
            need(type(donor) is int and 0 <= donor < len(before) and donor != target, 'export elementary donor invalid')
            raw[target] = free(raw[target] + raw[donor])
        elif move['op'] == 'AC3':
            c = word(move['by'])
            need(len(c) == 1 and abs(c[0]) in {abs(x) for w in before for x in w}, 'export elementary conjugator invalid')
            raw[target] = free(inv(c) + raw[target] + c)
        else:
            raise AssertionError('unknown elementary export operation')
        need(tuple(raw) == after, 'export elementary endpoint differs')
    else:
        need(verify.verify_event(event, known_trivial=True) == after, 'saved event replay differs')
    need(all(free(w) == w for w in after), 'export boundary is not freely reduced')
    need(len({abs(x) for w in after for x in w}) == len(after), 'export boundary is not balanced on its occurring generators')
    return after


class Chain:
    def __init__(self, initial):
        self.initial = words(initial)
        self.current = self.initial
        self.events = []
        self.lineage = []

    def add(self, event):
        event = json.loads(json.dumps(event))
        need(words(event['before']) == self.current, 'export event chain is discontinuous')
        self.current = replay_event(event)
        self.events.append(event)

    def equivalent(self, target):
        target = words(target)
        if self.current == target:
            return
        remaining, rows = set(range(len(self.current))), []
        for desired in target:
            match = next(((i, witness) for i in sorted(remaining)
                          if (witness := equivalence_witness(self.current[i], desired)) is not None), None)
            need(match is not None, 'cannot connect exact source boundary by relator equivalence')
            index, (sign, c) = match
            remaining.remove(index)
            rows.append({'input_index': index, 'sign': sign, 'conjugator': c})
        self.add({'kind': 'export_relator_equivalence', 'before': self.current, 'after': target, 'rows': rows})

    def basis(self, forward, backward):
        if all(tuple(w) == (g,) for g, w in forward.items()):
            return
        raw = tuple(image(w, forward) for w in self.current)
        self.add({'kind': 'export_basis_map_composite', 'before': self.current, 'after': raw,
                  'images': forward, 'inverse_images': backward,
                  'required_hypothesis': 'known balanced presentation of the trivial group'})

    def define(self, helper, defining, templates, *, cuts=None):
        mapping = {g: (g,) for g in {abs(x) for w in self.current for x in w}} | {helper: defining}
        rows = []
        for index, (old, template) in enumerate(zip(self.current, templates)):
            oriented = image(template, mapping)
            match = equivalence_witness(old, oriented)
            need(match is not None, 'legacy template expansion is not the claimed old relator')
            sign, c = match
            rows.append({'input_index': index, 'sign': sign, 'conjugator': c, 'oriented': oriented, 'template': template})
        event = {'kind': 'export_defining_template_composite', 'before': self.current,
                 'after': ((-helper,) + defining,) + tuple(templates), 'helper': helper,
                 'defining_word': defining, 'rows': rows,
                 'required_hypothesis': 'known balanced presentation of the trivial group'}
        if cuts is not None:
            event['literal_cuts'] = cuts
        self.add(event)


class Exporter:
    def __init__(self, table_path):
        self.sources, self.cache = {}, {}
        self.table_path = table_path.resolve()
        self.table = self.load(self.table_path)
        self.old_table = self.load(OLD / 'u124_final_table.json')
        self.old_rows = {r['name']: r for r in self.old_table['rows']}
        self.prior_table = self.load(PRIOR / 'all124.json')
        need(self.sources[str((PRIOR / 'all124.json').relative_to(ROOT))]['sha256'] == verify.BASELINE_SHA256, 'pinned phase baseline changed')
        need(self.prior_table['baseline_sha256'] == verify.sha(OLD / 'u124_final_table.json'), 'prior table source hash differs')
        self.prior_rows = {r['name']: r for r in self.prior_table['rows']}
        source = self.old_table['baseline_sources']['best']
        csv_path = ROOT / source['path']
        self.pin(csv_path, source['sha256'])
        with csv_path.open(newline='') as handle:
            entries = list(csv.DictReader(handle))
        self.starts = {r['name']: decode([r['r1'], r['r2']]) for r in entries}
        need(len(entries) == len(self.starts) == 124 and sum(verify.size(w) for w in self.starts.values()) == 2356, 'saved rank2 start denominator/total differs')
        need(set(self.starts) == set(self.old_rows) == set(self.prior_rows) == {r['name'] for r in self.table['rows']}, 'certificate ID sets differ')
        for name, old in self.old_rows.items():
            need(self.starts[name] == decode(old['starting_words']), 'saved rank2 table words differ from pinned CSV')
        self.prior_witnesses = {}
        path = PRIOR / 'shortening_witnesses.jsonl'
        self.pin(path)
        for line in path.read_text().splitlines():
            record = json.loads(line)
            need(record['name'] not in self.prior_witnesses and record['old_table_sha256'] == verify.sha(OLD / 'u124_final_table.json'), 'prior witness duplicate or old-table hash differs')
            self.prior_witnesses[record['name']] = record
        self.baseline = verify.load_baseline()

    def pin(self, path, expected=None):
        path = path.resolve()
        raw = path.read_bytes()
        actual = digest(raw)
        need(expected is None or actual == expected, 'source hash changed: ' + str(path))
        key = str(path.relative_to(ROOT))
        need(key not in self.sources or self.sources[key]['sha256'] == actual, 'source changed during export: ' + key)
        self.sources[key] = {'sha256': actual, 'bytes': len(raw)}
        return raw

    def load(self, path, expected=None):
        path = path.resolve()
        if path not in self.cache:
            self.cache[path] = json.loads(self.pin(path, expected))
        elif expected is not None:
            need(self.sources[str(path.relative_to(ROOT))]['sha256'] == expected, 'cached source expected hash differs')
        return self.cache[path]

    def resolve(self, path, pointer):
        obj = self.load(path)
        for key in pointer.removeprefix('#').strip('/').split('/'):
            if key:
                key = key.replace('~1', '/').replace('~0', '~')
                obj = obj[int(key)] if isinstance(obj, list) else obj[key]
        return obj

    def stamp(self, chain, path, pointer, first):
        chain.lineage.append({'source_file': str(path.resolve().relative_to(ROOT)),
                              'source_sha256': self.sources[str(path.resolve().relative_to(ROOT))]['sha256'],
                              'source_pointer': pointer, 'first_event_index': first,
                              'past_last_event_index': len(chain.events),
                              'boundary_before': chain.initial if first == 0 else chain.events[first - 1]['after'],
                              'boundary_after': chain.current})

    def legacy(self, chain, keeper):
        pointer = keeper['source_certificate_pointer']
        source_name, separator, fragment = pointer.partition('#')
        if source_name.startswith('data/'):
            need(pointer == f'data/ms_unsolved_reps/aca_124_best.csv#name={keeper["name"]}', 'unexpected identity source')
            chain.equivalent(decode(keeper['best_words']))
            return
        witness = keeper['certificate_witness']
        path = OLD / source_name
        need(source_name == witness['source_file'] and '/' + fragment.strip('/') == witness['json_pointer'], 'legacy source witness pointer differs')
        self.load(path, witness['source_sha256'])
        for file_key, hash_key in (('audit_file', 'audit_sha256'), ('auditor_file', 'auditor_sha256')):
            self.pin(OLD / witness[file_key], witness[hash_key])
        self.pin(OLD / witness['proof'])
        record = self.resolve(path, fragment)
        first_event = len(chain.events)
        if source_name == 'stable_dictionary_compression_report.json':
            row_pointer = fragment.rsplit('/best', 1)[0]
            row = self.resolve(path, row_pointer)
            need(row['name'] == keeper['name'], 'literal source row name differs')
            chain.equivalent(decode(row['input']))
            chain.define(3, decode([record['defining_word']])[0], decode(record['compressed_relators']), cuts=record['cuts'])
            chain.equivalent(decode(record['relators']))
        elif source_name == 'primitive_compression_report.json':
            tokens = fragment.strip('/').split('/')
            row = self.resolve(path, '/'.join(tokens[:2]))
            attempt = self.resolve(path, '/'.join(tokens[:4]))
            boundary = int(tokens[5])
            need(row['name'] == keeper['name'] and boundary >= 2, 'primitive source row/boundary differs')
            chain.equivalent(decode(attempt['input']))
            candidate = attempt['candidate']
            templates = [None, None]
            templates[candidate['source']] = decode([candidate['isolator']])[0]
            templates[1 - candidate['source']] = decode([candidate['companion_template']])[0]
            chain.define(3, decode([candidate['defining_word']])[0], templates)
            chain.equivalent(decode(attempt['initial_rank3']))
            if boundary >= 3:
                chain.equivalent(decode(attempt['initial_normalization']['after']))
            position = 3
            for step in attempt['whitehead_steps']:
                if position >= boundary:
                    break
                chain.equivalent(decode(step['before']))
                forward = {LETTERS[g]: decode([w])[0] for g, w in step['images'].items()}
                backward = {LETTERS[g]: decode([w])[0] for g, w in step['inverse_images'].items()}
                chain.basis(forward, backward)
                need(chain.current == decode(step['raw_image']), 'legacy primitive raw image differs')
                position += 1
                if position < boundary:
                    chain.equivalent(decode(step['after']))
                    position += 1
            need(chain.current == decode(record['relators']), 'legacy primitive selected boundary differs')
        elif source_name == 'recursive_stable_compression_report.json':
            need(record['name'] == keeper['name'], 'recursive source row name differs')
            self.legacy(chain, record['source_keeper'])
            chain.equivalent(decode(record['input']))
            for item in record['events']:
                need(item['kind'] == 'compression_round', 'unsupported legacy recursive event requires explicit adapter')
                round_ = record['rounds'][item['index']]
                chain.equivalent(decode(round_['before']))
                best = round_['best']
                if best is None:
                    continue
                chain.define(LETTERS[best['helper']], decode([best['defining_word']])[0], decode(best['compressed_relators']), cuts=best['cuts'])
                chain.equivalent(decode(best['relators']))
            need(not record['singleton_deletions'] and chain.current == decode(record['final_relators']), 'recursive final boundary differs')
        elif source_name == 'stable_rank3_ac_descent_report.json':
            need(record['name'] == keeper['name'], 'ordinary rank3 source row name differs')
            chain.equivalent(decode(record['input']))
            defining = record['source_witness']
            chain.define(3, decode([defining['defining_word']])[0], decode(defining['compressed_relators']), cuts=defining['cuts'])
            chain.equivalent(decode(defining['relators']))
            for original in witness['ordinary_suffix_moves']:
                move = deepcopy(original)
                if move['op'] == 'AC3':
                    move['by'] = decode([move['by']])[0]
                before = chain.current
                raw = list(before)
                i = move['target']
                if move['op'] == 'AC1':
                    raw[i] = inv(raw[i])
                elif move['op'] == 'AC2':
                    raw[i] = free(raw[i] + raw[move['donor']])
                else:
                    raw[i] = free(inv(move['by']) + raw[i] + move['by'])
                chain.add({'kind': 'export_ordinary_elementary', 'before': before, 'after': tuple(raw), 'move': move})
            need(chain.current == decode(record['result']['endpoint']), 'ordinary rank3 suffix endpoint differs')
        else:
            raise AssertionError('unhandled legacy source: ' + source_name)
        chain.equivalent(decode(keeper['best_words']))
        self.stamp(chain, path, fragment, first_event)

    def prior(self, chain, name):
        prior = self.prior_rows[name]
        if name not in self.prior_witnesses:
            self.legacy(chain, self.old_rows[name])
        else:
            saved = self.prior_witnesses[name]
            witness = saved['witness']
            expected_pointer = self.old_rows[name]['source_certificate_pointer'] if witness['source'] == 'saved_best' else self.old_rows[name]['best_rank2_source_certificate_pointer']
            need(saved['source_pointer'] == expected_pointer, 'prior source pointer is stale')
            if witness['source'] == 'saved_best':
                self.legacy(chain, self.old_rows[name])
            else:
                need(witness['source'] == 'saved_rank2', 'unknown prior witness source')
            forward = {LETTERS[c]: (g,) for c, g in saved['input_letter_map'].items()}
            backward = {g: (LETTERS[c],) for c, g in saved['input_letter_map'].items()}
            chain.basis(forward, backward)
            chain.equivalent(words(witness['initial']))
            first = len(chain.events)
            for event in witness['events']:
                chain.add(event)
            need(chain.current == words(witness['endpoint']), 'prior witness endpoint differs')
            pointer_file, _, pointer = prior['witness_pointer'].partition('#')
            path = PRIOR / pointer_file
            original = self.resolve(path, pointer)
            need(original == witness, 'prior exported witness differs from actual table pointer')
            self.stamp(chain, path, pointer, first)
        chain.equivalent(self.baseline[name]['words'])
        need(verify.size(chain.current) == prior['best_any_rank_length'], 'prior total differs')

    def export_row(self, row):
        name = row['name']
        chain = Chain(self.starts[name])
        source_file = (HERE / row['witness_file']).resolve()
        if source_file == (PRIOR / 'all124.json').resolve():
            self.prior(chain, name)
        else:
            need(row['witness_file'] in self.table['inputs'], 'current witness file is absent from input manifest')
            self.load(source_file, self.table['inputs'][row['witness_file']])
            source = self.resolve(source_file, row['witness_pointer'])
            need(source['name'] == name, 'current pointer selects another presentation')
            verify.verify_record(source, self.baseline)
            source_key = source['source_key']
            if source_key == 'current_best':
                self.prior(chain, name)
            elif source_key == 'previous_best':
                self.legacy(chain, self.old_rows[name])
            else:
                need(source_key == 'saved_rank2', 'unknown current witness source')
            chain.equivalent(words(source['initial']))
            first = len(chain.events)
            count = row['witness_prefix_events']
            need(type(count) is int and 0 <= count <= len(source['events']), 'current witness prefix count invalid')
            for event in source['events'][:count]:
                chain.add(event)
            self.stamp(chain, source_file, row['witness_pointer'], first)
        chain.equivalent(words(row['words']))
        need(verify.size(chain.current) == row['best_length'] and len(chain.current) == row['best_rank'], 'current export words/length/rank differ')
        boundaries = [{'event_count': 0, 'rank': len(chain.initial), 'length': verify.size(chain.initial)}]
        boundaries += [{'event_count': i + 1, 'rank': len(e['after']), 'length': verify.size(e['after'])} for i, e in enumerate(chain.events)]
        record = {'schema': 'u124_flat_stable_composite_v1', 'name': name,
                  'initial': chain.initial, 'initial_length': verify.size(chain.initial),
                  'initial_source': {'file': 'data/ms_unsolved_reps/aca_124_best.csv',
                                     'sha256': self.old_table['baseline_sources']['best']['sha256'], 'selector': 'name=' + name},
                  'known_triviality_premise': 'This exact saved Miller-Schupp presentation is known to present the trivial group by its preserved input lineage. Triviality is not inferred from determinant.',
                  'events': chain.events, 'endpoint': chain.current, 'endpoint_length': row['best_length'],
                  'endpoint_rank': row['best_rank'], 'length_gain': verify.size(chain.initial) - row['best_length'],
                  'lineage_segments': chain.lineage, 'boundaries': boundaries,
                  'flat_at_stable_composite_level': True, 'unresolved_lineage_segments': 0,
                  'fully_expanded_elementary_stable_AC': False,
                  'search_work_performed_by_exporter': 0,
                  'scope': 'All relators are retained and counted at every stored boundary. Defining additions/removals and ambient maps are theorem-backed stable composites; their normal-closure elementary expansions are not emitted.'}
        replay_record(json.loads(json.dumps(record)))
        return record


def replay_record(record):
    current = words(record['initial'])
    need(len(current) == 2 and verify.size(current) == record['initial_length'], 'export start is not the stated rank2 tuple')
    for event in record['events']:
        need(words(event['before']) == current, 'flat export chain discontinuity')
        current = replay_event(event)
    need(current == words(record['endpoint']) and len(current) == record['endpoint_rank'] and verify.size(current) == record['endpoint_length'], 'flat export endpoint differs')
    need(record['length_gain'] == record['initial_length'] - record['endpoint_length'], 'flat export gain differs')
    expected = [{'event_count': 0, 'rank': 2, 'length': verify.size(record['initial'])}]
    expected += [{'event_count': i + 1, 'rank': len(e['after']), 'length': verify.size(e['after'])} for i, e in enumerate(record['events'])]
    need(record['boundaries'] == expected, 'flat export boundary accounting differs')
    return current


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--table', type=Path, default=HERE / 'CURRENT.json')
    parser.add_argument('--check', action='store_true', help='Replay emitted certificates without reconstructing source lineages.')
    args = parser.parse_args()
    output_path = OUT / 'all124_stable_composite.jsonl'
    manifest_path = OUT / 'manifest.json'
    if args.check:
        rows = [json.loads(line) for line in output_path.read_text().splitlines()]
        manifest = json.loads(manifest_path.read_text())
        need(verify.sha(output_path) == manifest['certificate_sha256'], 'export JSONL hash differs')
        for row in rows:
            replay_record(row)
        need(len(rows) == len({r['name'] for r in rows}) == 124, 'export ID count differs')
        print(json.dumps({'status': 'PASS', 'rows': len(rows), 'initial_total': sum(r['initial_length'] for r in rows), 'endpoint_total': sum(r['endpoint_length'] for r in rows)}, indent=2))
        return
    exporter = Exporter(args.table)
    rows = []
    for row in exporter.table['rows']:
        try:
            rows.append(exporter.export_row(row))
        except Exception as exc:
            raise AssertionError(f'{row["name"]}: {exc}') from exc
    need(sum(r['endpoint_length'] for r in rows) == exporter.table['summary']['best_total'], 'full export total differs from current table')
    OUT.mkdir(parents=True, exist_ok=True)
    current_raw = args.table.read_bytes()
    snapshot_name = 'current_' + digest(current_raw)[:16] + '.json'
    need(digest(current_raw) == exporter.sources[str(args.table.resolve().relative_to(ROOT))]['sha256'], 'CURRENT changed during export; rerun against the new snapshot')
    (OUT / snapshot_name).write_bytes(current_raw)
    partial = output_path.with_suffix('.jsonl.partial')
    partial.write_text(''.join(json.dumps(row, separators=(',', ':')) + '\n' for row in rows))
    reread = [json.loads(line) for line in partial.read_text().splitlines()]
    for row in reread:
        replay_record(row)
    need([r['name'] for r in reread] == [r['name'] for r in rows], 'export readback ID order differs')
    partial.replace(output_path)
    for source in (Path(__file__), HERE / 'verify.py', PRIOR / 'audit.py', OLD / 'STABLE_CERTIFICATE_CONVENTIONS.md'):
        exporter.pin(source)
    summary = {'status': 'PASS', 'rows': len(rows), 'saved_rank2_total': sum(r['initial_length'] for r in rows),
               'endpoint_total': sum(r['endpoint_length'] for r in rows),
               'endpoint_rank_counts': dict(Counter(str(r['endpoint_rank']) for r in rows)),
               'strictly_shortened_rows': sum(r['length_gain'] > 0 for r in rows),
               'flat_composite_events': sum(len(r['events']) for r in rows),
               'event_kinds': dict(Counter(e['kind'] for r in rows for e in r['events'])),
               'maximum_certified_rank': max(b['rank'] for r in rows for b in r['boundaries']),
               'unresolved_lineage_segments': 0, 'fully_expanded_elementary_stable_AC': False,
               'current_snapshot': snapshot_name, 'current_snapshot_sha256': digest(current_raw),
               'certificate_file': output_path.name, 'certificate_sha256': verify.sha(output_path),
               'sources': exporter.sources,
               'replay_command': 'python research/u124_rank_3h_20260912/export_paths.py --check',
               'searches_performed': 0}
    manifest_path.write_text(json.dumps(summary, indent=2) + '\n')
    (HERE / 'verification_full_export.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({k: v for k, v in summary.items() if k != 'sources'}, indent=2))


if __name__ == '__main__':
    main()
