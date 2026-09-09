"""Resumable serial census evaluation with a fixed 1,000-unit search policy."""
import argparse
import csv
import gc
import hashlib
import json
import os
from pathlib import Path
import time

for variable in ('NUMBA_NUM_THREADS', 'OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
    os.environ[variable] = '1'
from research.supermoves_20260908.final_policy import search
from research.supermoves_20260908.certificate_decoder_compact_moves import decode_elementary
from research.supermoves_20260908.certificate_decoder import replay_elementary
from research.supermoves_20260908.certificate_words_numba import canon_rel
from research.supermoves_20260908.cheap_gates import _bs_patterns_for_length

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT_SHA = '7e220253bd0d950378d6ca6944be46ff4b77e49f30067b9ff6c6c6da82f64ae2'
POPULATION = 72779


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--offset', type=int, default=0)
    parser.add_argument('--limit', type=int, default=POPULATION)
    parser.add_argument('--cpu-slice', type=float, default=2.)
    parser.add_argument('--cooldown', type=float, default=6.)
    parser.add_argument('--shard-size', type=int, default=1000)
    args = parser.parse_args()
    if args.offset < 0 or args.limit < 1 or args.shard_size < 1 or not 0 < args.cpu_slice < float('inf') or not 0 <= args.cooldown < float('inf'):
        raise ValueError('invalid batch parameters')
    data = args.input.read_bytes()
    if hashlib.sha256(data).hexdigest() != INPUT_SHA:
        raise ValueError('unexpected census input hash')
    rows = list(csv.DictReader(data.decode().splitlines()))
    if len(rows) != POPULATION or any(row['name'] != f'ac19_{i}' for i, row in enumerate(rows)):
        raise ValueError('census must contain all72779 sequential unique IDs')
    args.out.mkdir(parents=True, exist_ok=True)
    source_manifest = json.loads((HERE / 'FINAL_PORTABILITY_CHECK.json').read_text())['source_sha256']
    for name, digest in source_manifest.items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest:
            raise ValueError('frozen source changed: ' + name)
    source_manifest[str(Path(__file__).relative_to(ROOT))] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    end = min(POPULATION, args.offset + args.limit)
    manifest = dict(input=str(args.input.resolve()), input_sha256=INPUT_SHA, population=POPULATION,
                    offset=args.offset, end=end, budget=1000, cap=None, threads=1,
                    cpu_slice=args.cpu_slice, cooldown=args.cooldown,
                    source_sha256=source_manifest,
                    certificate='Every solve compact-decoded and independently replayed; mixed path retained, expanded move arrays discarded.',
                    scope='Fixed donor250 / plainS20-prefix872 / incumbent remainder. Shared heterogeneous work units, not calibrated CPU-equivalent nodes.')
    manifest_path = args.out / f'manifest_{args.offset:05d}_{end:05d}.json'
    if manifest_path.exists():
        raise ValueError('this interval already has a manifest')
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    warm = time.perf_counter()
    search(('xyX', 'yyx'), budget=5)
    canon_rel('xy' * 40)
    warmup = time.perf_counter() - warm
    totals = dict(rows=0, solved=0, verified=0, errors=0, nodes=0, search_wall=0., search_cpu=0.,
                  certificate_wall=0., certificate_cpu=0., elementary_moves=0, cooldown_wall=0.)
    started = time.perf_counter()
    slice_cpu = time.process_time()
    position = args.offset
    while position < end:
        stop = min(end, position + args.shard_size)
        output = args.out / f'rows_{position:05d}_{stop:05d}.jsonl'
        partial = output.with_suffix('.jsonl.partial')
        if output.exists() or partial.exists():
            raise ValueError('refuse overwrite: ' + str(output))
        with partial.open('x') as stream:
            while position < stop:
                row = rows[position]
                pair = [row['r1'], row['r2']]
                record = dict(index=position, name=row['name'], pair=pair, budget=1000)
                wall, cpu = time.perf_counter(), time.process_time()
                try:
                    result = search(pair, budget=1000)
                    record.update(search_wall=time.perf_counter()-wall, search_cpu=time.process_time()-cpu,
                                  solved=bool(result['solved']), nodes_explored=result['nodes_explored'],
                                  route=result['policy_route'], best_state=result.get('best_state'),
                                  prepass_charges=result['prepass_charges'], plain_charges=result['plain_charges'])
                    if not 0 <= record['nodes_explored'] <= 1000:
                        raise ValueError('shared budget exceeded')
                    if result['solved']:
                        wall, cpu = time.perf_counter(), time.process_time()
                        moves = decode_elementary(pair, result['states'], result['steps'], result.get('elementary_tail'))
                        if replay_elementary(pair, moves) != ['x', 'y']:
                            raise ValueError('independent elementary replay failed')
                        record.update(certificate_wall=time.perf_counter()-wall,
                                      certificate_cpu=time.process_time()-cpu, elementary_verified=True,
                                      elementary_count=len(moves), states=result['states'], steps=result['steps'])
                        if 'elementary_tail' in result:
                            record['elementary_tail'] = result['elementary_tail']
                        del moves
                    del result
                except Exception as error:
                    record.update(solved=False, error_type=type(error).__name__, error=str(error),
                                  error_wall=time.perf_counter()-wall, error_cpu=time.process_time()-cpu)
                stream.write(json.dumps(record, separators=(',', ':')) + '\n')
                stream.flush()
                totals['rows'] += 1
                totals['solved'] += record['solved']
                totals['verified'] += bool(record.get('elementary_verified'))
                totals['errors'] += 'error' in record
                totals['nodes'] += record.get('nodes_explored', 0)
                totals['elementary_moves'] += record.get('elementary_count', 0)
                for key in ('search_wall', 'search_cpu', 'certificate_wall', 'certificate_cpu'):
                    totals[key] += record.get(key, 0.)
                position += 1
                if time.process_time() - slice_cpu >= args.cpu_slice:
                    before = time.perf_counter()
                    time.sleep(args.cooldown)
                    totals['cooldown_wall'] += time.perf_counter()-before
                    slice_cpu = time.process_time()
                if position % 250 == 0 or position == end:
                    print(json.dumps(dict(totals, next_offset=position,
                                          elapsed=time.perf_counter()-started)), flush=True)
        partial.replace(output)
        _bs_patterns_for_length.cache_clear()
        gc.collect()
        checkpoint = dict(totals, next_offset=position, warmup_wall=warmup,
                          elapsed=time.perf_counter()-started, manifest=manifest_path.name)
        output.with_suffix('.summary.json').write_text(json.dumps(checkpoint, indent=2) + '\n')
    print(json.dumps(dict(totals, next_offset=position, warmup_wall=warmup,
                          elapsed=time.perf_counter()-started, complete_interval=True)), flush=True)


if __name__ == '__main__':
    main()
