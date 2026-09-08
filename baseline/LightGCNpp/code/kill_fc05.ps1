Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -like '*force_c 0.5*' } | ForEach-Object { taskkill /PID $($_.ProcessId) /F }
