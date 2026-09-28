"""Evaluate the individual task-allocation environment with the team validator."""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import time

from assignment_env import AssignmentEnv, VALIDATOR_ROOT, demo_tasks, greedy_action, load_tasks
from waam_validator import run_validation

ROOT = Path(__file__).resolve().parent


def evaluate(policy, output, seed=42, scenario=None, tasks=None):
    scenario = Path(scenario) if scenario else VALIDATOR_ROOT / 'examples/sample_job'
    env = AssignmentEnv(scenario, tasks if tasks is not None else demo_tasks())
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    trace = []
    started = time.perf_counter()
    try:
        observation, info = env.reset(seed=seed)
        env.action_space.seed(seed)
        done = False
        while not done:
            action = (greedy_action(env) if policy == 'greedy' else
                      0 if policy == 'single' else
                      env.index % 3 if policy == 'round_robin' else
                      int(env.action_space.sample()))
            observation, reward, terminated, truncated, info = env.step(action)
            trace.append(dict(action=action, robot_id=action+1, reward=reward, **info))
            done = terminated or truncated
        planning_s = time.perf_counter() - started
        record = dict(policy=policy, seed=seed, planning_s=planning_s,
                      observation_size=len(observation), steps=trace,
                      schedule_complete=info['schedule_complete'])
        if info['schedule_complete']:
            job = env.export(output / 'input')
            record['input_sha256'] = {name: hashlib.sha256((job/name).read_bytes()).hexdigest()
                                      for name in ['config.yaml', 'target.stl']}
            result = run_validation(job, output / 'validation')
            record['validation'] = result.summary_dict()
            record['status'] = result.status
            record['makespan_s'] = result.schedule.makespan_s
        else:
            record.update(status='INFEASIBLE', makespan_s=None)
        (output/'experiment.json').write_text(json.dumps(record, ensure_ascii=False, indent=2),
                                               encoding='utf-8')
        print(f'{policy}: {record["status"]}, makespan={record["makespan_s"]}, '
              f'planning={planning_s:.3f}s', flush=True)
        return record
    finally:
        env.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--policy', choices=['all', 'greedy', 'single', 'round_robin', 'random'], default='all')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--scenario', type=Path)
    parser.add_argument('--tasks', type=Path)
    args = parser.parse_args()
    if bool(args.scenario) != bool(args.tasks):
        parser.error('Custom scenarios require BOTH --scenario and --tasks')
    output = args.output or ROOT/'results'/datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    policies = ['single', 'round_robin', 'greedy', 'random'] if args.policy == 'all' else [args.policy]
    for policy in policies:
        evaluate(policy, output/policy, scenario=args.scenario,
                 tasks=load_tasks(args.tasks) if args.tasks else None)


if __name__ == '__main__':
    main()
