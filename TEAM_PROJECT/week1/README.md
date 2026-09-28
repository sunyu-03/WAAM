# 1주차 제출 — 로봇 작업 배정형 WAAM 환경

## 이번 주 완성한 것

1. **개인 환경 `AssignmentEnv` 구현**: 준비된 적층 구간을 로봇 1·2·3 중 누구에게 배정할지 결정한다.
2. **`run_validation` 평가**: 환경이 만든 CSV를 팀 저장소의 검증기에 넣어 실제 PASS/FAIL과 makespan을 확인했다.
3. **의사코드 작성**: `docs/의사코드.md`에 실제 함수 흐름과 같은 순서로 정리했다.

팀원별로 환경을 만든 뒤 비교하는 과제이므로, 팀의 좌표 제어형 환경과 구분되는
**작업 배정형 후보 환경**을 제출한다. 이것이 최선의 환경이라는 결론은 아직 아니다.
PPO 학습 및 여러 형상에 대한 일반화 실험은 이번 완료 범위에 포함하지 않는다.

## 가장 먼저 볼 파일

| 파일 | 역할 |
|---|---|
| `docs/환경설계.md` | 내 환경의 상태·행동·보상·제약, 팀 참고 환경과의 차이 |
| `docs/의사코드.md` | 발표·제출용 의사코드 |
| `docs/검증결과.md` | 실제 실행 결과와 한계, 팀 비교 방법 |
| `assignment_env.py` | 개인 환경 본체: reset, step, candidate, export |
| `run_assignment.py` | 4가지 배정 규칙 실행 → CSV 생성 → run_validation |
| `tasks.sample.json` | 샘플 형상을 4개 구간으로 나눈 작업 목록 |
| `results/week1_verified/` | 개인 환경의 실제 검증 결과 4종 |
| `environment/` | 팀 저장소의 environment 원본 스냅샷, 수정하지 않음 |
| `UPSTREAM.json` | 참고 저장소 커밋과 원본 파일 목록·Git blob 해시 |

`week1_env.py`, `run_week1.py`, `test_week1.py`는 **참고 환경을 이용한 검증기 대조 실험**이다.
개인 제출 환경의 본체는 `assignment_env.py`이다. 대조 실험의 20.16초와 개인 환경의
54.02초는 작업 분할·복귀 조건이 달라 직접 성능 비교하면 안 된다.

## 내 노트북에서 실행

`실행_개인환경.cmd`를 더블클릭한다. 기존 `WAAM/.venv`의 Python을 자동으로 찾는다.
실행마다 `results/날짜_시간/`에 새 결과를 만든다. 기존 검증 증거를 덮어쓰지 않는다.
성공하면 각 방식의 PASS와 makespan이 표시된다.

PowerShell로 직접 실행하려면:

```powershell
cd "$env:USERPROFILE\Desktop\WAAM\TEAM_PROJECT\week1"
& "..\..\.venv\Scripts\python.exe" -B run_assignment.py
& "..\..\.venv\Scripts\python.exe" -B -m pytest test_assignment.py test_week1.py -q
```

평가 결과는 각 방식 폴더의 `validation/validation_report.md` 또는 `summary.json`을 연다.
`input/`에는 검증에 실제 사용한 config.yaml, target.stl, trajectory.csv가 함께 있다.
Validator 화면에서 확인하려면 이 `input` 폴더를 선택한다.

## 팀원의 다른 컴퓨터에서 처음 실행

Python 3.13으로 다음 명령을 실행한다. 검증에 사용한 버전은 Python 3.13.3이다.

```powershell
cd "본인 컴퓨터의 week1 폴더"
py -3.13 -m venv .venv
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
& ".\.venv\Scripts\python.exe" -B run_assignment.py
& ".\.venv\Scripts\python.exe" -B -m pytest test_assignment.py test_week1.py -q
```

의존성 신규 설치 과정은 이번 검증에서 다시 실행하지 않았다. 실행은 기존에 준비된
WAAM 가상환경으로 검증했다. 전체 dependency 목록은 참고 저장소의 lock을 그대로 따른다.
pandas는 원본 `environment/test_gym_wrapper.py` 전체 테스트 실행에만 추가로 필요하다.
이번 개인 환경과 보조 환경의 14개 테스트에는 pandas가 필요하지 않다.

## 다른 형상에 적용하려면

샘플 작업은 샘플 STL 전용이다. 다른 STL을 선택하는 것만으로 작업 경로가 생기지 않는다.
새 형상의 적층 구간 목록을 별도로 준비하고, 낮은 층부터 정렬해야 한다.

```powershell
& "..\..\.venv\Scripts\python.exe" -B run_assignment.py --scenario "새_시나리오_폴더" --tasks "새_작업목록.json"
```

새 작업 목록은 `tasks.sample.json`과 같은 구조이며, 각 start/end는 mm 단위 XYZ이다.
작업 수가 바뀌면 관측 크기도 달라지므로, 향후 하나의 PPO 모델로 여러 크기를 학습하려면
고정 최대 개수·패딩·마스크 등의 추가 설계가 필요하다.

## 참고 코드와 내 구현의 구분

- 참고: https://github.com/Kor-Lazyman/AiNAlgos/tree/e9767f3fc0b1e76bff3b59c68fdc0a3ddb3f3ac5/environment
- 팀 기준: config 해석, 경로 규칙, XY 도달 범위, 충돌·형상 검사, `run_validation`을 재사용했다.
- 개인 구현: 작업 배정형 Gym 환경, 후보 출발 시간 탐색, 관측과 보상, 실행·평가 연결, 테스트·설명 문서.
- 이전에 이 프로젝트에서 만든 배정형 초안을 팀 검증기 버전에 연결해 이번 제출본으로 정리했다.
- 원본 저작권·라이선스는 `environment/LICENSE`, `environment/NOTICE`에 보존했다.
- GitHub에는 아직 업로드하지 않았다. 이 폴더는 로컬 제출 준비본이다.
