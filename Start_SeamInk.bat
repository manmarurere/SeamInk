@echo off
rem Starts SeamInk (Penumbra auto version) and opens it in the browser. Read-only.
cd /d "%~dp0"
set "PY="
py -3 -c "import sys; sys.exit(sys.version_info < (3, 8))" >nul 2>nul
if not errorlevel 1 set "PY=py -3"
if defined PY goto run
python -c "import sys; sys.exit(sys.version_info < (3, 8))" >nul 2>nul
if not errorlevel 1 set "PY=python"
if defined PY goto run
echo Python 3.8 or later was not found.
echo Install it from https://www.python.org/downloads/ and tick "Add python.exe to PATH".
echo.
echo Python 3.8 以上が見つかりません。
echo https://www.python.org/downloads/ からインストールしてください。
echo インストール時に「Add python.exe to PATH」にチェックを入れてください。
pause
exit /b 1
:run
%PY% -I seamink_server.py %*
if errorlevel 1 pause