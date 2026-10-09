"""Mixed-job route PPO training and independent complete-job evaluation."""
from __future__ import annotations
import argparse
import json
import time
from pathlib import Path
from run_pipeline import ROOT, Task, official_tasks, source_hashes, run_validation
import gymnasium as gym
import numpy as np
from algorithm.environment.route_ppo_env import RoutePPOEnv, CONTRACT
from train import digest, write_json, task_records, save_checkpoint, restore_rng, check_resume

def load_cases(manifest, section):
    manifest=Path(manifest).resolve()
    data=json.loads(manifest.read_text(encoding='utf-8'))
    if data.get('version')!=1:
        raise ValueError('Dataset manifest version must be 1')
    cases=[]
    names=set()
    for item in data.get(section,[]):
        name=item['name']
        if name in names or not name or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for c in name):
            raise ValueError('Case names must be unique simple folder names')
        names.add(name)
        job=(manifest.parent/item['job']).resolve()
        if 'tasks_json' in item:
            records=json.loads((manifest.parent/item['tasks_json']).read_text(encoding='utf-8'))
        else:
            generated,_=official_tasks(job/'target.stl',job/'config.yaml',data.get('reach_margin_mm',1.0))
            records=[r.to_dict() for r in generated]
        tasks=[Task(tuple(r['start_xyz_mm']),tuple(r['end_xyz_mm'])) for r in records]
        if not tasks:
            raise ValueError('Empty dataset case')
        cases.append(dict(name=name,job=job,tasks=tasks,
                          identity=dict(name=name,inputs={n:digest(job/n) for n in ('target.stl','config.yaml')},
                                        tasks=task_records(tasks))))
    return cases,float(data.get('reach_margin_mm',1.0))

class MixedRouteEnv(gym.Env):
    metadata={'render_modes':[]}
    def __init__(self,cases,margin):
        super().__init__()
        if not cases:
            raise ValueError('At least one training job required')
        self.envs=[RoutePPOEnv(c['job'],c['tasks'],margin,cache_limit=512 if len(c['tasks'])<=32 else 0) for c in cases]
        self.action_space=self.envs[0].action_space
        self.observation_space=self.envs[0].observation_space
        self.current=None
        self.selected_counts=np.zeros(len(cases),int)
        self.resume_sampler_state=None
    def reset(self,*,seed=None,options=None):
        super().reset(seed=seed)
        # SB3 seeds the VecEnv on its first reset after load. Restore the saved
        # sampler after that seed, so it cannot accidentally replace the state.
        if self.resume_sampler_state is not None:
            self.np_random.bit_generator.state=self.resume_sampler_state
            self.resume_sampler_state=None
        index=int(self.np_random.integers(len(self.envs)))
        self.current=self.envs[index]
        self.selected_counts[index]+=1
        obs,info=self.current.reset()
        info['dataset_case']=index
        return obs,info
    def action_masks(self):
        return self.current.action_masks()
    def step(self,action):
        return self.current.step(action)
    def close(self):
        for env in self.envs:
            env.close()

def concurrency(rows):
    events={}
    for robot,source in enumerate(rows):
        for a,b in zip(source[:-1],source[1:]):
            if a[4] in ('T','D') and b[0]>a[0]:
                events.setdefault(a[0],[]).append((robot,1))
                events.setdefault(b[0],[]).append((robot,-1))
    active=np.zeros(3,int)
    last=0.
    overlap=0.
    peak=0
    for t in sorted(events):
        count=int((active>0).sum())
        if count>=2:
            overlap+=t-last
        for r,delta in events[t]:
            active[r]+=delta
        peak=max(peak,int((active>0).sum()))
        last=t
    return dict(simultaneous_motion_s=overlap,max_moving_robots=peak)

def evaluate(model,case,margin,out,method):
    env=RoutePPOEnv(case['job'],case['tasks'],margin,cache_limit=0)
    try:
        obs,_=env.reset(seed=42)
        while not env.done:
            if method=='greedy':
                action=env.greedy_action()
            else:
                action,_=model.predict(obs,deterministic=True,action_masks=env.action_masks())
            obs,_,_,_,_=env.step(int(action))
            if len(env.trace)%100==0:
                print(f"{case['name']} {method}: {len(env.trace)}/{len(env.tasks)}",flush=True)
        job=env.export(out/'job')
        result=run_validation(job,out/'validation')
        report=dict(status=result.status,makespan_s=result.schedule.makespan_s,trace=env.trace,
                    trajectory_sha256=digest(job/'trajectory.csv'),validation=result.summary_dict(),
                    **concurrency(env.completed_rows))
        write_json(out/'run.json',report)
        print(f"{case['name']} {method}: {result.status}, {result.schedule.makespan_s:.3f}s, overlap={report['simultaneous_motion_s']:.3f}s",flush=True)
        return report
    finally:
        env.close()

def save_routes(model,checkpoint,signature,lineage,pool):
    save_checkpoint(model,checkpoint,signature,lineage)
    rng_path=checkpoint.with_suffix('.rng.json')
    rng=json.loads(rng_path.read_text(encoding='utf-8'))
    rng['dataset_sampler']=pool.np_random.bit_generator.state
    write_json(rng_path,rng)
    manifest_path=checkpoint.with_suffix('.json')
    manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
    manifest['rng_sha256']=digest(rng_path)
    manifest['resume_semantics']+=' Mixed-job sampler RNG is restored; partially planned episode is not restored.'
    write_json(manifest_path,manifest)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dataset',type=Path,required=True)
    p.add_argument('--eval-dataset',type=Path,help='Independent evaluation manifest; only its evaluation section is used')
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--timesteps',type=int,default=2048)
    p.add_argument('--seed',type=int,default=42)
    p.add_argument('--resume',type=Path)
    p.add_argument('--eval-only',action='store_true')
    p.add_argument('--ppo-only',action='store_true',help='Skip the same-decoder greedy comparison')
    p.add_argument('--cost-prior',action='store_true',help='Initialize linear actor logits with negative candidate makespan and work finish, then train PPO')
    a=p.parse_args()
    if a.timesteps<=0 or (a.eval_only and not a.resume):
        p.error('Positive timesteps required; eval-only requires resume')
    if a.resume and a.cost_prior:
        p.error('Cost initialization applies only to new models; resume keeps saved policy')
    cases,margin=load_cases(a.dataset,'train')
    evaluations,eval_margin=load_cases(a.eval_dataset or a.dataset,'evaluation')
    if not evaluations or eval_margin!=margin:
        p.error('Evaluation cases required; train/evaluation reach margin must match')
    signature=dict(contract=CONTRACT,reach_margin_mm=margin,training_dataset=[c['identity'] for c in cases])
    parent=check_resume(a.resume.resolve(),signature) if a.resume else None
    if parent and parent['lineage']['seed']!=a.seed:
        raise ValueError('Resume seed differs from checkpoint')
    import random
    import torch
    import importlib.metadata
    from sb3_contrib import MaskablePPO
    from stable_baselines3.common.callbacks import BaseCallback
    from stable_baselines3.common.logger import configure
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    random.seed(a.seed)
    np.random.seed(a.seed)
    torch.manual_seed(a.seed)
    out=a.out.resolve()
    out.mkdir(parents=True,exist_ok=False)
    report=dict(status='ERROR',signature=signature,seed=a.seed,source_sha256=source_hashes(),
                evaluation_dataset=[c['identity'] for c in evaluations],
                packages={n:importlib.metadata.version(n) for n in ('torch','stable-baselines3','sb3-contrib','gymnasium','numpy')})
    started=time.perf_counter()
    pool=None
    try:
        pool=MixedRouteEnv(cases,margin)
        lineage=dict(seed=a.seed,source_sha256=report['source_sha256'],packages=report['packages'],
                     parent_checkpoint_sha256=digest(a.resume) if a.resume else None,
                     actor_initialization=parent['lineage'].get('actor_initialization','random') if parent else ('negative candidate time cost prior' if a.cost_prior else 'random'))
        report['actor_initialization']=lineage['actor_initialization']
        if a.resume:
            model=MaskablePPO.load(a.resume,env=pool,device='cpu')
            restore_rng(a.resume)
            rng=json.loads(a.resume.with_suffix('.rng.json').read_text(encoding='utf-8'))
            if 'dataset_sampler' in rng:
                pool.np_random.bit_generator.state=rng['dataset_sampler']
                pool.resume_sampler_state=rng['dataset_sampler']
            report['parent_manifest']=parent
        else:
            model=MaskablePPO('MlpPolicy',pool,device='cpu',seed=a.seed,n_steps=128,batch_size=64,
                              n_epochs=5,gamma=1.,gae_lambda=.95,learning_rate=3e-4,ent_coef=.005,
                              policy_kwargs={'net_arch':{'pi':[],'vf':[64,64]} if a.cost_prior else [64,64]},verbose=0)
            if a.cost_prior:
                # This is a disclosed heuristic initialization, not a PPO-only
                # improvement claim. Evaluation still uses the saved learned actor.
                with torch.no_grad():
                    model.policy.action_net.weight.zero_()
                    model.policy.action_net.bias.zero_()
                    for action in range(CONTRACT['action_count']):
                        model.policy.action_net.weight[action,19+13*action+9]=-100.
                        model.policy.action_net.weight[action,19+13*action+8]=-0.1
        report['initial_timesteps']=model.num_timesteps
        class Progress(BaseCallback):
            def _on_step(self):
                if self.num_timesteps%128==0:
                    print(f'Route PPO steps={self.num_timesteps}',flush=True)
                return True
            def _on_rollout_start(self):
                if self.num_timesteps and self.num_timesteps%512==0:
                    save_routes(self.model,out/f'checkpoint_{self.num_timesteps}.zip',signature,lineage,pool)
        if not a.eval_only:
            model.set_logger(configure(str(out/'logs'),['csv']))
            model.learn(a.timesteps,reset_num_timesteps=False,callback=Progress())
        checkpoint=out/'ppo_routes.zip'
        save_routes(model,checkpoint,signature,lineage,pool)
        model=MaskablePPO.load(checkpoint,device='cpu')
        report['total_timesteps']=model.num_timesteps
        report['actual_additional_steps']=model.num_timesteps-report['initial_timesteps']
        report['training_episode_starts']={c['name']:int(n) for c,n in zip(cases,pool.selected_counts)}
        report['evaluations']={}
        for case in evaluations:
            report['evaluations'][case['name']]={}
            for method in (('ppo',) if a.ppo_only else ('ppo','greedy')):
                report['evaluations'][case['name']][method]=evaluate(model,case,margin,out/case['name']/method,method)
                # Preserve completed cases if a later large case fails.
                write_json(out/'run.json',report)
        report['status']='PASS' if all(v['status']=='PASS' for methods in report['evaluations'].values() for v in methods.values()) else 'FAIL'
    except Exception as exc:
        report['error']=f'{type(exc).__name__}: {exc}'
        raise
    finally:
        if pool:
            pool.close()
        report['elapsed_s']=time.perf_counter()-started
        report['source_changed_during_run']=report['source_sha256']!=source_hashes()
        write_json(out/'run.json',report)
    return 0 if report['status']=='PASS' else 2

if __name__=='__main__':
    raise SystemExit(main())
