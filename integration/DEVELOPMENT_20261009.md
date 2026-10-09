# WAAM 범용 파이프라인 개발 결과 — 2026-10-09

후속 PPO 학습 연결 결과는 [PPO_20261009.md](PPO_20261009.md)를 확인한다. 아래는 PPO 연결 전 6개 모델의 Greedy 파이프라인 기록이다.

저장 위치는 `C:\Users\User\Desktop\AInAlgorithm\waam_generalization`이다. 기존 팀원 파일, 원본 첨부, 성공 코드와 두 PPO 체크포인트를 보존하고 별도 통합 브랜치에서 개발했다.

## 코드에서 볼 부분

- `run_pipeline.py`: 실제 실행 진입점. 작업 생성 또는 저장 작업 로드, 배정, 공식 검증과 실행 기록 저장.
- `algorithm/preprocessing/task_generator.py`: 공식 STL 층·단면 추출, 형상 후보 탐색, 직선 병합, 조건을 다시 검사하는 경로·전략 재사용.
- `algorithm/preprocessing/reach.py`: 로봇의 원형 XY reach와 선분의 교차를 계산하여 안전 여유 1mm를 둔 구간 분할. 어떤 로봇도 담당할 수 없는 구간은 좌표를 표시하고 중단.
- `algorithm/serial_scheduler.py`: 작업별 홈 복귀 기준 방식과, 층 안에서 위치를 유지하는 최근접 작업 순서 배정. 한 번에 한 로봇을 이동하며 다른 로봇은 홈에서 대기한다. 각 이동·적층 후보 및 마지막 홈 복귀를 공식 검사하고, 전체 출력은 다시 공식 Validator로 검증한다.
- `algorithm/environment/waam_env.py`: 누락된 WAAMBaselineEnv adapter와 현재 작업 후보 검사 캐시. 기존 AssignmentEnv는 수정하지 않았다.
- `run_models.py`: 원하는 공개 모델들을 새 결과 폴더에 차례로 실행하고 matrix.json을 만드는 진입점.
- `train.py`: PPO 계약이 맞지 않는 상태에서 학습을 잘못 시작하지 않도록 중단한다. 실제 학습을 수행하는 파일로 해석하면 안 된다.

## 실제 검증과 재현

7개 테스트가 통과했다. 직선 형상 보존, 서로 다른 reach 영역에 걸친 선분 분할, 도달 불가능 구간·접선의 거부, top/center 층 및 높이, 도달 불가능 로봇 거부, 4개 작업의 층별 경로에 대한 공식 PASS를 검사한다.

초기 Model01의 전체 6층에 대해 동일한 저장 작업으로 배정 방식을 비교했다. 작업마다 홈에 복귀하는 방식은 약 44,997.96초, 층별 위치 유지 방식은 853.951917초였고 두 방식 모두 공식 PASS였다. 초기 버전의 재실행 CSV는 바이트 단위로 동일함을 확인했다. 이후 도달 여유를 배정에도 적용하고 최근접 탐색을 개선한 최종 결과는 다음 표다. 최종 버전은 Model05를 포함한 6개 모델 모두에서 실행 중 소스 변경 없이 PASS를 받았다.

| 모델 | 층 | 작업 수 | Makespan (s) | Coverage | IoU | 최소 reach 여유 (mm) | 결과 |
|---|---:|---:|---:|---:|---:|---:|---|
| 01 | 6 | 2,442 | 854.33 | 95.92% | 92.16% | 1.284 | PASS |
| 02 | 8 | 7,088 | 2,379.23 | 98.65% | 94.32% | 1.787 | PASS |
| 03 | 6 | 3,894 | 1,489.38 | 97.14% | 93.60% | 1.758 | PASS |
| 04 | 50 | 4,450 | 48,267.64 | 94.24% | 94.10% | 1.663 | PASS |
| 05 | 350 | 64,919 | 243,307.63 | 93.12% | 90.73% | 1.002 | PASS |
| 06 | 51 | 775 | 5,563.40 | 95.25% | 95.25% | 38.165 | PASS |

충돌은 모든 모델에서 0건이며, 전체 reach와 형상 검사를 통과했다. 표의 초 단위 값은 제작 경로의 Makespan이다. 프로그램의 실제 실행 시간과 구분해야 한다. Model05의 저장 작업 배정·공식 검증 실행은 이 환경에서 약 962초가 걸렸다.

공식 결과 표는 `benchmark_results.json` 및 `benchmark_results.csv`를 확인한다. 생성만 끝난 결과는 GENERATED_NOT_VALIDATED이며 PASS로 집계하지 않는다. 각 결과에는 task 목록, trajectory.csv, 공식 summary.json/validation_report.md, 입력 SHA256, 패키지 버전과 소스 해시가 있다. 실행 중 소스가 바뀌었는지도 표시한다. 초기 개발 과정의 일부 실행은 이 표시가 true이며, 저장된 정확한 task 목록으로 최종 배정·검증을 재실행할 수 있다. 소스 변경 감지 이전 실행은 해당 필드가 없다.

원래 성공 코드의 Model02 PPO 궤적은 현재 공식 Validator로 다시 검증해 PASS, 2,338.0458초를 확인했다. STL/config도 새 Model02 입력과 바이트 단위로 동일하다. 이 값은 새 범용 기준의 2,379.2277초보다 짧으므로 기존 해를 보존한다. 모델 번호별 전용 분기 없이 새 입력 파이프라인을 구현했다는 점과 특정 기존 알고리즘보다 빠르다는 주장을 구분해야 한다. 다른 모델에서도 생성 경로와 Coverage·IoU가 바뀌므로 PPO 정책의 우열을 직접 비교하는 실험이 아니다. 이 결과는 검증된 실행 가능 해이며 전역 최적해를 증명하지 않는다.

정확한 입력과 작업·CSV·보고서는 evidence/20261009/01~06에 보관했다. benchmark_index.json에는 상대 경로와 SHA256이 있다. runtime.lock은 실제 Python 3.13 Windows 실행 환경의 67개 패키지 버전을 기록한 스냅샷이다. 새 PC의 독립 환경 설치 및 휠 해시 고정까지 검증한 것은 아니다.

## VS Code에서 실행

현재처럼 integration 폴더를 열었다면 run_pipeline.py 또는 run_models.py를 클릭해서 코드를 볼 수 있다. 터미널도 integration 폴더에서 열고 다음을 실행한다. 결과 폴더 이름은 매번 새 이름을 사용한다.

```powershell
& 'C:\Users\User\Desktop\WAAM_Validator-main\.venv\Scripts\python.exe' .\run_pipeline.py --job 'C:\Users\User\Desktop\WAAM_Validator-main\tests\01' --out .\runs\my_model01_001 --scheduler layer
```

코드 워크스페이스 파일 `waam.code-workspace`를 열면 F5의 `WAAM: Model 01 공식 검증` 설정을 사용할 수 있다. 디버그 설정 자체의 F5 UI 실행은 이번 작업에서 직접 조작하지 않았으며, 같은 실행 인자는 터미널에서 검증했다.

6개 모델을 모두 새로 생성·검증하려면 다음 명령을 사용한다. Model05는 350층이며 오래 걸릴 수 있다.

```powershell
& 'C:\Users\User\Desktop\WAAM_Validator-main\.venv\Scripts\python.exe' .\run_models.py --out .\runs\all_models_001
```

이번에 저장한 task 목록을 재사용해서 배정·공식 검증을 반복하려면 다음을 사용한다. STL/config는 지정 모델 폴더에서 읽고 최종 Validator도 다시 실행한다.

```powershell
& 'C:\Users\User\Desktop\WAAM_Validator-main\.venv\Scripts\python.exe' .\run_models.py --reuse-index .\benchmark_index.json --out .\runs\replay_all_001
```

## 남은 단계

PPO는 아직 연결하지 않았다. 기존 체크포인트는 centroid XY/200, 경로 길이/100, 3개 로봇의 적층 길이·작업 수와 base까지의 거리/2000 등을 포함한 13값 관측을 사용한다. 새 AssignmentEnv의 관측 길이는 작업 수에 따라 달라지고, 첨부 연속 좌표 wrapper의 행동도 다르다. 같은 Discrete(3) 또는 같은 관측 길이라는 이유만으로 정책·보상 의미가 같다고 볼 수 없다. 새 학습 환경의 고정 관측, reach 행동 마스크, 경로 배정의 의미, Validator 기반 보상, checkpoint 메타데이터·재개 계약을 정한 뒤 별도 checkpoint를 만들어야 한다.

enviornment.py 원본은 아직 확보되지 않았다. 현재 구현은 기존 저장소의 공식 Validator와 AssignmentEnv를 사용한다. 병렬 로봇 배정, 실제 공정의 추가 시간 모델, 다중 seed PPO 학습, 최적성 증명 및 최종 GitHub 제출은 이번 기준 파이프라인 검증과 별도 단계다. 원격 main은 수정하지 않았다.
