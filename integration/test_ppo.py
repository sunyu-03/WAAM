"""Checks for the PPO observation/action contract and safe serial decoder."""
import tempfile
import unittest
from pathlib import Path
import numpy as np
from run_pipeline import ROOT, Task, run_validation
from algorithm.environment.ppo_env import SerialPPOEnv
from train import signatures, check_resume, rollout, digest, write_json

SAMPLE = ROOT.parent/'TEAM_PROJECT/week1/environment/examples/sample_job'

def segments(n):
    xs = np.linspace(-40,40,n+1)
    return [Task((float(x),0.,2.),(float(y),0.,2.)) for x,y in zip(xs[:-1],xs[1:])]

class PPOTests(unittest.TestCase):
    def test_fixed_observation_independent_of_task_count(self):
        for n in (1,4,8):
            env = SerialPPOEnv(SAMPLE,segments(n))
            obs,_ = env.reset(seed=42)
            self.assertEqual(obs.shape,(16,))
            self.assertEqual(obs.dtype,np.float32)
            self.assertTrue(env.observation_space.contains(obs))
            self.assertTrue(np.isfinite(obs).all())
            env.close()

    def test_masked_action_rejected_without_state_change(self):
        env = SerialPPOEnv(SAMPLE,segments(4),reach_margin_mm=1320)
        self.assertFalse(env.action_masks()[2])
        obs = env._observation().copy()
        with self.assertRaisesRegex(ValueError,'masked actions'):
            env.step(2)
        self.assertEqual(env.index,0)
        self.assertEqual(env.makespan,0)
        np.testing.assert_array_equal(env._observation(),obs)
        with self.assertRaises(ValueError):
            env.step(-1)
        env.close()

    def test_decoder_matches_sum_and_official_validation(self):
        env = SerialPPOEnv(SAMPLE,segments(4))
        metrics = rollout(env,method='greedy')
        optimum = np.where(env.masks,env.durations,np.inf).min(axis=1).sum()
        self.assertAlmostEqual(metrics['makespan_s'],optimum)
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp') as folder:
            job = env.export(Path(folder)/'job')
            result = run_validation(job,Path(folder)/'validation')
            self.assertEqual(result.status,'PASS')
            self.assertAlmostEqual(result.schedule.makespan_s,optimum)
        with self.assertRaises(RuntimeError):
            env.step(0)
        env.reset()
        with self.assertRaises(RuntimeError):
            env.export(ROOT/'tmp/should_not_exist')
        env.close()

    def test_missing_legacy_manifest_rejected(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp') as folder:
            legacy = Path(folder)/'legacy.zip'
            legacy.write_bytes(b'not deserialized')
            with self.assertRaisesRegex(ValueError,'legacy checkpoints'):
                check_resume(legacy,signatures(SAMPLE,segments(4),1.0))

    def test_invalid_margin_rejected(self):
        for margin in (-1,float('nan'),float('inf')):
            with self.assertRaises(ValueError):
                SerialPPOEnv(SAMPLE,segments(4),margin)

    def test_checkpoint_integrity_and_contract_checked_before_loading(self):
        signature = signatures(SAMPLE,segments(4),1.0)
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp') as folder:
            checkpoint = Path(folder)/'model.zip'
            checkpoint.write_bytes(b'opaque checkpoint; never unpickled')
            rng = checkpoint.with_suffix('.rng.json')
            rng.write_text('{}')
            manifest = dict(signature=signature,checkpoint_sha256=digest(checkpoint),rng_sha256=digest(rng))
            write_json(checkpoint.with_suffix('.json'),manifest)
            self.assertEqual(check_resume(checkpoint,signature),manifest)
            with self.assertRaisesRegex(ValueError,'contract'):
                check_resume(checkpoint,signatures(SAMPLE,segments(8),1.0))
            rng.write_text('{"changed":true}')
            with self.assertRaisesRegex(ValueError,'RNG'):
                check_resume(checkpoint,signature)
            checkpoint.write_bytes(b'changed checkpoint')
            with self.assertRaisesRegex(ValueError,'Checkpoint SHA256'):
                check_resume(checkpoint,signature)

if __name__ == '__main__':
    unittest.main()
