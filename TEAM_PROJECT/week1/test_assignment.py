import csv

import numpy as np
import pytest

from assignment_env import (
    AssignmentEnv as WaamEnv,
    Task,
    VALIDATOR_ROOT,
    demo_tasks,
    greedy_action,
    run_validation,
    run_collision_analysis,
)
from waam_validator.collision import check_arm_envelope_xy, check_tcp_radius_xy


@pytest.fixture
def env():
    return WaamEnv(VALIDATOR_ROOT / "examples/sample_job", demo_tasks())


def test_sb3_contract(env):
    from stable_baselines3.common.env_checker import check_env

    check_env(env, warn=True)


def test_greedy_export_official_pass(env, tmp_path):
    rewards = []
    while not env.done:
        _, reward, _, _, info = env.step(greedy_action(env))
        rewards.append(reward)
    assert info["schedule_complete"]
    assert sum(rewards) == pytest.approx(1.0 - env.makespan / env.time_scale)
    output = env.export(tmp_path / "job")
    for name in ("config.yaml", "target.stl"):
        assert (output / name).read_bytes() == (env.scenario / name).read_bytes()
    result = run_validation(output)
    assert result.status == "PASS", result.failure_reasons
    assert not result.warnings
    assert result.schedule.makespan_s == pytest.approx(env.makespan)
    rows = list(csv.DictReader((output / "trajectory.csv").open(encoding="utf-8")))
    for robot in ("1", "2", "3"):
        own = [r for r in rows if r["robot_id"] == robot]
        assert len(own) >= 2
        assert float(own[0]["time_s"]) == 0
        assert own[-1]["mode"] == "W"
    with pytest.raises(FileExistsError):
        env.export(output)


def test_no_partial_export_or_step_after_end(env, tmp_path):
    with pytest.raises(RuntimeError):
        env.export(tmp_path / "partial")
    while not env.done:
        env.step(greedy_action(env))
    with pytest.raises(RuntimeError):
        env.step(0)


def test_seeded_reset_and_invalid_action(env):
    env.randomize_direction = True
    a, _ = env.reset(seed=123)
    b, _ = env.reset(seed=123)
    np.testing.assert_array_equal(a, b)
    assert env.index == 0 and env.makespan == 0
    with pytest.raises(ValueError):
        env.step(3)


def test_failed_action_does_not_change_schedule(env, monkeypatch):
    before = env._observation().copy()
    monkeypatch.setattr(
        env, "candidate", lambda robot: (None, "collision_or_constraint", 0.0)
    )
    after, reward, terminated, truncated, info = env.step(0)
    np.testing.assert_array_equal(before, after)
    assert reward == -2 and terminated and not truncated
    assert not info["schedule_complete"]


def test_official_geometry_boundaries():
    # Parallel arm centrelines: two radii 100 + clearance 50 = 250 mm.
    def arm(gap):
        return check_arm_envelope_xy(
            np.array([0.0, 0.0]),
            np.array([100.0, 0.0]),
            100.0,
            np.array([0.0, gap]),
            np.array([100.0, gap]),
            100.0,
            50.0,
            1e-6,
            True,
        )

    assert arm(250.0).collision
    assert not arm(251.0).collision
    assert arm(230.0).safety_margin_mm == pytest.approx(-20.0)
    assert check_tcp_radius_xy(
        np.array([0.0, 0.0]), 20.0, np.array([40.0, 0.0]), 20.0, True
    ).collision


def test_reject_bad_geometry():
    with pytest.raises(ValueError):
        WaamEnv(
            VALIDATOR_ROOT / "examples/sample_job",
            [Task((0.0, 0.0, 2.0), (0.0, 0.0, 2.0))],
        )
    with pytest.raises(ValueError):
        WaamEnv(
            VALIDATOR_ROOT / "examples/sample_job",
            [Task((0.0, 0.0, 2.0), (10.0, 0.0, 4.0))],
        )


def test_waiting_robot_collision_is_checked(env):
    # Put another robot at the next deposition point for the whole candidate.
    env.homes[1] = env.tasks[0].start
    env.rows[1] = [[0.0, *env.homes[1], "W"]]
    rows, reason, _ = env.candidate(0)
    assert rows is None and reason == "collision_or_constraint"


def test_reach_rejects_assignment(env):
    # Change only this fixture's base to exercise action reach check.
    env.bases[0, :2] = [1e6, 1e6]
    rows, reason, _ = env.candidate(0)
    assert rows is None and reason == "unreachable"


def test_collision_between_waypoints(env):
    # TCP endpoints are apart, but the two TCPs coincide halfway through.
    rows = [
        [[0.0, -100.0, 0.0, 2.0, "T"], [2.0, 100.0, 0.0, 2.0, "W"]],
        [[0.0, 100.0, 0.0, 2.0, "T"], [2.0, -100.0, 0.0, 2.0, "W"]],
        [[0.0, *env.homes[2], "W"], [2.0, *env.homes[2], "W"]],
    ]
    result = run_collision_analysis(env._trajectory(rows), env.config)
    assert any(
        e.collision_type == "TCP_RADIUS" and e.start_s > 0 and e.end_s < 2
        for e in result.events
    )


def test_complete_assignment_does_not_imply_complete_shape(tmp_path):
    partial = WaamEnv(
        VALIDATOR_ROOT / 'examples/sample_job',
        [Task((-40.0, 0.0, 2.0), (0.0, 0.0, 2.0))],
    )
    _, _, terminated, _, info = partial.step(0)
    assert terminated and info['schedule_complete']
    result = run_validation(partial.export(tmp_path / 'partial_shape'))
    assert result.status == 'FAIL'
    assert not result.shape.passed
    assert result.collision_free


def test_task_validation_checks_returned_violations(env, monkeypatch):
    import assignment_env
    from waam_validator.errors import ValidationMessages

    messages = ValidationMessages()
    messages.violation('ROBOT_XY_REACH_VIOLATION', 'Placeholder robot cannot reach')
    monkeypatch.setattr(assignment_env, 'validate_trajectory_set', lambda *_: messages)
    env._validate_tasks()  # Reach must be checked against the selected robot later.
    messages.violation('WAIT_POSITION_CHANGED', 'Invalid process result')
    with pytest.raises(ValueError, match='WAIT_POSITION_CHANGED'):
        env._validate_tasks()
