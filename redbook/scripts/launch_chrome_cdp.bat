@echo off
REM Launch Chrome with remote debugging for CDP automation
REM Close all Chrome windows first, then run this script
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
echo Chrome launched with CDP on port 9222
echo Verify: curl http://localhost:9222/json
