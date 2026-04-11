@echo off
taskkill /f /im pythonw.exe

cd /d "%~dp0"
call venv\Scripts\activate
pythonw pinkgamer.py