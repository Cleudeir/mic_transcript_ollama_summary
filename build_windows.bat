@echo off
REM Build the app as a Windows .exe with PyInstaller
REM Ensure you have icon.ico in the project root

set PYTHON_EXE=%~dp0.venv\Scripts\python.exe
set MAIN_SCRIPT=main.py
set ICON_FILE=icon.ico
set DIST_DIR=dist

%PYTHON_EXE% -m pip install pyinstaller

REM Build with onefile and windowed mode
%PYTHON_EXE% -m PyInstaller --onefile --windowed --icon %ICON_FILE% --name MicrophoneTranscriber %MAIN_SCRIPT%

REM Move .exe to project root for convenience
move %DIST_DIR%\MicrophoneTranscriber.exe .

echo Build complete. Run run_windows.bat to start the app.
