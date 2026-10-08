\# PPO Generalization Performance



\## 1. 실험 목적



Model 01에서 학습한 PPO 정책을 추가 학습 없이 Model 02, 03, 04에 적용하여 새로운 형상에 대한 작업 배정 성능을 평가했다.



각 모델에서 동일한 작업 경로를 사용하여 Greedy와 Constrained PPO의 Makespan을 비교했다.



\## 2. PPO Makespan 개선율



!\[PPO Improvement](./improvement.svg)



\## 3. 작업시간 단축 결과



!\[Time Saved](./time\_saved.svg)



\## 4. 모델별 성능 비교



| 모델 | Greedy (s) | Constrained PPO (s) | 개선율 | Validator |

|---|---:|---:|---:|---|

| Model 02 | 2,468.05 | 2,338.05 | 5.27% | PASS |

| Model 03 | 2,227.78 | 2,205.13 | 1.02% | PASS |

| Model 04 | 113,437.75 | 113,062.00 | 0.33% | PASS |



\## 5. 실험 결과 해석



\- 세 가지 새로운 형상에서 Constrained PPO의 Makespan 개선을 확인했다.

\- Model 02에서 5.27%로 가장 높은 개선율을 기록했다.

\- Model 04에서도 개선이 나타났지만 0.33%로 상대적으로 작았다.

\- 모든 결과는 공식 WAAM Validator에서 PASS를 받았다.



\*\*참고:\*\* TensorBoard 그래프의 Step 2, 3, 4는 학습 단계가 아니라 각각 Model 02, 03, 04를 의미한다.



본 결과는 Safety Filter가 적용된 PPO의 평가이며, 순수 PPO 정책의 독립적인 안전성 또는 충분한 일반화 성능을 입증한 것은 아니다.



\## 6. 향후 계획



Model 05 및 Model 06에서도 동일한 PPO 정책을 평가하고, 대형·복잡 형상에 대한 적용 가능성과 Makespan 개선 효과를 추가 분석할 예정이다.



