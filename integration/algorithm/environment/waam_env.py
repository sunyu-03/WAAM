"""Explicit discrete task-allocation adapter; existing PPO weights are incompatible."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'.deps'))
sys.path.insert(0, str(ROOT.parent/'TEAM_PROJECT/week1'))
from assignment_env import AssignmentEnv, Task

class WAAMBaselineEnv(AssignmentEnv):
    def __init__(self, scenario):
        job = Path(scenario['job_dir'])
        if Path(scenario['stl_path']) != job/'target.stl' or Path(scenario['config_path']) != job/'config.yaml':
            raise ValueError('Scenario requires target.stl and config.yaml in the same job directory')
        tasks = [Task(tuple(t['start_xyz_mm']), tuple(t['end_xyz_mm'])) for t in scenario['tasks']]
        super().__init__(job, tasks)
        self.ppo_ready = False
