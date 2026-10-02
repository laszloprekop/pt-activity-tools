@echo off
rem Drag .pka files (or a folder) onto this file. Writes <name>_fixed.pka next to each original.
set PKA_FIX_PAUSE=1
where py >nul 2>nul && (py -3 "%~dp0pka_fix.py" %*) || (python "%~dp0pka_fix.py" %*)
