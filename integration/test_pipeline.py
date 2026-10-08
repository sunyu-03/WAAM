import tempfile
import unittest
from pathlib import Path
import numpy as np
import yaml
from run_pipeline import official_tasks, merge_collinear, ROOT, AssignmentEnv, Task

SAMPLE = ROOT.parent/'TEAM_PROJECT/week1/environment/examples/sample_job'

class PipelineTests(unittest.TestCase):
    def test_exact_collinear_merge(self):
        edges = merge_collinear([((0, 0), (1, 0)), ((1, 0), (2, 0))])
        self.assertEqual(len(edges), 1)
        self.assertAlmostEqual(np.linalg.norm(edges[0][1]-edges[0][0]), 2)

    def test_top_and_center_keep_same_layers(self):
        top, _ = official_tasks(SAMPLE/'target.stl', SAMPLE/'config.yaml')
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp') as tmp:
            data = yaml.safe_load((SAMPLE/'config.yaml').read_text())
            data['process']['tcp_z_reference'] = 'center'
            config = Path(tmp)/'config.yaml'
            config.write_text(yaml.safe_dump(data))
            center, _ = official_tasks(SAMPLE/'target.stl', config)
        self.assertEqual([t.layer for t in top], [t.layer for t in center])
        self.assertEqual(len(top), 1)
        self.assertAlmostEqual(top[0].start_xyz_mm[2], 2)
        self.assertAlmostEqual(center[0].start_xyz_mm[2], 1)

    def test_unreachable_robot_rejected(self):
        env = AssignmentEnv(SAMPLE, [Task((0, 0, 2), (10, 0, 2))])
        env.bases[0, :2] = [100000, 100000]
        rows, reason, _ = env.candidate(0)
        self.assertIsNone(rows)
        self.assertEqual(reason, 'unreachable')
        env.close()

if __name__ == '__main__':
    unittest.main()
