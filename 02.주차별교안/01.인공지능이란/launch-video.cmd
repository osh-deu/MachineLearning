@echo off
setlocal
set "LECTURE_PY=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\pythonw.exe"
if exist "%LECTURE_PY%" (
  start "" "%LECTURE_PY%" "%~dp0lecture_server.py"
  exit /b
)
where pyw.exe >nul 2>nul
if not errorlevel 1 (
  start "" pyw.exe -3 "%~dp0lecture_server.py"
  exit /b
)
where pythonw.exe >nul 2>nul
if not errorlevel 1 (
  start "" pythonw.exe "%~dp0lecture_server.py"
  exit /b
)
echo Python 3 is required to open this lecture with embedded videos.
pause
