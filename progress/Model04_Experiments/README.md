# Model 04 | Hybrid Toolpath 개발 및 PPO 평가



## 1. 실험 목적



다중 연결 영역과 넓은 내부 단면을 가진 Model 04에 기존 경로 생성 알고리즘을 적용하고, 형상 정확도와 작업시간을 개선한다.



- 대상: Model 04

- 적층 레이어: 50개

- 로봇: 3대

- 검증 도구: WAAM Validator v1.0.1



## 2. 기존 Centerline 알고리즘의 한계



Model 02·03에서 성공한 Centerline 알고리즘을 Model 04에 적용했으나 공식 Validator에서 FAIL이 발생했다.



| 지표 | Centerline v1 |
|---|---:|
| Coverage | 29.12% |
| Underfill | 70.88% |
| IoU | 29.12% |
| Collision | 0 |
| Validator | FAIL |



넓은 내부 영역을 충분히 적층하지 못하는 것이 주요 실패 원인으로 분석되었다.



## 3. Hybrid Toolpath 도입



기존 Centerline에 Raster Infill을 결합하여 미적층 영역을 보완했다.



**개선 과정**



1. Centerline 단독 경로 생성

2. Raster Infill 추가 (8mm 간격)

3. Raster 간격 6mm로 조정

4. 50개 레이어 전체 사전 형상 검사

5. 공식 Validator 검증



Raster 간격을 6mm로 조정한 결과, 사전 계산에서 50개 레이어 모두 IoU 90% 이상을 기록했다.



## 4. 공식 Validator 결과



| 평가 지표 | Centerline v1 | Hybrid v2 |
|---|---:|---:|
| Coverage | 29.12% | **96.14%** |
| IoU | 29.12% | **96.13%** |
| Collision | 0 | 0 |
| Validator | FAIL | **PASS** |



Hybrid 방식의 도입으로 형상 검증 기준을 충족했다.



[공식 Validator 상세 보고서](./validation_report.md)



## 5. Constrained PPO Dry Run



Model 01에서 학습한 PPO 정책을 재학습 없이 Model 04의 작업 배정에 적용했다.



| 평가 지표 | 결과 |
|---|---:|
| 총 작업 수 | 13,508개 |
| Greedy Makespan | 113,437.75초 |
| Constrained PPO Makespan | 113,062.00초 |
| Makespan 개선율 | **0.33%** |
| Safety Filter 개입 | 120회 |



Greedy 대비 예상 작업시간을 약 375.75초 단축했다.



[Dry Run 상세 결과](./ppo_dryrun_summary.json)



## 6. 한계 및 향후 계획



- Hybrid 방식은 형상 정확도를 개선했지만 경로 길이와 작업시간이 증가했다.

- PPO Dry Run에서 작업시간 개선이 나타났으나, PPO 결과의 공식 Validator 검증은 별도로 필요하다.

- 현재는 순차 작업 스케줄을 사용하고 있으므로 병렬 작업 최적화가 향후 과제다.

- Model 05·06까지 적용 범위를 확장하고 새로운 STL에 대한 일반화 성능을 추가 검증할 예정이다.



## 7. Constrained PPO 공식 검증 완료



기존 Model 01에서 학습한 PPO 정책을 추가 학습 없이 Model 04에 적용했다. 도달 가능성 제약을 적용하기 위해 Safety Filter를 함께 사용했다.



### 최종 결과



| 평가 지표 | Greedy | Constrained PPO |
|---|---:|---:|
| Makespan | 113,437.75 s | 113,062.00 s |
| Coverage | 96.14% | 96.14% |
| IoU | 96.13% | 96.13% |
| Collision Events | 0 | 0 |
| Validator | PASS | PASS |



**Greedy 대비 약 375.75초(0.33%) 작업시간 단축**



총 13,508개 작업 중 120개에서 Safety Filter가 개입했다.



본 실험에서는 Model 01에서 학습한 정책을 다른 형상에 적용하여 작업시간 개선을 확인했다. 단, Constrained PPO를 사용했으며 단일 학습 정책에 대한 평가이므로 일반화 성능을 충분히 입증하려면 추가 검증이 필요하다.



[공식 PPO 결과](./ppo_official_summary.json)



[공식 PPO Validator 보고서](./ppo_validation_report.md)



