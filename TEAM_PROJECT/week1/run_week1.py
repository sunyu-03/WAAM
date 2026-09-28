"""Generate trajectories through reset/step and evaluate with run_validation."""
from __future__ import annotations

import argparse
import csv
from datetime import datetime
import hashlib
import json
from pathlib import Path
import shutil
import time

from week1_env import Week1Env
from waam_validator import run_validation

ROOT = Path(__file__).resolve().parent


def demo_episode(case='pass'):
    env = Week1Env(max_steps=8)
    trace = []
    try:
        env.reset(seed=42)

        def act(targets, modes):
            _, reward, terminated, truncated, info = env.step(
                env.action_from_targets(targets, modes)
            )
            trace.append(dict(step=len(trace)+1, reward=reward,
                              terminated=terminated, truncated=truncated, **info))

        targets = env.state[:, 1:4].copy()
        if case == 'collision':
            targets[:] = [0, 0, 2]
            act(targets, ['T'] * 3)
        else:
            targets[0] = [-40, 0, 2]
            act(targets, ['T', 'F', 'F'])
            targets[0] = [40 if case == 'pass' else 0, 0, 2]
            act(targets, ['D', 'F', 'F'])
        act(env.state[:, 1:4], ['F'] * 3)
        return env.get_trajectory(), trace, env.job_dir
    finally:
        env.close()


def evaluate(case, output):
    """Keep scenario files intact; reject overwriting previous evidence."""
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    job = output / 'input'
    job.mkdir()
    started = time.perf_counter()
    trajectory, trace, source = demo_episode(case)
    hashes = {}
    for name in ('config.yaml', 'target.stl'):
        shutil.copy2(source / name, job / name)
        hashes[name] = hashlib.sha256((job / name).read_bytes()).hexdigest()
    with (job / 'trajectory.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.writer(stream)
        writer.writerow(trajectory)
        writer.writerows(zip(*trajectory.values(), strict=True))
    result = run_validation(job, output / 'validation')
    summary = result.summary_dict()
    record = dict(case=case, expected_status='PASS' if case == 'pass' else 'FAIL',
                  actual_status=result.status, elapsed_s=time.perf_counter()-started,
                  input_sha256=hashes, steps=trace, validation=summary)
    (output / 'experiment.json').write_text(
        json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8'
    )
    print(f'{case}: {result.status}; makespan={result.schedule.makespan_s:.6f}s; '
          f'collision_events={len(result.collision.events)}; output={output}')
    if result.status != record['expected_status']:
        raise RuntimeError(f'Unexpected status: {record["actual_status"]}')
    if case == 'collision' and result.collision_free:
        raise RuntimeError('Collision negative control did not detect a collision')
    if case == 'missing' and result.shape.passed:
        raise RuntimeError('Incomplete deposition unexpectedly passed shape validation')
    if case == 'pass' and (result.warnings or result.violations):
        raise RuntimeError('Positive control produced warnings or violations')
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', choices=['all', 'pass', 'collision', 'missing'], default='all')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    output = args.output or ROOT / 'results' / datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    cases = ['pass', 'collision', 'missing'] if args.case == 'all' else [args.case]
    for case in cases:
        evaluate(case, output / case)


if __name__ == '__main__':
    main()
