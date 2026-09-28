# VS Code에서 실행하기

1. `week1.code-workspace` 파일을 VS Code로 연다.
2. `Ctrl+Shift+P`를 누르고 `Python: Select Interpreter`를 선택한다.
3. `Enter interpreter path` → `Find`에서 아래 파일을 선택한다.

```text
C:\Users\User\Desktop\WAAM\TEAM_PROJECT\week1\.venv\Scripts\python.exe
```

4. 다시 `Ctrl+Shift+P` → `Developer: Reload Window`로 창을 새로 고친다.
5. 실행은 `실행_개인환경.cmd`를 더블클릭한다.

`assignment_env.py`는 환경의 정의이므로 그것만 실행해도 실험 결과가 나오지는 않는다.
VS Code 터미널에서는 week1 폴더에서 다음을 실행한다.

```powershell
& ".\.venv\Scripts\python.exe" -B run_assignment.py
```

VS Code가 이전에 선택한 Python을 기억하는 경우 기본 설정만 바꿔도 자동 전환되지 않을 수 있다.
위의 2~3번을 한 번 진행하면 된다. `python.analysis.extraPaths`에는 팀 검증기의 소스 위치를 설정했다.
