# WAAM 다중 로봇 작업 배정 및 Makespan 최적화 — 진행 기록

> **1차 실험 정리 | 2026-10-08**  
> 3대 로봇의 WAAM(Wire Arc Additive Manufacturing) 작업을 대상으로, STL 형상별 적층 경로를 생성하고 로봇 도달 가능성·형상 정확도·충돌 조건을 확인한 뒤 작업 완료시간(Makespan)을 최소화하는 프로젝트입니다.

## 한눈에 보는 진행 상황

- **Model 01~05:** 모델별 실험 수행 및 공식 WAAM Validator PASS 기록 확보
- **Model 02~05:** Model 01에서 학습한 PPO 정책을 *재학습 없이* 적용하고 Greedy 대비 Makespan 감소 확인
- **경로 생성:** 얇은 벽의 Centerline → 넓은 면적을 위한 Hybrid → 대형 형상의 Raster-only로 발전
- **안전 제약:** 로봇의 XY 도달 범위를 확인하는 Safety Filter 도입; Model 05에는 별도의 **5 mm 도달 여유 제약** 적용
- **시각화:** TensorBoard 학습 지표와 모델별 PPO 일반화 평가를 GitHub에 기록
- **다음 목표:** Model 06 형상 분석 및 Greedy/PPO 공식 검증

## 1. 모델별 최종 성과

| 모델 | 채택한 경로 생성 방식 | 레이어 / 작업 경로 | Greedy Makespan | Constrained PPO Makespan | 단축률 | Validator |
|---|---|---:|---:|---:|---:|---|
| [01](./PPO_Model01/README.md) | Honeycomb 기준 실험 | 작업 30개 | 1,654.84 s | **1,643.83 s** | **0.67%** | PASS (기존 실험) |
| [02](./Model02_Experiments/README.md) | Centerline + Reach 분할 | 8층 / 24개 | 2,468.05 s | **2,338.05 s** | **5.27%** | 양쪽 PASS |
| [03](./Model03_Experiments/README.md) | Centerline + Reach 분할 | 6층 / 144개 | 2,227.78 s | **2,205.13 s** | **1.02%** | 양쪽 PASS |
| [04](./Model04_Experiments/README.md) | Centerline + Raster Hybrid | 50층 / 13,508개 | 113,437.75 s | **113,062.00 s** | **0.33%** | 양쪽 PASS |
| [05](./Model05_Experiments/README.md) | Raster-only + Reach-aware Greedy | 350층 / 75,868개 | 409,508.19 s | **406,350.91 s** | **0.77%** | 양쪽 PASS* |
| 06 | 형상 분석 및 알고리즘 선정 예정 | — | — | — | — | 미진행 |

**Makespan**은 시뮬레이션상 전체 작업 완료시간(초)입니다. 서로 다른 모델은 형상과 작업 수가 다르므로, **모델 간 절대 시간보다 같은 모델 안에서의 Greedy–PPO 비교**에 의미가 있습니다.

\* Model 05의 **PPO 공식 PASS**는 2026-10-08 로컬 WAAM Validator 실행 결과로 확인했습니다(Coverage 및 IoU 약 91.14%, 충돌 0건). 현재 GitHub의 Model 05 개별 README/JSON에는 구버전의 ‘검증 진행 중’·‘NOT_RUN’ 기록이 남아 있어, **최신 공식 검증 요약과 보고서 업로드가 후속 작업**입니다. 이 표는 로컬 최종 결과를 반영합니다.

## 2. 개발·개선 과정

### Model 01 — PPO 학습 기반 구축

- Honeycomb 형상의 **30개 작업 / 3대 로봇** 배정을 위한 PPO 강화학습 환경 구현
- 학습 설정: **30,000 timesteps, seed 42, 관측값 13개, 로봇 선택 행동 3개, MLP [64, 64]**
- TensorBoard에서 **Reward, Episode Length, Value Loss**를 기록
- 기존 기준 실험에서 Makespan **0.67% 단축** 및 Validator PASS 보고

[Model 01 학습 과정과 그래프 보기](./PPO_Model01/README.md)

### Model 02 — 실패 분석을 통한 Centerline·Safety Filter 도입

1. 내부 축소 Raster는 얇은 벽을 충분히 채우지 못해 **Coverage 5.03%**로 FAIL.
2. 축소 없는 Raster는 Coverage가 높아졌지만 과적층으로 **IoU 59.36%**에 그쳐 FAIL.
3. Centerline으로 형상 추종 문제를 개선했으나 긴 경로의 로봇 도달 범위 위반 발생.
4. **Centerline 분할 + Reach-aware Greedy**로 Coverage **99.14%**, IoU **98.33%**, 충돌 **0건**, 공식 PASS.
5. PPO가 도달 불가능한 로봇을 선택한 문제는 **Safety Filter**로 해결. 24개 작업 중 8개 선택 변경, 작업시간 **5.27% 단축** 및 공식 PASS.

[Model 02 실험 기록](./Model02_Experiments/README.md)

### Model 03 — 복잡한 내부 구조로 확장

- 내부 구멍이 많은 형상에 Model 02의 Centerline 접근법을 적용
- **6층, 144개 경로**, Coverage **98.66%**, IoU **98.16%**, 충돌 **0건**
- 추가 학습 없이 PPO 평가: **1.02% Makespan 개선**, Greedy·PPO 공식 PASS

[Model 03 실험 기록](./Model03_Experiments/README.md)

### Model 04 — 넓은 내부 면적의 미적층 문제 해결

- Centerline 단독 시 **Coverage/IoU 약 29.12%**, 공식 FAIL
- **Centerline + Raster Infill (Hybrid)**로 전환하고 간격을 조정
- 최종 공식 검증: Coverage **96.14%**, IoU **96.13%**, 충돌 **0건**, PASS
- **13,508개 작업**에 동결된 PPO 정책 및 Safety Filter 적용: **120회 개입**, Makespan **0.33% 개선**, 공식 PASS

[Model 04 실험 기록과 검증 보고서](./Model04_Experiments/README.md)

### Model 05 — 대형 형상과 반복 계산 최적화

- **350층, 75,868개 경로**의 대형 STL 형상
- Centerline 단독의 낮은 사전 형상 충전율 확인 → Hybrid/Raster 간격 비교 → **Raster-only 5.5 mm** 채택
- 350층 사전 형상 검사: 평균 IoU **91.21%**, 최저 **90.66%**, 90% 미만 **0층**
- 도달 가능성 확인 후 **최소 5 mm XY Reach 여유**를 둔 Greedy 배정: fallback **0건**
- Greedy 공식 Validator **PASS**: Coverage/IoU 약 **91.14%**, 충돌 **0건**
- 원본 작업 경로를 별도 캐시에 저장하여 STL 슬라이싱과 경로 생성을 반복하지 않고 **75,868개 동일 경로를 PPO에 재사용**
- 기존 Model 01 PPO 정책에 5 mm Reach Safety Filter 적용: **217회 개입**, 최소 도달 여유 **5.425 mm**
- PPO 공식 Validator **PASS**: Makespan **409,508.19 → 406,350.91 s**, **약 3,157.28초(52분 37초), 0.77% 단축**; Coverage/IoU 약 **91.14%**, 충돌 **0건**

[Model 05 실험 기록 및 기존 업로드 자료](./Model05_Experiments/README.md)

## 3. PPO 학습 설계 — 하이퍼파라미터, 상태·행동, 보상함수

> **자료 출처 및 확인 범위:** Model 01의 학습 횟수·시드·관측/행동 차원·신경망 구조는 [Model 01 실험 기록](./PPO_Model01/README.md)에 명시되어 있습니다. 아래의 **추가 하이퍼파라미터 및 구체적인 보상식은 기존 실험 설명을 정리한 값**으로, 현재 공개 저장소에는 원본 Model 01 학습 스크립트가 없어 **코드와 최종 대조가 필요합니다.** 학습 중의 Reward 그래프만으로 보상식의 계수를 검증할 수는 없습니다.

### 3.1 PPO 학습의 목적

Model 01의 Honeycomb 형상에서 **3대 로봇에 적층 작업을 순서대로 배정**하는 정책을 학습했습니다. 경로 생성기 자체를 학습한 것이 아니라, 이미 생성한 각 경로에 대해 **어느 로봇을 배정할지** 결정하는 문제입니다.

- **상태(State / Observation):** 현재 작업의 위치·길이, 진행도, 로봇의 누적 부하, 로봇과 작업 사이 거리 등
- **행동(Action):** 로봇 1·2·3 중 하나 선택 → \`Discrete(3)\`
- **보상(Reward):** 불가능한 배정을 억제하고, 작업 완료와 짧은 Makespan을 장려
- **평가(Evaluation):** 학습된 정책을 Model 02~05에 **재학습 없이** 적용한 뒤, 동일 경로에서 Greedy와 비교하고 WAAM Validator로 검증

### 3.2 하이퍼파라미터 (Hyperparameters)

하이퍼파라미터는 학습 도중 정책이 스스로 찾아내는 값이 아니라, **학습을 시작하기 전에 지정하는 설정값**입니다.

| 항목 | 값 | 역할·선택 이유 | 확인 상태 |
|---|---:|---|---|
| 총 학습 단계 (Total timesteps) | **30,000** | 환경에서 행동·보상을 수집하며 학습하는 총 단계 수 | GitHub 기록 확인 |
| 난수 시드 (Seed) | **42** | 재현 가능한 비교를 위한 난수 초기화 | GitHub 기록 확인 |
| 관측 차원 (Observation dimension) | **13** | 작업 및 로봇별 부하·거리 정보를 정책에 입력 | GitHub 기록 확인 |
| 행동 공간 (Action space) | **Discrete(3)** | 3대 로봇 중 하나를 선택 | GitHub 기록 확인 |
| 정책 신경망 (Policy network) | **MLP [64, 64]** | 64개 뉴런을 가진 은닉층 2개 사용 | GitHub 기록 확인 |
| 학습률 (Learning rate) | 0.0003 | 정책 파라미터를 업데이트하는 크기; 너무 크면 불안정, 너무 작으면 학습이 느릴 수 있음 | 원본 코드 재확인 필요 |
| Rollout 길이 (\`n_steps\`) | 300 | PPO 업데이트 전에 환경에서 수집하는 단계 수 | 원본 코드 재확인 필요 |
| 미니배치 크기 (Batch size) | 60 | 모은 데이터를 나눠 최적화할 때 사용하는 묶음 크기 | 원본 코드 재확인 필요 |
| 할인율 (\`gamma\`, γ) | 0.99 | 이후에 받는 보상까지 고려하는 정도 | 원본 코드 재확인 필요 |
| GAE 계수 (\`gae_lambda\`, λ) | 0.95 | Advantage 추정의 편향·분산을 조절 | 원본 코드 재확인 필요 |
| 엔트로피 계수 (\`ent_coef\`) | 0.02 | 초기 학습에서 다양한 로봇 선택을 탐색하도록 장려 | 원본 코드 재확인 필요 |

위 값들이 **최적값임을 증명한 하이퍼파라미터 튜닝 실험은 수행하지 않았습니다.** 서로 다른 시드, 보상 가중치, 학습률 등에 대한 비교가 후속 과제입니다.

### 3.3 상태(Observation) 13개와 행동(Action) 3개

Model 02~05 평가에서 사용한 **동결 PPO 정책의 13개 입력 특성**은 다음과 같습니다.

| 특성 | 차원 | 의미 |
|---|---:|---|
| 전체 작업 진행도 | 1 | 현재 작업 인덱스 / 전체 작업 수 |
| 경로 중심의 X, Y 좌표 | 2 | 작업 위치 |
| 경로 길이 | 1 | 현재 작업 규모 |
| 로봇별 누적 경로 길이 | 3 | 로봇 1·2·3에 이미 배정한 작업량 |
| 로봇별 누적 작업 개수 | 3 | 로봇 1·2·3의 배정 횟수 |
| 경로 중심부터 로봇 베이스까지 거리 | 3 | 로봇 1·2·3과 현재 작업 사이 거리 |
| **합계** | **13** | 정책 네트워크의 입력 |

이 특성들은 코드에서 정해진 기준값으로 정규화한 후 정책에 전달됩니다. 정책은 각 로봇의 선택 확률을 출력합니다. **원본 학습 환경도 위 특성과 정규화를 동일하게 사용했는지는 학습 스크립트에서 최종 확인해야 합니다.**

### 3.4 보상함수(Reward Function) 설계

보상은 **단계별 보상(step reward)**과 **종료 보상(terminal reward)**으로 구분됩니다. 다음 수식과 계수는 **기존 Model 01 실험 설명에 기반한 정리이며 원본 학습 코드 확인 전까지 잠정 값**입니다.

**① 도달 불가능한 로봇 배정에 대한 패널티**

- 해당 로봇이 경로를 수행할 수 없는 경우 **−10**의 패널티를 부여하고 에피소드를 종료하도록 설계한 것으로 기록되어 있습니다.
- 짧은 작업시간보다 *실행 가능성*을 우선하도록 학습시키려는 목적입니다.

**② 각 작업에서 이동거리와 부하 불균형에 대한 패널티**

$
R_{\text{step}}
=
-0.02\frac{d}{1500}
-0.02\frac{\sigma(L)}{420}
$

- \`d\`: 선택한 로봇과 현재 작업 사이 거리
- \`\sigma(L)\`: 세 로봇 누적 작업량의 표준편차
- 거리나 부하 불균형이 커질수록 보상이 작아지는 구조입니다.

예시: \`d = 750 mm\`, \`\sigma(L) = 42\`이면 단계 보상은 \`−0.012\`입니다. **이는 수식 설명을 위한 예시이지 실험 로그에서 추출한 값은 아닙니다.**

**③ 모든 작업을 정상 완료했을 때 Makespan 중심의 종료 보너스**

$
R_{\text{terminal}}
=
2+10\left(
\frac{T_{\text{baseline}}-T_{\text{final}}}
{T_{\text{baseline}}}
\right)
$

- \`T_baseline\`: 기준 Greedy Makespan
- \`T_final\`: PPO 배정 결과 Makespan
- 정상 완료 보너스에 **Greedy 대비 완료시간 단축률**을 반영하려는 구조입니다.

예를 들어 Greedy가 1,000초, PPO가 900초라면 종료 보너스는 \`2 + 10 × 0.1 = 3\`입니다. 실제 에피소드 보상에는 각 단계의 보상·패널티도 영향을 미칩니다.

### 3.5 학습 보상과 실행 안전성은 별개 — Safety Filter

**학습 중에 큰 패널티를 주었다고 해서 새로운 형상에서 모든 제약을 반드시 지키는 것은 아닙니다.** 실제 Model 02에서는 동결 PPO가 도달할 수 없는 로봇을 우선 선택하여 배정에 실패하는 문제가 있었습니다.

이를 해결하기 위해 평가 단계에서 다음 절차를 적용했습니다.

1. 각 경로에 대해 **끝점을 포함한 경로 전체가 로봇 XY 도달 범위 안에 있는지** 검사
2. PPO 정책이 출력한 3대 로봇의 선택 확률 계산
3. **실행 가능한 로봇 중 PPO 확률이 가장 높은 로봇**을 최종 선택
4. 전체 궤적에 대해 공식 WAAM Validator의 **Reach·Collision·Coverage·IoU** 검증 수행

Model 05에서는 여기에 **로봇 도달 반경보다 5 mm 안쪽에서 작업할 것**이라는 추가 여유 조건을 적용했습니다. 이 5 mm는 프로젝트에서 지정한 보수적 여유값이며 실제 로봇의 안전 인증 기준은 아닙니다.

**해석상 주의:** 현재 결과는 **Safety Filter를 결합한 Constrained PPO**의 결과입니다. *순수 PPO 정책이 단독으로 안전성을 보장했다*는 결론이나 *모든 형상에 일반화가 입증됐다*는 결론으로 해석하지 않습니다.

### 3.6 TensorBoard 학습 결과와 추후 검증

[Model 01 TensorBoard 기록](./PPO_Model01/README.md)에 Reward, Episode Length, Value Loss 그래프가 정리되어 있습니다. 이는 **학습 중 어떤 수치가 어떻게 변했는지**를 보여주는 자료이며, Model 02~05의 **형상별 Makespan 평가**와는 서로 다른 실험 단계입니다.

> **별도 환경 주의:** [TEAM_PROJECT/week1/assignment_env.py](../TEAM_PROJECT/week1/assignment_env.py)의 보상식은 성공 시 \`1.0\` 보너스와 \`−(makespan 증가량)/time_scale\`을 사용하고, 불가능한 행동에 \`−2.0\`을 부여하는 **다른 환경**의 구현입니다. 이 수치를 위 Model 01 보상식과 혼동하면 안 됩니다.

**최종 발표 전 확인할 자료:** Model 01 원본 학습 Python 파일의 \`PPO(...)\` 설정값 및 \`step()\` 내 보상 계산식. 확인되면 이 섹션의 '원본 코드 재확인 필요' 표시를 실제 코드 기준으로 갱신합니다.

## 4. PPO 평가 원칙과 해석

- **동결된 정책(Frozen PPO):** Model 01에서 학습된 PPO를 Model 02~05에 추가 학습 없이 적용했습니다.
- **동일 경로 비교:** 각 모델 내에서 Greedy와 PPO가 같은 작업 경로를 사용하도록 구성해 경로 생성 방식의 차이와 작업 배정 효과를 구별했습니다.
- **Constrained PPO:** 로봇의 도달 가능성을 확인한 뒤 PPO 확률이 가장 높은 **실행 가능한 로봇**을 선택합니다. 따라서 결과는 *Safety Filter를 포함한 PPO 시스템*의 성과이지 순수 PPO의 독립적인 안전성 입증이 아닙니다.
- **Dry Run과 공식 검증 구별:** 예상 Makespan 계산만으로 PASS라고 판단하지 않고, 가능한 경우 공식 WAAM Validator로 형상 품질·Reach·충돌을 검증했습니다.
- **한계:** 특정 형상들과 단일 학습 정책에 대한 평가입니다. 실제 장비 안전성, 일반적인 모든 형상에 대한 성능, 병렬 로봇 운영 최적화가 보장되는 것은 아닙니다.

## 5. TensorBoard 및 결과 시각화

학습 과정과 다른 형상에서의 성능 평가를 구분했습니다.

- **PPO 학습 지표:** [Model 01 Reward · Episode Length · Value Loss](./PPO_Model01/README.md)
- **일반화 평가:** [Greedy vs Constrained PPO 비교 대시보드](./PPO_Generalization/README.md)

![PPO Makespan 개선율 — Model 02~04 기록 그래프](./PPO_Generalization/improvement.svg)

*위 TensorBoard 그래프는 업로드 당시의 **Model 02~04**만 포함합니다. Model 05의 공식 PASS 결과는 상단 표에 반영했으며, 그래프 추가는 후속 작업입니다. 그래프의 Step 2·3·4는 학습 스텝이 아니라 모델 번호입니다.*

## 6. 자료 위치

| 경로 | 내용 |
|---|---|
| [PPO_Model01](./PPO_Model01/) | PPO 학습 기록 및 TensorBoard 그래프 |
| [Model02_Experiments](./Model02_Experiments/) | Raster 실패 분석, Centerline, Safety Filter, 공식 비교 |
| [Model03_Experiments](./Model03_Experiments/) | 복잡한 내부 형상 일반화 평가 |
| [Model04_Experiments](./Model04_Experiments/) | Hybrid 경로, 공식 검증·PPO 결과 |
| [Model05_Experiments](./Model05_Experiments/) | 350층 사전 검사, Reach 사전 검사, 경로 계획, PPO Dry Run |
| [PPO_Generalization](./PPO_Generalization/) | 모델별 비교 그래프와 평가 표 |

실험 원본 STL/config, 개발 중인 로컬 코드, 대용량 trajectory 및 PPO 체크포인트는 **GitHub에 모두 포함되어 있지 않을 수 있습니다.** 저장소 내 자료와 로컬 최종 검증 결과의 차이는 위에서 별도로 표시했습니다.

## 7. 다음 작업 (Model 06 및 기록 마무리)

- [x] Model 01 PPO 학습 및 기록
- [x] Model 02·03 Greedy/PPO 공식 검증
- [x] Model 04 Hybrid 경로 및 Greedy/PPO 공식 검증
- [x] Model 05 Raster-only Greedy 공식 검증
- [x] Model 05 Constrained PPO 공식 검증 (2026-10-08 로컬 결과)
- [ ] **Model 05 최신 PPO 공식 결과 JSON·Validator 보고서 업로드 및 개별 README 갱신**
- [ ] **TensorBoard 일반화 비교 그래프에 Model 05 추가**
- [ ] **Model 06:** STL/config 형상 분석 → 적절한 경로 생성 → Greedy 공식 검증 → 동결 PPO 평가·공식 검증
- [ ] 발표 자료: 모델별 실패 원인, 알고리즘 전환 이유, Validator PASS 근거 및 Makespan 비교 정리

---

**작성 기준일:** 2026-10-08 · **실험 단계:** Model 01~05 완료, Model 06 준비 중  
이 문서는 각 실험 폴더와 검증 자료로 이동하기 위한 **progress 메인 인덱스**입니다.
