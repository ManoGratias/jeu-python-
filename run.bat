@echo off
cd /d "%~dp0"
echo Lancement de Cyber Jump...
python main.py
if errorlevel 1 pause
