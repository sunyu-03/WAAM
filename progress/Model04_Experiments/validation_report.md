# WAAM Validator Report

## Overall Result

**PASS**

- WAAM Validator version: 1.0.1

## Input Summary

- Directory: `C:\Users\User\Desktop\AInAlgorithm\sample\0929\code_ver.1\model04_hybrid_v2\my_job`
- Trajectory rows: 294674
- Target watertight: True

## Schedule

- Makespan: 113437.75 s
- R1: completion 113437.75 s; Deposition 27005.06 s; Travel 1298.98 s; Wait 85133.72 s
- R2: completion 113437.75 s; Deposition 33872.78 s; Travel 1262.28 s; Wait 78302.69 s
- R3: completion 113437.75 s; Deposition 21760.64 s; Travel 1222.01 s; Wait 90455.10 s

## Robot XY Reach

- Passed: True
- R1: max XY distance 1498.49 / 1500.00 mm; XY margin 1.51 mm; violating points 0
- R2: max XY distance 1499.91 / 1500.00 mm; XY margin 0.09 mm; violating points 0
- R3: max XY distance 1499.90 / 1500.00 mm; XY margin 0.10 mm; violating points 0

## Collision

- Arm Envelope events: 0
- Minimum Arm Envelope safety margin: 532.25 mm
- Arm centerline distance at worst case:
  782.25 mm
- Arm required centerline distance at worst case:
  250.00 mm
- TCP_RADIUS events: 0
- Minimum TCP distance: 782.25 mm

## Shape

- Target layer-integrated volume: 6661016.843 mm³
- Deposited volume: 6404024.739 mm³
- Intersection volume: 6403627.331 mm³
- Underfill volume: 257389.467 mm³
- Overfill volume: 397.407 mm³
- Coverage: 96.14%
- Underfill: 3.86%
- Overfill: 0.01%
- IoU: 96.13%
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
