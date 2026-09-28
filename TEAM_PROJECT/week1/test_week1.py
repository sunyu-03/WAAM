"""Behavioral regression tests for the week 1 changes and real evaluator."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from environment import env as checks
from run_week1 import evaluate
from week1_env import Week1Env


class Week1Tests(unittest.TestCase):
    def test_past_collision_prevents_later_success(self):
        env = Week1Env()
        self.addCleanup(env.close)
        env.reset()
        with patch.object(checks, 'check_collision', side_effect=[0, 1]), \
             patch.object(checks, 'check_validation', return_value=1), \
             patch.object(checks, 'check_shape', return_value=1):
            env.step(env.action_from_targets(env.state[:, 1:4], ['W'] * 3))
            _, reward, done, truncated, info = env.step(
                env.action_from_targets(env.state[:, 1:4], ['F'] * 3)
            )
        self.assertTrue(done)
        self.assertFalse(truncated)
        self.assertEqual(info['upstream_success'], 1)
        self.assertEqual(info['success'], 0)
        self.assertEqual(info['reward_terminal'], -env.terminal_penalty)
        self.assertAlmostEqual(reward, sum(info[k] for k in
                               ['reward_makespan', 'reward_collision', 'reward_terminal']))
        _, info = env.reset()
        self.assertTrue(info['episode_collision_free'])

    def test_real_run_validation_positive_and_negative_controls(self):
        with tempfile.TemporaryDirectory() as directory:
            for case in ['pass', 'collision', 'missing']:
                with self.subTest(case=case):
                    record = evaluate(case, Path(directory) / case)
                    self.assertEqual(record['actual_status'], record['expected_status'])

    def test_sb3_interface(self):
        from stable_baselines3.common.env_checker import check_env
        env = Week1Env(max_steps=3)
        self.addCleanup(env.close)
        check_env(env, warn=True)


if __name__ == '__main__':
    unittest.main()
