# WAAM Validator Report

## Overall Result

**PASS**

- WAAM Validator version: 1.0.1

## Input Summary

- Directory: `ppo/my_job`
- Trajectory rows: 23013
- Target watertight: True

## Schedule

- Makespan: 7089.33 s
- R1: completion 7089.33 s; Deposition 3890.25 s; Travel 918.84 s; Wait 2280.23 s
- R2: completion 7089.33 s; Deposition 0.00 s; Travel 0.00 s; Wait 7089.33 s
- R3: completion 7089.33 s; Deposition 1660.75 s; Travel 131.48 s; Wait 5297.09 s

## Robot XY Reach

- Passed: True
- R1: max XY distance 1383.33 / 1500.00 mm; XY margin 116.67 mm; violating points 0
- R2: max XY distance 400.00 / 1500.00 mm; XY margin 1100.00 mm; violating points 0
- R3: max XY distance 1488.91 / 1500.00 mm; XY margin 11.09 mm; violating points 0

## Collision

- Arm Envelope events: 0
- Minimum Arm Envelope safety margin: 641.71 mm
- Arm centerline distance at worst case:
  891.71 mm
- Arm required centerline distance at worst case:
  250.00 mm
- TCP_RADIUS events: 0
- Minimum TCP distance: 891.71 mm

## Shape

- Target layer-integrated volume: 636120.000 mm³
- Deposited volume: 631425.056 mm³
- Intersection volume: 631425.056 mm³
- Underfill volume: 4694.944 mm³
- Overfill volume: 0.000 mm³
- Coverage: 99.26%
- Underfill: 0.74%
- Overfill: 0.00%
- IoU: 99.26%
- Failed layers: 0 / 51

## Failure Reasons

None

## Warnings

None

## Validation Violations

These findings contribute to a normal `FAIL`; they do not mean that the pipeline ended with
the fatal status `ERROR`.

None

## Output Files

- `summary.json`
- `validation_report.md`
- `robot_metrics.csv`
- `collision_events.csv`
- `layer_metrics.csv`
- `run.log`
- `validation_inputs.json`

## Interpretation Limitations

본 검증기는 각 로봇을 폭이 고정된 Base–TCP 2D Capsule로 단순화하고, XY 평면상 Capsule 안전 여유와 TCP 허용 원 침범만을 로봇 간 충돌로 판단한다. 검사는 adaptive sample 기반이며 연속시간 swept collision을 보증하지 않는다. 실제 로봇 링크, 관절 자세, Z 방향 분리, 지그 및 환경 충돌은 반영하지 않는다. 형상 검증은 일정한 비드 폭과 layer 높이를 가정한 명목 기하 모델이며 열변형, 비드 형상 변화, 용융풀 거동 및 공정 불안정성을 예측하지 않는다.
