@echo off
set "DIR=C:\Users\xu.yan1\papers\recommendation-system-learning\baseline\PRISM"
cd /d "%DIR%"
echo E15 launch triggered at %DATE% %TIME% > logs\e15_bat_trigger.txt
start "" /MIN "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File "run_e15.ps1" -Groups T,A -Seeds 42,2025
exit /b 0
