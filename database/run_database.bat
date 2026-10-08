@echo off
REM ============================================================================
REM BATCH RUNNER FOR STUDENT COMPANION DATABASE
REM ============================================================================
powershell -ExecutionPolicy Bypass -File "%~dp0run_database.ps1"
pause

