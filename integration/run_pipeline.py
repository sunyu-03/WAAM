"""STL/config -> generated tasks -> reach-aware greedy -> bundled validator."""
from __future__ import annotations
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / '.deps'))
sys.path.insert(0, str(ROOT.parent / 'TEAM_PROJECT' / 'week1'))
from assignment_env import AssignmentEnv, Task
from algorithm.environment.waam_env import WAAMBaselineEnv
from waam_validator import run_validation
from waam_validator.config.loader import load_config
from waam_validator.shape.target import load_target_mesh, determine_evaluation_layers, slice_target_layers
import numpy as np
from shapely import LineString, MultiLineString, line_merge, get_parts

from algorithm.preprocessing.task_generator import generate_scenario_tasks as official_tasks, merge_collinear

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--job', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    job = a.job.resolve()
    out = a.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    report = dict(seed=42, policy='reach-aware greedy', status='ERROR', ppo='NOT_CONNECTED')
    try:
        records, layer_metrics = official_tasks(job/'target.stl', job/'config.yaml')
        (out/'tasks.json').write_text(json.dumps([r.to_dict() for r in records], indent=2), encoding='utf-8')
        (out/'precheck.json').write_text(json.dumps(layer_metrics, indent=2), encoding='utf-8')
        env = WAAMBaselineEnv(dict(job_dir=str(job), stl_path=str(job/'target.stl'),
                                   config_path=str(job/'config.yaml'), tasks=[r.to_dict() for r in records]))
        trace = []
        while not env.done:
            choices = []
            for robot in range(3):
                rows, reason, departure = env.candidate(robot)
                if rows is not None:
                    choices.append((max(s[-1][0] for s in rows), robot, rows, departure))
            if not choices:
                raise RuntimeError(f'No feasible robot for task {env.index}')
            _, robot, _, _ = min(choices, key=lambda x: (x[0], x[1]))
            _, _, _, _, info = env.step(robot)
            trace.append(dict(task=env.index-1, robot_id=robot+1, makespan_s=env.makespan))
            print(f'Task {env.index}/{len(records)} makespan={env.makespan:.3f}', flush=True)
        exported = env.export(out/'job')
        result = run_validation(exported, out/'validation')
        report.update(status=result.status, makespan_s=result.schedule.makespan_s,
                      validation=result.summary_dict(), task_count=len(records), trace=trace)
        env.close()
    except Exception as exc:
        report['error'] = f'{type(exc).__name__}: {exc}'
        raise
    finally:
        report['elapsed_s'] = time.perf_counter()-started
        report['input_sha256'] = {n: hashlib.sha256((job/n).read_bytes()).hexdigest() for n in ('target.stl','config.yaml')}
        report['source_commit'] = subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()
        report['source_sha256'] = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                                  for path in sorted(ROOT.rglob('*.py'))
                                  if '.deps' not in path.parts and 'tmp' not in path.parts and 'runs' not in path.parts}
        report['python'] = sys.version
        report['packages'] = {n: importlib.metadata.version(n) for n in ('numpy','shapely','trimesh','polars','pydantic','PyYAML','gymnasium','scikit-image')}
        (out/'run.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Official validator: {report['status']}")
    return 0 if report['status'] == 'PASS' else 2

if __name__ == '__main__':
    sys.exit(main())
