@echo off
cd /d "D:\recommendation-system-learning"
set PAPER_INTAKE_DB_PATH=D:\recommendation-system-learning\data\paper_catalog\catalog.sqlite3

rem Bridge Paper Sentinel discoveries into paper_intake before the S1-S5 stages.
rem Sentinel's scheduled task runs with --no-dispatch, so its candidates never
rem reach this repository unless we import them here.
"C:/ProgramData/miniconda3/python.exe" scripts/import_sentinel_candidates.py >> "D:\recommendation-system-learning\data\logs\sentinel_import.log" 2>&1

rem Run S1-S5.  The Python process writes structured records to runs.jsonl via
rem redbook.infrastructure.run_log; do NOT redirect stdout there (that would
rem mix raw JSON with log lines and break log readers).
"C:/ProgramData/miniconda3/python.exe" scripts/daily_paper_ingest.py >> "D:\recommendation-system-learning\data\logs\ingest_stdout.log" 2>&1
