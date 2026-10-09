"""Train new MaskablePPO checkpoints with an explicit, fixed WAAM contract."""
from __future__ import annotations
import argparse
import hashlib
import importlib.metadata
import json
import random
import sys
import time
from pathlib import Path

from run_pipeline import ROOT, Task, official_tasks, source_hashes, run_validation
from algorithm.environment.ppo_env import CONTRACT, SerialPPOEnv
import numpy as np

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')

def task_records(tasks):
    return [dict(task_id=i, layer=t.start[2], start_xyz_mm=list(t.start), end_xyz_mm=list(t.end))
            for i, t in enumerate(tasks)]

def signatures(job, tasks, margin):
    return dict(contract=CONTRACT, reach_margin_mm=margin,
                input_sha256={n:digest(job/n) for n in ('config.yaml','target.stl')},
                tasks_sha256=hashlib.sha256(json.dumps(task_records(tasks),sort_keys=True).encode()).hexdigest())

def check_resume(checkpoint, signature):
    manifest = checkpoint.with_suffix('.json')
    if not manifest.is_file():
        raise ValueError('Checkpoint has no waam-serial-masked-v1 manifest. Preserved 13-feature legacy checkpoints are incompatible.')
    data = json.loads(manifest.read_text(encoding='utf-8'))
    if data.get('signature') != signature:
        raise ValueError('Checkpoint contract, task list, inputs, or reach margin differs; refusing incompatible resume')
    if data.get('checkpoint_sha256') != digest(checkpoint):
        raise ValueError('Checkpoint SHA256 does not match its manifest')
    if digest(checkpoint.with_suffix('.rng.json')) != data.get('rng_sha256'):
        raise ValueError('Checkpoint RNG sidecar SHA256 mismatch')
    return data

def save_checkpoint(model, checkpoint, signature, lineage):
    import torch
    model.save(checkpoint)
    state = np.random.get_state()
    rng = dict(python=random.getstate(), numpy=[state[0],state[1].tolist(),state[2],state[3],state[4]],
               torch=torch.get_rng_state().tolist())
    rng_path = checkpoint.with_suffix('.rng.json')
    write_json(rng_path, rng)
    write_json(checkpoint.with_suffix('.json'), dict(signature=signature, lineage=lineage,
               checkpoint_sha256=digest(checkpoint), rng_sha256=digest(rng_path),
               total_timesteps=model.num_timesteps,
               resume_semantics='Policy, optimizer, timestep counter and global RNG restored; environment resets at a new rollout. Not bitwise mid-rollout continuation.'))

def restore_rng(checkpoint):
    import torch
    rng = json.loads(checkpoint.with_suffix('.rng.json').read_text())
    def tuples(value):
        return tuple(tuples(x) for x in value) if isinstance(value,list) else value
    random.setstate(tuples(rng['python']))
    state = rng['numpy']
    np.random.set_state((state[0],np.asarray(state[1],dtype=np.uint32),state[2],state[3],state[4]))
    torch.set_rng_state(torch.tensor(rng['torch'],dtype=torch.uint8))

def rollout(env, model=None, method='ppo', seed=42):
    obs, _ = env.reset(seed=seed)
    rng = np.random.default_rng(seed)
    while not env.done:
        mask = env.action_masks()
        if method == 'greedy':
            action = int(np.argmin(np.where(mask,env.durations[env.index],np.inf)))
        elif method == 'random':
            action = int(rng.choice(np.flatnonzero(mask)))
        else:
            action, _ = model.predict(obs, deterministic=True, action_masks=mask)
            action = int(action)
        obs, _, _, _, _ = env.step(action)
    return dict(makespan_s=env.makespan, trace=list(env.trace))

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--job',type=Path, required=True)
    p.add_argument('--out',type=Path, required=True, help='A NEW output directory')
    p.add_argument('--tasks-json',type=Path)
    p.add_argument('--demo-segments',type=int, help='Only bundled sample_job: exactly partition its -40..40 mm bead')
    p.add_argument('--timesteps',type=int, default=8192, help='Additional steps; rounded up to complete 128-step rollouts')
    p.add_argument('--seed',type=int, default=42)
    p.add_argument('--reach-margin-mm',type=float, default=1.0)
    p.add_argument('--resume',type=Path)
    p.add_argument('--eval-only',action='store_true', help='Requires --resume; no learning')
    a = p.parse_args()
    if a.timesteps <= 0 or (a.demo_segments is not None and a.demo_segments <= 0):
        p.error('timesteps and demo-segments must be positive')
    if a.eval_only and not a.resume:
        p.error('--eval-only requires --resume')
    if a.tasks_json and a.demo_segments:
        p.error('--tasks-json and --demo-segments are mutually exclusive')
    job, out = a.job.resolve(), a.out.resolve()
    if a.demo_segments:
        sample = ROOT.parent/'TEAM_PROJECT/week1/environment/examples/sample_job'
        if any(digest(job/n)!=digest(sample/n) for n in ('config.yaml','target.stl')):
            p.error('--demo-segments only supports the exact bundled sample inputs')
        xs = np.linspace(-40,40,a.demo_segments+1)
        tasks = [Task((float(x),0.,2.),(float(y),0.,2.)) for x,y in zip(xs[:-1],xs[1:])]
    elif a.tasks_json:
        records = json.loads(a.tasks_json.read_text(encoding='utf-8'))
        tasks = [Task(tuple(t['start_xyz_mm']),tuple(t['end_xyz_mm'])) for t in records]
    else:
        records, _ = official_tasks(job/'target.stl',job/'config.yaml',a.reach_margin_mm)
        tasks = [Task(tuple(t.start_xyz_mm),tuple(t.end_xyz_mm)) for t in records]
    signature = signatures(job,tasks,a.reach_margin_mm)
    parent = check_resume(a.resume.resolve(),signature) if a.resume else None
    if parent and parent['lineage']['seed'] != a.seed:
        raise ValueError('Resume seed must match the checkpoint manifest seed')
    # Check compatibility before loading any checkpoint with torch.
    import torch
    from sb3_contrib import MaskablePPO
    from stable_baselines3.common.callbacks import BaseCallback
    from stable_baselines3.common.logger import configure
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    random.seed(a.seed)
    np.random.seed(a.seed)
    torch.manual_seed(a.seed)
    out.mkdir(parents=True,exist_ok=False)
    report = dict(status='ERROR',signature=signature, source_sha256=source_hashes(),
                  seed=a.seed, requested_additional_steps=0 if a.eval_only else a.timesteps,
                  task_count=len(tasks), limitations=CONTRACT['scheduler'],
                  packages={n:importlib.metadata.version(n) for n in ('torch','stable-baselines3','sb3-contrib','gymnasium','numpy')})
    write_json(out/'tasks.json',task_records(tasks))
    started = time.perf_counter()
    env = None
    try:
        env = SerialPPOEnv(job,tasks,a.reach_margin_mm)
        report['mask_statistics'] = {str(i):int((env.masks.sum(axis=1)==i).sum()) for i in (1,2,3)}
        lineage = dict(seed=a.seed, parent_checkpoint_sha256=digest(a.resume) if a.resume else None,
                       source_sha256=report['source_sha256'], packages=report['packages'])
        if a.resume:
            model = MaskablePPO.load(a.resume, env=env, device='cpu', force_reset=True)
            restore_rng(a.resume)
            report['parent_manifest'] = parent
        else:
            model = MaskablePPO('MlpPolicy',env, seed=a.seed, device='cpu',learning_rate=3e-4,
                                n_steps=128,batch_size=64,n_epochs=10,gamma=0.0,gae_lambda=1.0,
                                ent_coef=0.01,policy_kwargs={'net_arch':[64,64]},verbose=0)
        report['initial_timesteps'] = model.num_timesteps
        report['before_training'] = rollout(env, model)
        class PeriodicCheckpoint(BaseCallback):
            def _on_step(self):
                if self.num_timesteps % 1024 == 0:
                    print(f'PPO steps={self.num_timesteps}',flush=True)
                return True
            def _on_rollout_start(self):
                # At this point the preceding rollout has already been trained.
                if self.model.num_timesteps and self.model.num_timesteps % 2048 == 0:
                    save_checkpoint(self.model,out/f'checkpoint_{self.model.num_timesteps}.zip',signature,lineage)
        if not a.eval_only:
            model.set_logger(configure(str(out/'logs'),['csv']))
            model.learn(total_timesteps=a.timesteps,reset_num_timesteps=False,callback=PeriodicCheckpoint())
        checkpoint = out/'ppo_serial.zip'
        save_checkpoint(model,checkpoint,signature,lineage)
        # Reload from disk before evaluation: exported trajectory uses saved weights.
        model = MaskablePPO.load(checkpoint,env=env,device='cpu')
        report['total_timesteps'] = model.num_timesteps
        report['actual_additional_steps'] = model.num_timesteps-report['initial_timesteps']
        report['checkpoint_sha256'] = digest(checkpoint)
        report['evaluations'] = {}
        for method in ('ppo','greedy','random'):
            metrics = rollout(env,model,method,a.seed)
            exported = env.export(out/method/'job')
            result = run_validation(exported,out/method/'validation')
            metrics.update(status=result.status,official_makespan_s=result.schedule.makespan_s,
                           trajectory_sha256=digest(exported/'trajectory.csv'), validation=result.summary_dict())
            report['evaluations'][method] = metrics
            print(f'{method}: official={result.status}, makespan={result.schedule.makespan_s:.6f}',flush=True)
        report['status'] = 'PASS' if all(x['status']=='PASS' for x in report['evaluations'].values()) else 'FAIL'
    except Exception as exc:
        report['error'] = f'{type(exc).__name__}: {exc}'
        raise
    finally:
        if env:
            env.close()
        report['elapsed_s'] = time.perf_counter()-started
        report['source_changed_during_run'] = report['source_sha256'] != source_hashes()
        report['python'] = sys.version
        write_json(out/'run.json',report)
    return 0 if report['status']=='PASS' else 2

if __name__ == '__main__':
    sys.exit(main())
