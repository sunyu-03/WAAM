import tempfile
import unittest
from pathlib import Path
import numpy as np
import yaml
from types import SimpleNamespace
from algorithm.preprocessing.reach import split_by_reach
from shapely import LineString, unary_union
from run_pipeline import official_tasks, merge_collinear, ROOT, AssignmentEnv, Task
from algorithm.serial_scheduler import schedule_layers
from waam_validator import run_validation

SAMPLE = ROOT.parent/'TEAM_PROJECT/week1/environment/examples/sample_job'

class PipelineTests(unittest.TestCase):
    def test_layer_route_official_validation(self):
        env = AssignmentEnv(SAMPLE, [Task((x,0,2),(x+20,0,2)) for x in (-40,-20,0,20)])
        trace = schedule_layers(env)
        self.assertEqual(sorted(t['task'] for t in trace), [0,1,2,3])
        self.assertLess(env.makespan, 40)
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp') as tmp:
            job = env.export(Path(tmp)/'job')
            result = run_validation(job,Path(tmp)/'validation')
            self.assertEqual(result.status,'PASS')
        env.close()

    def test_reach_split_preserves_geometry(self):
        robots = [SimpleNamespace(base_xyz_mm=(x, 0, 0), xy_reach_radius_mm=6) for x in (0, 8)]
        original = [((0, 0), (8, 0))]
        pieces = split_by_reach(original, robots, margin_mm=1)
        self.assertEqual(len(pieces), 2)
        self.assertTrue(unary_union([LineString(p) for p in pieces]).equals(LineString(original[0])))
        for a, b in pieces:
            self.assertTrue(any(max(np.linalg.norm(a-np.array(r.base_xyz_mm[:2])), np.linalg.norm(b-np.array(r.base_xyz_mm[:2]))) <= 5+1e-9 for r in robots))

    def test_reach_gap_is_rejected(self):
        robots = [SimpleNamespace(base_xyz_mm=(x, 0, 0), xy_reach_radius_mm=3) for x in (0, 8)]
        with self.assertRaisesRegex(ValueError, 'Unreachable edge'):
            split_by_reach([((0, 0), (8, 0))], robots, margin_mm=0)

    def test_reach_tangent_does_not_cover_line(self):
        robot = SimpleNamespace(base_xyz_mm=(0, 1, 0), xy_reach_radius_mm=1)
        with self.assertRaisesRegex(ValueError, 'Unreachable edge'):
            split_by_reach([((-1, 0), (1, 0))], [robot], margin_mm=0)

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
