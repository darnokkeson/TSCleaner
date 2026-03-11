@echo off
:: Enable delayed variable expansion
setlocal enabledelayedexpansion
:: Folder structure:
::  (root)                         <- this .bat file is here
::  ├── ts_process_folder.bat
::  ├── film1.ts
::  ├── nagranie.ts
::  └── CLEANER\
::      ├── PYTHON_WIN\
::      │   └── python.exe
::      └── SCRIPT\
::          ├── ts_clean_up.py
::          └── ts_watcher.py

:: Root folder is the folder where this .bat file is located
set "ROOT=%~dp0"
:: Path to embedded Python executable
set "PYTHON_EXE=%ROOT%CLEANER\PYTHON_WIN\python.exe"
:: Path to the Python watcher script
set "WATCHER_SCRIPT=%ROOT%CLEANER\SCRIPT\ts_watcher.py"

:: --- Verify that embedded Python exists ---
if not exist "%PYTHON_EXE%" (
    echo  [BLAD] Nie znaleziono Pythona: %PYTHON_EXE%
    echo  Upewnij sie, ze folder PYTHON_WIN istnieje w katalogu CLEANER.
    echo.
    pause
    exit /b 1
)

:: --- Verify that the watcher script exists ---
if not exist "%WATCHER_SCRIPT%" (
    echo  [BLAD] Nie znaleziono skryptu: %WATCHER_SCRIPT%
    echo  Upewnij sie, ze plik ts_watcher.py istnieje w folderze CLEANER\SCRIPT.
    echo.
    pause
    exit /b 1
)

:: --- Launch the Python watcher ---
"%PYTHON_EXE%" "%WATCHER_SCRIPT%"