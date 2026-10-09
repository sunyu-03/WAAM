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
from algorithm.preprocessing.task_generator import DepositionTask
from algorithm.serial_scheduler import schedule_serial, schedule_layers

def source_hashes():
    paths = list(ROOT.rglob('*.py'))
    backend = ROOT.parent/'TEAM_PROJECT/week1'
    paths.extend(backend.glob('*.py'))
    paths.extend((backend/'environment').rglob('*.py'))
    return {str(path.relative_to(ROOT.parent)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(paths) if not any(part in ('.deps','.venv','tmp','runs','__pycache__') for part in path.parts)}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--job', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--generate-only', action='store_true')
    p.add_argument('--reach-margin-mm', type=float, default=1.0)
    p.add_argument('--scheduler', choices=['serial', 'layer', 'overlap'], default='layer')
    p.add_argument('--tasks-json', type=Path, help='Reuse a saved task list; full official validation still required')
    a = p.parse_args()
    job = a.job.resolve()
    out = a.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    report = dict(seed=42, policy='reach-aware greedy', status='ERROR', ppo='NOT_CONNECTED')
    report['scheduler'] = a.scheduler
    report['source_sha256'] = source_hashes()
    env = None
    try:
        if a.tasks_json:
            task_source = a.tasks_json.resolve()
            data = json.loads(task_source.read_text(encoding='utf-8'))
            records = [DepositionTask(t['task_id'], t['layer'], np.asarray(t['start_xyz_mm'], float),
                                      np.asarray(t['end_xyz_mm'], float)) for t in data]
            layer_metrics = []
            report['task_source'] = dict(path=str(task_source), sha256=hashlib.sha256(task_source.read_bytes()).hexdigest())
        else:
            records, layer_metrics = official_tasks(job/'target.stl', job/'config.yaml', a.reach_margin_mm)
        (out/'tasks.json').write_text(json.dumps([r.to_dict() for r in records], indent=2), encoding='utf-8')
        (out/'precheck.json').write_text(json.dumps(layer_metrics, indent=2), encoding='utf-8')
        report.update(task_count=len(records), reach_margin_mm=a.reach_margin_mm)
        if a.generate_only:
            report['status'] = 'GENERATED_NOT_VALIDATED'
            print(f'Generated {len(records)} tasks; official validation NOT_RUN', flush=True)
            return 0
        env = WAAMBaselineEnv(dict(job_dir=str(job), stl_path=str(job/'target.stl'),
                                   config_path=str(job/'config.yaml'), tasks=[r.to_dict() for r in records],
                                   reach_margin_mm=a.reach_margin_mm))
        trace = []
        if a.scheduler == 'serial':
            trace = schedule_serial(env)
        elif a.scheduler == 'layer':
            trace = schedule_layers(env)
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
    except Exception as exc:
        report['error'] = f'{type(exc).__name__}: {exc}'
        raise
    finally:
        if env is not None:
            env.close()
        report['elapsed_s'] = time.perf_counter()-started
        report['input_sha256'] = {n: hashlib.sha256((job/n).read_bytes()).hexdigest() if (job/n).is_file() else None for n in ('target.stl','config.yaml')}
        commit = subprocess.run(['git', '--work-tree', str(ROOT.parent), '--git-dir', str(ROOT.parent/'.git'), 'rev-parse','HEAD'], capture_output=True, text=True)
        report['source_commit'] = commit.stdout.strip() if commit.returncode == 0 else None
        report['source_changed_during_run'] = report['source_sha256'] != source_hashes()
        report['python'] = sys.version
        report['packages'] = {n: importlib.metadata.version(n) for n in ('numpy','shapely','trimesh','polars','pydantic','PyYAML','gymnasium','scikit-image')}
        (out/'run.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Official validator: {report['status']}")
    return 0 if report['status'] == 'PASS' else 2

if __name__ == '__main__':
    sys.exit(main())
