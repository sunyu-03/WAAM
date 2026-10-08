# WAAM Validator Report

## Overall Result

**PASS**

- WAAM Validator version: 1.0.1

## Input Summary

- Directory: `C:\Users\User\Desktop\AInAlgorithm\sample\0929\code_ver.1\model04_ppo_official_v1\my_job`
- Trajectory rows: 294409
- Target watertight: True

## Schedule

- Makespan: 113062.00 s
- R1: completion 113062.00 s; Deposition 28960.46 s; Travel 1203.00 s; Wait 82898.54 s
- R2: completion 113062.00 s; Deposition 19735.77 s; Travel 1018.79 s; Wait 92307.45 s
- R3: completion 113062.00 s; Deposition 33942.26 s; Travel 1185.72 s; Wait 77934.02 s

## Robot XY Reach

- Passed: True
- R1: max XY distance 1493.36 / 1500.00 mm; XY margin 6.64 mm; violating points 0
- R2: max XY distance 1404.80 / 1500.00 mm; XY margin 95.20 mm; violating points 0
- R3: max XY distance 1433.02 / 1500.00 mm; XY margin 66.98 mm; violating points 0

## Collision

- Arm Envelope events: 0
- Minimum Arm Envelope safety margin: 551.10 mm
- Arm centerline distance at worst case:
  801.10 mm
- Arm required centerline distance at worst case:
  250.00 mm
- TCP_RADIUS events: 0
- Minimum TCP distance: 801.10 mm

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
