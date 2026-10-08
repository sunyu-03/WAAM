# WAAM Validator Report

## Overall Result

**PASS**

- WAAM Validator version: 1.0.1

## Input Summary

- Directory: `C:\Users\User\Desktop\AInAlgorithm\waam_generalization\integration\runs\final_matrix_20261009\01\job`
- Trajectory rows: 3156
- Target watertight: True

## Schedule

- Makespan: 854.33 s
- R1: completion 827.34 s; Deposition 564.39 s; Travel 147.43 s; Wait 115.52 s
- R2: completion 854.33 s; Deposition 30.77 s; Travel 111.74 s; Wait 711.82 s
- R3: completion 854.33 s; Deposition 0.00 s; Travel 0.00 s; Wait 854.33 s

## Robot XY Reach

- Passed: True
- R1: max XY distance 1498.72 / 1500.00 mm; XY margin 1.28 mm; violating points 0
- R2: max XY distance 1378.84 / 1500.00 mm; XY margin 121.16 mm; violating points 0
- R3: max XY distance 400.00 / 1500.00 mm; XY margin 1100.00 mm; violating points 0

## Collision

- Arm Envelope events: 0
- Minimum Arm Envelope safety margin: 640.43 mm
- Arm centerline distance at worst case:
  890.43 mm
- Arm required centerline distance at worst case:
  250.00 mm
- TCP_RADIUS events: 0
- Minimum TCP distance: 890.43 mm

## Shape

- Target layer-integrated volume: 116840.445 mm³
- Deposited volume: 116838.950 mm³
- Intersection volume: 112070.716 mm³
- Underfill volume: 4769.708 mm³
- Overfill volume: 4768.239 mm³
- Coverage: 95.92%
- Underfill: 4.08%
- Overfill: 4.08%
- IoU: 92.16%
- Failed layers: 0 / 6

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
