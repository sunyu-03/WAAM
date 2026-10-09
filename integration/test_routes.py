import tempfile
import unittest
from pathlib import Path
import numpy as np
from run_pipeline import ROOT, run_validation
from make_route_demo import make
from train_routes import load_cases, MixedRouteEnv, concurrency
from algorithm.environment.route_ppo_env import RoutePPOEnv, OBS_SIZE
from test_ppo import SAMPLE, segments

class RouteTests(unittest.TestCase):
    def test_fixed_contract_and_invalid_action(self):
        for n in (1,4):
            env=RoutePPOEnv(SAMPLE,segments(n))
            obs,_=env.reset(seed=42)
            self.assertEqual(obs.shape,(OBS_SIZE,))
            self.assertTrue(env.observation_space.contains(obs))
            with self.assertRaises(ValueError):
                env.step(-1)
            self.assertEqual(len(env.trace),0)
            env.close()

    def test_route_retains_pose_and_validates(self):
        env=RoutePPOEnv(SAMPLE,segments(4))
        while not env.done:
            env.step(env.greedy_action())
        self.assertLess(env.makespan,31)
        self.assertTrue(any(t['departure_s']<env.trace[0]['makespan_s'] for t in env.trace[1:]))
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp') as folder:
            self.assertEqual(run_validation(env.export(Path(folder)/'job'),Path(folder)/'validation').status,'PASS')
        with self.assertRaises(RuntimeError):
            env.step(0)
        env.close()

    def test_mixed_inputs_layers_and_actual_concurrency(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp') as folder:
            manifest=make(Path(folder)/'fixtures')
            train,margin=load_cases(manifest,'train')
            evaluation,_=load_cases(manifest,'evaluation')
            self.assertNotEqual(train[0]['identity']['inputs']['target.stl'],train[1]['identity']['inputs']['target.stl'])
            pool=MixedRouteEnv(train,margin)
            sequence=[]
            for _ in range(8):
                obs,info=pool.reset(seed=42 if not sequence else None)
                sequence.append(info['dataset_case'])
                self.assertEqual(obs.shape,(OBS_SIZE,))
            self.assertEqual(set(sequence),{0,1})
            pool.close()
            overlap=[]
            for case in evaluation[1:]:
                env=RoutePPOEnv(case['job'],case['tasks'],margin,cache_limit=0)
                while not env.done:
                    env.step(env.greedy_action())
                self.assertEqual(sorted(t['task'] for t in env.trace),list(range(len(env.tasks))))
                overlap.append(concurrency(env.completed_rows)['simultaneous_motion_s'])
                result=run_validation(env.export(Path(folder)/case['name']/'job'),Path(folder)/case['name']/'validation')
                self.assertEqual(result.status,'PASS')
                if case['name']=='layers_heldout':
                    first=[t for t in env.trace if env.tasks[t['task']].start[2]==2]
                    second=[t for t in env.trace if env.tasks[t['task']].start[2]==4]
                    self.assertGreaterEqual(min(t['departure_s'] for t in second),first[-1]['makespan_s']-1e-7)
                env.close()
            self.assertTrue(all(t>0 for t in overlap))

    def test_concurrency_event_accounting(self):
        rows=[[[0,0,0,0,'T'],[3,0,0,0,'W']],[[1,0,0,0,'T'],[2,0,0,0,'W']],[[0,0,0,0,'W']]]
        self.assertEqual(concurrency(rows),dict(simultaneous_motion_s=1.,max_moving_robots=2))

if __name__=='__main__':
    unittest.main()
