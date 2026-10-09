# WAAM Validator Report

## Overall Result

**PASS**

- WAAM Validator version: 1.0.1

## Input Summary

- Directory: `C:\Users\User\Desktop\AInAlgorithm\waam_generalization\integration\runs\route_public06_greedy_20261009_001\job`
- Trajectory rows: 1714
- Target watertight: True

## Schedule

- Makespan: 5649.97 s
- R1: completion 5649.97 s; Deposition 3240.25 s; Travel 901.20 s; Wait 1508.52 s
- R2: completion 5649.97 s; Deposition 59.00 s; Travel 72.52 s; Wait 5518.45 s
- R3: completion 5649.97 s; Deposition 1298.00 s; Travel 78.99 s; Wait 4272.98 s

## Robot XY Reach

- Passed: True
- R1: max XY distance 1455.85 / 1500.00 mm; XY margin 44.15 mm; violating points 0
- R2: max XY distance 1359.11 / 1500.00 mm; XY margin 140.89 mm; violating points 0
- R3: max XY distance 1496.24 / 1500.00 mm; XY margin 3.76 mm; violating points 0

## Collision

- Arm Envelope events: 0
- Minimum Arm Envelope safety margin: 644.69 mm
- Arm centerline distance at worst case:
  894.69 mm
- Arm required centerline distance at worst case:
  250.00 mm
- TCP_RADIUS events: 0
- Minimum TCP distance: 894.69 mm

## Shape

- Target layer-integrated volume: 636120.000 mm³
- Deposited volume: 605909.296 mm³
- Intersection volume: 605909.296 mm³
- Underfill volume: 30210.704 mm³
- Overfill volume: 0.000 mm³
- Coverage: 95.25%
- Underfill: 4.75%
- Overfill: 0.00%
- IoU: 95.25%
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
