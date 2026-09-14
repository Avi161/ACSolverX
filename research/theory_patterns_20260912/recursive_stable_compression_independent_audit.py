"""Independent exact-prefix audit; does not import the compression author modules."""
from copy import deepcopy
from functools import lru_cache
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
REPORT = HERE/'recursive_stable_compression_report.json'
EXPECTED_REPORT = '3e6a3d89e652b292051e58cd297abcbf8d29b9bfcceff166d72c8aadc9de0ce2'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inverse(word):
    return word.swapcase()[::-1]


def reduce_word(word):
    require(isinstance(word,str), 'nonword')
    stack = []
    for c in word:
        require(c in 'xXyYzZuUvVwW', 'alphabet')
        if stack and stack[-1] == c.swapcase():
            stack.pop()
        else:
            stack.append(c)
    return ''.join(stack)


def boundary(label, words, basis):
    require(len(set(basis)) == len(basis) == len(words), 'rank or repeated basis')
    require(all(g in 'xyzuvw' for g in basis), 'invalid basis')
    require(all(reduce_word(w) == w and all(c.lower() in basis for c in w) for w in words), 'invalid boundary words')
    return {'label':label,'basis':list(basis),'rank':len(basis),'relators':list(words),
            'relator_lengths':list(map(len,words)),'total_length':sum(map(len,words))}


@lru_cache(None)
def checker(filename):
    spec = importlib.util.spec_from_file_location('_independent_seed_'+Path(filename).stem,HERE/filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def resolve(value, pointer):
    for part in pointer.strip('/').split('/'):
        value = value[int(part)] if isinstance(value,list) else value[part]
    return value


def verify_source(record):
    if 'source_keeper' in record:
        row = record['source_keeper']
        witness = row['certificate_witness']
    else:
        row = None
        witness = record['source_prefix']
    for f,h in [('audit_file','audit_sha256'),('source_file','source_sha256'),('auditor_file','auditor_sha256')]:
        require(sha(HERE/witness[f]) == witness[h], 'changed seed provenance '+f)
    source = json.loads((HERE/witness['source_file']).read_text())
    module = checker(witness['auditor_file'])
    if row is None:
        checked = module.verify_prefix(resolve(source,witness['json_pointer']))
        words = checked['endpoint']
        require(checked['endpoint_total_length'] == sum(map(len,words)), 'continuation source endpoint length')
    elif witness['source_file'] == 'primitive_compression_report.json':
        parts = witness['json_pointer'].strip('/').split('/')
        attempt = source['rows'][int(parts[1])]['attempts'][int(parts[3])]
        require(attempt['input'] == row['starting_words'], 'primitive initial source')
        checked = module.verify_prefix(attempt,witness['boundary_index'])
        words = checked['relators']
    elif witness['source_file'] == 'stable_dictionary_compression_report.json':
        checked = module.verify_prefix(row['starting_words'],resolve(source,witness['json_pointer']))
        words = checked['relators']
    else:
        raise ValueError('unsupported source family')
    require(record['input'] == words, 'seed input mismatch')
    if row is not None:
        require(row['best_words'] == words and row['best_any_rank_length'] == sum(map(len,words)), 'keeper source mismatch')
    return witness


def verify_prefix(record):
    verify_source(record)
    current,basis = list(record['input']),list(record['input_basis'])
    boundaries = [boundary('audited_seed',current,basis)]
    require(record['input_rank'] == len(basis), 'input rank')
    require(not record['singleton_deletions'], 'this audit accepts no unreviewed deletion path')
    require(record['ordinary_suffix_moves'] == 0, 'unexpected ordinary suffix')
    require(record['events'] == [{'kind':'compression_round','index':i} for i in range(len(record['rounds']))], 'event sequence')
    charged = 0
    for stage in record['rounds']:
        require(stage['before'] == current and stage['basis_before'] == basis, 'round source')
        used,generated = stage['defining_word_candidates'],stage['definitions_generated']
        require(type(used) is int and type(generated) is int and 0 <= used <= generated, 'candidate accounting')
        require(stage['definition_screen_complete'] == (used == generated), 'completeness flag')
        charged += used
        w = stage['best']
        if w is None:
            continue
        helper,definition = w['helper'],w['defining_word']
        require(helper in 'xyzuvw' and len(helper) == 1 and helper not in basis, 'helper not fresh')
        require(len(definition) >= 2 and reduce_word(definition) == definition and all(c.lower() in basis for c in definition), 'invalid old-word definition')
        require(w['basis_before'] == basis and w['basis_after'] == basis+[helper], 'basis extension')
        require(len(w['cuts']) == len(w['compressed_relators']) == len(w['rotation_conjugators']) == len(current), 'missing relator')
        oriented,tokens = [],[]
        for original,cut,conjugator,template in zip(current,w['cuts'],w['rotation_conjugators'],w['compressed_relators']):
            require(type(cut) is int and 0 <= cut < max(1,len(original)), 'invalid cut')
            require(conjugator == original[:cut], 'cyclic conjugator')
            rotated = original[cut:]+original[:cut]
            require(reduce_word(inverse(conjugator)+original+conjugator) == rotated, 'rotation replay')
            expanded = ''.join(definition if c == helper else inverse(definition) if c == helper.upper() else c for c in template)
            require(expanded == rotated, 'literal expansion')
            oriented.append(rotated)
            tokens.append(sum(c.lower() == helper for c in template))
        old_total = sum(map(len,current))
        next_basis = basis+[helper]
        added = [helper.upper()+definition,*oriented]
        current = [helper.upper()+definition,*w['compressed_relators']]
        total = sum(map(len,current))
        require(w['relators'] == current and w['rank'] == len(current), 'complete retained tuple')
        require(w['input_total_length'] == old_total, 'compression input length')
        require(w['total_length'] == w['formula_length'] == total < old_total, 'strict all-relator gain')
        require(w['token_counts'] == tokens and total == old_total+len(definition)+1-sum(tokens)*(len(definition)-1), 'token formula')
        boundaries += [boundary('cyclic_orientations',oriented,basis),boundary('defining_relator_added',added,next_basis),boundary('literal_compression',current,next_basis)]
        basis = next_basis
    require(record['boundaries'] == boundaries, 'saved boundary mismatch')
    require(record['final_relators'] == current and record['final_basis'] == basis and record['final_rank'] == len(basis), 'final tuple')
    require(record['input_length'] == sum(map(len,record['input'])) and record['final_length'] == sum(map(len,current)), 'endpoint lengths')
    gain = record['input_length']-record['final_length']
    require(record['additional_length_gain'] == gain and record['strict_gain_from_audited_seed'] == (gain>0), 'gain metadata')
    require(charged == record['defining_word_candidates'] <= record['candidate_limit'] <= 1000, 'candidate cap')
    require(len(basis) <= record['rank_limit'] <= 6 and record['solved'] is False, 'rank or solve claim')
    best = min(boundaries,key=lambda b:b['total_length'])
    return {**best,'independently_verified':True,'certificate_kind':'independently_verified_theorem_backed_recursive_stable_prefix',
            'expanded_normal_products':False,'source_provenance_verified':True}


def main():
    require(sha(REPORT) == EXPECTED_REPORT, 'report is not frozen audited snapshot')
    report = json.loads(REPORT.read_text())
    for name,key in [('recursive_stable_compression.py','module_sha256'),('recursive_stable_compression_checks.py','checks_sha256'),('STABLE_CERTIFICATE_CONVENTIONS.md','conventions_sha256')]:
        require(sha(HERE/name) == report[key], 'author source hash')
    require(hashlib.sha256(report['source_table_text'].encode()).hexdigest() == report['source_table_sha256'], 'embedded source table hash')
    table = json.loads(report['source_table_text'])
    keepers = {r['name']:r for r in table['rows'] if r['gain_this_session'] > 0}
    require(len(keepers) == 85 and set(keepers) == {r['name'] for r in report['records']}, 'source cohort')
    rows = []
    for i,record in enumerate(report['records']):
        require(record['source_keeper'] == keepers[record['name']] and record['source_table_sha256'] == report['source_table_sha256'], 'exact source keeper')
        checked = verify_prefix(record)
        rows.append({'name':record['name'],'source_record_index':i,'json_pointer':f'/records/{i}',
                     'minimum_relators':checked['relators'],'minimum_rank':checked['rank'],
                     'minimum_total_length':checked['total_length'],'input_total_length':record['input_length'],
                     'additional_gain':record['input_length']-checked['total_length'],
                     'source_provenance_verified':True})
    continuation = [verify_prefix(r) for r in report['continuations']]
    gains = [r for r in rows if r['additional_gain']]
    require(len(gains) == 6 and all(r['additional_gain'] == 1 and r['minimum_rank'] == 4 for r in gains), 'expected six rank4 gains')
    require(sum(r['defining_word_candidates'] for r in report['records']) == 9144, 'base charges')
    require(sum(r['defining_word_candidates'] for r in report['records']+report['continuations']) == 9201, 'combined charges')
    require(report['continuations'][0]['defining_word_candidates'] == 57 and report['continuations'][0]['input_length'] == 15, 'continuation accounting')
    sample = next(r for r in report['records'] if r['additional_length_gain'])
    rejected = []
    for kind in ('fresh_helper','compressed_word','cut','definition_retention','boundary_length','final_rank','provenance'):
        bad = deepcopy(sample)
        w = next(s['best'] for s in bad['rounds'] if s['best'])
        if kind == 'fresh_helper':w['helper']='x'
        elif kind == 'compressed_word':w['compressed_relators'][0]+='x'
        elif kind == 'cut':w['cuts'][0]=-1
        elif kind == 'definition_retention':w['relators'].pop(0)
        elif kind == 'boundary_length':bad['boundaries'][-1]['total_length']-=1
        elif kind == 'final_rank':bad['final_rank']-=1
        else:bad['source_keeper']['certificate_witness']['source_sha256']='0'*64
        try:verify_prefix(bad)
        except ValueError:rejected.append(kind)
        else:raise AssertionError('corruption accepted '+kind)
    out = {'status':'pass','source_report_sha256':sha(REPORT),'audit_script_sha256':sha(Path(__file__)),
           'source_table_sha256':report['source_table_sha256'],'rows':rows,'continuations_checked':len(continuation),
           'additional_gain_ids':[r['name'] for r in gains],'additional_total_reduction':sum(r['additional_gain'] for r in rows),
           'all_recursive_candidates':9201,'corruptions_rejected':rejected,
           'scope':'All85 prefixes and exact seed provenance replayed; six rank4 gains admitted as theorem-backed stable prefixes. Candidate completeness/optimality and normal-product expansion are not independently certified.'}
    (HERE/'recursive_stable_compression_independent_audit.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='rows'},indent=2))


if __name__ == '__main__':
    main()
