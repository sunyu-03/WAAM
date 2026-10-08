# WAAM 범용화 통합 1차 결과 — 2026-10-08

프로젝트: `C:\Users\User\Desktop\AInAlgorithm\waam_generalization`

독립 Git 저장소를 새 폴더에 복제하고 `integration/generalization-20261008` 브랜치를 만들었다. 기준 커밋은 `d584b29a108d1b7d70f88fe730e72b090e018719`이다. 상위 AInAlgorithm 저장소의 sample/test_1, 기존 성공 코드, 체크포인트는 수정하지 않았다. 통합 변경은 `integration/`에만 있다.

## 구현 및 실제 검증

`target.stl/config.yaml → 공식 단면·층 계산 → 첨부 V5 형상 후보 탐색 → 동일 직선 조각 병합 → reach-aware greedy → 공식 WAAM Validator 1.0.1 → trajectory.csv/검증 보고서`를 구현했다. Greedy는 각 로봇 후보의 도달성, 전체 궤적 규칙, 대기·주차 로봇을 포함한 충돌을 검사하고 후보 Makespan이 가장 작은 로봇을 선택한다. 반환 시 home까지 이동하는 보수적 작업 배정 방식이다.

공식 sample_job의 STL/config를 실제 읽어 만든 작업으로 검증했다. 작업 160개가 정확한 직선 병합 후 1개가 되었고, Makespan은 **30.469707263485695초**, 공식 결과는 **PASS**, 충돌 **0건**, reach **PASS**다. 반복 실행의 trajectory.csv도 비교한다. 이 값은 작은 샘플의 결과이며 공개 Model 01~06의 새 범용 알고리즘 결과로 해석하면 안 된다.

단위 검증은 직선 병합, top/center의 층 보존과 TCP 높이, 도달 불가능 로봇 거부를 포함한다. 실행 결과는 `runs/final_sample/run.json`, `runs/final_sample/validation/summary.json`, `runs/final_sample/job/trajectory.csv`에 있다. 실패·중단된 초기 실행 폴더도 남겨 두었다.

## import와 행동공간 분석

- 원본 train.py의 `algorithm.environment.waam_env.WAAMBaselineEnv`는 첨부 자료에 없었다. 통합 폴더에 명시적인 discrete 작업 배정 adapter를 구현하여 해당 import를 해결했다.
- 원본 `task_generater.py`를 `algorithm/preprocessing/task_generator.py`로 정리했다. `generate_tasks`, `build_scenario`를 제공한다. 원본의 top TCP 최상층 누락 가능성을 공식 층 계산으로 수정했다. 형상 단면은 TCP 높이와 분리하여 공식 중간 평면을 사용한다.
- 첨부 gym_wrapper.py는 `WaamGymEnv(job_dir)`이고 `(3,5)` 관측 / `(3,4)` 연속 행동을 사용한다. `from . import env`도 패키지 내 env.py를 요구한다. 원본 그대로 `originals/`에 보존했다.
- 기존 PPO ZIP의 관측은 `(13,)`, 행동은 `Discrete(3)`, 학습은 30,000 timestep/seed 42다. 통합 작업 배정 환경은 작업 수에 따라 관측 길이가 달라지므로 기존 PPO와도 직접 호환되지 않는다.
- 통합 train.py는 의도적으로 학습을 중단한다. 이름을 맞췄다는 이유만으로 PPO를 연결하지 않는다. 기존 checkpoint를 load/save하지 않았다.
- `enviornment.py`는 이전 대화의 복구 가능한 첨부 목록에도 없고 지정 프로젝트에서 찾지 못했다. 해당 원본 분석은 아직 못 했다. 기존 저장소의 environment/env.py와 AssignmentEnv를 분석·활용했다.

## 6개 모델의 기존 성공 기록

아래는 기존 실험의 알려진 최선 값이다. 전역 최적해/최적값을 증명한 결과가 아니며 이번 실행에서 6개 모델을 재검증한 것도 아니다.

| 모델 | Greedy (s) | 기존 PPO (s) | 근거 및 상태 |
|---|---:|---:|---|
| 01 | 1,654.8365 | 1,643.8301 | 로컬 ppo_training_summary와 기존 progress의 PASS 기록 |
| 02 | 2,468.0531 | 2,338.0458 | progress/Model02_Experiments/ppo_comparison_summary.json, 양쪽 PASS |
| 03 | 2,227.7794 | 2,205.1287 | progress/Model03_Experiments/summary.json, 양쪽 PASS |
| 04 | 113,437.75 | 113,062.0021 | progress/Model04_Experiments/ppo_official_summary.json, PPO PASS |
| 05 | 409,508.1900 | 406,350.9116 | 로컬 model05_ppo_official_v1/ppo_comparison_summary.json은 PASS; GitHub dryrun JSON은 NOT_RUN |
| 06 | 7,228.0658 | 7,089.3252 | progress/Model06_Experiments/summary.json, 양쪽 PASS |

체크포인트의 내용도 구분해야 한다. `ppo_model_01.zip`의 SHA256은 `7b6e0bd4b99dcad32d44a35cfcb07871759a7edf8c706e90108c48991b147a32`, `tensorboard_experiment/ppo_model_01.zip`은 `5712a83467ad346e3a275fd71a3ad18737db4a0f9c20eb48e4b2161c9e317d0b`이다. Model06 기록은 두 번째 해시를 참조한다. 기존 결과를 첫 번째 checkpoint의 성능이라고 일괄 단정할 수 없다. 각 실행의 checkpoint 해시, 생성 작업, 입력 해시, 배정, validator 버전을 묶어서 보관해야 한다.

## VS Code 실행

`integration/waam.code-workspace`를 열고 프로젝트 루트에서 터미널을 실행한다. 지금 실제 테스트한 인터프리터는 기존 Validator의 `.venv`이며 추가 패키지는 이 프로젝트의 `integration/.deps`에서만 읽는다. 기존 환경에는 패키지를 설치하지 않았다.

```powershell
& 'C:\Users\User\Desktop\WAAM_Validator-main\.venv\Scripts\python.exe' integration/run_pipeline.py --job TEAM_PROJECT/week1/environment/examples/sample_job --out integration/runs/my_sample_001
& 'C:\Users\User\Desktop\WAAM_Validator-main\.venv\Scripts\python.exe' integration/test_pipeline.py
```

출력 폴더는 매번 새 이름을 사용한다. 같은 폴더에 덮어쓰기를 시도하면 실패한다. 공개 모델을 지정하려면 `--job 'C:\Users\User\Desktop\WAAM_Validator-main\tests\01'`로 바꾼다. 아직 공개 모델 6개 전체의 범용 경로 성공은 검증하지 않았다.

다른 PC에서는 Python 3.13 환경을 만들고 `integration/requirements.txt`의 패키지를 설치한다. Validator 소스는 이 저장소의 `TEAM_PROJECT/week1/environment/src`를 고정해 읽는다. 실제 실행에는 Python 버전, 직접 패키지 버전, 입력·통합 소스 SHA256과 기반 커밋을 저장한다. 모든 간접 의존성/휠 해시까지 고정한 완전한 lock은 후속 작업이다.

## 남은 장애물과 다음 단계

1. enviornment.py 원본 확보 및 팀원의 의도와 비교.
2. 긴 선분이 여러 로봇 reach 영역에 걸칠 때의 자동 분할과 모든 로봇이 불가능한 구간의 명확한 진단. 현재는 후보를 거부하며 무리하게 배정하지 않는다.
3. 복잡한 단면에서 형상 후보가 전부 실패하면 경로 생성을 중단한다. 6개 공개 모델의 범용 생성·공식 검증, 특히 Model04/05의 대규모 작업에 대한 캐시·성능 개선이 필요하다. 현재 후보마다 누적 전체 궤적을 검사하는 환경은 대형 모델에 비용이 크다.
4. 고정 크기 관측·작업 마스크·Discrete 로봇 배정 의미와 reward를 확정한 뒤 PPO를 연결한다. checkpoint에는 환경 계약, 소스, 설정, seed, 학습 step, optimizer 상태, 평가 기록을 함께 관리한다.
5. 각 모델의 검증된 최선 trajectory/값과 checkpoint 증거를 분리하여 제출한다. 최적성 증명이 없으면 best-known으로 표기한다. GitHub 제출 전에 Model05의 상충 기록과 모든 입력/STL·코드/모델의 대응을 정리한다. 현재 원격 main에는 변경을 올리지 않았다.

기존 checkpoint 목록과 첨부 원본 및 결과 JSON의 해시는 `source_inventory.json`에서 확인할 수 있다. 원본 ZIP 안의 메타데이터만 읽었으며 pickle 객체는 실행하지 않았다.
