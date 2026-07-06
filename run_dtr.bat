@echo off
:: Change the directory to exactly where this script is located
cd /d "%~dp0"

:: Launch the app using the virtual environment's windowless Python
start "" "venv\Scripts\pythonw.exe" "main.py"