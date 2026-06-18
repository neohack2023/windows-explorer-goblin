@echo off
setlocal

REM Windows Explorer Goblin launcher
REM Requires AutoHotkey v2 and Python 3.10+.

set SCRIPT_DIR=%~dp0
set AHK_SCRIPT=%SCRIPT_DIR%ahk\ExplorerGoblin.ahk

where py >nul 2>nul
if errorlevel 1 (
  echo [Explorer Goblin] Python launcher 'py' was not found.
  echo Install Python 3.10+ and enable the launcher, then try again.
  pause
  exit /b 1
)

where AutoHotkey64.exe >nul 2>nul
if errorlevel 1 (
  where AutoHotkey.exe >nul 2>nul
  if errorlevel 1 (
    echo [Explorer Goblin] AutoHotkey was not found in PATH.
    echo Double-click ahk\ExplorerGoblin.ahk manually, or add AutoHotkey v2 to PATH.
    pause
    exit /b 1
  ) else (
    start "Explorer Goblin" AutoHotkey.exe "%AHK_SCRIPT%"
  )
) else (
  start "Explorer Goblin" AutoHotkey64.exe "%AHK_SCRIPT%"
)

echo [Explorer Goblin] Running. In Explorer, select a file/folder and press Ctrl + Space.
endlocal
