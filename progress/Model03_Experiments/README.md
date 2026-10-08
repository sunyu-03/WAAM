# Model 03 | 복잡한 내부 구조에 대한 알고리즘 확장



## 1. 실험 목적



Model 02에서 개발한 Centerline 기반 경로 생성 및 Constrained PPO 알고리즘을 내부 구멍이 많은 새로운 형상에 적용하여 성능을 평가한다.



**이번 실험은 기존 알고리즘을 별도로 재학습하지 않고 새로운 형상으로 확장했다는 점에 의미가 있다.**



## 2. 형상 및 실험 조건



| 항목 | 내용 |
|---|---|
| 대상 형상 | Model 03 |
| 적층 레이어 | 6개 |
| 최대 내부 구멍 | 9개 |
| 레이어당 작업 경로 | 24개 |
| 총 작업 경로 | 144개 |
| 로봇 수 | 3대 |
| 경로 생성 | Centerline + Reach 분할 |
| 작업 배정 | Greedy / Constrained PPO |



## 3. 경로 생성 결과



Model 02에서 개발한 Centerline 기반 알고리즘을 Model 03에 적용했다.



별도의 경로 생성 방식 변경 없이 `trajectory.csv` 생성에 성공했으며, 공식 Validator에서 다음 결과를 얻었다.



- Coverage: **98.66%**

- IoU: **98.16%**

- 충돌 이벤트: **0건**

- Validator: **PASS**



이를 통해 기존 경로 생성 방식이 Model 03의 복잡한 내부 구조에도 적용 가능함을 확인했다.



## 4. PPO 작업시간 비교



Model 01에서 학습한 PPO 정책을 재학습 없이 적용하고, 동일한 Centerline 경로에 대해 Greedy와 성능을 비교했다.



| 평가 지표 | Greedy | Constrained PPO |
|---|---:|---:|
| Makespan | 2,227.78초 | **2,205.13초** |
| Coverage | 98.66% | 98.66% |
| IoU | 98.16% | 98.16% |
| Collision | 0 | 0 |
| Validator | PASS | PASS |



**작업 완료시간 약 22.65초 단축, Greedy 대비 1.02% 개선**



[상세 실험 데이터](./summary.json)



## 5. Model 02와 비교



| 항목 | Model 02 | Model 03 |
|---|---:|---:|
| 총 작업 수 | 24 | 144 |
| Constrained PPO 개선율 | 5.27% | 1.02% |
| Coverage | 99.14% | 98.66% |
| IoU | 98.33% | 98.16% |
| Validator | PASS | PASS |



Model 03은 Model 02보다 작업 경로 수가 많았지만, 기존 정책을 사용하여 공식 Validator PASS와 작업시간 개선을 확인했다.



다만 개선율은 Model 02보다 작게 나타났다.



## 6. 결론 및 향후 과제



새로운 형상에서 Centerline 기반 경로 생성기의 적용 가능성과 Constrained PPO의 작업시간 개선 효과를 확인했다.



그러나 두 형상에 대한 결과만으로 충분한 범용성을 입증했다고 보기는 어렵다.



향후 Model 04~06의 서로 다른 형상 구조에서도 경로 생성, 안전 제약, 작업시간 최적화 성능을 검증할 예정이다.


