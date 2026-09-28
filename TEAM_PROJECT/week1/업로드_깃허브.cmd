@echo off
setlocal
cd /d "%~dp0..\.."

echo [1/4] Keeping unrelated deleted files out of this upload...
git restore --staged -- .gitignore README.md docs/2026-09-20-meeting-notes.md results/README.md src/README.md
if errorlevel 1 goto :failed

echo [2/4] Adding TEAM_PROJECT/week1 only...
git add -- TEAM_PROJECT/week1
if errorlevel 1 goto :failed

echo [3/4] Creating a commit...
git commit -m "feat: add week1 WAAM assignment environment"
if errorlevel 1 goto :failed

echo [4/4] Uploading to GitHub...
git push origin main
if errorlevel 1 goto :failed

echo.
echo SUCCESS: week1 was uploaded to sunyu-03/WAAM.
pause
exit /b 0

:failed
echo.
echo Upload stopped. Take a screenshot of this window and send it to me.
pause
exit /b 1
