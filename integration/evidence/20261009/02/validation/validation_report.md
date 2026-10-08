# WAAM Validator Report

## Overall Result

**PASS**

- WAAM Validator version: 1.0.1

## Input Summary

- Directory: `C:\Users\User\Desktop\AInAlgorithm\waam_generalization\integration\runs\final_matrix_20261009\02\job`
- Trajectory rows: 7187
- Target watertight: True

## Schedule

- Makespan: 2379.23 s
- R1: completion 2307.20 s; Deposition 1653.44 s; Travel 149.01 s; Wait 504.74 s
- R2: completion 2379.23 s; Deposition 429.83 s; Travel 146.94 s; Wait 1802.46 s
- R3: completion 2379.23 s; Deposition 0.00 s; Travel 0.00 s; Wait 2379.23 s

## Robot XY Reach

- Passed: True
- R1: max XY distance 1498.21 / 1500.00 mm; XY margin 1.79 mm; violating points 0
- R2: max XY distance 1493.24 / 1500.00 mm; XY margin 6.76 mm; violating points 0
- R3: max XY distance 400.00 / 1500.00 mm; XY margin 1100.00 mm; violating points 0

## Collision

- Arm Envelope events: 0
- Minimum Arm Envelope safety margin: 573.38 mm
- Arm centerline distance at worst case:
  823.38 mm
- Arm required centerline distance at worst case:
  250.00 mm
- TCP_RADIUS events: 0
- Minimum TCP distance: 823.38 mm

## Shape

- Target layer-integrated volume: 254007.549 mm³
- Deposited volume: 262218.202 mm³
- Intersection volume: 250569.803 mm³
- Underfill volume: 3437.743 mm³
- Overfill volume: 11648.400 mm³
- Coverage: 98.65%
- Underfill: 1.35%
- Overfill: 4.59%
- IoU: 94.32%
- Failed layers: 0 / 8

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
