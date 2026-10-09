# WAAM Validator Report

## Overall Result

**PASS**

- WAAM Validator version: 1.0.1

## Input Summary

- Directory: `C:\Users\User\Desktop\AInAlgorithm\waam_generalization\integration\runs\final_matrix_20261009\04\job`
- Trajectory rows: 9142
- Target watertight: True

## Schedule

- Makespan: 48267.64 s
- R1: completion 48118.19 s; Deposition 27874.09 s; Travel 1287.71 s; Wait 18956.39 s
- R2: completion 48267.64 s; Deposition 14336.70 s; Travel 978.29 s; Wait 32952.65 s
- R3: completion 31289.80 s; Deposition 3435.28 s; Travel 355.57 s; Wait 27498.94 s

## Robot XY Reach

- Passed: True
- R1: max XY distance 1498.34 / 1500.00 mm; XY margin 1.66 mm; violating points 0
- R2: max XY distance 1494.74 / 1500.00 mm; XY margin 5.26 mm; violating points 0
- R3: max XY distance 1405.57 / 1500.00 mm; XY margin 94.43 mm; violating points 0

## Collision

- Arm Envelope events: 0
- Minimum Arm Envelope safety margin: 550.73 mm
- Arm centerline distance at worst case:
  800.73 mm
- Arm required centerline distance at worst case:
  250.00 mm
- TCP_RADIUS events: 0
- Minimum TCP distance: 800.73 mm

## Shape

- Target layer-integrated volume: 6661016.843 mm³
- Deposited volume: 6287188.610 mm³
- Intersection volume: 6277198.338 mm³
- Underfill volume: 383818.480 mm³
- Overfill volume: 9990.272 mm³
- Coverage: 94.24%
- Underfill: 5.76%
- Overfill: 0.15%
- IoU: 94.10%
- Failed layers: 0 / 50

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
