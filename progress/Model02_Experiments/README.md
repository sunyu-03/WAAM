# Model 02 | WAAM 경로 생성 및 PPO 작업 할당 최적화

## 1. 실험 개요

**목적:** Model 01에서 개발한 강화학습 기반 작업 할당 알고리즘을 새로운 형상인 Model 02에 적용하고, Greedy 알고리즘과 성능을 비교한다.

- 대상: 교수님 제공 Model 02 STL
- 로봇: 3대
- 적층 레이어: 8개
- 최종 작업 경로: 24개
- 검증 도구: WAAM Validator v1.0.1
- 강화학습 알고리즘: PPO

## 2. 경로 생성 알고리즘의 발전 과정

| 버전 | 개발 내용 | Coverage | IoU | 결과 |
|---|---|---:|---:|---|
| v3 | 내부 축소 Raster | 5.03% | 4.90% | FAIL |
| v4 | Raster 축소 제거 | 93.07% | 59.36% | FAIL |
| v5 | 경로 길이 분포 분석 | 93.07% | 59.36% | FAIL |
| v6 | Centerline 도입 | - | - | 작업 배정 오류 |
| v7 | Centerline + Reach 분할 | **99.14%** | **98.33%** | PASS |

### 문제 1. Raster 경로의 형상 축소

비드 폭을 고려한 내부 축소 과정에서 얇은 구조가 대부분 사라져 Coverage가 약 5%에 머물렀다.

### 문제 2. Raster 경로의 과적층

내부 축소를 제거해 Coverage는 개선했지만 Overfill이 56.80%로 증가했으며, IoU는 59.36%에 그쳤다.

### 문제 3. Centerline 경로의 도달 범위 위반

Centerline을 도입하자 형상을 따라가는 경로를 생성할 수 있었지만, 일부 긴 경로를 단일 로봇에 배정할 수 없었다.

### 최종 해결 방법

Centerline 경로를 로봇 도달 가능 구간으로 분할하는 알고리즘을 적용했다.

그 결과 Coverage 99.14%, IoU 98.33%, 충돌 0건으로 공식 Validator PASS를 달성했다.

## 3. PPO 일반화 및 제약 적용

Model 01에서 학습한 PPO 정책을 추가 학습 없이 Model 02에 적용했다.

첫 번째 평가에서는 PPO가 도달 불가능한 로봇을 선택하여 작업 배정에 실패했다.

이를 개선하기 위해 **Safety Filter**를 도입했다.

- 작업별 도달 가능한 로봇을 계산
- PPO의 로봇 선택 확률을 확인
- 도달 가능한 로봇 중 PPO가 가장 선호하는 로봇을 선택
- 전체 작업에 대해 공식 Validator 검증

총 24개 작업 중 8개에서 Safety Filter가 기존 PPO 선택을 수정했다.

## 4. Greedy vs Constrained PPO

| 평가 지표 | Greedy | Constrained PPO |
|---|---:|---:|
| Makespan | 2,468.05초 | **2,338.05초** |
| Coverage | 99.14% | 99.14% |
| IoU | 98.33% | 98.33% |
| Collision | 0 | 0 |
| Validator | PASS | PASS |

**작업 완료시간 약 130.01초 단축, Greedy 대비 5.27% 개선**

[상세 실험 데이터](./ppo_comparison_summary.json)

## 5. 결론 및 한계

Model 02에서는 Centerline 기반 경로 생성과 도달 가능성 제약을 적용한 PPO를 결합하여 형상 검증과 작업시간 개선을 모두 달성했다.

다만 이 결과는 순수 PPO만의 일반화 성공을 의미하지 않는다. Safety Filter가 개입한 **Constrained PPO** 결과이며, 향후 다양한 형상과 조건에 대한 추가 검증이 필요하다.

또한 Raster 버전과 Centerline 버전의 Makespan 차이는 경로 자체가 달라진 결과이므로 PPO 최적화 효과로 해석하지 않는다.